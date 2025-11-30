/**
 * AudioVisualizer - Spotify-Style Bars
 *
 * Simple, clean audio visualization:
 * - Vertical bars (no complex oscilloscope)
 * - Professional auto-gain (RMS-based)
 * - Smooth animations
 */

import { useEffect, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface AudioVisualizerProps {
  getWaveformData: () => Uint8Array;
  isActive: boolean;
  isPaused?: boolean;
  className?: string;
  barCount?: number;
}

// Colors
const BAR_COLOR = '#0ea5e9';      // echo-500
const BAR_ACTIVE = '#38bdf8';     // echo-400 (louder)

export function AudioVisualizer({
  getWaveformData,
  isActive,
  isPaused = false,
  className,
  barCount = 24,
}: AudioVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const previousBarsRef = useRef<number[]>([]);

  // Auto-gain state
  const gainRef = useRef<number>(1);
  const rmsHistoryRef = useRef<number[]>([]);

  // Linear interpolation for smooth animations
  const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

  // Calculate RMS (Root Mean Square) for auto-gain
  const calculateRMS = useCallback((data: Uint8Array): number => {
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      const normalized = (data[i] - 128) / 128;
      sum += normalized * normalized;
    }
    return Math.sqrt(sum / data.length);
  }, []);

  // Professional auto-gain algorithm
  const updateAutoGain = useCallback((rms: number): number => {
    const history = rmsHistoryRef.current;
    history.push(rms);
    if (history.length > 30) history.shift(); // Keep ~0.5s history at 60fps

    // Target level with headroom
    const targetLevel = 0.35;

    // Use average RMS for stability
    const avgRms = history.reduce((a, b) => a + b, 0) / history.length;

    if (avgRms < 0.01) return gainRef.current; // Silence, keep current gain

    // Calculate desired gain
    const desiredGain = targetLevel / avgRms;

    // Clamp gain to reasonable range (0.5x - 4x)
    const clampedGain = Math.min(Math.max(desiredGain, 0.5), 4.0);

    // Smooth transition (attack faster than release)
    const isAttack = clampedGain > gainRef.current;
    const smoothing = isAttack ? 0.15 : 0.05;

    gainRef.current = lerp(gainRef.current, clampedGain, smoothing);
    return gainRef.current;
  }, []);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (!isActive || isPaused) {
      // Draw idle state - flat bars at minimum height
      const barWidth = (width / barCount) * 0.7;
      const gap = (width / barCount) * 0.3;
      const minHeight = 4;

      ctx.fillStyle = BAR_COLOR;
      ctx.globalAlpha = 0.3;

      for (let i = 0; i < barCount; i++) {
        const x = i * (barWidth + gap) + gap / 2;
        const barHeight = minHeight;
        const y = (height - barHeight) / 2;
        const radius = barWidth / 2;

        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, radius);
        ctx.fill();
      }

      ctx.globalAlpha = 1;
      animationRef.current = requestAnimationFrame(draw);
      return;
    }

    // Get audio data
    const dataArray = getWaveformData();
    const bufferLength = dataArray.length;

    if (bufferLength === 0) {
      animationRef.current = requestAnimationFrame(draw);
      return;
    }

    // Calculate RMS and update auto-gain
    const rms = calculateRMS(dataArray);
    const gain = updateAutoGain(rms);

    // Calculate bar values
    const samplesPerBar = Math.floor(bufferLength / barCount);
    const barWidth = (width / barCount) * 0.7;
    const gap = (width / barCount) * 0.3;
    const maxBarHeight = height * 0.85;
    const minBarHeight = 4;

    // Initialize previous bars if needed
    if (previousBarsRef.current.length !== barCount) {
      previousBarsRef.current = new Array(barCount).fill(0);
    }

    for (let i = 0; i < barCount; i++) {
      // Calculate amplitude for this bar (use max in range for more visual punch)
      let maxAmplitude = 0;
      const startSample = i * samplesPerBar;

      for (let j = 0; j < samplesPerBar; j++) {
        const sampleIndex = startSample + j;
        if (sampleIndex < bufferLength) {
          const amplitude = Math.abs(dataArray[sampleIndex] - 128) / 128;
          maxAmplitude = Math.max(maxAmplitude, amplitude);
        }
      }

      // Apply auto-gain
      const amplified = Math.min(maxAmplitude * gain, 1);

      // Smooth with previous frame (decay slower than attack)
      const previous = previousBarsRef.current[i];
      const isRising = amplified > previous;
      const smoothing = isRising ? 0.4 : 0.15;
      const smoothed = lerp(previous, amplified, smoothing);
      previousBarsRef.current[i] = smoothed;

      // Calculate bar dimensions
      const barHeight = Math.max(minBarHeight, smoothed * maxBarHeight);
      const x = i * (barWidth + gap) + gap / 2;
      const y = (height - barHeight) / 2;
      const radius = Math.min(barWidth / 2, barHeight / 2);

      // Color based on intensity
      if (smoothed > 0.7) {
        ctx.fillStyle = BAR_ACTIVE;
        ctx.globalAlpha = 0.9 + smoothed * 0.1;
      } else {
        ctx.fillStyle = BAR_COLOR;
        ctx.globalAlpha = 0.5 + smoothed * 0.4;
      }

      // Draw rounded bar
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, radius);
      ctx.fill();
    }

    ctx.globalAlpha = 1;
    animationRef.current = requestAnimationFrame(draw);
  }, [getWaveformData, isActive, isPaused, barCount, calculateRMS, updateAutoGain]);

  // Handle canvas resize
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.scale(dpr, dpr);
        }
      }
    });

    resizeObserver.observe(canvas);
    return () => resizeObserver.disconnect();
  }, []);

  // Start/stop animation
  useEffect(() => {
    animationRef.current = requestAnimationFrame(draw);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [draw]);

  // Reset gain when recording starts
  useEffect(() => {
    if (isActive && !isPaused) {
      gainRef.current = 1;
      rmsHistoryRef.current = [];
      previousBarsRef.current = [];
    }
  }, [isActive, isPaused]);

  return (
    <canvas
      ref={canvasRef}
      className={cn('w-full h-full', className)}
    />
  );
}

export default AudioVisualizer;
