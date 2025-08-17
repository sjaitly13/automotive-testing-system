#!/usr/bin/env python3
"""
Main entry point for the Automotive Infotainment Performance Testing System.
Launches the main infotainment interface and initializes all components.
"""

import sys
import os
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging, get_logger
from utils.config_loader import get_config
from interface.infotainment_ui import InfotainmentInterface
from monitoring.performance_monitor import get_performance_monitor
from simulation.platform_simulator import PlatformSimulator, PlatformMode

def main():
    """Main application entry point."""
    try:
        # Setup logging
        logger = setup_logging("main", "INFO")
        logger.info("=" * 60)
        logger.info("Automotive Infotainment Performance Testing System")
        logger.info("=" * 60)
        logger.info("Starting system initialization...")
        
        # Load configuration
        config = get_config()
        if not config.validate():
            logger.error("Configuration validation failed. Exiting.")
            sys.exit(1)
        
        logger.info("Configuration loaded successfully")
        
        # Initialize platform simulator
        platform_mode = PlatformMode(config.get('platform.mode', 'hybrid'))
        platform_simulator = PlatformSimulator(platform_mode)
        
        logger.info(f"Platform simulator initialized in {platform_mode.value} mode")
        
        # Start platform simulation
        platform_simulator.start()
        
        # Initialize performance monitoring
        performance_monitor = get_performance_monitor()
        
        # Create and run the main interface
        logger.info("Launching infotainment interface...")
        
        app = InfotainmentInterface()
        
        # Start performance monitoring
        performance_monitor.start_monitoring()
        
        logger.info("System initialization completed successfully")
        logger.info("Infotainment interface is now running")
        logger.info("Press Ctrl+C to exit")
        
        # Run the main application
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            logger.info("Performing system cleanup...")
            
            # Stop platform simulation
            if 'platform_simulator' in locals():
                platform_simulator.stop()
            
            # Stop performance monitoring
            if 'performance_monitor' in locals():
                performance_monitor.stop_monitoring()
            
            logger.info("System shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main() 