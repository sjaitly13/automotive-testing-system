"""
Performance monitoring system for the infotainment testing system.
Tracks CPU, memory, response times, and other system metrics in real-time.
"""

import time
import threading
import psutil
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.config_loader import get_config

@dataclass
class PerformanceMetric:
    """Represents a single performance measurement."""
    timestamp: float
    metric_name: str
    value: float
    unit: str
    component: str
    additional_data: Dict[str, Any] = None

@dataclass
class SystemSnapshot:
    """Represents a complete system state snapshot."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    process_count: int
    response_time_ms: float
    frame_rate: float
    error_count: int

class PerformanceMonitor:
    """Monitors system performance metrics in real-time."""
    
    def __init__(self, sampling_rate_hz: float = 10.0):
        self.logger = get_logger("performance_monitor")
        self.config = get_config()
        
        # Configuration
        self.sampling_rate_hz = sampling_rate_hz
        self.sampling_interval = 1.0 / sampling_rate_hz
        
        # Data storage
        self.metrics: List[PerformanceMetric] = []
        self.snapshots: List[SystemSnapshot] = []
        self.max_storage_size = 10000  # Maximum number of metrics to store
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance thresholds
        self.thresholds = self.config.get_performance_thresholds()
        
        # Callbacks for alerts
        self.alert_callbacks: List[Callable] = []
        
        # Database connection
        self.db_path = Path("data/performance_data.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
        self.logger.info("Performance Monitor initialized")
    
    def _init_database(self) -> None:
        """Initialize SQLite database for performance data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    metric_name TEXT,
                    value REAL,
                    unit TEXT,
                    component TEXT,
                    additional_data TEXT
                )
            ''')
            
            # Create snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_available_mb REAL,
                    disk_usage_percent REAL,
                    network_io TEXT,
                    process_count INTEGER,
                    response_time_ms REAL,
                    frame_rate REAL,
                    error_count INTEGER
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON performance_metrics(metric_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON system_snapshots(timestamp)')
            
            conn.commit()
            conn.close()
            self.logger.info("Performance database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                start_time = time.time()
                
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check thresholds and trigger alerts
                self._check_thresholds()
                
                # Calculate sleep time to maintain sampling rate
                elapsed = time.time() - start_time
                sleep_time = max(0, self.sampling_interval - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)
    
    def _collect_system_metrics(self) -> None:
        """Collect current system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self._add_metric("cpu_usage", cpu_percent, "%", "system")
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)
            self._add_metric("memory_usage", memory_percent, "%", "system")
            self._add_metric("memory_available", memory_available_mb, "MB", "system")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            self._add_metric("disk_usage", disk_percent, "%", "system")
            
            # Network I/O
            network = psutil.net_io_counters()
            self._add_metric("network_bytes_sent", network.bytes_sent, "bytes", "network")
            self._add_metric("network_bytes_recv", network.bytes_recv, "bytes", "network")
            
            # Process count
            process_count = len(psutil.pids())
            self._add_metric("process_count", process_count, "count", "system")
            
            # Create system snapshot
            snapshot = SystemSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                process_count=process_count,
                response_time_ms=0.0,  # Will be updated by other components
                frame_rate=0.0,        # Will be updated by other components
                error_count=0          # Will be updated by other components
            )
            
            self.snapshots.append(snapshot)
            self._save_snapshot_to_db(snapshot)
            
            # Limit storage size
            if len(self.snapshots) > self.max_storage_size:
                self.snapshots.pop(0)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _add_metric(self, name: str, value: float, unit: str, component: str, 
                    additional_data: Dict[str, Any] = None) -> None:
        """Add a performance metric."""
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_name=name,
            value=value,
            unit=unit,
            component=component,
            additional_data=additional_data or {}
        )
        
        self.metrics.append(metric)
        self._save_metric_to_db(metric)
        
        # Limit storage size
        if len(self.metrics) > self.max_storage_size:
            self.metrics.pop(0)
    
    def _save_metric_to_db(self, metric: PerformanceMetric) -> None:
        """Save metric to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            additional_data_json = json.dumps(metric.additional_data) if metric.additional_data else None
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, metric_name, value, unit, component, additional_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metric.timestamp,
                metric.metric_name,
                metric.value,
                metric.unit,
                metric.component,
                additional_data_json
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save metric to database: {e}")
    
    def _save_snapshot_to_db(self, snapshot: SystemSnapshot) -> None:
        """Save system snapshot to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            network_io_json = json.dumps(snapshot.network_io)
            
            cursor.execute('''
                INSERT INTO system_snapshots 
                (timestamp, cpu_percent, memory_percent, memory_available_mb, 
                 disk_usage_percent, network_io, process_count, response_time_ms, 
                 frame_rate, error_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot.timestamp,
                snapshot.cpu_percent,
                snapshot.memory_percent,
                snapshot.memory_available_mb,
                snapshot.disk_usage_percent,
                network_io_json,
                snapshot.process_count,
                snapshot.response_time_ms,
                snapshot.frame_rate,
                snapshot.error_count
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save snapshot to database: {e}")
    
    def _check_thresholds(self) -> None:
        """Check performance thresholds and trigger alerts."""
        try:
            if not self.snapshots:
                return
            
            latest = self.snapshots[-1]
            
            # Check CPU threshold
            cpu_threshold = self.thresholds.get('cpu_usage', {}).get('max_percentage', 80.0)
            if latest.cpu_percent > cpu_threshold:
                self._trigger_alert("high_cpu_usage", {
                    'current': latest.cpu_percent,
                    'threshold': cpu_threshold,
                    'timestamp': latest.timestamp
                })
            
            # Check memory threshold
            memory_threshold = self.thresholds.get('memory_usage', {}).get('max_percentage', 85.0)
            if latest.memory_percent > memory_threshold:
                self._trigger_alert("high_memory_usage", {
                    'current': latest.memory_percent,
                    'threshold': memory_threshold,
                    'timestamp': latest.timestamp
                })
            
            # Check disk threshold
            if latest.disk_usage_percent > 90.0:
                self._trigger_alert("high_disk_usage", {
                    'current': latest.disk_usage_percent,
                    'threshold': 90.0,
                    'timestamp': latest.timestamp
                })
                
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    def _trigger_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Trigger a performance alert."""
        alert_message = f"Performance alert: {alert_type} - {data}"
        self.logger.warning(alert_message)
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, data)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Add a callback function for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def update_response_time(self, response_time_ms: float) -> None:
        """Update the current response time metric."""
        self._add_metric("response_time", response_time_ms, "ms", "ui")
        
        # Update latest snapshot
        if self.snapshots:
            self.snapshots[-1].response_time_ms = response_time_ms
    
    def update_frame_rate(self, frame_rate: float) -> None:
        """Update the current frame rate metric."""
        self._add_metric("frame_rate", frame_rate, "fps", "ui")
        
        # Update latest snapshot
        if self.snapshots:
            self.snapshots[-1].frame_rate = frame_rate
    
    def update_error_count(self, error_count: int) -> None:
        """Update the current error count metric."""
        self._add_metric("error_count", error_count, "count", "system")
        
        # Update latest snapshot
        if self.snapshots:
            self.snapshots[-1].error_count = error_count
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        return {
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_available_mb': latest.memory_available_mb,
            'disk_usage_percent': latest.disk_usage_percent,
            'process_count': latest.process_count,
            'response_time_ms': latest.response_time_ms,
            'frame_rate': latest.frame_rate,
            'error_count': latest.error_count,
            'timestamp': latest.timestamp
        }
    
    def get_metrics_history(self, metric_name: str, 
                           start_time: Optional[float] = None,
                           end_time: Optional[float] = None) -> List[PerformanceMetric]:
        """Get historical metrics for a specific metric name."""
        if not start_time:
            start_time = time.time() - 3600  # Last hour
        if not end_time:
            end_time = time.time()
        
        return [
            metric for metric in self.metrics
            if (metric.metric_name == metric_name and
                start_time <= metric.timestamp <= end_time)
        ]
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)."""
        try:
            if not self.snapshots:
                return 100.0
            
            latest = self.snapshots[-1]
            score = 100.0
            
            # Deduct points for high CPU usage
            if latest.cpu_percent > 80:
                score -= 20
            elif latest.cpu_percent > 60:
                score -= 10
            
            # Deduct points for high memory usage
            if latest.memory_percent > 85:
                score -= 20
            elif latest.memory_percent > 70:
                score -= 10
            
            # Deduct points for high disk usage
            if latest.disk_usage_percent > 90:
                score -= 15
            
            # Deduct points for slow response time
            if latest.response_time_ms > 200:
                score -= 15
            elif latest.response_time_ms > 100:
                score -= 5
            
            # Deduct points for low frame rate
            if latest.frame_rate < 30:
                score -= 10
            elif latest.frame_rate < 50:
                score -= 5
            
            # Deduct points for errors
            if latest.error_count > 0:
                score -= min(20, latest.error_count * 5)
            
            return max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 50.0
    
    def export_metrics(self, file_path: str, format: str = "json") -> bool:
        """Export performance metrics to file."""
        try:
            if format.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump({
                        'metrics': [asdict(m) for m in self.metrics],
                        'snapshots': [asdict(s) for s in self.snapshots]
                    }, f, indent=2, default=str)
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False
            
            self.logger.info(f"Metrics exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            return False
    
    def clear_old_data(self, older_than_hours: int = 24) -> None:
        """Clear old performance data."""
        try:
            cutoff_time = time.time() - (older_than_hours * 3600)
            
            # Clear from memory
            self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
            self.snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
            
            # Clear from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM performance_metrics WHERE timestamp < ?', (cutoff_time,))
            cursor.execute('DELETE FROM system_snapshots WHERE timestamp < ?', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleared performance data older than {older_than_hours} hours")
            
        except Exception as e:
            self.logger.error(f"Failed to clear old data: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return performance_monitor 