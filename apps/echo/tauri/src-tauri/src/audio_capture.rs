//! Audio capture module using cpal for cross-platform audio I/O.
//!
//! Supports:
//! - Microphone input
//! - System audio (WASAPI loopback on Windows)
//! - Both sources mixed together

use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use hound::{WavSpec, WavWriter};
use std::fs::File;
use std::io::BufWriter;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::time::Instant;

#[cfg(windows)]
use crate::wasapi_loopback::LoopbackCapture;

/// Audio source type
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AudioSource {
    Microphone,
    System,
    Both,
}

/// Recording result
pub struct RecordingResult {
    pub recording_id: String,
    pub duration_seconds: f64,
    pub file_size_bytes: u64,
    pub output_path: String,
}

/// Recording status
pub struct RecordingStatus {
    pub is_recording: bool,
    pub recording_id: Option<String>,
    pub duration_seconds: f64,
    pub source: Option<String>,
}

/// Available audio devices
pub struct AudioDevices {
    pub input_devices: Vec<AudioDevice>,
    pub output_devices: Vec<AudioDevice>,
}

pub struct AudioDevice {
    pub id: String,
    pub name: String,
    pub is_default: bool,
}

/// Audio capture state
struct CaptureState {
    recording_id: String,
    source: AudioSource,
    output_path: PathBuf,
    start_time: Instant,
    input_samples: Arc<Mutex<Vec<f32>>>,
}

/// Main audio capture struct
pub struct AudioCapture {
    state: Option<CaptureState>,
    #[allow(dead_code)]
    input_stream: Option<cpal::Stream>,
    #[cfg(windows)]
    loopback_capture: Option<LoopbackCapture>,
    #[cfg(not(windows))]
    #[allow(dead_code)]
    output_stream: Option<cpal::Stream>,
}

impl AudioCapture {
    pub fn new() -> Self {
        Self {
            state: None,
            input_stream: None,
            #[cfg(windows)]
            loopback_capture: None,
            #[cfg(not(windows))]
            output_stream: None,
        }
    }

    /// List available audio devices
    pub fn list_devices() -> Result<AudioDevices, Box<dyn std::error::Error>> {
        let host = cpal::default_host();

        let mut input_devices = Vec::new();
        let mut output_devices = Vec::new();

        // Get default devices
        let default_input = host.default_input_device();
        let default_output = host.default_output_device();

        // List input devices
        if let Ok(devices) = host.input_devices() {
            for device in devices {
                if let Ok(name) = device.name() {
                    let is_default = default_input
                        .as_ref()
                        .map(|d| d.name().ok() == Some(name.clone()))
                        .unwrap_or(false);

                    input_devices.push(AudioDevice {
                        id: name.clone(),
                        name,
                        is_default,
                    });
                }
            }
        }

        // List output devices (for loopback)
        if let Ok(devices) = host.output_devices() {
            for device in devices {
                if let Ok(name) = device.name() {
                    let is_default = default_output
                        .as_ref()
                        .map(|d| d.name().ok() == Some(name.clone()))
                        .unwrap_or(false);

                    output_devices.push(AudioDevice {
                        id: name.clone(),
                        name,
                        is_default,
                    });
                }
            }
        }

        Ok(AudioDevices {
            input_devices,
            output_devices,
        })
    }

    /// Start recording audio
    pub fn start(
        &mut self,
        recording_id: String,
        source: AudioSource,
        output_path: String,
    ) -> Result<(), Box<dyn std::error::Error>> {
        if self.state.is_some() {
            return Err("Already recording".into());
        }

        let host = cpal::default_host();

        // Create capture state with shared sample buffer
        let input_samples = Arc::new(Mutex::new(Vec::with_capacity(44100 * 2 * 60))); // 1 min capacity

        self.state = Some(CaptureState {
            recording_id,
            source,
            output_path: PathBuf::from(&output_path),
            start_time: Instant::now(),
            input_samples: input_samples.clone(),
        });

        // Setup streams based on source
        match source {
            AudioSource::Microphone => {
                self.setup_input_stream(&host)?;
            }
            AudioSource::System => {
                self.setup_loopback_stream(&host)?;
            }
            AudioSource::Both => {
                self.setup_input_stream(&host)?;
                self.setup_loopback_stream(&host)?;
            }
        }

        log::info!("Started recording: {} -> {}",
            self.state.as_ref().unwrap().recording_id,
            output_path
        );

        Ok(())
    }

