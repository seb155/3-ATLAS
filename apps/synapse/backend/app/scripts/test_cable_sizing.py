import logging

from app.services.cable_sizing import CableSizingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_cable_sizing():
    logger.info("Starting Cable Sizing Tests...")

    # Test Case 1: 10HP Motor @ 600V (Standard)
    # FLC should be 11A
    # Min Ampacity = 11 * 1.25 = 13.75A
    # Size should be 14 AWG (20A)
    logger.info("\n--- Test Case 1: 10HP Motor @ 600V, 50m ---")
    result = CableSizingService.size_cable(hp=10, length_meters=50, voltage_str="600V")
    logger.info(f"Result: {result}")
    assert result["flc"] == 11.0
    assert result["cable_size"] == "14 AWG"
    assert result["voltage_drop_percent"] < 3.0
    logger.info("✅ Test Case 1 Passed")

    # Test Case 2: 100HP Motor @ 600V (Large Load)
    # FLC = 99A
    # Min Ampacity = 99 * 1.25 = 123.75A
    # Size should be 1 AWG (130A)
    logger.info("\n--- Test Case 2: 100HP Motor @ 600V, 100m ---")
    result = CableSizingService.size_cable(hp=100, length_meters=100, voltage_str="600V")
    logger.info(f"Result: {result}")
    assert result["flc"] == 99.0
    assert result["cable_size"] == "1 AWG"
    logger.info("✅ Test Case 2 Passed")

    # Test Case 3: Long Distance (Voltage Drop Check)
    # 10HP Motor @ 600V, 300m
    # 14 AWG (10.5 Ohm/km) -> VD% = (1.732 * 11 * 10.5 * 300) / 1000 = 60V / 600 = 10% (Too high!)
    # Should upsize significantly.
    logger.info("\n--- Test Case 3: 10HP Motor @ 600V, 300m (Long Run) ---")
    result = CableSizingService.size_cable(hp=10, length_meters=300, voltage_str="600V")
    logger.info(f"Result: {result}")
    assert result["voltage_drop_percent"] < 3.0
    assert result["is_upsized"] is True
    logger.info(f"Upsized to: {result['cable_size']}")
    logger.info("✅ Test Case 3 Passed")

    logger.info("\n🎉 All Tests Passed!")


if __name__ == "__main__":
    test_cable_sizing()
