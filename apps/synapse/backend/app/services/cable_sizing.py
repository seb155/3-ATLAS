"""
Cable Sizing Service
Based on Canadian Electrical Code (CEC) Standards.

Features:
- Motor FLC Lookup (Table 44)
- Ampacity Lookup (Table 2)
- Voltage Drop Calculation
"""

import math


class CableSizingService:
    # CEC Table 44 - Three Phase AC Motor Full Load Current (Approximate for 600V)
    # HP -> Amps at 575V
    MOTOR_FLC_575V = {
        1: 1.4,
        1.5: 2.0,
        2: 2.7,
        3: 3.9,
        5: 6.1,
        7.5: 9.0,
        10: 11.0,
        15: 17.0,
        20: 22.0,
        25: 27.0,
        30: 32.0,
        40: 41.0,
        50: 52.0,
        60: 62.0,
        75: 77.0,
        100: 99.0,
        125: 125.0,
        150: 144.0,
        200: 192.0,
    }

    # CEC Table 2 - Allowable Ampacity for Copper Conductors (Not more than 3 conductors)
    # Size (AWG/kcmil) -> {75C: Amps, 90C: Amps}
    # We typically use 75C column for termination limits, even if wire is 90C.
    AMPACITY_TABLE_COPPER = {
        "14 AWG": 20,
        "12 AWG": 25,
        "10 AWG": 35,
        "8 AWG": 50,
        "6 AWG": 65,
        "4 AWG": 85,
        "3 AWG": 100,
        "2 AWG": 115,
        "1 AWG": 130,
        "1/0 AWG": 150,
        "2/0 AWG": 175,
        "3/0 AWG": 200,
        "4/0 AWG": 230,
        "250 kcmil": 255,
        "350 kcmil": 310,
        "500 kcmil": 380,
        "750 kcmil": 475,
    }

    # Resistance (Ohms/km) at 75C for AC (Approximate generic values for calculation)
    # Size -> Ohms/km
    CABLE_IMPEDANCE = {
        "14 AWG": 10.5,
        "12 AWG": 6.6,
        "10 AWG": 4.1,
        "8 AWG": 2.6,
        "6 AWG": 1.6,
        "4 AWG": 1.0,
        "3 AWG": 0.8,
        "2 AWG": 0.6,
        "1 AWG": 0.5,
        "1/0 AWG": 0.4,
        "2/0 AWG": 0.3,
        "3/0 AWG": 0.25,
        "4/0 AWG": 0.2,
        "250 kcmil": 0.17,
        "350 kcmil": 0.12,
        "500 kcmil": 0.09,
        "750 kcmil": 0.06,
    }

    @staticmethod
    def get_motor_flc(hp: float, voltage: str = "600V") -> float:
        """
        Get Full Load Current (FLC) for a 3-phase motor.
        Currently supports 575V/600V only (standard for this project).
        """
        # Simple interpolation or nearest match could be added,
        # but for MVP we match exact standard sizes or round up.

        # Find next largest HP in table
        sorted_hps = sorted(CableSizingService.MOTOR_FLC_575V.keys())
        for standard_hp in sorted_hps:
            if standard_hp >= hp:
                return CableSizingService.MOTOR_FLC_575V[standard_hp]

        # Fallback for very large motors (linear extrapolation approx)
        if hp > 200:
            return hp * 0.96  # Rough estimate

        return 0.0

    @staticmethod
    def calculate_min_ampacity(flc: float, load_type: str = "MOTOR") -> float:
        """
        Calculate minimum required ampacity.
        Motors: 125% of FLC (CEC 28-106)
        Others: 100% or 125% depending on continuous load.
        """
        if load_type == "MOTOR":
            return flc * 1.25
        return flc

    @staticmethod
    def select_cable_size(min_ampacity: float) -> str:
        """
        Select smallest cable size that meets ampacity requirement.
        Uses 75C column of Table 2.
        """
        for size, ampacity in CableSizingService.AMPACITY_TABLE_COPPER.items():
            if ampacity >= min_ampacity:
                return size

        return "OVER_LIMIT"

    @staticmethod
    def calculate_voltage_drop(
        length_meters: float, current: float, size: str, voltage: float = 600.0
    ) -> float:
        """
        Calculate Voltage Drop percentage.
        Formula: VD = (sqrt(3) * I * Z * L) / 1000
        Where:
            I = Current (Amps) - Use FLC (not 125%)
            Z = Impedance (Ohms/km)
            L = Length (Meters)

        Returns:
            Voltage Drop Percentage (e.g., 2.5 for 2.5%)
        """
        if size not in CableSizingService.CABLE_IMPEDANCE:
            return 0.0

        impedance = CableSizingService.CABLE_IMPEDANCE[size]

        # 3-Phase Voltage Drop Formula
        vd_volts = (math.sqrt(3) * current * impedance * length_meters) / 1000

        vd_percent = (vd_volts / voltage) * 100
        return round(vd_percent, 2)

    @staticmethod
    def size_cable(
        hp: float, length_meters: float, voltage_str: str = "600V", max_vd_percent: float = 3.0
    ) -> dict:
        """
        Perform full cable sizing calculation.

        Returns:
            Dict with selected size, ampacity, voltage drop, etc.
        """
        voltage_val = 600.0 if "600" in voltage_str else 480.0  # Simple parsing

        # 1. Get FLC
        flc = CableSizingService.get_motor_flc(hp, voltage_str)

        # 2. Get Min Ampacity (125%)
        min_ampacity = CableSizingService.calculate_min_ampacity(flc, "MOTOR")

        # 3. Select Initial Size based on Ampacity
        selected_size = CableSizingService.select_cable_size(min_ampacity)

        if selected_size == "OVER_LIMIT":
            return {"error": "Load too high for standard cables"}

        # 4. Check Voltage Drop
        vd_percent = CableSizingService.calculate_voltage_drop(
            length_meters, flc, selected_size, voltage_val
        )

        # 5. Upsize if VD > Limit (Iterative)
        # Get list of sizes
        sizes = list(CableSizingService.AMPACITY_TABLE_COPPER.keys())
        current_idx = sizes.index(selected_size)

        while vd_percent > max_vd_percent and current_idx < len(sizes) - 1:
            current_idx += 1
            selected_size = sizes[current_idx]
            vd_percent = CableSizingService.calculate_voltage_drop(
                length_meters, flc, selected_size, voltage_val
            )

        return {
            "cable_size": selected_size,
            "flc": flc,
            "min_ampacity": min_ampacity,
            "cable_ampacity": CableSizingService.AMPACITY_TABLE_COPPER[selected_size],
            "voltage_drop_percent": vd_percent,
            "voltage_drop_volts": (vd_percent / 100) * voltage_val,
            "is_upsized": sizes.index(selected_size)
            > sizes.index(CableSizingService.select_cable_size(min_ampacity)),
        }
