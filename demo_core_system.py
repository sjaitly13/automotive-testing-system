#!/usr/bin/env python3
"""
Demo script for the Automotive Infotainment Performance Testing System.
Showcases core functionality without UI dependencies.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_platform_simulation():
    """Demonstrate platform simulation capabilities."""
    print("🚗 Platform Simulation Demo")
    print("=" * 50)
    
    try:
        from simulation.platform_simulator import PlatformSimulator, PlatformMode, TaskPriority, SimulatedTask
        
        # Create simulators for different platforms
        print("Creating platform simulators...")
        qnx_sim = PlatformSimulator(PlatformMode.QNX)
        android_sim = PlatformSimulator(PlatformMode.ANDROID)
        hybrid_sim = PlatformSimulator(PlatformMode.HYBRID)
        
        print("✓ QNX Simulator: Real-time constraints, priority queues")
        print("✓ Android Simulator: App management, memory handling")
        print("✓ Hybrid Simulator: Combines both behaviors")
        
        # Start hybrid simulator
        hybrid_sim.start()
        
        # Create and submit tasks
        print("\nSubmitting simulated tasks...")
        tasks = [
            ("media_playback", TaskPriority.HIGH, 0.05, 50, 0.1),
            ("navigation_update", TaskPriority.CRITICAL, 0.02, 30, 0.2),
            ("bluetooth_sync", TaskPriority.LOW, 0.1, 20, 0.05),
            ("system_maintenance", TaskPriority.BACKGROUND, 0.3, 10, 0.01)
        ]
        
        for name, priority, exec_time, memory, cpu in tasks:
            task = hybrid_sim.create_task(
                name=name,
                priority=priority,
                execution_time=exec_time,
                memory_usage=memory,
                cpu_usage=cpu
            )
            hybrid_sim.submit_task(task)
            print(f"  ✓ {name} (Priority: {priority.name})")
        
        # Let tasks run for a moment
        time.sleep(2)
        
        # Get performance metrics
        metrics = hybrid_sim.get_performance_metrics()
        print(f"\nPerformance Metrics:")
        print(f"  QNX Tasks: {metrics.get('qnx', {}).get('total_tasks', 0)}")
        print(f"  Android Apps: {metrics.get('android', {}).get('running_apps_count', 0)}")
        print(f"  System Health: {metrics.get('overall_system_health', 0)}%")
        
        hybrid_sim.stop()
        print("✓ Platform simulation demo completed\n")
        
    except Exception as e:
        print(f"✗ Platform simulation error: {e}\n")

def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print("📊 Performance Monitoring Demo")
    print("=" * 50)
    
    try:
        from monitoring.performance_monitor import get_performance_monitor
        
        # Get performance monitor
        monitor = get_performance_monitor()
        print("Starting performance monitoring...")
        monitor.start_monitoring()
        
        # Let it collect some data
        time.sleep(3)
        
        # Get current metrics
        metrics = monitor.get_current_metrics()
        if metrics:
            print("Current System Metrics:")
            print(f"  CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
            print(f"  Available Memory: {metrics.get('memory_available_mb', 0):.1f} MB")
            print(f"  Disk Usage: {metrics.get('disk_usage_percent', 0):.1f}%")
            print(f"  Process Count: {metrics.get('process_count', 0)}")
        
        # Get system health score
        health_score = monitor.get_system_health_score()
        print(f"  System Health Score: {health_score:.0f}%")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("✓ Performance monitoring demo completed\n")
        
    except Exception as e:
        print(f"✗ Performance monitoring error: {e}\n")

def demo_automation():
    """Demonstrate automation capabilities."""
    print("🤖 Automation Demo")
    print("=" * 50)
    
    try:
        from automation.run_tests import AutomatedTestRunner
        
        # Create test runner
        test_runner = AutomatedTestRunner()
        print(f"Created test runner with {len(test_runner.test_scenarios)} test scenarios:")
        
        for scenario in test_runner.test_scenarios:
            print(f"  • {scenario.name}: {scenario.description}")
            print(f"    Duration: {scenario.duration_seconds}s, Operations: {scenario.operations_per_minute}/min")
        
        print("\nTest scenarios cover:")
        print("  ✓ Basic functionality testing")
        print("  ✓ Stress testing")
        print("  ✓ Platform-specific testing")
        print("  ✓ Real-world simulation")
        
        print("✓ Automation demo completed\n")
        
    except Exception as e:
        print(f"✗ Automation error: {e}\n")

def demo_ml_analysis():
    """Demonstrate machine learning analysis capabilities."""
    print("🧠 Machine Learning Analysis Demo")
    print("=" * 50)
    
    try:
        from analysis.ml_analyzer import MLPerformanceAnalyzer
        
        # Create ML analyzer
        analyzer = MLPerformanceAnalyzer()
        print("ML Performance Analyzer created")
        
        # Check status
        status = analyzer.get_model_status()
        print(f"ML System Status:")
        print(f"  Enabled: {status['ml_enabled']}")
        print(f"  Model Type: {status['model_type']}")
        print(f"  Models Available: {len(status['models_available'])}")
        
        if status['ml_enabled']:
            print("\nCapabilities:")
            print("  ✓ Performance prediction")
            print("  ✓ Bottleneck detection")
            print("  ✓ Optimization recommendations")
            print("  ✓ Historical data analysis")
            
            # Try to collect training data
            print("\nCollecting training data...")
            if analyzer.collect_training_data():
                print(f"  ✓ Collected {len(analyzer.training_data)} training samples")
                
                # Try to train models
                print("Training ML models...")
                if analyzer.train_models():
                    print("  ✓ Models trained successfully")
                    
                    # Try to make a prediction
                    prediction = analyzer.predict_performance()
                    if prediction:
                        print("  ✓ Performance prediction generated")
                        print(f"    CPU Usage: {prediction.predicted_cpu_usage:.1f}%")
                        print(f"    Memory Usage: {prediction.predicted_memory_usage:.1f}%")
                        print(f"    Bottleneck Risk: {prediction.bottleneck_risk}")
                else:
                    print("  ⚠️  Model training failed (insufficient data)")
            else:
                print("  ⚠️  Training data collection failed")
        
        print("✓ ML analysis demo completed\n")
        
    except Exception as e:
        print(f"✗ ML analysis error: {e}\n")

def main():
    """Run all demos."""
    print("🚗 AUTOMOTIVE INFOTAINMENT PERFORMANCE TESTING SYSTEM")
    print("=" * 70)
    print("This demo showcases the core system capabilities without UI dependencies.")
    print("The system simulates automotive infotainment testing similar to Ford Motor Company.\n")
    
    demos = [
        demo_platform_simulation,
        demo_performance_monitoring,
        demo_automation,
        demo_ml_analysis
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"Demo failed: {e}\n")
    
    print("🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Install tkinter for full UI experience")
    print("2. Run: python src/main.py (for full interface)")
    print("3. Run: python src/automation/run_tests.py (for automated testing)")
    print("4. Run: python src/analysis/ml_analyzer.py (for ML analysis)")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 