    /// Setup microphone input stream
    fn setup_input_stream(&mut self, host: &cpal::Host) -> Result<(), Box<dyn std::error::Error>> {
        let device = host
            .default_input_device()
            .ok_or("No input device available")?;

        let config = device.default_input_config()?;

        log::info!("Input device: {}", device.name()?);
        log::info!("Input config: {:?}", config);

        // Get the shared sample buffer from state
        let samples = self
            .state
            .as_ref()
            .map(|s| s.input_samples.clone())
            .ok_or("No capture state")?;

        // Memory limit: 10 minutes at 44.1kHz stereo
        const MAX_SAMPLES: usize = 44100 * 2 * 60 * 10;

        let stream = device.build_input_stream(
            &config.into(),
            move |data: &[f32], _: &cpal::InputCallbackInfo| {
                if let Ok(mut samples_guard) = samples.lock() {
                    // Check memory limit
                    if samples_guard.len() + data.len() > MAX_SAMPLES {
                        // Remove oldest samples to make room
                        let remove = (samples_guard.len() + data.len()) - MAX_SAMPLES;
                        samples_guard.drain(0..remove.min(samples_guard.len()));
                    }
                    samples_guard.extend_from_slice(data);
                }
            },
            |err| {
                log::error!("Input stream error: {}", err);
            },
            None,
        )?;

        stream.play()?;
        self.input_stream = Some(stream);

        Ok(())
    }

    /// Setup WASAPI loopback stream (system audio)
    #[cfg(windows)]
    fn setup_loopback_stream(&mut self, _host: &cpal::Host) -> Result<(), Box<dyn std::error::Error>> {
        // Use native WASAPI loopback capture
        let mut loopback = LoopbackCapture::new()
            .map_err(|e| format!("Failed to create loopback capture: {}", e))?;

        loopback
            .start()
            .map_err(|e| format!("Failed to start loopback capture: {}", e))?;

        self.loopback_capture = Some(loopback);
        log::info!("WASAPI loopback capture started");

        Ok(())
    }

    /// Setup WASAPI loopback stream (system audio) - non-Windows stub
    #[cfg(not(windows))]
    fn setup_loopback_stream(&mut self, host: &cpal::Host) -> Result<(), Box<dyn std::error::Error>> {
        let device = host
            .default_output_device()
            .ok_or("No output device available")?;

        log::info!("Loopback device: {}", device.name()?);
        log::warn!("WASAPI loopback is only available on Windows");

        Ok(())
    }

