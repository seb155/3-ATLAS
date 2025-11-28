// Domain: Instrumentation & Automation

export enum IOType {
  AI = 'AI',
  AO = 'AO',
  DI = 'DI',
  DO = 'DO',
  PROFIBUS = 'PROFIBUS',
  ETHERNET = 'ETHERNET',
  HARDWIRED = 'HARDWIRED',
  PROFINET = 'PROFINET',
  ETHERNET_IP = 'ETHERNET_IP',
  MODBUS_TCP = 'MODBUS_TCP'
}

export enum LocationType {
  SITE = 'SITE',
  AREA = 'AREA',
  EHOUSE = 'EHOUSE',
  ROOM = 'ROOM',
  CABINET = 'CABINET',
  JUNCTION_BOX = 'JUNCTION_BOX',
  // UI-specific types (for display purposes)
  MCC = 'MCC',
  PLC = 'PLC',
  PANEL = 'PANEL',
  JB = 'JB',
  RIO = 'RIO'
}

export enum AssetType {
  INSTRUMENT = 'INSTRUMENT',
  MOTOR = 'MOTOR',
  VALVE = 'VALVE',
  CONTROL_SYSTEM = 'CONTROL_SYSTEM',
  PUMP = 'PUMP',
  TANK = 'TANK'
}

// Engineering Domain Data
export interface MechanicalData {
  weightKg?: number;
  material?: string;
  modelNo?: string;
}

export interface ElectricalData {
  voltage?: string;
  powerKW?: number;
  loadType?: string;
  mccId?: string;
}

export interface ProcessData {
  fluid?: string;
  minRange?: number;
  maxRange?: number;
  units?: string;
  setpoint?: string;
}

export interface PurchasingData {
  workPackageId?: string;
  poNumber?: string;
  status?: string;
}

// The Core "Asset" Entity
export interface Asset {
  id: string;
  tag: string;
  description: string;
  type: AssetType;

  // FBS (Functional) - OPTIONAL to match API
  area?: string;
  system?: string;

  // Domains - All optional
  ioType?: string;
  mechanical?: MechanicalData;
  electrical?: ElectricalData;
  process?: ProcessData;
  purchasing?: PurchasingData;

  manufacturerPartId?: string;

  // LBS (Location) - Dynamic Link
  locationId?: string;

  metadata?: any;
}

// The Physical Node (LBS)
export interface PhysicalLocation {
  id: string;
  name: string;
  type: LocationType;
  parentId?: string;
  capacitySlots?: number;
  designHeatDissipation?: number;
  ipRating?: string;
  description?: string;
  metadata?: any;
}

// Generated Cable
export interface Cable {
  id: string;
  tag: string;
  fromId: string;
  fromName: string;
  toId: string;
  toName: string;
  type: 'INSTRUMENT' | 'HOMERUN' | 'SYSTEM' | 'POWER';
}

// Catalog Item
export interface ManufacturerPart {
  id: string;
  manufacturer: string;
  model: string;
  description: string;
  channels?: number;
  ioType?: IOType;
}

export interface RackCalculationResult {
  locationName: string;
  ioType: IOType;
  requiredSignals: number;
  spareIncluded: number;
  cardsRequired: number;
  cardModel: string;
  slotsUsed: number;
  channelsPerCard?: number;
}
