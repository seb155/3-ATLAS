/**
 * WaveformVisualizer Component
 *
 * Real-time audio waveform visualization using canvas.
 * Displays audio amplitude as animated bars.
 */

import { useEffect, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface WaveformVisualizerProps {
  getWaveformData: () => Uint8Array;
  isRecording: boolean;
  isPaused?: boolean;
  className?: string;
  barColor?: string;
  barCount?: number;
}

export function WaveformVisualizer({
  getWaveformData,
  isRecording,
  isPaused = false,
  className,
  barColor = '#0ea5e9', // echo-500
  barCount = 32,
}: WaveformVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = 'transparent';
    ctx.clearRect(0, 0, width, height);

    if (!isRecording || isPaused) {
      // Draw flat line when not recording or paused
      ctx.fillStyle = '#475569'; // slate-600
      const barWidth = width / barCount - 2;
      const centerY = height / 2;
      const minHeight = 4;

      for (let i = 0; i < barCount; i++) {
        const x = i * (barWidth + 2) + 1;
        ctx.fillRect(x, centerY - minHeight / 2, barWidth, minHeight);
      }
      return;
    }

    // Get waveform data
    const dataArray = getWaveformData();
    const bufferLength = dataArray.length;

    // Calculate bar dimensions
    const barWidth = width / barCount - 2;
    const step = Math.floor(bufferLength / barCount);

    ctx.fillStyle = barColor;

    for (let i = 0; i < barCount; i++) {
      // Average the data points for this bar
      let sum = 0;
      const start = i * step;
      const end = Math.min(start + step, bufferLength);

      for (let j = start; j < end; j++) {
        // Convert from 0-255 to -128 to 127, then take absolute value
        sum += Math.abs(dataArray[j] - 128);
      }

      const average = sum / (end - start);

      // Scale to bar height (0-128 maps to minHeight to height)
      const minHeight = 4;
      const maxHeight = height - 4;
      const barHeight = Math.max(minHeight, (average / 128) * maxHeight);

      // Draw bar centered vertically
      const x = i * (barWidth + 2) + 1;
      const y = (height - barHeight) / 2;

      // Rounded rectangle
      const radius = barWidth / 2;
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, radius);
      ctx.fill();
    }

    // Continue animation loop
    animationFrameRef.current = requestAnimationFrame(draw);
  }, [getWaveformData, isRecording, isPaused, barColor, barCount]);

  useEffect(() => {
    if (isRecording && !isPaused) {
      animationFrameRef.current = requestAnimationFrame(draw);
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRecording, isPaused, draw]);

  // Handle canvas resize
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        canvas.width = width * window.devicePixelRatio;
        canvas.height = height * window.devicePixelRatio;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
      }
    });

    resizeObserver.observe(canvas);
    return () => resizeObserver.disconnect();
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={cn(
        'w-full h-full',
        className
      )}
      style={{
        width: '100%',
        height: '100%',
      }}
    />
  );
}

// Simple bar-based visualizer (alternative, no canvas)
interface SimpleWaveformProps {
  getWaveformData: () => Uint8Array;
  isRecording: boolean;
  isPaused?: boolean;
  className?: string;
  barCount?: number;
}

export function SimpleWaveform({
  getWaveformData,
  isRecording,
  isPaused = false,
  className,
  barCount = 20,
}: SimpleWaveformProps) {
  const barsRef = useRef<HTMLDivElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  const updateBars = useCallback(() => {
    if (!barsRef.current) return;

    const bars = barsRef.current.children;
    if (!isRecording || isPaused) {
      // Set all bars to minimum height
      for (let i = 0; i < bars.length; i++) {
        (bars[i] as HTMLElement).style.height = '20%';
      }
      return;
    }

    const dataArray = getWaveformData();
    const step = Math.floor(dataArray.length / barCount);

    for (let i = 0; i < bars.length; i++) {
      let sum = 0;
      const start = i * step;
      const end = Math.min(start + step, dataArray.length);

      for (let j = start; j < end; j++) {
        sum += Math.abs(dataArray[j] - 128);
      }

      const average = sum / (end - start);
      const heightPercent = Math.max(20, (average / 128) * 100);
      (bars[i] as HTMLElement).style.height = `${heightPercent}%`;
    }

    animationFrameRef.current = requestAnimationFrame(updateBars);
  }, [getWaveformData, isRecording, isPaused, barCount]);

  useEffect(() => {
    if (isRecording && !isPaused) {
      animationFrameRef.current = requestAnimationFrame(updateBars);
    } else {
      updateBars(); // Update once to show flat line
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRecording, isPaused, updateBars]);

  return (
    <div
      ref={barsRef}
      className={cn(
        'flex items-center justify-center gap-1 h-full',
        className
      )}
    >
      {Array.from({ length: barCount }).map((_, i) => (
        <div
          key={i}
          className="w-1 bg-echo-500 rounded-full transition-[height] duration-75"
          style={{ height: '20%' }}
        />
      ))}
    </div>
  );
}
