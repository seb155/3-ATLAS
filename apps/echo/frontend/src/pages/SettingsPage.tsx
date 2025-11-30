import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Cpu, HardDrive, Languages, Mic, Monitor, Info, Check } from 'lucide-react';
import { healthApi } from '@/services/api';
import { cn } from '@/lib/utils';

export function SettingsPage() {
  const { data: health, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.check,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-2xl font-semibold text-white">Settings</h2>

      {/* System Status */}
      <section className="space-y-4">
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <Info className="w-5 h-5 text-echo-500" />
          System Status
        </h3>

        {isLoading ? (
          <div className="glass rounded-lg p-4">
            <div className="animate-pulse flex items-center gap-4">
              <div className="w-3 h-3 rounded-full bg-slate-600" />
              <div className="h-4 bg-slate-600 rounded w-32" />
            </div>
          </div>
        ) : (
          <div className="glass rounded-lg p-4 space-y-4">
            <StatusItem
              label="Database"
              status={health?.database === 'healthy' ? 'connected' : 'disconnected'}
              ok={health?.database === 'healthy'}
            />
            <StatusItem
              label="Whisper Model"
              status={health?.whisper === 'loaded' ? 'loaded' : 'not loaded'}
              ok={health?.whisper === 'loaded'}
            />
            <StatusItem
              label="Version"
              status={health?.version || '0.1.0'}
              ok={true}
            />
          </div>
        )}
      </section>

      {/* Whisper Settings */}
      <section className="space-y-4">
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-echo-500" />
          Transcription
        </h3>

        <div className="glass rounded-lg p-4 space-y-4">
          <SettingRow
            icon={<Cpu className="w-4 h-4" />}
            label="Whisper Model"
            value={health?.details?.whisper_model || 'large-v3'}
          />
          <SettingRow
            icon={<Monitor className="w-4 h-4" />}
            label="Device"
            value={health?.details?.whisper_device || 'cuda'}
          />
          <SettingRow
            icon={<Languages className="w-4 h-4" />}
            label="Default Language"
            value="Auto-detect (FR-CA / EN)"
          />
        </div>
      </section>

      {/* Audio Settings */}
      <section className="space-y-4">
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <Mic className="w-5 h-5 text-echo-500" />
          Audio
        </h3>

        <div className="glass rounded-lg p-4 space-y-4">
          <SettingRow
            icon={<Mic className="w-4 h-4" />}
            label="Sample Rate"
            value="44100 Hz"
          />
          <SettingRow
            icon={<HardDrive className="w-4 h-4" />}
            label="Storage Path"
            value={health?.details?.audio_storage || '/app/data'}
          />
          <SettingRow
            icon={<Monitor className="w-4 h-4" />}
            label="System Audio"
            value="WASAPI Loopback"
          />
        </div>
      </section>

      {/* About */}
      <section className="space-y-4">
        <h3 className="text-lg font-medium text-white">About ECHO</h3>

        <div className="glass rounded-lg p-4 text-sm text-slate-400 space-y-2">
          <p>
            <strong className="text-white">ECHO</strong> is a voice recording and transcription
            application built for the AXIOM platform.
          </p>
          <p>
            Features:
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Microphone and system audio recording (WASAPI loopback)</li>
            <li>GPU-accelerated transcription (faster-whisper)</li>
            <li>French Canadian and English support</li>
            <li>Real-time transcription</li>
            <li>Export to SRT, VTT, TXT, JSON</li>
          </ul>
        </div>
      </section>
    </div>
  );
}

interface StatusItemProps {
  label: string;
  status: string;
  ok: boolean;
}

function StatusItem({ label, status, ok }: StatusItemProps) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        <span className={ok ? 'text-green-400' : 'text-red-400'}>{status}</span>
        <div
          className={cn(
            'w-2 h-2 rounded-full',
            ok ? 'bg-green-500' : 'bg-red-500'
          )}
        />
      </div>
    </div>
  );
}

interface SettingRowProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function SettingRow({ icon, label, value }: SettingRowProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2 text-slate-400">
        {icon}
        <span>{label}</span>
      </div>
      <span className="text-white">{value}</span>
    </div>
  );
}
