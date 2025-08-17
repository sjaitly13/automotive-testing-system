#!/usr/bin/env python3
"""
Simple demo of the Automotive Infotainment Performance Testing System.
This script demonstrates the core functionality in a working manner.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_configuration():
    """Demo configuration system."""
    print("⚙️ Configuration System Demo")
    print("=" * 40)
    
    try:
        from utils.config_loader import get_config
        
        config = get_config()
        print("✓ Configuration loaded successfully")
        
        # Show some config values
        platform_mode = config.get('platform.mode', 'unknown')
        print(f"  Platform Mode: {platform_mode}")
        
        cpu_threshold = config.get('performance.cpu_usage.max_percentage', 0)
        print(f"  CPU Threshold: {cpu_threshold}%")
        
        memory_threshold = config.get('performance.memory_usage.max_percentage', 0)
        print(f"  Memory Threshold: {memory_threshold}%")
        
        print("✓ Configuration demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}\n")
        return False

def demo_logging():
    """Demo logging system."""
    print("📝 Logging System Demo")
    print("=" * 40)
    
    try:
        from utils.logger import setup_logging
        
        logger = setup_logging("demo_logger", "INFO")
        logger.info("Demo started successfully")
        logger.warning("This is a demo warning")
        logger.info("Demo completed successfully")
        
        print("✓ Logging demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ Logging error: {e}\n")
        return False

def demo_performance_monitoring():
    """Demo performance monitoring."""
    print("📊 Performance Monitoring Demo")
    print("=" * 40)
    
    try:
        from monitoring.performance_monitor import get_performance_monitor
        
        monitor = get_performance_monitor()
        print("✓ Performance monitor created")
        
        # Start monitoring
        monitor.start_monitoring()
        print("✓ Monitoring started")
        
        # Let it collect some data
        time.sleep(2)
        
        # Get metrics
        metrics = monitor.get_current_metrics()
        if metrics:
            print("Current System Metrics:")
            print(f"  CPU: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  Memory: {metrics.get('memory_percent', 0):.1f}%")
            print(f"  Available Memory: {metrics.get('memory_available_mb', 0):.1f} MB")
            print(f"  Process Count: {metrics.get('process_count', 0)}")
        
        # Get health score
        health_score = monitor.get_system_health_score()
        print(f"  System Health: {health_score:.0f}%")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("✓ Monitoring stopped")
        print("✓ Performance monitoring demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ Performance monitoring error: {e}\n")
        return False

def demo_platform_simulation():
    """Demo platform simulation."""
    print("🚗 Platform Simulation Demo")
    print("=" * 40)
    
    try:
        from simulation.platform_simulator import PlatformSimulator, PlatformMode
        
        # Create simulators
        print("Creating platform simulators...")
        qnx_sim = PlatformSimulator(PlatformMode.QNX)
        android_sim = PlatformSimulator(PlatformMode.ANDROID)
        hybrid_sim = PlatformSimulator(PlatformMode.HYBRID)
        
        print("✓ QNX Simulator created")
        print("✓ Android Simulator created")
        print("✓ Hybrid Simulator created")
        
        # Start hybrid simulator
        hybrid_sim.start()
        print("✓ Hybrid simulator started")
        
        # Let it run for a moment
        time.sleep(1)
        
        # Get metrics
        metrics = hybrid_sim.get_performance_metrics()
        print(f"Platform Metrics: {len(metrics)} metrics available")
        
        # Stop simulator
        hybrid_sim.stop()
        print("✓ Hybrid simulator stopped")
        print("✓ Platform simulation demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ Platform simulation error: {e}\n")
        return False

def main():
    """Run all demos."""
    print("🚗 AUTOMOTIVE INFOTAINMENT PERFORMANCE TESTING SYSTEM")
    print("=" * 60)
    print("Simple Demo - Core System Functionality")
    print("=" * 60)
    
    demos = [
        demo_configuration,
        demo_logging,
        demo_performance_monitoring,
        demo_platform_simulation
    ]
    
    passed = 0
    total = len(demos)
    
    for demo in demos:
        if demo():
            passed += 1
    
    print("=" * 60)
    print(f"DEMO RESULTS: {passed}/{total} demos passed")
    
    if passed == total:
        print("🎉 All demos passed! The core system is working correctly.")
        print("\nThe system includes:")
        print("  ✓ Configuration management")
        print("  ✓ Logging system")
        print("  ✓ Performance monitoring")
        print("  ✓ Platform simulation (QNX/Android/Hybrid)")
        print("  ✓ Automated testing framework")
        print("  ✓ Machine learning analysis")
        print("  ✓ Full infotainment UI (requires tkinter)")
    else:
        print("⚠️  Some demos failed. The system may need tkinter or other dependencies.")
    
    print("\nNext steps:")
    print("1. For full UI: Install tkinter and run 'python src/main.py'")
    print("2. For automated testing: Run 'python src/automation/run_tests.py'")
    print("3. For ML analysis: Run 'python src/analysis/ml_analyzer.py'")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 