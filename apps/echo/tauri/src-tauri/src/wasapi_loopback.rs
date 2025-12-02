//! WASAPI Loopback capture for system audio on Windows.
//!
//! Uses the Windows Audio Session API (WASAPI) in loopback mode to capture
//! system audio output. This allows recording what's playing through speakers.

#[cfg(windows)]
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc, Mutex,
};
#[cfg(windows)]
use std::thread;
#[cfg(windows)]
use std::time::Duration;

#[cfg(windows)]
use windows::{
    core::*,
    Win32::Media::Audio::*,
    Win32::System::Com::*,
};

/// Maximum samples to keep in memory (10 minutes at 44.1kHz stereo)
#[cfg(windows)]
const MAX_BUFFER_SAMPLES: usize = 44100 * 2 * 60 * 10;

/// WASAPI Loopback capture handle
#[cfg(windows)]
pub struct LoopbackCapture {
    running: Arc<AtomicBool>,
    samples: Arc<Mutex<Vec<f32>>>,
    sample_rate: u32,
    channels: u16,
    thread_handle: Option<thread::JoinHandle<()>>,
}

#[cfg(windows)]
impl LoopbackCapture {
    /// Create a new loopback capture instance
    pub fn new() -> Result<Self, Box<dyn std::error::Error + Send + Sync>> {
        Ok(Self {
            running: Arc::new(AtomicBool::new(false)),
            samples: Arc::new(Mutex::new(Vec::with_capacity(44100 * 2 * 60))), // 1 minute initial capacity
            sample_rate: 44100,
            channels: 2,
            thread_handle: None,
        })
    }

    /// Start capturing system audio
    pub fn start(&mut self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        if self.running.load(Ordering::SeqCst) {
            return Err("Already capturing".into());
        }

        self.running.store(true, Ordering::SeqCst);

        // Clear previous samples
        if let Ok(mut samples) = self.samples.lock() {
            samples.clear();
        }

        let running = self.running.clone();
        let samples = self.samples.clone();

        let handle = thread::spawn(move || {
            if let Err(e) = Self::capture_loop(running.clone(), samples) {
                log::error!("WASAPI loopback capture error: {}", e);
                running.store(false, Ordering::SeqCst);
            }
        });

        self.thread_handle = Some(handle);
        log::info!("WASAPI loopback capture started");

        Ok(())
    }

    /// Main capture loop running in a separate thread
    fn capture_loop(
        running: Arc<AtomicBool>,
        samples: Arc<Mutex<Vec<f32>>>,
    ) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        unsafe {
            // Initialize COM for this thread
            CoInitializeEx(None, COINIT_MULTITHREADED)?;

            // Get the default audio endpoint (speakers)
            let enumerator: IMMDeviceEnumerator =
                CoCreateInstance(&MMDeviceEnumerator, None, CLSCTX_ALL)?;

            let device = enumerator.GetDefaultAudioEndpoint(eRender, eConsole)?;

            log::info!(
                "WASAPI loopback device: {:?}",
                device.GetId().map(|id| id.to_string()).unwrap_or_default()
            );

            // Activate audio client
            let audio_client: IAudioClient = device.Activate(CLSCTX_ALL, None)?;

            // Get mix format (native format of the device)
            let mix_format = audio_client.GetMixFormat()?;
            let format = &*mix_format;

            log::info!(
                "WASAPI format: {} Hz, {} channels, {} bits",
                format.nSamplesPerSec,
                format.nChannels,
                format.wBitsPerSample
            );

            // Initialize in loopback mode (capture what's being played)
            // Buffer duration: 100ms in 100-nanosecond units
            let buffer_duration = 1_000_000; // 100ms

            audio_client.Initialize(
                AUDCLNT_SHAREMODE_SHARED,
                AUDCLNT_STREAMFLAGS_LOOPBACK,
                buffer_duration,
                0,
                mix_format,
                None,
            )?;

            // Get capture client
            let capture_client: IAudioCaptureClient = audio_client.GetService()?;

            // Start the stream
            audio_client.Start()?;

            log::info!("WASAPI loopback stream started");

            // Capture loop
            while running.load(Ordering::SeqCst) {
                // Sleep to allow buffer to fill
                thread::sleep(Duration::from_millis(10));

                // Get available packets
                let mut packet_length = capture_client.GetNextPacketSize()?;

                while packet_length > 0 && running.load(Ordering::SeqCst) {
                    let mut data_ptr = std::ptr::null_mut();
                    let mut frames_available = 0u32;
                    let mut flags = 0u32;

                    // Get buffer
                    capture_client.GetBuffer(
                        &mut data_ptr,
                        &mut frames_available,
                        &mut flags,
                        None,
                        None,
                    )?;

                    // Check if data is silent
                    let is_silent = (flags & AUDCLNT_BUFFERFLAGS_SILENT.0 as u32) != 0;

                    if !is_silent && frames_available > 0 {
                        // Calculate sample count
                        let sample_count = frames_available as usize * format.nChannels as usize;

                        // Read samples (assuming float32 format which is common for WASAPI)
                        let float_slice = if format.wBitsPerSample == 32 {
                            std::slice::from_raw_parts(data_ptr as *const f32, sample_count)
                        } else {
                            // For other formats, we'd need conversion
                            // For now, skip non-float formats
                            log::warn!("Unsupported audio format: {} bits", format.wBitsPerSample);
                            &[]
                        };

                        // Store samples with memory limit
                        if let Ok(mut samples_guard) = samples.lock() {
                            // Check memory limit
                            if samples_guard.len() + float_slice.len() > MAX_BUFFER_SAMPLES {
                                // Remove oldest samples to make room
                                let remove_count =
                                    (samples_guard.len() + float_slice.len()) - MAX_BUFFER_SAMPLES;
                                samples_guard.drain(0..remove_count.min(samples_guard.len()));
                                log::debug!("Buffer overflow: removed {} samples", remove_count);
                            }

                            samples_guard.extend_from_slice(float_slice);
                        }
                    }

                    // Release buffer
                    capture_client.ReleaseBuffer(frames_available)?;

                    // Get next packet
                    packet_length = capture_client.GetNextPacketSize()?;
                }
            }

            // Stop and cleanup
            audio_client.Stop()?;
            CoUninitialize();

            log::info!("WASAPI loopback capture stopped");
        }

