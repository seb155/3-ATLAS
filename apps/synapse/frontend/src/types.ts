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
    JB = 'JB',  // Alias display name for JUNCTION_BOX
    RIO = 'RIO'
}

export enum AssetType {
    INSTRUMENT = 'INSTRUMENT',
    MOTOR = 'MOTOR',
    VALVE = 'VALVE',
    CONTROL_SYSTEM = 'CONTROL_SYSTEM',
    PUMP = 'PUMP',
    TANK = 'TANK',
    AREA = 'AREA',
    AGITATOR = 'AGITATOR',
    BALL_MILL = 'BALL_MILL',
    LEVEL_TRANSMITTER = 'LEVEL_TRANSMITTER',
    CABLE = 'CABLE'
}

export enum RuleValidationStatus {
    DRAFT = 'DRAFT',
    DEV_VALIDATED = 'DEV_VALIDATED',
    PROD_READY = 'PROD_READY',
    DEPRECATED = 'DEPRECATED'
}

export enum AssetDataStatus {
    FRESH_IMPORT = 'FRESH_IMPORT',
    IN_REVIEW = 'IN_REVIEW',
    VALIDATED = 'VALIDATED',
    ERROR = 'ERROR'
}

export interface PhysicalLocation {
    id: string;
    name: string;
    type: LocationType;
    parentId?: string;
    description?: string;
    metadata?: Record<string, unknown>;
    [key: string]: unknown;
}

export interface Asset {
    id: string;
    tag: string;
    description: string;
    type: AssetType;
    area?: string;
    system?: string;
    ioType?: string;
    locationId?: string;
    packageId?: string;
    manufacturerPartId?: string;
    dataStatus?: AssetDataStatus;

    electrical?: {
        voltage?: string;
        powerKW?: number;
        loadType?: string;
    };

    process?: {
        fluid?: string;
        minRange?: number;
        maxRange?: number;
        units?: string;
    };

    purchasing?: {
        workPackageId?: string;
        status?: string;
    };

    metadata?: Record<string, unknown>;
}

export enum IOType {
    DI = 'DI',
    DO = 'DO',
    AI = 'AI',
    AO = 'AO',
    RTD = 'RTD',
    TC = 'TC',
    PROFIBUS = 'PROFIBUS',
    HART = 'HART',
    MODBUS = 'MODBUS'
}

export interface Cable {
    id: string;
    tag: string;
    fromId: string;
    fromName: string;
    toId: string;
    toName: string;
    type: 'INSTRUMENT' | 'HOMERUN' | 'SYSTEM' | 'POWER';
}

export interface ManufacturerPart {
    id: string;
    model: string;
    manufacturer: string;
    ioType?: string;
    channels?: number;
    description?: string;
}

export interface RackCalculationResult {
    locationName: string;
    ioType: IOType;
    requiredSignals: number;
    spareIncluded: number;
    cardsRequired: number;
    cardModel: string;
    slotsUsed: number;
    channelsPerCard: number;
}
