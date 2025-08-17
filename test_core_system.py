#!/usr/bin/env python3
"""
Core system test script for the infotainment system.
Tests core functionality without UI dependencies.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_core_imports():
    """Test core imports without UI components."""
    print("Testing core imports...")

    try:
        from src.utils.logger import setup_logging, get_logger
        from src.utils.config_loader import get_config
        print("✓ Utils imported successfully")

        from src.simulation.platform_simulator import PlatformSimulator, PlatformMode
        print("✓ Simulation modules imported successfully")

        from src.monitoring.performance_monitor import get_performance_monitor
        print("✓ Monitoring modules imported successfully")

        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from src.utils.config_loader import get_config

        config = get_config()
        if config.validate():
            print("✓ Configuration loaded and validated successfully")

            # Test some config values
            platform_mode = config.get('platform.mode', 'unknown')
            print(f"  Platform mode: {platform_mode}")

            cpu_threshold = config.get('performance.cpu_usage.max_percentage', 0)
            print(f"  CPU threshold: {cpu_threshold}%")

            return True
        else:
            print("✗ Configuration validation failed")
            return False

    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_logging():
    """Test logging system."""
    print("\nTesting logging...")

    try:
        from src.utils.logger import setup_logging

        logger = setup_logging("test_logger", "INFO")
        logger.info("Test log message")
        logger.warning("Test warning message")
        print("✓ Logging system working")
        return True

    except Exception as e:
        print(f"✗ Logging error: {e}")
        return False

def test_platform_simulation():
    """Test platform simulation."""
    print("\nTesting platform simulation...")

    try:
        from src.simulation.platform_simulator import PlatformSimulator, PlatformMode

        # Test QNX mode
        qnx_sim = PlatformSimulator(PlatformMode.QNX)
        print("✓ QNX simulator created")

        # Test Android mode
        android_sim = PlatformSimulator(PlatformMode.ANDROID)
        print("✓ Android simulator created")

        # Test Hybrid mode
        hybrid_sim = PlatformSimulator(PlatformMode.HYBRID)
        print("✓ Hybrid simulator created")

        return True

    except Exception as e:
        print(f"✗ Platform simulation error: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring."""
    print("\nTesting performance monitoring...")

    try:
        from src.monitoring.performance_monitor import get_performance_monitor

        monitor = get_performance_monitor()
        print("✓ Performance monitor created")

        # Get current metrics
        metrics = monitor.get_current_metrics()
        if metrics:
            print("✓ Performance metrics collected")
            print(f"  CPU: {metrics.get('cpu_percent', 'N/A')}%")
            print(f"  Memory: {metrics.get('memory_percent', 'N/A')}%")
        else:
            print("  No metrics available yet")

        return True

    except Exception as e:
        print(f"✗ Performance monitoring error: {e}")
        return False

def test_automation():
    """Test automation system."""
    print("\nTesting automation system...")

    try:
        from src.automation.run_tests import AutomatedTestRunner

        test_runner = AutomatedTestRunner()
        print("✓ Test runner created")

        # Test test scenario creation
        scenarios = test_runner.test_scenarios
        print(f"✓ {len(scenarios)} test scenarios created")

        return True

    except Exception as e:
        print(f"✗ Automation error: {e}")
        return False

def test_ml_analysis():
    """Test ML analysis system."""
    print("\nTesting ML analysis system...")

    try:
        from src.analysis.ml_analyzer import MLPerformanceAnalyzer

        analyzer = MLPerformanceAnalyzer()
        print("✓ ML analyzer created")

        # Check status
        status = analyzer.get_model_status()
        print(f"✓ ML system status: {status['ml_enabled']}")

        return True

    except Exception as e:
        print(f"✗ ML analysis error: {e}")
        return False

def main():
    """Run all core tests."""
    print("=" * 60)
    print("CORE INFOTAINMENT SYSTEM TEST")
    print("=" * 60)

    tests = [
        test_core_imports,
        test_configuration,
        test_logging,
        test_platform_simulation,
        test_performance_monitoring,
        test_automation,
        test_ml_analysis
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"CORE TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All core tests passed! The system is ready to run.")
        print("\nTo run the infotainment interface (requires tkinter):")
        print("  python src/main.py")
        print("\nTo run automated tests:")
        print("  python src/automation/run_tests.py")
        print("\nTo run ML analysis:")
        print("  python src/analysis/ml_analyzer.py")
    else:
        print("⚠️  Some core tests failed. Please check the errors above.")

    print("=" * 60)

if __name__ == "__main__":
    main() 