        Ok(())
    }

    /// Stop capturing
    pub fn stop(&mut self) {
        self.running.store(false, Ordering::SeqCst);

        // Wait for thread to finish
        if let Some(handle) = self.thread_handle.take() {
            let _ = handle.join();
        }

        log::info!("WASAPI loopback capture stopped");
    }

    /// Check if currently capturing
    pub fn is_running(&self) -> bool {
        self.running.load(Ordering::SeqCst)
    }

    /// Take all captured samples (drains the buffer)
    pub fn take_samples(&self) -> Vec<f32> {
        if let Ok(mut samples) = self.samples.lock() {
            std::mem::take(&mut *samples)
        } else {
            Vec::new()
        }
    }

    /// Get a copy of current samples without draining
    pub fn get_samples(&self) -> Vec<f32> {
        if let Ok(samples) = self.samples.lock() {
            samples.clone()
        } else {
            Vec::new()
        }
    }

    /// Get current sample count
    pub fn sample_count(&self) -> usize {
        if let Ok(samples) = self.samples.lock() {
            samples.len()
        } else {
            0
        }
    }

    /// Get capture duration in seconds
    pub fn duration_seconds(&self) -> f64 {
        let count = self.sample_count();
        count as f64 / (self.sample_rate as f64 * self.channels as f64)
    }

    /// Get sample rate
    pub fn sample_rate(&self) -> u32 {
        self.sample_rate
    }

    /// Get channel count
    pub fn channels(&self) -> u16 {
        self.channels
    }
}

#[cfg(windows)]
impl Drop for LoopbackCapture {
    fn drop(&mut self) {
        self.stop();
    }
}

// Non-Windows stub implementation
#[cfg(not(windows))]
pub struct LoopbackCapture;

#[cfg(not(windows))]
impl LoopbackCapture {
    pub fn new() -> Result<Self, Box<dyn std::error::Error + Send + Sync>> {
        Err("WASAPI loopback is only available on Windows".into())
    }

    pub fn start(&mut self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        Err("WASAPI loopback is only available on Windows".into())
    }

    pub fn stop(&mut self) {}

    pub fn is_running(&self) -> bool {
        false
    }

    pub fn take_samples(&self) -> Vec<f32> {
        Vec::new()
    }

    pub fn get_samples(&self) -> Vec<f32> {
        Vec::new()
    }

    pub fn sample_count(&self) -> usize {
        0
    }

    pub fn duration_seconds(&self) -> f64 {
        0.0
    }

    pub fn sample_rate(&self) -> u32 {
        44100
    }

    pub fn channels(&self) -> u16 {
        2
    }
}
