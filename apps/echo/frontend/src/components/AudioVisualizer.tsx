/**
 * AudioVisualizer - Neon Oscilloscope Style
 *
 * A modern audio visualizer combining:
 * - Oscilloscope wave line (main visual)
 * - Neon glow effects
 * - Mirror bars at bottom
 * - Auto-gain for sensitivity
 */

import { useEffect, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface AudioVisualizerProps {
  getWaveformData: () => Uint8Array;
  isActive: boolean;
  isPaused?: boolean;
  className?: string;
  sensitivity?: number; // 1-10, default 5
}

// Color scheme
const COLORS = {
  primary: '#00ffff',      // Cyan
  secondary: '#0ea5e9',    // Echo blue
  glow: 'rgba(0, 255, 255, 0.4)',
  grid: 'rgba(255, 255, 255, 0.05)',
  peak: '#ff3366',
  background: 'transparent',
};

export function AudioVisualizer({
  getWaveformData,
  isActive,
  isPaused = false,
  className,
  sensitivity = 6,
}: AudioVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const previousDataRef = useRef<number[]>([]);
  const peakLevelRef = useRef<number>(0);
  const avgLevelRef = useRef<number>(0.1);

  // Amplify weak signals with logarithmic scaling
  const amplify = useCallback((value: number): number => {
    const normalized = Math.abs(value - 128) / 128;
    const gain = sensitivity / 5;
    // Square root for logarithmic feel (boosts quiet sounds)
    const amplified = Math.pow(normalized, 0.4) * gain;
    return Math.min(1, amplified);
  }, [sensitivity]);

  // Linear interpolation for smooth animations
  const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const centerY = height * 0.45; // Slightly above center for wave
    const barAreaY = height * 0.75; // Bottom area for bars

    // Clear with slight fade for trailing effect
    ctx.fillStyle = 'rgba(15, 23, 42, 0.3)'; // slate-900 with alpha
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    const gridLines = 5;
    for (let i = 0; i <= gridLines; i++) {
      const y = (height * 0.9 / gridLines) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Center line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();

    if (!isActive || isPaused) {
      // Draw flat line when inactive
      ctx.strokeStyle = COLORS.secondary;
      ctx.lineWidth = 2;
      ctx.shadowColor = COLORS.glow;
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.moveTo(0, centerY);
      ctx.lineTo(width, centerY);
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Reset animation
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

    // Calculate current level for auto-gain
    let sum = 0;
    let peak = 0;
    for (let i = 0; i < bufferLength; i++) {
      const amplitude = Math.abs(dataArray[i] - 128);
      sum += amplitude;
      if (amplitude > peak) peak = amplitude;
    }
    const currentLevel = sum / bufferLength / 128;

    // Smooth auto-gain adjustment
    avgLevelRef.current = lerp(avgLevelRef.current, Math.max(0.05, currentLevel), 0.05);
    peakLevelRef.current = lerp(peakLevelRef.current, peak / 128, 0.1);

    // Prepare smooth data with interpolation from previous frame
    const smoothData: number[] = [];
    const sliceWidth = width / bufferLength;

    for (let i = 0; i < bufferLength; i++) {
      const raw = amplify(dataArray[i]);
      // Apply auto-gain normalization
      const normalized = raw / Math.max(avgLevelRef.current * 2, 0.1);
      const clamped = Math.min(1, normalized);

      // Smooth with previous frame
      const previous = previousDataRef.current[i] ?? clamped;
      const smoothed = lerp(previous, clamped, 0.4);
      smoothData.push(smoothed);
    }
    previousDataRef.current = smoothData;

    // Draw glow layer (blur effect)
    ctx.save();
    ctx.filter = 'blur(8px)';
    ctx.strokeStyle = COLORS.glow;
    ctx.lineWidth = 6;
    ctx.beginPath();

    for (let i = 0; i < bufferLength; i++) {
      const x = i * sliceWidth;
      const amplitude = smoothData[i];
      const y = centerY + (amplitude * height * 0.35 * (i % 2 === 0 ? 1 : -1));

      if (i === 0) {
        ctx.moveTo(x, centerY);
      }
      // Create smooth wave
      const prevY = i > 0 ? centerY + (smoothData[i-1] * height * 0.35 * ((i-1) % 2 === 0 ? 1 : -1)) : centerY;
      const cpX = x - sliceWidth / 2;
      ctx.quadraticCurveTo(cpX, prevY, x, y);
    }
    ctx.stroke();
    ctx.restore();

    // Draw main oscilloscope line
    const gradient = ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, COLORS.secondary);
    gradient.addColorStop(0.5, COLORS.primary);
    gradient.addColorStop(1, COLORS.secondary);

    ctx.strokeStyle = gradient;
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.shadowColor = COLORS.primary;
    ctx.shadowBlur = 15;

    ctx.beginPath();

    let x = 0;
    for (let i = 0; i < bufferLength; i++) {
      const amplitude = smoothData[i];
      // Create oscillating wave
      const offset = (dataArray[i] - 128) / 128;
      const y = centerY + (offset * amplitude * height * 0.35);

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        // Smooth curve
        const prevX = (i - 1) * sliceWidth;
        const prevOffset = (dataArray[i-1] - 128) / 128;
        const prevY = centerY + (prevOffset * smoothData[i-1] * height * 0.35);
        const cpX = (prevX + x) / 2;
        ctx.quadraticCurveTo(prevX, prevY, cpX, (prevY + y) / 2);
      }
      x += sliceWidth;
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Draw mirror bars at bottom
    const barCount = 32;
    const barWidth = (width / barCount) - 2;
    const barStep = Math.floor(bufferLength / barCount);

    for (let i = 0; i < barCount; i++) {
      // Average data for this bar
      let barSum = 0;
      const start = i * barStep;
      for (let j = start; j < start + barStep && j < bufferLength; j++) {
        barSum += smoothData[j];
      }
      const barHeight = (barSum / barStep) * height * 0.2;

      const barX = i * (barWidth + 2) + 1;
      const barY = barAreaY;

      // Color based on intensity
      const intensity = barSum / barStep;
      if (intensity > 0.8) {
        ctx.fillStyle = COLORS.peak;
      } else {
        const alpha = 0.3 + intensity * 0.5;
        ctx.fillStyle = `rgba(14, 165, 233, ${alpha})`; // echo-500
      }

      // Draw rounded bar
      const radius = barWidth / 2;
      ctx.beginPath();
      ctx.roundRect(barX, barY - barHeight, barWidth, barHeight, [radius, radius, 0, 0]);
      ctx.fill();

      // Reflection (inverted, faded)
      ctx.fillStyle = `rgba(14, 165, 233, ${0.1 + intensity * 0.1})`;
      ctx.beginPath();
      ctx.roundRect(barX, barY + 2, barWidth, barHeight * 0.3, [0, 0, radius, radius]);
      ctx.fill();
    }

    // Draw peak indicator
    if (peakLevelRef.current > 0.7) {
      ctx.fillStyle = COLORS.peak;
      ctx.shadowColor = COLORS.peak;
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(width - 15, 15, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // Continue animation
    animationRef.current = requestAnimationFrame(draw);
  }, [getWaveformData, isActive, isPaused, amplify]);

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

  return (
    <canvas
      ref={canvasRef}
      className={cn('w-full h-full rounded-lg', className)}
      style={{
        background: 'linear-gradient(180deg, rgba(15,23,42,1) 0%, rgba(30,41,59,1) 100%)',
      }}
    />
  );
}

export default AudioVisualizer;
