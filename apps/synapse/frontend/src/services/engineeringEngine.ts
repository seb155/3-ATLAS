
import { Asset, PhysicalLocation, Cable, IOType, RackCalculationResult, ManufacturerPart, LocationType } from '../types';

export class CabinetPlanner {

  private static getLocationMap(locations: PhysicalLocation[]) {
    return new Map(locations.map(l => [l.id, l]));
  }

  // Generate FBS Tree
  static getFBSTree(assets: Asset[]) {
    if (!Array.isArray(assets)) return [];
    const areas = Array.from(new Set(assets.map(i => i.area))).sort();
    return areas.map(area => {
      const areaAssets = assets.filter(i => i.area === area);
      const systems = Array.from(new Set(areaAssets.map(i => i.system))).sort();
      return {
        id: `area-${area}`,
        name: `Area ${area}`,
        type: 'AREA',
        children: systems.map(sys => ({
          id: `sys-${area}-${sys}`,
          name: sys,
          type: 'SYSTEM',
          originalSystem: sys,
          originalArea: area
        }))
      };
    });
  }

  // Generate WBS Tree (Work Packages)
  static getWBSTree(assets: Asset[]) {
    if (!Array.isArray(assets)) return [];
    const pkgs = Array.from(new Set(assets.map(a => a.purchasing?.workPackageId || 'Unassigned'))).sort();

    return pkgs.map(pkg => {
      return {
        id: `pkg-${pkg}`,
        name: pkg,
        type: 'PACKAGE',
        children: [] // Packages are usually flat or have sub-packages, keeping flat for PoC
      };
    });
  }

  // Cable Generation (Updated for Asset type)
  static generateCableSchedule(assets: Asset[], locations: PhysicalLocation[]): Cable[] {
    const cables: Cable[] = [];
    const locationMap = this.getLocationMap(locations);

    // 1. Asset Cables
    assets.forEach(inst => {
      if (inst.locationId && locationMap.has(inst.locationId)) {
        const parentLoc = locationMap.get(inst.locationId)!;
        cables.push({
          id: `C-${inst.tag}`,
          tag: `C-${inst.tag}`,
          fromId: inst.id,
          fromName: inst.tag,
          toId: parentLoc.id,
          toName: parentLoc.name,
          type: 'INSTRUMENT'
        });
      }
    });

    // 2. Inter-Location Cables
    locations.forEach(loc => {
      if (loc.parentId && locationMap.has(loc.parentId)) {
        const cableWorthyTypes = [
          LocationType.JB, LocationType.PANEL, LocationType.RIO, LocationType.PLC, LocationType.MCC
        ];

        if (cableWorthyTypes.includes(loc.type)) {
          const parentLoc = locationMap.get(loc.parentId)!;
          const isUsed = assets.some(i => i.locationId === loc.id) ||
            this.hasDescendantAssets(loc.id, locations, assets);
          const alwaysCable = [LocationType.PANEL, LocationType.PLC, LocationType.RIO, LocationType.MCC].includes(loc.type);

          if (isUsed || alwaysCable) {
            let cableType: 'HOMERUN' | 'SYSTEM' | 'POWER' = 'HOMERUN';
            if (loc.type === LocationType.MCC) cableType = 'POWER';
            else if (loc.type === LocationType.PLC) cableType = 'POWER';
            else if (loc.type === LocationType.PANEL) cableType = 'SYSTEM';

            cables.push({
              id: `CB-${loc.name}`,
              tag: `CB-${loc.name}`,
              fromId: loc.id,
              fromName: loc.name,
              toId: parentLoc.id,
              toName: parentLoc.name,
              type: cableType
            });
          }
        }
      }
    });
    return cables;
  }

  static hasDescendantAssets(rootId: string, locations: PhysicalLocation[], assets: Asset[]): boolean {
    const descendants = this.getDescendantLocationIds(rootId, locations);
    return assets.some(i => i.locationId && descendants.includes(i.locationId));
  }

  static getDescendantLocationIds(rootId: string, locations: PhysicalLocation[]): string[] {
    const children = locations.filter(l => l.parentId === rootId);
    let ids = children.map(c => c.id);
    children.forEach(c => {
      ids = [...ids, ...this.getDescendantLocationIds(c.id, locations)];
    });
    return ids;
  }

  static calculateRacks(
    assets: Asset[],
    locationId: string,
    locations: PhysicalLocation[],
    sparePercentage: number,
    catalog: ManufacturerPart[]
  ): RackCalculationResult[] {

    const descendantIds = this.getDescendantLocationIds(locationId, locations);
    const targetLocations = [locationId, ...descendantIds];

    const relevantAssets = assets.filter(i =>
      i.locationId && targetLocations.includes(i.locationId)
    );

    const ioCounts: Record<string, number> = {};
    relevantAssets.forEach(inst => {
      ioCounts[inst.ioType] = (ioCounts[inst.ioType] || 0) + 1;
    });

    const results: RackCalculationResult[] = [];
    for (const [type, count] of Object.entries(ioCounts)) {
      const card = catalog.find(p => p.ioType === type && p.channels);
      if (!card || !card.channels) continue;

      const spareMultiplier = 1 + (sparePercentage / 100);
      const requiredWithSpare = Math.ceil(count * spareMultiplier);
      const cardsNeeded = Math.ceil(requiredWithSpare / card.channels);

      results.push({
        locationName: locationId,
        ioType: type as IOType,
        requiredSignals: count,
        spareIncluded: requiredWithSpare,
        cardsRequired: cardsNeeded,
        cardModel: card.model,
        slotsUsed: cardsNeeded,
        channelsPerCard: card.channels
      });
    }
    return results;
  }

  static getSignalNodes(asset: Asset, locations: PhysicalLocation[]) {
    const locationMap = this.getLocationMap(locations);
    const connectedLoc = asset.locationId ? locationMap.get(asset.locationId) : null;
    // Connection string is appended to name to show destination in Tree
    const connectionString = connectedLoc ? ` -> ${connectedLoc.name}` : '';

    const signals = [];
    // Use assetId in the signal node to simplify lookup later
    if (asset.ioType === IOType.PROFIBUS) {
      signals.push({
        id: `sig-${asset.id}-stat`,
        name: `Status Word${connectionString}`,
        type: 'SIGNAL',
        assetId: asset.id
      });
      signals.push({
        id: `sig-${asset.id}-ctrl`,
        name: `Control Word${connectionString}`,
        type: 'SIGNAL',
        assetId: asset.id
      });
    } else {
      signals.push({
        id: `sig-${asset.id}-io`,
        name: `${asset.ioType} Signal${connectionString}`,
        type: 'SIGNAL',
        assetId: asset.id
      });
    }
    return signals;
  }
}
