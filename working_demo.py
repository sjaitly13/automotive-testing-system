#!/usr/bin/env python3
"""
Working Demo of the Automotive Infotainment Performance Testing System.
This script demonstrates the core functionality by directly importing modules.
"""

import sys
import time
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_configuration():
    """Demo configuration system."""
    print("⚙️ Configuration System Demo")
    print("=" * 40)
    
    try:
        # Direct import
        sys.path.insert(0, str(Path(__file__).parent / "src" / "utils"))
        from config_loader import get_config
        
        config = get_config()
        print("✓ Configuration loaded successfully")
        print(f"  Platform Mode: {config.get('platform.mode', 'unknown')}")
        print(f"  CPU Threshold: {config.get('performance.cpu_usage.max_percentage', 'unknown')}%")
        print(f"  Memory Threshold: {config.get('performance.memory_usage.max_percentage', 'unknown')}%")
        
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
        # Direct import
        sys.path.insert(0, str(Path(__file__).parent / "src" / "utils"))
        from logger import setup_logging
        
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
    """Demo performance monitoring system."""
    print("📊 Performance Monitoring Demo")
    print("=" * 40)
    
    try:
        # Direct import
        sys.path.insert(0, str(Path(__file__).parent / "src" / "monitoring"))
        from performance_monitor import get_performance_monitor
        
        monitor = get_performance_monitor()
        print("✓ Performance monitor created")
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(2)  # Let it collect some data
        
        # Get current metrics
        metrics = monitor.get_current_metrics()
        if metrics:
            print(f"  CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
            print(f"  System Health: {monitor.get_system_health_score():.0f}%")
        else:
            print("  No metrics available yet")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        print("✓ Performance monitoring demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ Performance monitoring error: {e}\n")
        return False

def demo_platform_simulation():
    """Demo platform simulation system."""
    print("🚗 Platform Simulation Demo")
    print("=" * 40)
    
    try:
        # Direct import
        sys.path.insert(0, str(Path(__file__).parent / "src" / "simulation"))
        from platform_simulator import PlatformSimulator, PlatformMode, TaskPriority
        
        # Create simulator
        simulator = PlatformSimulator(PlatformMode.HYBRID)
        print("✓ Hybrid platform simulator created")
        
        # Start simulator
        simulator.start()
        print("✓ Simulator started")
        
        # Create and submit some tasks
        for i in range(3):
            task = simulator.create_task(
                name=f"Demo Task {i+1}",
                priority=TaskPriority.NORMAL,
                execution_time=0.1,
                memory_usage=50
            )
            success = simulator.submit_task(task)
            if success:
                print(f"  ✓ Task {i+1} submitted")
            else:
                print(f"  ✗ Task {i+1} failed to submit")
        
        # Let tasks run
        time.sleep(1)
        
        # Get performance metrics
        metrics = simulator.get_performance_metrics()
        if metrics:
            print(f"  Overall System Health: {metrics.get('overall_system_health', 'N/A')}%")
            if 'qnx' in metrics:
                qnx_metrics = metrics['qnx']
                print(f"  QNX Tasks Completed: {qnx_metrics.get('completed_tasks', 0)}")
            if 'android' in metrics:
                android_metrics = metrics['android']
                print(f"  Android Apps Running: {android_metrics.get('running_apps_count', 0)}")
        
        # Stop simulator
        simulator.stop()
        print("✓ Simulator stopped")
        
        print("✓ Platform simulation demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ Platform simulation error: {e}\n")
        return False

def demo_automation():
    """Demo automation system."""
    print("🤖 Automation System Demo")
    print("=" * 40)
    
    try:
        # Direct import
        sys.path.insert(0, str(Path(__file__).parent / "src" / "automation"))
        from run_tests import AutomatedTestRunner
        
        runner = AutomatedTestRunner()
        print("✓ Test runner created")
        
        # Get available test scenarios
        scenarios = runner.get_test_scenarios()
        print(f"  Available test scenarios: {len(scenarios)}")
        
        # Run a simple test
        test_result = runner.run_single_test("basic_system_test")
        if test_result:
            print(f"  ✓ Test completed: {test_result.name}")
            print(f"    Status: {test_result.status}")
            print(f"    Duration: {test_result.duration:.2f}s")
        else:
            print("  ⚠️ Test result not available")
        
        print("✓ Automation demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ Automation error: {e}\n")
        return False

def demo_ml_analysis():
    """Demo machine learning analysis system."""
    print("🧠 Machine Learning Analysis Demo")
    print("=" * 40)
    
    try:
        # Direct import
        sys.path.insert(0, str(Path(__file__).parent / "src" / "analysis"))
        from ml_analyzer import MLPerformanceAnalyzer
        
        analyzer = MLPerformanceAnalyzer()
        print("✓ ML analyzer created")
        
        # Collect some sample data
        sample_data = {
            'cpu_usage': [45.2, 67.8, 23.1, 89.4, 34.7],
            'memory_usage': [62.3, 78.9, 45.6, 91.2, 56.8],
            'response_time': [125.4, 89.2, 156.7, 234.1, 98.5]
        }
        
        # Train a simple model
        success = analyzer.train_model(sample_data)
        if success:
            print("  ✓ Model trained successfully")
            
            # Make a prediction
            prediction = analyzer.predict_performance({
                'cpu_usage': 75.0,
                'memory_usage': 80.0
            })
            
            if prediction:
                print(f"  ✓ Performance prediction: {prediction.estimated_response_time:.1f}ms")
                print(f"    Confidence: {prediction.confidence:.1f}%")
                print(f"    Recommendation: {prediction.recommendation}")
        else:
            print("  ⚠️ Model training incomplete")
        
        print("✓ ML analysis demo completed\n")
        return True
        
    except Exception as e:
        print(f"✗ ML analysis error: {e}\n")
        return False

def main():
    """Run all demos."""
    print("🚗 AUTOMOTIVE INFOTAINMENT PERFORMANCE TESTING SYSTEM")
    print("=" * 60)
    print("Working Demo - Core System Functionality")
    print("=" * 60)
    
    demos = [
        demo_configuration,
        demo_logging,
        demo_performance_monitoring,
        demo_platform_simulation,
        demo_automation,
        demo_ml_analysis
    ]
    
    passed = 0
    total = len(demos)
    
    for demo in demos:
        if demo():
            passed += 1
    
    print("=" * 60)
    print(f"DEMO RESULTS: {passed}/{total} demos passed")
    
    if passed == total:
        print("🎉 All demos completed successfully!")
        print("\n🎯 Your system is fully operational!")
    elif passed >= total * 0.7:
        print("✅ Most demos completed successfully!")
        print("\n🔧 Core functionality is working well!")
    else:
        print("⚠️  Some demos failed. The system may need tkinter or other dependencies.")
    
    print("\n🚀 Next steps:")
    print("1. For full UI: Install tkinter and run 'python src/main.py'")
    print("2. For automated testing: Run 'python src/automation/run_tests.py'")
    print("3. For ML analysis: Run 'python src/analysis/ml_analyzer.py'")
    print("\n📚 For more information, see README.md")
    print("\n🌐 Your project is live on GitHub:")
    print("   https://github.com/sjaitly13/automotive-testing-system")

if __name__ == "__main__":
    main() 