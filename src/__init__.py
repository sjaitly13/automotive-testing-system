"""
Automotive Infotainment Performance Testing System

A comprehensive simulation and testing framework for automotive infotainment systems
"""

__version__ = "1.0.0"
__author__ = "Sarisha Jaitly"
__description__ = "Automated Performance Testing for In-Vehicle Infotainment System"

# Core components (no UI dependencies)
from .monitoring.performance_monitor import get_performance_monitor
from .simulation.platform_simulator import PlatformSimulator, PlatformMode
from .automation.run_tests import AutomatedTestRunner
from .analysis.ml_analyzer import MLPerformanceAnalyzer

__all__ = [
    'get_performance_monitor',
    'PlatformSimulator',
    'PlatformMode',
    'AutomatedTestRunner',
    'MLPerformanceAnalyzer'
] 