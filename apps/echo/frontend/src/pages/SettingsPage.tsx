import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Cpu,
  HardDrive,
  Languages,
  Mic,
  Monitor,
  Info,
  RefreshCw,
  Check,
  AlertCircle,
  Zap,
} from 'lucide-react';
import { healthApi, settingsApi, WhisperSettings } from '@/services/api';
import { cn } from '@/lib/utils';

export function SettingsPage() {
  const queryClient = useQueryClient();
  const [isSaving, setIsSaving] = useState(false);

  const { data: health, isLoading: isHealthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.check,
    refetchInterval: 30000,
  });

  const { data: whisperSettings, isLoading: isSettingsLoading } = useQuery({
    queryKey: ['whisper-settings'],
    queryFn: settingsApi.getWhisperSettings,
    refetchInterval: 10000,
  });

  const updateSettingsMutation = useMutation({
    mutationFn: settingsApi.updateWhisperSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whisper-settings'] });
      queryClient.invalidateQueries({ queryKey: ['health'] });
    },
  });

  const reloadModelMutation = useMutation({
    mutationFn: settingsApi.reloadModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whisper-settings'] });
      queryClient.invalidateQueries({ queryKey: ['health'] });
    },
  });

  const handleModelChange = async (model: string) => {
    setIsSaving(true);
    try {
      await updateSettingsMutation.mutateAsync({ model });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeviceChange = async (device: string) => {
    setIsSaving(true);
    try {
      await updateSettingsMutation.mutateAsync({ device });
    } finally {
      setIsSaving(false);
    }
  };

  const handleReloadModel = async () => {
    await reloadModelMutation.mutateAsync();
  };

  const isLoading = isHealthLoading || isSettingsLoading;

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
              status={whisperSettings?.model_loaded ? 'loaded' : 'not loaded'}
              ok={whisperSettings?.model_loaded}
            />
            <StatusItem
              label="Active Device"
              status={whisperSettings?.active_device?.toUpperCase() || 'unknown'}
              ok={!!whisperSettings?.active_device}
            />
            <StatusItem
              label="Version"
              status={health?.version || '0.1.0'}
              ok={true}
            />
          </div>
        )}
      </section>

      {/* Whisper Model Selection */}
      <section className="space-y-4">
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-echo-500" />
          Transcription Model
        </h3>

        <div className="glass rounded-lg p-4 space-y-4">
          {/* Model Selector */}
          <div className="space-y-2">
            <label className="text-sm text-slate-400">Whisper Model</label>
            <div className="grid grid-cols-2 gap-2">
              {whisperSettings?.available_models?.map((model) => (
                <ModelButton
                  key={model.name}
                  model={model}
                  selected={whisperSettings?.model === model.name}
                  onClick={() => handleModelChange(model.name)}
                  disabled={isSaving}
                />
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Larger models are more accurate for Quebec French but slower.
              The model will be downloaded on first use.
            </p>
          </div>
        </div>
      </section>

      {/* Device Selection */}
      <section className="space-y-4">
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-echo-500" />
          Compute Device
        </h3>

        <div className="glass rounded-lg p-4 space-y-4">
          {/* Device Selector */}
          <div className="space-y-2">
            <label className="text-sm text-slate-400">Device Preference</label>
            <div className="grid grid-cols-2 gap-2">
              <DeviceButton
                device="auto"
                label="Auto"
                description="Best available"
                selected={whisperSettings?.device === 'auto'}
                available={true}
                onClick={() => handleDeviceChange('auto')}
                disabled={isSaving}
              />
              <DeviceButton
                device="npu"
                label="NPU"
                description={whisperSettings?.device_info?.npu?.name || 'AMD Ryzen AI'}
                selected={whisperSettings?.device === 'npu'}
                available={whisperSettings?.available_devices?.includes('npu')}
                onClick={() => handleDeviceChange('npu')}
                disabled={isSaving}
              />
              <DeviceButton
                device="gpu"
                label="GPU"
                description={whisperSettings?.device_info?.gpu?.name || 'CUDA GPU'}
                selected={whisperSettings?.device === 'gpu'}
                available={whisperSettings?.available_devices?.includes('gpu')}
                onClick={() => handleDeviceChange('gpu')}
                disabled={isSaving}
              />
              <DeviceButton
                device="cpu"
                label="CPU"
                description={whisperSettings?.device_info?.cpu?.name || 'Processor'}
                selected={whisperSettings?.device === 'cpu'}
                available={true}
                onClick={() => handleDeviceChange('cpu')}
                disabled={isSaving}
              />
            </div>
          </div>

          {/* Device Status */}
          <div className="border-t border-slate-700 pt-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Currently using:</span>
              <span className="text-white font-medium">
                {whisperSettings?.active_device?.toUpperCase() || 'Unknown'}
              </span>
            </div>
            {Object.entries(whisperSettings?.device_info || {}).map(([type, info]) => (
              <DeviceStatusRow key={type} type={type} info={info} />
            ))}
          </div>

          {/* Reload Button */}
          <button
            onClick={handleReloadModel}
            disabled={reloadModelMutation.isPending}
            className={cn(
              'w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg',
              'bg-echo-600 hover:bg-echo-700 text-white transition-colors',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            <RefreshCw className={cn('w-4 h-4', reloadModelMutation.isPending && 'animate-spin')} />
            {reloadModelMutation.isPending ? 'Reloading...' : 'Reload Model'}
          </button>
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
            icon={<Languages className="w-4 h-4" />}
            label="Default Language"
            value="Auto-detect (FR-CA / EN)"
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
            <li>Hardware-accelerated transcription (NPU/GPU/CPU)</li>
            <li>French Canadian and English support with bilingual detection</li>
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
  ok?: boolean;
}

function StatusItem({ label, status, ok = true }: StatusItemProps) {
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

interface ModelButtonProps {
  model: {
    name: string;
    size: string;
    speed: string;
    quality: string;
  };
  selected: boolean;
  onClick: () => void;
  disabled?: boolean;
}

function ModelButton({ model, selected, onClick, disabled }: ModelButtonProps) {
  const qualityColors: Record<string, string> = {
    basic: 'text-slate-400',
    good: 'text-blue-400',
    better: 'text-purple-400',
    best: 'text-green-400',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'p-3 rounded-lg border text-left transition-all',
        selected
          ? 'border-echo-500 bg-echo-500/20'
          : 'border-slate-700 hover:border-slate-600',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-white font-medium">{model.name}</span>
        {selected && <Check className="w-4 h-4 text-echo-500" />}
      </div>
      <div className="text-xs text-slate-400 mt-1">
        {model.size} &bull; {model.speed}
      </div>
      <div className={cn('text-xs mt-1', qualityColors[model.quality] || 'text-slate-400')}>
        {model.quality.charAt(0).toUpperCase() + model.quality.slice(1)} quality
      </div>
    </button>
  );
}

interface DeviceButtonProps {
  device: string;
  label: string;
  description: string;
  selected: boolean;
  available: boolean;
  onClick: () => void;
  disabled?: boolean;
}

function DeviceButton({
  device,
  label,
  description,
  selected,
  available,
  onClick,
  disabled,
}: DeviceButtonProps) {
  const deviceIcons: Record<string, React.ReactNode> = {
    auto: <Zap className="w-5 h-5" />,
    npu: <Cpu className="w-5 h-5" />,
    gpu: <Monitor className="w-5 h-5" />,
    cpu: <Cpu className="w-5 h-5" />,
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || !available}
      className={cn(
        'p-3 rounded-lg border text-left transition-all',
        selected
          ? 'border-echo-500 bg-echo-500/20'
          : available
          ? 'border-slate-700 hover:border-slate-600'
          : 'border-slate-800 bg-slate-800/50 opacity-50',
        (disabled || !available) && 'cursor-not-allowed'
      )}
    >
      <div className="flex items-center gap-2">
        <span className={selected ? 'text-echo-500' : 'text-slate-400'}>
          {deviceIcons[device]}
        </span>
        <span className="text-white font-medium">{label}</span>
        {selected && <Check className="w-4 h-4 text-echo-500 ml-auto" />}
        {!available && device !== 'auto' && (
          <AlertCircle className="w-4 h-4 text-red-400 ml-auto" />
        )}
      </div>
      <div className="text-xs text-slate-400 mt-1 truncate">
        {available ? description : 'Not available'}
      </div>
    </button>
  );
}

interface DeviceStatusRowProps {
  type: string;
  info: {
    name: string;
    status: string;
    details?: string;
  };
}

function DeviceStatusRow({ type, info }: DeviceStatusRowProps) {
  const statusColors: Record<string, string> = {
    available: 'text-green-400',
    unavailable: 'text-slate-500',
    error: 'text-red-400',
  };

  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-slate-500 uppercase">{type}</span>
      <div className="flex items-center gap-2">
        <span className="text-slate-400 truncate max-w-[200px]" title={info.name}>
          {info.name}
        </span>
        <span className={statusColors[info.status] || 'text-slate-400'}>
          {info.status}
        </span>
      </div>
    </div>
  );
}