    /// Stop recording and save the file
    pub fn stop(&mut self) -> Result<RecordingResult, Box<dyn std::error::Error>> {
        let state = self.state.take().ok_or("Not recording")?;

        // Stop streams
        self.input_stream = None;

        // Get input samples
        let input_samples = if let Ok(samples) = state.input_samples.lock() {
            samples.clone()
        } else {
            Vec::new()
        };

        // Get loopback samples if available
        #[cfg(windows)]
        let loopback_samples = if let Some(ref mut loopback) = self.loopback_capture {
            loopback.stop();
            loopback.take_samples()
        } else {
            Vec::new()
        };

        #[cfg(not(windows))]
        let loopback_samples: Vec<f32> = Vec::new();

        #[cfg(windows)]
        {
            self.loopback_capture = None;
        }

        #[cfg(not(windows))]
        {
            self.output_stream = None;
        }

        let duration = state.start_time.elapsed().as_secs_f64();

        // Combine samples (if both sources)
        let combined_samples = match state.source {
            AudioSource::Microphone => input_samples,
            AudioSource::System => loopback_samples,
            AudioSource::Both => {
                // Mix both sources
                let max_len = input_samples.len().max(loopback_samples.len());
                let mut mixed = Vec::with_capacity(max_len);

                for i in 0..max_len {
                    let input = input_samples.get(i).copied().unwrap_or(0.0);
                    let loopback = loopback_samples.get(i).copied().unwrap_or(0.0);
                    // Simple mix: average both sources, clamp to prevent clipping
                    let mixed_sample = ((input + loopback) / 2.0).clamp(-1.0, 1.0);
                    mixed.push(mixed_sample);
                }

                mixed
            }
        };

        // Write WAV file
        let spec = WavSpec {
            channels: 2,
            sample_rate: 44100,
            bits_per_sample: 16,
            sample_format: hound::SampleFormat::Int,
        };

        let file = File::create(&state.output_path)?;
        let writer = BufWriter::new(file);
        let mut wav_writer = WavWriter::new(writer, spec)?;

        // Convert f32 samples to i16 and write
        for &sample in &combined_samples {
            let sample_i16 = (sample.clamp(-1.0, 1.0) * i16::MAX as f32) as i16;
            wav_writer.write_sample(sample_i16)?;
        }

        wav_writer.finalize()?;

        // Get file size
        let file_size = std::fs::metadata(&state.output_path)?.len();

        log::info!(
            "Stopped recording: {} ({:.2}s, {} bytes, {} samples)",
            state.recording_id,
            duration,
            file_size,
            combined_samples.len()
        );

        Ok(RecordingResult {
            recording_id: state.recording_id,
            duration_seconds: duration,
            file_size_bytes: file_size,
            output_path: state.output_path.to_string_lossy().to_string(),
        })
    }

    /// Get current recording status
    pub fn status(&self) -> RecordingStatus {
        match &self.state {
            Some(state) => RecordingStatus {
                is_recording: true,
                recording_id: Some(state.recording_id.clone()),
                duration_seconds: state.start_time.elapsed().as_secs_f64(),
                source: Some(format!("{:?}", state.source)),
            },
            None => RecordingStatus {
                is_recording: false,
                recording_id: None,
                duration_seconds: 0.0,
                source: None,
            },
        }
    }
}

impl Default for AudioCapture {
    fn default() -> Self {
        Self::new()
    }
}

// Implement serde for the result types
impl serde::Serialize for RecordingResult {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut state = serializer.serialize_struct("RecordingResult", 4)?;
        state.serialize_field("recording_id", &self.recording_id)?;
        state.serialize_field("duration_seconds", &self.duration_seconds)?;
        state.serialize_field("file_size_bytes", &self.file_size_bytes)?;
        state.serialize_field("output_path", &self.output_path)?;
        state.end()
    }
}

impl serde::Serialize for RecordingStatus {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut state = serializer.serialize_struct("RecordingStatus", 4)?;
        state.serialize_field("is_recording", &self.is_recording)?;
        state.serialize_field("recording_id", &self.recording_id)?;
        state.serialize_field("duration_seconds", &self.duration_seconds)?;
        state.serialize_field("source", &self.source)?;
        state.end()
    }
}

impl serde::Serialize for AudioDevices {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut state = serializer.serialize_struct("AudioDevices", 2)?;
        state.serialize_field("input_devices", &self.input_devices)?;
        state.serialize_field("output_devices", &self.output_devices)?;
        state.end()
    }
}

impl serde::Serialize for AudioDevice {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut state = serializer.serialize_struct("AudioDevice", 3)?;
        state.serialize_field("id", &self.id)?;
        state.serialize_field("name", &self.name)?;
        state.serialize_field("is_default", &self.is_default)?;
        state.end()
    }
}
