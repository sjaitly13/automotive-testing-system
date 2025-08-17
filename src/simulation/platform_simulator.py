"""
Platform simulator for the infotainment testing system.
Simulates QNX real-time behavior and Android app management.
"""

import time
import threading
import queue
import random
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import psutil
import asyncio

from ..utils.logger import get_logger
from ..utils.config_loader import get_config

class PlatformMode(Enum):
    """Platform simulation modes."""
    QNX = "qnx"
    ANDROID = "android"
    HYBRID = "hybrid"

class TaskPriority(Enum):
    """Task priority levels for QNX simulation."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

@dataclass
class SimulatedTask:
    """Represents a simulated task in the system."""
    id: str
    name: str
    priority: TaskPriority
    execution_time: float
    deadline: float
    memory_usage: int
    cpu_usage: float
    created_at: float
    status: str = "pending"

class QNXSimulator:
    """Simulates QNX real-time operating system behavior."""
    
    def __init__(self):
        self.logger = get_logger("qnx_simulator")
        self.config = get_config()
        self.qnx_config = self.config.get_platform_config().get('qnx', {})
        
        # Real-time constraints
        self.real_time_constraint = self.qnx_config.get('real_time_constraint', 0.016)
        self.max_response_time = self.qnx_config.get('max_response_time', 0.100)
        self.priority_levels = self.qnx_config.get('priority_levels', 5)
        
        # Task management
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[str, SimulatedTask] = {}
        self.completed_tasks: List[SimulatedTask] = []
        self.failed_tasks: List[SimulatedTask] = []
        
        # Performance tracking
        self.response_times: List[float] = []
        self.missed_deadlines = 0
        self.total_tasks = 0
        
        # Threading
        self.scheduler_thread = None
        self.running = False
        
        self.logger.info("QNX Simulator initialized")
    
    def start(self) -> None:
        """Start the QNX scheduler."""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("QNX Scheduler started")
    
    def stop(self) -> None:
        """Stop the QNX scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        self.logger.info("QNX Scheduler stopped")
    
    def submit_task(self, task: SimulatedTask) -> bool:
        """Submit a task to the scheduler."""
        try:
            # Calculate priority score (lower is higher priority)
            priority_score = task.priority.value
            
            # Add deadline factor
            time_until_deadline = task.deadline - time.time()
            if time_until_deadline < 0:
                self.logger.warning(f"Task {task.name} has already missed deadline")
                return False
            
            # Adjust priority based on deadline urgency
            if time_until_deadline < self.real_time_constraint:
                priority_score -= 10  # Boost priority for urgent tasks
            
            self.task_queue.put((priority_score, time.time(), task))
            self.total_tasks += 1
            self.logger.debug(f"Task {task.name} submitted with priority {priority_score}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to submit task {task.name}: {e}")
            return False
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop for task execution."""
        while self.running:
            try:
                if not self.task_queue.empty():
                    # Get highest priority task
                    priority_score, submit_time, task = self.task_queue.get_nowait()
                    
                    # Check if task can meet deadline
                    current_time = time.time()
                    if current_time + task.execution_time > task.deadline:
                        self.logger.warning(f"Task {task.name} cannot meet deadline")
                        self.missed_deadlines += 1
                        task.status = "failed"
                        self.failed_tasks.append(task)
                        continue
                    
                    # Execute task
                    self._execute_task(task, submit_time)
                else:
                    time.sleep(0.001)  # Small delay when no tasks
                    
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(0.001)
    
    def _execute_task(self, task: SimulatedTask, submit_time: float) -> None:
        """Execute a single task."""
        try:
            task.status = "running"
            self.running_tasks[task.id] = task
            
            # Simulate task execution
            start_time = time.time()
            time.sleep(task.execution_time)
            end_time = time.time()
            
            # Calculate response time
            response_time = end_time - submit_time
            self.response_times.append(response_time)
            
            # Check if deadline was met
            if end_time <= task.deadline:
                task.status = "completed"
                self.completed_tasks.append(task)
                self.logger.debug(f"Task {task.name} completed in {response_time:.3f}s")
            else:
                task.status = "failed"
                self.failed_tasks.append(task)
                self.missed_deadlines += 1
                self.logger.warning(f"Task {task.name} missed deadline")
            
            # Remove from running tasks
            del self.running_tasks[task.id]
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.name}: {e}")
            task.status = "failed"
            self.failed_tasks.append(task)
            del self.running_tasks[task.id]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.response_times:
            return {}
        
        avg_response_time = sum(self.response_times) / len(self.response_times)
        max_response_time = max(self.response_times)
        min_response_time = min(self.response_times)
        
        success_rate = len(self.completed_tasks) / self.total_tasks if self.total_tasks > 0 else 0
        
        return {
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'min_response_time': min_response_time,
            'success_rate': success_rate,
            'missed_deadlines': self.missed_deadlines,
            'total_tasks': self.total_tasks,
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'running_tasks': len(self.running_tasks),
            'queued_tasks': self.task_queue.qsize()
        }

class AndroidSimulator:
    """Simulates Android app management and behavior."""
    
    def __init__(self):
        self.logger = get_logger("android_simulator")
        self.config = get_config()
        self.android_config = self.config.get_platform_config().get('android', {})
        
        # Android-specific parameters
        self.app_launch_delay = self.android_config.get('app_launch_delay', 0.500)
        self.multitasking_enabled = self.android_config.get('multitasking_enabled', True)
        self.memory_limit_mb = self.android_config.get('memory_limit_mb', 2048)
        self.gc_interval = self.android_config.get('garbage_collection_interval', 5.0)
        
        # App management
        self.running_apps: Dict[str, Dict[str, Any]] = {}
        self.app_history: List[str] = []
        self.memory_usage = 0
        self.last_gc_time = time.time()
        
        # Performance tracking
        self.app_launch_times: List[float] = []
        self.memory_pressure_events = 0
        
        self.logger.info("Android Simulator initialized")
    
    def launch_app(self, app_name: str, app_id: str) -> bool:
        """Launch an Android app."""
        try:
            start_time = time.time()
            
            # Check memory availability
            if self.memory_usage >= self.memory_limit_mb * 0.9:  # 90% threshold
                self.logger.warning(f"Memory pressure detected, attempting garbage collection")
                self._garbage_collect()
                
                if self.memory_usage >= self.memory_limit_mb * 0.95:
                    self.logger.error(f"Insufficient memory to launch {app_name}")
                    return False
            
            # Simulate app launch delay
            time.sleep(self.app_launch_delay)
            
            # Add random variation to launch time
            variation = random.uniform(0.8, 1.2)
            actual_launch_time = self.app_launch_delay * variation
            
            # Calculate memory usage for app (simulated)
            app_memory = random.randint(50, 200)  # 50-200 MB per app
            
            # Launch app
            self.running_apps[app_id] = {
                'name': app_name,
                'launch_time': actual_launch_time,
                'memory_usage': app_memory,
                'start_time': time.time(),
                'status': 'running'
            }
            
            self.memory_usage += app_memory
            self.app_history.append(app_name)
            self.app_launch_times.append(actual_launch_time)
            
            # Keep only last 10 apps in history
            if len(self.app_history) > 10:
                self.app_history.pop(0)
            
            self.logger.info(f"App {app_name} launched in {actual_launch_time:.3f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch app {app_name}: {e}")
            return False
    
    def close_app(self, app_id: str) -> bool:
        """Close an Android app."""
        try:
            if app_id not in self.running_apps:
                return False
            
            app = self.running_apps[app_id]
            self.memory_usage -= app['memory_usage']
            del self.running_apps[app_id]
            
            self.logger.info(f"App {app['name']} closed, freed {app['memory_usage']}MB")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close app {app_id}: {e}")
            return False
    
    def switch_app(self, app_id: str) -> bool:
        """Switch to a different app (Android multitasking)."""
        if not self.multitasking_enabled:
            self.logger.warning("Multitasking not enabled")
            return False
        
        if app_id not in self.running_apps:
            self.logger.error(f"App {app_id} not running")
            return False
        
        # Simulate app switching delay
        switch_delay = random.uniform(0.1, 0.3)
        time.sleep(switch_delay)
        
        self.logger.info(f"Switched to app {self.running_apps[app_id]['name']}")
        return True
    
    def _garbage_collect(self) -> None:
        """Simulate Android garbage collection."""
        current_time = time.time()
        if current_time - self.last_gc_time < self.gc_interval:
            return
        
        # Simulate memory cleanup
        cleanup_amount = random.randint(50, 200)
        self.memory_usage = max(0, self.memory_usage - cleanup_amount)
        self.last_gc_time = current_time
        self.memory_pressure_events += 1
        
        self.logger.info(f"Garbage collection completed, freed {cleanup_amount}MB")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.app_launch_times:
            return {}
        
        avg_launch_time = sum(self.app_launch_times) / len(self.app_launch_times)
        max_launch_time = max(self.app_launch_times)
        min_launch_time = min(self.app_launch_times)
        
        return {
            'avg_app_launch_time': avg_launch_time,
            'max_app_launch_time': max_launch_time,
            'min_app_launch_time': min_launch_time,
            'running_apps_count': len(self.running_apps),
            'memory_usage_mb': self.memory_usage,
            'memory_usage_percentage': (self.memory_usage / self.memory_limit_mb) * 100,
            'memory_pressure_events': self.memory_pressure_events,
            'app_history': self.app_history.copy()
        }

class HybridSimulator:
    """Combines QNX and Android simulation for realistic behavior."""
    
    def __init__(self):
        self.logger = get_logger("hybrid_simulator")
        self.qnx_simulator = QNXSimulator()
        self.android_simulator = AndroidSimulator()
        
        # Hybrid-specific settings
        self.platform_switch_threshold = 0.8  # Switch platforms when load > 80%
        self.current_primary_platform = "qnx"
        
        self.logger.info("Hybrid Simulator initialized")
    
    def start(self) -> None:
        """Start both simulators."""
        self.qnx_simulator.start()
        self.logger.info("Hybrid Simulator started")
    
    def stop(self) -> None:
        """Stop both simulators."""
        self.qnx_simulator.stop()
        self.logger.info("Hybrid Simulator stopped")
    
    def submit_task(self, task: SimulatedTask, platform: str = "auto") -> bool:
        """Submit task to appropriate platform."""
        if platform == "auto":
            # Auto-select platform based on task characteristics
            if task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                platform = "qnx"
            else:
                platform = "android"
        
        if platform == "qnx":
            return self.qnx_simulator.submit_task(task)
        elif platform == "android":
            # Convert task to app launch for Android
            return self.android_simulator.launch_app(task.name, task.id)
        else:
            self.logger.error(f"Unknown platform: {platform}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get combined performance metrics."""
        qnx_metrics = self.qnx_simulator.get_performance_metrics()
        android_metrics = self.android_simulator.get_performance_metrics()
        
        # Combine metrics
        combined_metrics = {
            'platform': 'hybrid',
            'qnx': qnx_metrics,
            'android': android_metrics
        }
        
        # Calculate overall system health
        if qnx_metrics and android_metrics:
            overall_health = 100
            
            # Deduct points for missed deadlines
            if qnx_metrics.get('missed_deadlines', 0) > 0:
                overall_health -= 20
            
            # Deduct points for memory pressure
            if android_metrics.get('memory_usage_percentage', 0) > 80:
                overall_health -= 15
            
            # Deduct points for slow response times
            if qnx_metrics.get('avg_response_time', 0) > 0.1:
                overall_health -= 10
            
            combined_metrics['overall_system_health'] = max(0, overall_health)
        
        return combined_metrics

