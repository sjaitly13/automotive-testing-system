
"""
Automated test runner for the infotainment performance testing system.
Executes predefined test scenarios and collects performance data.
"""

import sys
import time
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logging, get_logger
from utils.config_loader import get_config
from monitoring.performance_monitor import get_performance_monitor
from simulation.platform_simulator import PlatformSimulator, PlatformMode, TaskPriority, SimulatedTask

@dataclass
class TestResult:
    """Represents the result of a single test."""
    test_name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: Optional[str]
    performance_metrics: Dict[str, Any]
    platform_metrics: Dict[str, Any]

@dataclass
class TestScenario:
    """Represents a test scenario configuration."""
    name: str
    description: str
    duration_seconds: int
    operations_per_minute: int
    platform_mode: str
    stress_level: str  # low, medium, high
    include_bluetooth: bool
    include_navigation: bool
    include_media: bool

class AutomatedTestRunner:
    """Automated test runner for infotainment performance testing."""
    
    def __init__(self):
        self.logger = get_logger("test_runner")
        self.config = get_config()
        self.performance_monitor = get_performance_monitor()
        
        # Test state
        self.is_running = False
        self.current_test = None
        self.test_results: List[TestResult] = []
        
        # Platform simulator
        self.platform_simulator = None
        
        # Test scenarios
        self.test_scenarios = self._create_test_scenarios()
        
        self.logger.info("Automated Test Runner initialized")
    
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Create predefined test scenarios."""
        return [
            TestScenario(
                name="basic_functionality",
                description="Basic infotainment functionality testing",
                duration_seconds=300,  # 5 minutes
                operations_per_minute=60,
                platform_mode="hybrid",
                stress_level="low",
                include_bluetooth=True,
                include_navigation=True,
                include_media=True
            ),
            TestScenario(
                name="stress_test",
                description="High-stress performance testing",
                duration_seconds=600,  # 10 minutes
                operations_per_minute=120,
                platform_mode="hybrid",
                stress_level="high",
                include_bluetooth=True,
                include_navigation=True,
                include_media=True
            ),
            TestScenario(
                name="qnx_performance",
                description="QNX real-time performance testing",
                duration_seconds=300,
                operations_per_minute=80,
                platform_mode="qnx",
                stress_level="medium",
                include_bluetooth=False,
                include_navigation=True,
                include_media=False
            ),
            TestScenario(
                name="android_performance",
                description="Android app performance testing",
                duration_seconds=300,
                operations_per_minute=100,
                platform_mode="android",
                stress_level="medium",
                include_bluetooth=True,
                include_navigation=False,
                include_media=True
            ),
            TestScenario(
                name="real_world_simulation",
                description="Real-world usage simulation",
                duration_seconds=1800,  # 30 minutes
                operations_per_minute=45,
                platform_mode="hybrid",
                stress_level="low",
                include_bluetooth=True,
                include_navigation=True,
                include_media=True
            )
        ]
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all available test scenarios."""
        self.logger.info("Starting automated test suite")
        
        all_results = []
        
        for scenario in self.test_scenarios:
            try:
                self.logger.info(f"Running test scenario: {scenario.name}")
                result = self.run_test_scenario(scenario)
                all_results.append(result)
                
                # Brief pause between tests
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error running test scenario {scenario.name}: {e}")
                # Create failed result
                failed_result = TestResult(
                    test_name=scenario.name,
                    start_time=time.time(),
                    end_time=time.time(),
                    duration=0,
                    success=False,
                    error_message=str(e),
                    performance_metrics={},
                    platform_metrics={}
                )
                all_results.append(failed_result)
        
        self.logger.info("Automated test suite completed")
        return all_results
    
    def run_test_scenario(self, scenario: TestScenario) -> TestResult:
        """Run a specific test scenario."""
        self.logger.info(f"Starting test: {scenario.name}")
        self.logger.info(f"Description: {scenario.description}")
        self.logger.info(f"Duration: {scenario.duration_seconds} seconds")
        self.logger.info(f"Operations per minute: {scenario.operations_per_minute}")
        
        # Initialize platform simulator
        platform_mode = PlatformMode(scenario.platform_mode)
        self.platform_simulator = PlatformSimulator(platform_mode)
        self.platform_simulator.start()
        
        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        
        # Record start time
        start_time = time.time()
        
        try:
            # Run the test
            self._execute_test_scenario(scenario)
            
            # Record end time
            end_time = time.time()
            duration = end_time - start_time
            
            # Collect final metrics
            performance_metrics = self.performance_monitor.get_current_metrics()
            platform_metrics = self.platform_simulator.get_performance_metrics()
            
            # Create test result
            result = TestResult(
                test_name=scenario.name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=True,
                error_message=None,
                performance_metrics=performance_metrics,
                platform_metrics=platform_metrics
            )
            
            self.logger.info(f"Test {scenario.name} completed successfully in {duration:.2f} seconds")
            
        except Exception as e:
            # Record failure
            end_time = time.time()
            duration = end_time - start_time
            
            result = TestResult(
                test_name=scenario.name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=False,
                error_message=str(e),
                performance_metrics={},
                platform_metrics={}
            )
            
            self.logger.error(f"Test {scenario.name} failed after {duration:.2f} seconds: {e}")
        
        finally:
            # Cleanup
            if self.platform_simulator:
                self.platform_simulator.stop()
            
            self.performance_monitor.stop_monitoring()
        
        return result
    
    def _execute_test_scenario(self, scenario: TestScenario):
        """Execute the actual test scenario."""
        self.logger.info(f"Executing test scenario: {scenario.name}")
        
        # Calculate operation intervals
        operation_interval = 60.0 / scenario.operations_per_minute
        end_time = time.time() + scenario.duration_seconds
        
        operation_count = 0
        
        while time.time() < end_time:
            try:
                # Execute operations based on scenario
                if scenario.include_bluetooth:
                    self._simulate_bluetooth_operations()
                
                if scenario.include_navigation:
                    self._simulate_navigation_operations()
                
                if scenario.include_media:
                    self._simulate_media_operations()
                
                # Submit platform tasks
                self._submit_platform_tasks(scenario)
                
                operation_count += 1
                
                # Log progress
                if operation_count % 10 == 0:
                    elapsed = time.time() - (end_time - scenario.duration_seconds)
                    self.logger.info(f"Test progress: {elapsed:.1f}s elapsed, {operation_count} operations completed")
                
                # Wait for next operation
                time.sleep(operation_interval)
                
            except Exception as e:
                self.logger.error(f"Error during test execution: {e}")
                # Continue with next operation
        
        self.logger.info(f"Test scenario completed: {operation_count} operations executed")
    
    def _simulate_bluetooth_operations(self):
        """Simulate Bluetooth-related operations."""
        operations = [
            self._simulate_device_discovery,
            self._simulate_device_pairing,
            self._simulate_connection_management,
            self._simulate_data_transfer
        ]
        
        # Randomly select and execute operations
        operation = random.choice(operations)
        operation()
    
    def _simulate_device_discovery(self):
        """Simulate Bluetooth device discovery."""
        time.sleep(random.uniform(0.1, 0.5))
        self.logger.debug("Bluetooth device discovery simulated")
    
    def _simulate_device_pairing(self):
        """Simulate Bluetooth device pairing."""
        time.sleep(random.uniform(0.2, 1.0))
        self.logger.debug("Bluetooth device pairing simulated")
    
    def _simulate_connection_management(self):
        """Simulate Bluetooth connection management."""
        time.sleep(random.uniform(0.1, 0.3))
        self.logger.debug("Bluetooth connection management simulated")
    
    def _simulate_data_transfer(self):
        """Simulate Bluetooth data transfer."""
        time.sleep(random.uniform(0.05, 0.2))
        self.logger.debug("Bluetooth data transfer simulated")
    
    def _simulate_navigation_operations(self):
        """Simulate navigation-related operations."""
        operations = [
            self._simulate_route_calculation,
            self._simulate_map_rendering,
            self._simulate_gps_processing,
            self._simulate_turn_by_turn
        ]
        
        operation = random.choice(operations)
        operation()
    
    def _simulate_route_calculation(self):
        """Simulate route calculation."""
        time.sleep(random.uniform(0.1, 0.8))
        self.logger.debug("Route calculation simulated")
    
    def _simulate_map_rendering(self):
        """Simulate map rendering."""
        time.sleep(random.uniform(0.05, 0.3))
        self.logger.debug("Map rendering simulated")
    
    def _simulate_gps_processing(self):
        """Simulate GPS processing."""
        time.sleep(random.uniform(0.02, 0.1))
        self.logger.debug("GPS processing simulated")
    
    def _simulate_turn_by_turn(self):
        """Simulate turn-by-turn navigation."""
        time.sleep(random.uniform(0.1, 0.5))
        self.logger.debug("Turn-by-turn navigation simulated")
    
    def _simulate_media_operations(self):
        """Simulate media-related operations."""
        operations = [
            self._simulate_audio_playback,
            self._simulate_playlist_management,
            self._simulate_audio_processing,
            self._simulate_media_controls
        ]
        
        operation = random.choice(operations)
        operation()
    
    def _simulate_audio_playback(self):
        """Simulate audio playback."""
        time.sleep(random.uniform(0.02, 0.1))
        self.logger.debug("Audio playback simulated")
    
    def _simulate_playlist_management(self):
        """Simulate playlist management."""
        time.sleep(random.uniform(0.1, 0.4))
        self.logger.debug("Playlist management simulated")
    
    def _simulate_audio_processing(self):
        """Simulate audio processing."""
        time.sleep(random.uniform(0.05, 0.2))
        self.logger.debug("Audio processing simulated")
    
    def _simulate_media_controls(self):
        """Simulate media controls."""
        time.sleep(random.uniform(0.02, 0.08))
        self.logger.debug("Media controls simulated")
    
    def _submit_platform_tasks(self, scenario: TestScenario):
        """Submit tasks to the platform simulator."""
        if not self.platform_simulator:
            return
        
        # Create tasks based on stress level
        task_count = self._get_task_count_for_stress_level(scenario.stress_level)
        
        for _ in range(task_count):
            task = self._create_random_task()
            self.platform_simulator.submit_task(task)
    
    def _get_task_count_for_stress_level(self, stress_level: str) -> int:
        """Get the number of tasks to submit based on stress level."""
        if stress_level == "low":
            return random.randint(1, 3)
        elif stress_level == "medium":
            return random.randint(3, 8)
        else:  # high
            return random.randint(8, 15)
    
    def _create_random_task(self) -> SimulatedTask:
        """Create a random simulated task."""
        task_types = [
            ("media_playback", TaskPriority.NORMAL, 0.05, 50, 0.1),
            ("navigation_update", TaskPriority.HIGH, 0.1, 100, 0.2),
            ("bluetooth_sync", TaskPriority.LOW, 0.2, 30, 0.05),
            ("system_maintenance", TaskPriority.BACKGROUND, 0.5, 20, 0.01),
            ("user_interface", TaskPriority.HIGH, 0.02, 10, 0.05)
        ]
        
        task_type, priority, exec_time, memory, cpu = random.choice(task_types)
        
        return self.platform_simulator.create_task(
            name=task_type,
            priority=priority,
            execution_time=exec_time,
            memory_usage=memory,
            cpu_usage=cpu
        )
    
    def generate_test_report(self, results: List[TestResult]) -> str:
        """Generate a comprehensive test report."""
        self.logger.info("Generating test report")
        
        report = []
        report.append("=" * 80)
        report.append("INFOTAINMENT SYSTEM PERFORMANCE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(results)}")
        report.append("")
        
        # Summary statistics
        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]
        
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Successful Tests: {len(successful_tests)}")
        report.append(f"Failed Tests: {len(failed_tests)}")
        report.append(f"Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
        report.append("")
        
        # Individual test results
        report.append("DETAILED RESULTS")
        report.append("-" * 40)
        
        for result in results:
            report.append(f"Test: {result.test_name}")
            report.append(f"  Status: {'PASS' if result.success else 'FAIL'}")
            report.append(f"  Duration: {result.duration:.2f} seconds")
            
            if result.success:
                # Performance metrics
                perf = result.performance_metrics
                if perf:
                    report.append(f"  CPU Usage: {perf.get('cpu_percent', 'N/A'):.1f}%")
                    report.append(f"  Memory Usage: {perf.get('memory_percent', 'N/A'):.1f}%")
                    report.append(f"  Response Time: {perf.get('response_time_ms', 'N/A'):.1f}ms")
                
                # Platform metrics
                platform = result.platform_metrics
                if platform:
                    if 'qnx' in platform:
                        qnx = platform['qnx']
                        report.append(f"  QNX Tasks Completed: {qnx.get('completed_tasks', 'N/A')}")
                        report.append(f"  QNX Missed Deadlines: {qnx.get('missed_deadlines', 'N/A')}")
                    
                    if 'android' in platform:
                        android = platform['android']
                        report.append(f"  Android Apps Running: {android.get('running_apps_count', 'N/A')}")
                        report.append(f"  Memory Usage: {android.get('memory_usage_percentage', 'N/A'):.1f}%")
            else:
                report.append(f"  Error: {result.error_message}")
            
            report.append("")
        
        # Performance analysis
        if successful_tests:
            report.append("PERFORMANCE ANALYSIS")
            report.append("-" * 40)
            
            durations = [r.duration for r in successful_tests]
            avg_duration = sum(durations) / len(durations)
            report.append(f"Average Test Duration: {avg_duration:.2f} seconds")
            report.append(f"Fastest Test: {min(durations):.2f} seconds")
            report.append(f"Slowest Test: {max(durations):.2f} seconds")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 40)
        
        if failed_tests:
            report.append("• Investigate failed tests and fix underlying issues")
        
        if successful_tests:
            # Analyze performance patterns
            slow_tests = [r for r in successful_tests if r.duration > 300]  # > 5 minutes
            if slow_tests:
                report.append("• Consider optimizing slow test scenarios")
            
            # Check for performance issues
            high_cpu_tests = [r for r in successful_tests 
                            if r.performance_metrics.get('cpu_percent', 0) > 80]
            if high_cpu_tests:
                report.append("• Monitor CPU usage during high-stress scenarios")
        
        report.append("• Continue monitoring system performance in production")
        report.append("• Consider running stress tests periodically")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_test_results(self, results: List[TestResult], filename: str = None):
        """Save test results to a file."""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"data/test_results_{timestamp}.json"
        
        # Ensure data directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            serializable_result = {
                'test_name': result.test_name,
                'start_time': result.start_time,
                'end_time': result.end_time,
                'duration': result.duration,
                'success': result.success,
                'error_message': result.error_message,
                'performance_metrics': result.performance_metrics,
                'platform_metrics': result.platform_metrics
            }
            serializable_results.append(serializable_result)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        self.logger.info(f"Test results saved to {filename}")

def main():
    """Main function for running automated tests."""
    try:
        # Setup logging
        logger = setup_logging("test_runner", "INFO")
        logger.info("Starting automated test runner")
        
        # Create test runner
        test_runner = AutomatedTestRunner()
        
        # Run all tests
        results = test_runner.run_all_tests()
        
        # Generate report
        report = test_runner.generate_test_report(results)
        print(report)
        
        # Save results
        test_runner.save_test_results(results)
        
        # Save report to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_filename = f"reports/test_report_{timestamp}.txt"
        Path(report_filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        logger.info(f"Test report saved to {report_filename}")
        logger.info("Automated testing completed")
        
    except Exception as e:
        logger.error(f"Error in automated testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 