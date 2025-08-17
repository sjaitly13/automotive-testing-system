"""
Climate control widget for the infotainment interface.
Simulates HVAC system functionality with performance tracking.
"""

import tkinter as tk
from tkinter import ttk
import time
import random
from typing import Dict, List, Any

from ...utils.logger import get_logger
from ...monitoring.performance_monitor import get_performance_monitor

class ClimateWidget(ttk.Frame):
    """Climate control application widget."""
    
    def __init__(self, parent, main_interface):
        super().__init__(parent)
        self.main_interface = main_interface
        self.logger = get_logger("climate")
        self.performance_monitor = get_performance_monitor()
        
        # Climate state
        self.temperature = 22.0  # Celsius
        self.fan_speed = 2
        self.auto_mode = True
        self.defrost = False
        self.recirculation = False
        self.dual_zone = False
        self.driver_temp = 22.0
        self.passenger_temp = 22.0
        
        # Performance tracking
        self.operation_times = []
        
        self._create_widgets()
        self.logger.info("Climate Widget initialized")
    
    def _create_widgets(self):
        """Create all climate control UI elements."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_container, text="❄️ Climate Control", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Temperature control section
        self._create_temperature_section(main_container)
        
        # Fan and air flow section
        self._create_fan_section(main_container)
        
        # Mode controls section
        self._create_mode_section(main_container)
        
        # Zone control section
        self._create_zone_section(main_container)
        
        # Performance metrics
        self._create_performance_section(main_container)
    
    def _create_temperature_section(self, parent):
        """Create the temperature control section."""
        temp_frame = ttk.LabelFrame(parent, text="Temperature Control", padding=15)
        temp_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Main temperature display
        temp_display_frame = ttk.Frame(temp_frame)
        temp_display_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Driver temperature
        driver_temp_frame = ttk.Frame(temp_display_frame)
        driver_temp_frame.pack(side=tk.LEFT, expand=True)
        
        ttk.Label(driver_temp_frame, text="Driver", font=('Arial', 12, 'bold')).pack()
        
        self.driver_temp_var = tk.DoubleVar(value=self.driver_temp)
        self.driver_temp_label = ttk.Label(driver_temp_frame, text=f"{self.driver_temp:.1f}°C", 
                                         font=('Arial', 18, 'bold'))
        self.driver_temp_label.pack()
        
        # Driver temperature controls
        driver_controls_frame = ttk.Frame(driver_temp_frame)
        driver_controls_frame.pack(pady=(10, 0))
        
        self.driver_down_btn = ttk.Button(driver_controls_frame, text="⬇", 
                                         command=lambda: self._adjust_temperature('driver', -0.5), width=6)
        self.driver_down_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.driver_up_btn = ttk.Button(driver_controls_frame, text="⬆", 
                                       command=lambda: self._adjust_temperature('driver', 0.5), width=6)
        self.driver_up_btn.pack(side=tk.LEFT)
        
        # Passenger temperature
        passenger_temp_frame = ttk.Frame(temp_display_frame)
        passenger_temp_frame.pack(side=tk.RIGHT, expand=True)
        
        ttk.Label(passenger_temp_frame, text="Passenger", font=('Arial', 12, 'bold')).pack()
        
        self.passenger_temp_var = tk.DoubleVar(value=self.passenger_temp)
        self.passenger_temp_label = ttk.Label(passenger_temp_frame, text=f"{self.passenger_temp:.1f}°C", 
                                            font=('Arial', 18, 'bold'))
        self.passenger_temp_label.pack()
        
        # Passenger temperature controls
        passenger_controls_frame = ttk.Frame(passenger_temp_frame)
        passenger_controls_frame.pack(pady=(10, 0))
        
        self.passenger_down_btn = ttk.Button(passenger_controls_frame, text="⬇", 
                                            command=lambda: self._adjust_temperature('passenger', -0.5), width=6)
        self.passenger_down_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.passenger_up_btn = ttk.Button(passenger_controls_frame, text="⬆", 
                                          command=lambda: self._adjust_temperature('passenger', 0.5), width=6)
        self.passenger_up_btn.pack(side=tk.LEFT)
        
        # Sync button
        sync_frame = ttk.Frame(temp_frame)
        sync_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.sync_button = ttk.Button(sync_frame, text="🔄 Sync Temperatures", 
                                     command=self._sync_temperatures, width=20)
        self.sync_button.pack()
    
    def _create_fan_section(self, parent):
        """Create the fan and air flow section."""
        fan_frame = ttk.LabelFrame(parent, text="Fan & Air Flow", padding=15)
        fan_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Fan speed
        fan_speed_frame = ttk.Frame(fan_frame)
        fan_speed_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(fan_speed_frame, text="Fan Speed:").pack(side=tk.LEFT)
        
        self.fan_speed_var = tk.IntVar(value=self.fan_speed)
        self.fan_speed_scale = ttk.Scale(fan_speed_frame, from_=0, to=7, 
                                        variable=self.fan_speed_var, orient=tk.HORIZONTAL,
                                        command=self._on_fan_speed_change)
        self.fan_speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.fan_speed_label = ttk.Label(fan_speed_frame, text=f"Level {self.fan_speed}")
        self.fan_speed_label.pack(side=tk.RIGHT)
        
        # Air flow direction
        flow_frame = ttk.Frame(fan_frame)
        flow_frame.pack(fill=tk.X)
        
        ttk.Label(flow_frame, text="Air Flow:").pack(anchor=tk.W)
        
        flow_buttons_frame = ttk.Frame(flow_frame)
        flow_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.face_btn = ttk.Button(flow_buttons_frame, text="😊 Face", 
                                  command=lambda: self._set_air_flow('face'), width=10)
        self.face_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.feet_btn = ttk.Button(flow_buttons_frame, text="👣 Feet", 
                                  command=lambda: self._set_air_flow('feet'), width=10)
        self.feet_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.windshield_btn = ttk.Button(flow_buttons_frame, text="🪟 Windshield", 
                                        command=lambda: self._set_air_flow('windshield'), width=12)
        self.windshield_btn.pack(side=tk.LEFT)
    
    def _create_mode_section(self, parent):
        """Create the climate mode controls section."""
        mode_frame = ttk.LabelFrame(parent, text="Climate Modes", padding=15)
        mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Auto mode
        auto_frame = ttk.Frame(mode_frame)
        auto_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_var = tk.BooleanVar(value=self.auto_mode)
        self.auto_check = ttk.Checkbutton(auto_frame, text="🤖 Auto Mode", 
                                         variable=self.auto_var, command=self._toggle_auto_mode)
        self.auto_check.pack(side=tk.LEFT)
        
        # Defrost
        defrost_frame = ttk.Frame(mode_frame)
        defrost_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.defrost_var = tk.BooleanVar(value=self.defrost)
        self.defrost_check = ttk.Checkbutton(defrost_frame, text="🧊 Front Defrost", 
                                            variable=self.defrost_var, command=self._toggle_defrost)
        self.defrost_check.pack(side=tk.LEFT)
        
        # Recirculation
        recirc_frame = ttk.Frame(mode_frame)
        recirc_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.recirc_var = tk.BooleanVar(value=self.recirculation)
        self.recirc_check = ttk.Checkbutton(recirc_frame, text="🔄 Recirculation", 
                                           variable=self.recirc_var, command=self._toggle_recirculation)
        self.recirc_check.pack(side=tk.LEFT)
        
        # Dual zone
        dual_frame = ttk.Frame(mode_frame)
        dual_frame.pack(fill=tk.X)
        
        self.dual_var = tk.BooleanVar(value=self.dual_zone)
        self.dual_check = ttk.Checkbutton(dual_frame, text="👥 Dual Zone", 
                                         variable=self.dual_var, command=self._toggle_dual_zone)
        self.dual_check.pack(side=tk.LEFT)
    
    def _create_zone_section(self, parent):
        """Create the climate zone control section."""
        zone_frame = ttk.LabelFrame(parent, text="Zone Control", padding=15)
        zone_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Zone selection
        zone_select_frame = ttk.Frame(zone_frame)
        zone_select_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(zone_select_frame, text="Active Zone:").pack(side=tk.LEFT)
        
        self.zone_var = tk.StringVar(value="driver")
        zone_combo = ttk.Combobox(zone_select_frame, textvariable=self.zone_var, 
                                 values=["Driver", "Passenger", "Rear"], state="readonly", width=15)
        zone_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Zone-specific controls
        zone_controls_frame = ttk.Frame(zone_frame)
        zone_controls_frame.pack(fill=tk.X)
        
        # Seat heating/cooling
        seat_frame = ttk.Frame(zone_controls_frame)
        seat_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(seat_frame, text="Seat:").pack(side=tk.LEFT)
        
        self.seat_heat_btn = ttk.Button(seat_frame, text="🔥 Heat", 
                                       command=lambda: self._set_seat_mode('heat'), width=10)
        self.seat_heat_btn.pack(side=tk.LEFT, padx=(10, 5))
        
        self.seat_cool_btn = ttk.Button(seat_frame, text="❄️ Cool", 
                                       command=lambda: self._set_seat_mode('cool'), width=10)
        self.seat_cool_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.seat_off_btn = ttk.Button(seat_frame, text="⏹️ Off", 
                                      command=lambda: self._set_seat_mode('off'), width=10)
        self.seat_off_btn.pack(side=tk.LEFT)
        
        # Steering wheel heating
        wheel_frame = ttk.Frame(zone_controls_frame)
        wheel_frame.pack(fill=tk.X)
        
        ttk.Label(wheel_frame, text="Steering Wheel:").pack(side=tk.LEFT)
        
        self.wheel_heat_btn = ttk.Button(wheel_frame, text="🔥 Heat", 
                                        command=lambda: self._set_wheel_heating(True), width=10)
        self.wheel_heat_btn.pack(side=tk.LEFT, padx=(10, 5))
        
        self.wheel_off_btn = ttk.Button(wheel_frame, text="⏹️ Off", 
                                       command=lambda: self._set_wheel_heating(False), width=10)
        self.wheel_off_btn.pack(side=tk.LEFT)
    
    def _create_performance_section(self, parent):
        """Create the performance metrics section."""
        perf_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=15)
        perf_frame.pack(fill=tk.X)
        
        # Performance indicators
        perf_indicators_frame = ttk.Frame(perf_frame)
        perf_indicators_frame.pack(fill=tk.X)
        
        # Response time
        self.response_time_label = ttk.Label(perf_indicators_frame, text="Response Time: 0ms")
        self.response_time_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Operation count
        self.operation_count_label = ttk.Label(perf_indicators_frame, text="Operations: 0")
        self.operation_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Temperature changes
        self.temp_changes_label = ttk.Label(perf_indicators_frame, text="Temp Changes: 0")
        self.temp_changes_label.pack(side=tk.LEFT)
    
    def _adjust_temperature(self, zone, delta):
        """Adjust temperature for a specific zone."""
        try:
            start_time = time.time()
            
            if zone == 'driver':
                self.driver_temp = max(16.0, min(32.0, self.driver_temp + delta))
                self.driver_temp_var.set(self.driver_temp)
                self.driver_temp_label.config(text=f"{self.driver_temp:.1f}°C")
            elif zone == 'passenger':
                self.passenger_temp = max(16.0, min(32.0, self.passenger_temp + delta))
                self.passenger_temp_var.set(self.passenger_temp)
                self.passenger_temp_label.config(text=f"{self.passenger_temp:.1f}°C")
            
            # Simulate temperature adjustment delay
            time.sleep(0.1)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Temperature adjusted for {zone}: {self.driver_temp if zone == 'driver' else self.passenger_temp:.1f}°C")
            
        except Exception as e:
            self.logger.error(f"Error adjusting temperature: {e}")
    
    def _sync_temperatures(self):
        """Synchronize driver and passenger temperatures."""
        try:
            start_time = time.time()
            
            # Set both temperatures to driver temperature
            self.passenger_temp = self.driver_temp
            self.passenger_temp_var.set(self.passenger_temp)
            self.passenger_temp_label.config(text=f"{self.passenger_temp:.1f}°C")
            
            # Simulate sync operation
            time.sleep(0.2)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info("Temperatures synchronized")
            
        except Exception as e:
            self.logger.error(f"Error synchronizing temperatures: {e}")
    
    def _on_fan_speed_change(self, value):
        """Handle fan speed change."""
        try:
            self.fan_speed = int(float(value))
            self.fan_speed_label.config(text=f"Level {self.fan_speed}")
            
            # Simulate fan speed change
            time.sleep(0.05)
            
        except Exception as e:
            self.logger.error(f"Error changing fan speed: {e}")
    
    def _set_air_flow(self, direction):
        """Set air flow direction."""
        try:
            start_time = time.time()
            
            # Simulate air flow change
            time.sleep(0.1)
            
            self.logger.info(f"Air flow set to: {direction}")
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
        except Exception as e:
            self.logger.error(f"Error setting air flow: {e}")
    
    def _toggle_auto_mode(self):
        """Toggle automatic climate control mode."""
        try:
            start_time = time.time()
            
            self.auto_mode = self.auto_var.get()
            
            # Simulate mode change
            time.sleep(0.1)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Auto mode: {'enabled' if self.auto_mode else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error toggling auto mode: {e}")
    
    def _toggle_defrost(self):
        """Toggle front defrost mode."""
        try:
            start_time = time.time()
            
            self.defrost = self.defrost_var.get()
            
            # Simulate defrost operation
            time.sleep(0.1)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Front defrost: {'enabled' if self.defrost else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error toggling defrost: {e}")
    
    def _toggle_recirculation(self):
        """Toggle air recirculation mode."""
        try:
            start_time = time.time()
            
            self.recirculation = self.recirc_var.get()
            
            # Simulate recirculation change
            time.sleep(0.1)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Recirculation: {'enabled' if self.recirculation else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error toggling recirculation: {e}")
    
    def _toggle_dual_zone(self):
        """Toggle dual zone climate control."""
        try:
            start_time = time.time()
            
            self.dual_zone = self.dual_var.get()
            
            # Simulate dual zone change
            time.sleep(0.1)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Dual zone: {'enabled' if self.dual_zone else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error toggling dual zone: {e}")
    
    def _set_seat_mode(self, mode):
        """Set seat heating/cooling mode."""
        try:
            start_time = time.time()
            
            # Simulate seat mode change
            time.sleep(0.1)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Seat mode set to: {mode}")
            
        except Exception as e:
            self.logger.error(f"Error setting seat mode: {e}")
    
    def _set_wheel_heating(self, enabled):
        """Set steering wheel heating."""
        try:
            start_time = time.time()
            
            # Simulate wheel heating change
            time.sleep(0.1)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Steering wheel heating: {'enabled' if enabled else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error setting wheel heating: {e}")
    
    def update_performance_display(self):
        """Update performance metrics display."""
        try:
            # Update response time
            if self.operation_times:
                latest_response = self.operation_times[-1]
                self.response_time_label.config(text=f"Response Time: {latest_response:.1f}ms")
            
            # Update operation count
            self.operation_count_label.config(text=f"Operations: {len(self.operation_times)}")
            
            # Update temperature changes count
            temp_changes = len([op for op in self.operation_times if op > 50])  # Temperature ops are slower
            self.temp_changes_label.config(text=f"Temp Changes: {temp_changes}")
            
        except Exception as e:
            self.logger.error(f"Error updating performance display: {e}")
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance data for this widget."""
        return {
            'operation_times': self.operation_times,
            'temperature': self.temperature,
            'fan_speed': self.fan_speed,
            'auto_mode': self.auto_mode,
            'defrost': self.defrost,
            'recirculation': self.recirculation,
            'dual_zone': self.dual_zone,
            'driver_temp': self.driver_temp,
            'passenger_temp': self.passenger_temp
        } 