class PlatformSimulator:
    """Main platform simulator that manages all simulation modes."""
    
    def __init__(self, mode: PlatformMode = PlatformMode.HYBRID):
        self.logger = get_logger("platform_simulator")
        self.mode = mode
        
        # Initialize appropriate simulator
        if mode == PlatformMode.QNX:
            self.simulator = QNXSimulator()
        elif mode == PlatformMode.ANDROID:
            self.simulator = AndroidSimulator()
        else:
            self.simulator = HybridSimulator()
        
        self.logger.info(f"Platform Simulator initialized in {mode.value} mode")
    
    def start(self) -> None:
        """Start the platform simulator."""
        if hasattr(self.simulator, 'start'):
            self.simulator.start()
        self.logger.info("Platform Simulator started")
    
    def stop(self) -> None:
        """Stop the platform simulator."""
        if hasattr(self.simulator, 'stop'):
            self.simulator.stop()
        self.logger.info("Platform Simulator stopped")
    
    def submit_task(self, task: SimulatedTask, platform: str = "auto") -> bool:
        """Submit a task to the simulator."""
        if hasattr(self.simulator, 'submit_task'):
            return self.simulator.submit_task(task, platform)
        return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from the simulator."""
        if hasattr(self.simulator, 'get_performance_metrics'):
            return self.simulator.get_performance_metrics()
        return {}
    
    def create_task(self, name: str, priority: TaskPriority = TaskPriority.NORMAL,
                   execution_time: float = 0.1, deadline: float = None,
                   memory_usage: int = 100, cpu_usage: float = 0.1) -> SimulatedTask:
        """Create a new simulated task."""
        if deadline is None:
            deadline = time.time() + execution_time * 2
        
        task = SimulatedTask(
            id=f"task_{int(time.time() * 1000)}",
            name=name,
            priority=priority,
            execution_time=execution_time,
            deadline=deadline,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            created_at=time.time()
        )
        
        return task 