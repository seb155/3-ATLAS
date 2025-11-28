
import { Asset, AssetType, PhysicalLocation, ManufacturerPart, IOType, LocationType } from './types';

// Vendor Catalog (Keep for now as it's not yet in backend)
export const CATALOG: ManufacturerPart[] = [
  { id: 'card-ai-8', manufacturer: 'Rockwell', model: '1756-IF8', description: 'Analog Input 8-Ch', channels: 8, ioType: IOType.AI },
  { id: 'card-do-16', manufacturer: 'Rockwell', model: '1756-OB16', description: 'Digital Output 16-Ch', channels: 16, ioType: IOType.DO },
  { id: 'card-di-16', manufacturer: 'Rockwell', model: '1756-IB16', description: 'Digital Input 16-Ch', channels: 16, ioType: IOType.DI },
  { id: 'card-profi', manufacturer: 'Prosoft', model: 'MVI56-PDPMV1', description: 'Profibus Master', channels: 1, ioType: IOType.PROFIBUS },
];

