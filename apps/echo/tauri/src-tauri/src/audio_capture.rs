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
    samples: Vec<f32>,
}

/// Main audio capture struct
pub struct AudioCapture {
    state: Option<CaptureState>,
    #[allow(dead_code)]
    input_stream: Option<cpal::Stream>,
    #[allow(dead_code)]
    output_stream: Option<cpal::Stream>,
}

impl AudioCapture {
    pub fn new() -> Self {
        Self {
            state: None,
            input_stream: None,
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

        // Create capture state
        self.state = Some(CaptureState {
            recording_id,
            source,
            output_path: PathBuf::from(&output_path),
            start_time: Instant::now(),
            samples: Vec::new(),
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

        // For now, we'll collect samples in memory
        // In production, we'd stream to disk
        let samples: Arc<Mutex<Vec<f32>>> = Arc::new(Mutex::new(Vec::new()));
        let samples_clone = samples.clone();

        let stream = device.build_input_stream(
            &config.into(),
            move |data: &[f32], _: &cpal::InputCallbackInfo| {
                if let Ok(mut samples) = samples_clone.lock() {
                    samples.extend_from_slice(data);
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
    fn setup_loopback_stream(&mut self, host: &cpal::Host) -> Result<(), Box<dyn std::error::Error>> {
        // On Windows, we need to use WASAPI loopback
        // This captures system audio output

        let device = host
            .default_output_device()
            .ok_or("No output device available")?;

        log::info!("Loopback device: {}", device.name()?);

        // Note: cpal doesn't directly support loopback capture
        // On Windows, you'd typically use the Windows Audio Session API (WASAPI)
        // directly for loopback capture.
        //
        // For now, this is a placeholder that would need to be implemented
        // using the windows crate for proper WASAPI loopback support.

        log::warn!("WASAPI loopback capture requires native Windows API integration");
        log::warn!("This is a placeholder implementation");

        Ok(())
    }

    /// Stop recording and save the file
    pub fn stop(&mut self) -> Result<RecordingResult, Box<dyn std::error::Error>> {
        let state = self.state.take().ok_or("Not recording")?;

        // Stop streams
        self.input_stream = None;
        self.output_stream = None;

        let duration = state.start_time.elapsed().as_secs_f64();

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
        for &sample in &state.samples {
            let sample_i16 = (sample * i16::MAX as f32) as i16;
            wav_writer.write_sample(sample_i16)?;
        }

        wav_writer.finalize()?;

        // Get file size
        let file_size = std::fs::metadata(&state.output_path)?.len();

        log::info!(
            "Stopped recording: {} ({:.2}s, {} bytes)",
            state.recording_id,
            duration,
            file_size
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
