"""
Settings widget for the infotainment interface.
Provides system configuration and settings management with performance tracking.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
from typing import Dict, List, Any

from ...utils.logger import get_logger
from ...monitoring.performance_monitor import get_performance_monitor
from ...utils.config_loader import get_config

class SettingsWidget(ttk.Frame):
    """Settings application widget."""
    
    def __init__(self, parent, main_interface):
        super().__init__(parent)
        self.main_interface = main_interface
        self.logger = get_logger("settings")
        self.performance_monitor = get_performance_monitor()
        self.config = get_config()
        
        # Settings state
        self.current_settings = self._load_current_settings()
        self.original_settings = self.current_settings.copy()
        
        # Performance tracking
        self.operation_times = []
        
        self._create_widgets()
        self.logger.info("Settings Widget initialized")
    
    def _load_current_settings(self) -> Dict[str, Any]:
        """Load current system settings."""
        return {
            'display': {
                'brightness': 75,
                'contrast': 50,
                'theme': 'dark',
                'language': 'English',
                'units': 'metric'
            },
            'audio': {
                'volume': 70,
                'bass': 50,
                'treble': 50,
                'balance': 0,
                'fade': 0,
                'surround': True
            },
            'system': {
                'auto_lock': True,
                'power_save': False,
                'updates': True,
                'diagnostics': False,
                'backup': True
            },
            'connectivity': {
                'wifi': True,
                'bluetooth': True,
                'cellular': False,
                'hotspot': False
            }
        }
    
    def _create_widgets(self):
        """Create all settings UI elements."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_container, text="⚙️ System Settings", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Display settings tab
        self._create_display_tab()
        
        # Audio settings tab
        self._create_audio_tab()
        
        # System settings tab
        self._create_system_tab()
        
        # Connectivity settings tab
        self._create_connectivity_tab()
        
        # Control buttons
        self._create_control_buttons(main_container)
        
        # Performance metrics
        self._create_performance_section(main_container)
    
    def _create_display_tab(self):
        """Create the display settings tab."""
        display_frame = ttk.Frame(self.notebook)
        self.notebook.add(display_frame, text="🖥️ Display")
        
        # Brightness control
        brightness_frame = ttk.LabelFrame(display_frame, text="Brightness & Contrast", padding=15)
        brightness_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Brightness
        bright_frame = ttk.Frame(brightness_frame)
        bright_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(bright_frame, text="Brightness:").pack(side=tk.LEFT)
        
        self.brightness_var = tk.IntVar(value=self.current_settings['display']['brightness'])
        self.brightness_scale = ttk.Scale(bright_frame, from_=0, to=100, 
                                         variable=self.brightness_var, orient=tk.HORIZONTAL,
                                         command=self._on_brightness_change)
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.brightness_label = ttk.Label(bright_frame, text=f"{self.current_settings['display']['brightness']}%")
        self.brightness_label.pack(side=tk.RIGHT)
        
        # Contrast
        contrast_frame = ttk.Frame(brightness_frame)
        contrast_frame.pack(fill=tk.X)
        
        ttk.Label(contrast_frame, text="Contrast:").pack(side=tk.LEFT)
        
        self.contrast_var = tk.IntVar(value=self.current_settings['display']['contrast'])
        self.contrast_scale = ttk.Scale(contrast_frame, from_=0, to=100, 
                                       variable=self.contrast_var, orient=tk.HORIZONTAL,
                                       command=self._on_contrast_change)
        self.contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.contrast_label = ttk.Label(contrast_frame, text=f"{self.current_settings['display']['contrast']}%")
        self.contrast_label.pack(side=tk.RIGHT)
        
        # Theme selection
        theme_frame = ttk.LabelFrame(display_frame, text="Appearance", padding=15)
        theme_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Theme
        theme_select_frame = ttk.Frame(theme_frame)
        theme_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(theme_select_frame, text="Theme:").pack(side=tk.LEFT)
        
        self.theme_var = tk.StringVar(value=self.current_settings['display']['theme'])
        theme_combo = ttk.Combobox(theme_select_frame, textvariable=self.theme_var, 
                                  values=["light", "dark", "auto"], state="readonly", width=15)
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        theme_combo.bind('<<ComboboxSelected>>', self._on_theme_change)
        
        # Language
        lang_frame = ttk.Frame(theme_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        
        self.language_var = tk.StringVar(value=self.current_settings['display']['language'])
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                 values=["English", "Spanish", "French", "German", "Chinese"], 
                                 state="readonly", width=15)
        lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        lang_combo.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # Units
        units_frame = ttk.Frame(theme_frame)
        units_frame.pack(fill=tk.X)
        
        ttk.Label(units_frame, text="Units:").pack(side=tk.LEFT)
        
        self.units_var = tk.StringVar(value=self.current_settings['display']['units'])
        units_combo = ttk.Combobox(units_frame, textvariable=self.units_var, 
                                  values=["metric", "imperial"], state="readonly", width=15)
        units_combo.pack(side=tk.LEFT, padx=(10, 0))
        units_combo.bind('<<ComboboxSelected>>', self._on_units_change)
    
    def _create_audio_tab(self):
        """Create the audio settings tab."""
        audio_frame = ttk.Frame(self.notebook)
        self.notebook.add(audio_frame, text="🔊 Audio")
        
        # Volume settings
        volume_frame = ttk.LabelFrame(audio_frame, text="Volume & Balance", padding=15)
        volume_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Master volume
        master_vol_frame = ttk.Frame(volume_frame)
        master_vol_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(master_vol_frame, text="Master Volume:").pack(side=tk.LEFT)
        
        self.volume_var = tk.IntVar(value=self.current_settings['audio']['volume'])
        self.volume_scale = ttk.Scale(master_vol_frame, from_=0, to=100, 
                                     variable=self.volume_var, orient=tk.HORIZONTAL,
                                     command=self._on_volume_change)
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.volume_label = ttk.Label(master_vol_frame, text=f"{self.current_settings['audio']['volume']}%")
        self.volume_label.pack(side=tk.RIGHT)
        
        # Bass and treble
        eq_frame = ttk.Frame(volume_frame)
        eq_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Bass
        bass_frame = ttk.Frame(eq_frame)
        bass_frame.pack(side=tk.LEFT, expand=True)
        
        ttk.Label(bass_frame, text="Bass:").pack()
        
        self.bass_var = tk.IntVar(value=self.current_settings['audio']['bass'])
        self.bass_scale = ttk.Scale(bass_frame, from_=-20, to=20, 
                                   variable=self.bass_var, orient=tk.VERTICAL,
                                   command=self._on_bass_change)
        self.bass_scale.pack()
        
        self.bass_label = ttk.Label(bass_frame, text=str(self.current_settings['audio']['bass']))
        self.bass_label.pack()
        
        # Treble
        treble_frame = ttk.Frame(eq_frame)
        treble_frame.pack(side=tk.RIGHT, expand=True)
        
        ttk.Label(treble_frame, text="Treble:").pack()
        
        self.treble_var = tk.IntVar(value=self.current_settings['audio']['treble'])
        self.treble_scale = ttk.Scale(treble_frame, from_=-20, to=20, 
                                     variable=self.treble_var, orient=tk.VERTICAL,
                                     command=self._on_treble_change)
        self.treble_scale.pack()
        
        self.treble_label = ttk.Label(treble_frame, text=str(self.current_settings['audio']['treble']))
        self.treble_label.pack()
        
        # Balance and fade
        balance_frame = ttk.Frame(volume_frame)
        balance_frame.pack(fill=tk.X)
        
        # Balance
        bal_frame = ttk.Frame(balance_frame)
        bal_frame.pack(side=tk.LEFT, expand=True)
        
        ttk.Label(bal_frame, text="Balance (L/R):").pack()
        
        self.balance_var = tk.IntVar(value=self.current_settings['audio']['balance'])
        self.balance_scale = ttk.Scale(bal_frame, from_=-20, to=20, 
                                      variable=self.balance_var, orient=tk.HORIZONTAL,
                                      command=self._on_balance_change)
        self.balance_scale.pack()
        
        self.balance_label = ttk.Label(bal_frame, text=str(self.current_settings['audio']['balance']))
        self.balance_label.pack()
        
        # Fade
        fade_frame = ttk.Frame(balance_frame)
        fade_frame.pack(side=tk.RIGHT, expand=True)
        
        ttk.Label(fade_frame, text="Fade (F/B):").pack()
        
        self.fade_var = tk.IntVar(value=self.current_settings['audio']['fade'])
        self.fade_scale = ttk.Scale(fade_frame, from_=-20, to=20, 
                                   variable=self.fade_var, orient=tk.HORIZONTAL,
                                   command=self._on_fade_change)
        self.fade_scale.pack()
        
        self.fade_label = ttk.Label(fade_frame, text=str(self.current_settings['audio']['fade']))
        self.fade_label.pack()
        
        # Audio features
        features_frame = ttk.LabelFrame(audio_frame, text="Audio Features", padding=15)
        features_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.surround_var = tk.BooleanVar(value=self.current_settings['audio']['surround'])
        self.surround_check = ttk.Checkbutton(features_frame, text="Surround Sound", 
                                             variable=self.surround_var, command=self._on_surround_change)
        self.surround_check.pack(anchor=tk.W)
    
    def _create_system_tab(self):
        """Create the system settings tab."""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="💻 System")
        
        # System preferences
        prefs_frame = ttk.LabelFrame(system_frame, text="System Preferences", padding=15)
        prefs_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Auto lock
        self.auto_lock_var = tk.BooleanVar(value=self.current_settings['system']['auto_lock'])
        self.auto_lock_check = ttk.Checkbutton(prefs_frame, text="Auto-lock after inactivity", 
                                              variable=self.auto_lock_var, command=self._on_auto_lock_change)
        self.auto_lock_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Power save
        self.power_save_var = tk.BooleanVar(value=self.current_settings['system']['power_save'])
        self.power_save_check = ttk.Checkbutton(prefs_frame, text="Power saving mode", 
                                               variable=self.power_save_var, command=self._on_power_save_change)
        self.power_save_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Updates
        self.updates_var = tk.BooleanVar(value=self.current_settings['system']['updates'])
        self.updates_check = ttk.Checkbutton(prefs_frame, text="Automatic updates", 
                                            variable=self.updates_var, command=self._on_updates_change)
        self.updates_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Diagnostics
        self.diagnostics_var = tk.BooleanVar(value=self.current_settings['system']['diagnostics'])
        self.diagnostics_check = ttk.Checkbutton(prefs_frame, text="System diagnostics", 
                                                variable=self.diagnostics_var, command=self._on_diagnostics_change)
        self.diagnostics_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Backup
        self.backup_var = tk.BooleanVar(value=self.current_settings['system']['backup'])
        self.backup_check = ttk.Checkbutton(prefs_frame, text="Automatic backup", 
                                           variable=self.backup_var, command=self._on_backup_change)
        self.backup_check.pack(anchor=tk.W)
        
        # System info
        info_frame = ttk.LabelFrame(system_frame, text="System Information", padding=15)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        info_text = f"""
        Software Version: 2.1.0
        Hardware Model: Infotainment Pro
        Serial Number: IVT-2024-001
        Last Update: 2024-01-15
        Available Storage: 15.2 GB
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=('Courier', 10))
        info_label.pack(anchor=tk.W)
    
    def _create_connectivity_tab(self):
        """Create the connectivity settings tab."""
        connectivity_frame = ttk.Frame(self.notebook)
        self.notebook.add(connectivity_frame, text="📡 Connectivity")
        
        # Wireless settings
        wireless_frame = ttk.LabelFrame(connectivity_frame, text="Wireless Connections", padding=15)
        wireless_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # WiFi
        wifi_frame = ttk.Frame(wireless_frame)
        wifi_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.wifi_var = tk.BooleanVar(value=self.current_settings['connectivity']['wifi'])
        self.wifi_check = ttk.Checkbutton(wifi_frame, text="WiFi", 
                                         variable=self.wifi_var, command=self._on_wifi_change)
        self.wifi_check.pack(side=tk.LEFT)
        
        if self.current_settings['connectivity']['wifi']:
            wifi_status = ttk.Label(wifi_frame, text="Connected to HomeNetwork", foreground='green')
            wifi_status.pack(side=tk.RIGHT)
        
        # Bluetooth
        bluetooth_frame = ttk.Frame(wireless_frame)
        bluetooth_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.bluetooth_var = tk.BooleanVar(value=self.current_settings['connectivity']['bluetooth'])
        self.bluetooth_check = ttk.Checkbutton(bluetooth_frame, text="Bluetooth", 
                                              variable=self.bluetooth_var, command=self._on_bluetooth_change)
        self.bluetooth_check.pack(side=tk.LEFT)
        
        if self.current_settings['connectivity']['bluetooth']:
            bt_status = ttk.Label(bluetooth_frame, text="Paired with iPhone", foreground='green')
            bt_status.pack(side=tk.RIGHT)
        
        # Cellular
        cellular_frame = ttk.Frame(wireless_frame)
        cellular_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cellular_var = tk.BooleanVar(value=self.current_settings['connectivity']['cellular'])
        self.cellular_check = ttk.Checkbutton(cellular_frame, text="Cellular Data", 
                                             variable=self.cellular_var, command=self._on_cellular_change)
        self.cellular_check.pack(side=tk.LEFT)
        
        # Hotspot
        hotspot_frame = ttk.Frame(wireless_frame)
        hotspot_frame.pack(fill=tk.X)
        
        self.hotspot_var = tk.BooleanVar(value=self.current_settings['connectivity']['hotspot'])
        self.hotspot_check = ttk.Checkbutton(hotspot_frame, text="Mobile Hotspot", 
                                            variable=self.hotspot_var, command=self._on_hotspot_change)
        self.hotspot_check.pack(side=tk.LEFT)
        
        # Network settings
        network_frame = ttk.LabelFrame(connectivity_frame, text="Network Settings", padding=15)
        network_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Network buttons
        network_buttons_frame = ttk.Frame(network_frame)
        network_buttons_frame.pack(fill=tk.X)
        
        self.scan_btn = ttk.Button(network_buttons_frame, text="🔍 Scan Networks", 
                                  command=self._scan_networks, width=15)
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.forget_btn = ttk.Button(network_buttons_frame, text="🗑️ Forget Network", 
                                    command=self._forget_network, width=15)
        self.forget_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_btn = ttk.Button(network_buttons_frame, text="🔄 Reset Settings", 
                                   command=self._reset_network_settings, width=15)
        self.reset_btn.pack(side=tk.LEFT)
    
    def _create_control_buttons(self, parent):
        """Create the control buttons section."""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Apply and Reset buttons
        self.apply_btn = ttk.Button(control_frame, text="✅ Apply Changes", 
                                   command=self._apply_changes, width=15)
        self.apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_btn = ttk.Button(control_frame, text="🔄 Reset to Default", 
                                   command=self._reset_to_default, width=15)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_btn = ttk.Button(control_frame, text="📤 Export Settings", 
                                    command=self._export_settings, width=15)
        self.export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.import_btn = ttk.Button(control_frame, text="📥 Import Settings", 
                                    command=self._import_settings, width=15)
        self.import_btn.pack(side=tk.LEFT)
    
    def _create_performance_section(self, parent):
        """Create the performance metrics section."""
        perf_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=15)
        perf_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Performance indicators
        perf_indicators_frame = ttk.Frame(perf_frame)
        perf_indicators_frame.pack(fill=tk.X)
        
        # Response time
        self.response_time_label = ttk.Label(perf_indicators_frame, text="Response Time: 0ms")
        self.response_time_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Operation count
        self.operation_count_label = ttk.Label(perf_indicators_frame, text="Operations: 0")
        self.operation_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Settings changed
        self.settings_changed_label = ttk.Label(perf_indicators_frame, text="Settings Changed: 0")
        self.settings_changed_label.pack(side=tk.LEFT)
    
    # Event handlers for all settings changes
    def _on_brightness_change(self, value):
        """Handle brightness change."""
        self.current_settings['display']['brightness'] = int(float(value))
        self.brightness_label.config(text=f"{self.current_settings['display']['brightness']}%")
        self._log_setting_change('brightness', value)
    
    def _on_contrast_change(self, value):
        """Handle contrast change."""
        self.current_settings['display']['contrast'] = int(float(value))
        self.contrast_label.config(text=f"{self.current_settings['display']['contrast']}%")
        self._log_setting_change('contrast', value)
    
    def _on_theme_change(self, event):
        """Handle theme change."""
        self.current_settings['display']['theme'] = self.theme_var.get()
        self._log_setting_change('theme', self.theme_var.get())
    
    def _on_language_change(self, event):
        """Handle language change."""
        self.current_settings['display']['language'] = self.language_var.get()
        self._log_setting_change('language', self.language_var.get())
    
    def _on_units_change(self, event):
        """Handle units change."""
        self.current_settings['display']['units'] = self.units_var.get()
        self._log_setting_change('units', self.units_var.get())
    
    def _on_volume_change(self, value):
        """Handle volume change."""
        self.current_settings['audio']['volume'] = int(float(value))
        self.volume_label.config(text=f"{self.current_settings['audio']['volume']}%")
        self._log_setting_change('volume', value)
    
    def _on_bass_change(self, value):
        """Handle bass change."""
        self.current_settings['audio']['bass'] = int(float(value))
        self.bass_label.config(text=str(self.current_settings['audio']['bass']))
        self._log_setting_change('bass', value)
    
    def _on_treble_change(self, value):
        """Handle treble change."""
        self.current_settings['audio']['treble'] = int(float(value))
        self.treble_label.config(text=str(self.current_settings['audio']['treble']))
        self._log_setting_change('treble', value)
    
    def _on_balance_change(self, value):
        """Handle balance change."""
        self.current_settings['audio']['balance'] = int(float(value))
        self.balance_label.config(text=str(self.current_settings['audio']['balance']))
        self._log_setting_change('balance', value)
    
    def _on_fade_change(self, value):
        """Handle fade change."""
        self.current_settings['audio']['fade'] = int(float(value))
        self.fade_label.config(text=str(self.current_settings['audio']['fade']))
        self._log_setting_change('fade', value)
    
    def _on_surround_change(self):
        """Handle surround sound change."""
        self.current_settings['audio']['surround'] = self.surround_var.get()
        self._log_setting_change('surround', self.surround_var.get())
    
    def _on_auto_lock_change(self):
        """Handle auto-lock change."""
        self.current_settings['system']['auto_lock'] = self.auto_lock_var.get()
        self._log_setting_change('auto_lock', self.auto_lock_var.get())
    
    def _on_power_save_change(self):
        """Handle power save change."""
        self.current_settings['system']['power_save'] = self.power_save_var.get()
        self._log_setting_change('power_save', self.power_save_var.get())
    
    def _on_updates_change(self):
        """Handle updates change."""
        self.current_settings['system']['updates'] = self.updates_var.get()
        self._log_setting_change('updates', self.updates_var.get())
    
    def _on_diagnostics_change(self):
        """Handle diagnostics change."""
        self.current_settings['system']['diagnostics'] = self.diagnostics_var.get()
        self._log_setting_change('diagnostics', self.diagnostics_var.get())
    
    def _on_backup_change(self):
        """Handle backup change."""
        self.current_settings['system']['backup'] = self.backup_var.get()
        self._log_setting_change('backup', self.backup_var.get())
    
    def _on_wifi_change(self):
        """Handle WiFi change."""
        self.current_settings['connectivity']['wifi'] = self.wifi_var.get()
        self._log_setting_change('wifi', self.wifi_var.get())
    
    def _on_bluetooth_change(self):
        """Handle Bluetooth change."""
        self.current_settings['connectivity']['bluetooth'] = self.bluetooth_var.get()
        self._log_setting_change('bluetooth', self.bluetooth_var.get())
    
    def _on_cellular_change(self):
        """Handle cellular change."""
        self.current_settings['connectivity']['cellular'] = self.cellular_var.get()
        self._log_setting_change('cellular', self.cellular_var.get())
    
    def _on_hotspot_change(self):
        """Handle hotspot change."""
        self.current_settings['connectivity']['hotspot'] = self.hotspot_var.get()
        self._log_setting_change('hotspot', self.hotspot_var.get())
    
    def _log_setting_change(self, setting_name, value):
        """Log a setting change and track performance."""
        try:
            start_time = time.time()
            
            # Simulate setting change delay
            time.sleep(0.05)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Setting changed: {setting_name} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error logging setting change: {e}")
    
    def _apply_changes(self):
        """Apply all pending changes."""
        try:
            start_time = time.time()
            
            # Simulate applying changes
            time.sleep(0.5)
            
            # Save settings
            self._save_settings()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            messagebox.showinfo("Success", "Settings applied successfully!")
            self.logger.info("Settings applied successfully")
            
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
    
    def _reset_to_default(self):
        """Reset all settings to default values."""
        try:
            start_time = time.time()
            
            # Confirm reset
            if not messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to default?"):
                return
            
            # Simulate reset operation
            time.sleep(0.3)
            
            # Reset to original settings
            self.current_settings = self.original_settings.copy()
            self._refresh_ui_from_settings()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            messagebox.showinfo("Success", "Settings reset to default!")
            self.logger.info("Settings reset to default")
            
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def _export_settings(self):
        """Export current settings to file."""
        try:
            start_time = time.time()
            
            # Simulate export operation
            time.sleep(0.2)
            
            # Save to file
            with open('data/settings_export.json', 'w') as f:
                json.dump(self.current_settings, f, indent=2)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            messagebox.showinfo("Success", "Settings exported to data/settings_export.json")
            self.logger.info("Settings exported successfully")
            
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def _import_settings(self):
        """Import settings from file."""
        try:
            start_time = time.time()
            
            # Simulate import operation
            time.sleep(0.2)
            
            # Load from file
            with open('data/settings_export.json', 'r') as f:
                imported_settings = json.load(f)
            
            # Apply imported settings
            self.current_settings = imported_settings
            self._refresh_ui_from_settings()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            messagebox.showinfo("Success", "Settings imported successfully!")
            self.logger.info("Settings imported successfully")
            
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def _scan_networks(self):
        """Scan for available networks."""
        try:
            start_time = time.time()
            
            # Simulate network scan
            time.sleep(1.0)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            messagebox.showinfo("Network Scan", "Found 5 available networks")
            self.logger.info("Network scan completed")
            
        except Exception as e:
            self.logger.error(f"Error scanning networks: {e}")
    
    def _forget_network(self):
        """Forget current network."""
        try:
            start_time = time.time()
            
            # Simulate forget operation
            time.sleep(0.3)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            messagebox.showinfo("Success", "Network forgotten successfully")
            self.logger.info("Network forgotten")
            
        except Exception as e:
            self.logger.error(f"Error forgetting network: {e}")
    
    def _reset_network_settings(self):
        """Reset network settings."""
        try:
            start_time = time.time()
            
            # Simulate reset operation
            time.sleep(0.5)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            messagebox.showinfo("Success", "Network settings reset")
            self.logger.info("Network settings reset")
            
        except Exception as e:
            self.logger.error(f"Error resetting network settings: {e}")
    
    def _save_settings(self):
        """Save current settings."""
        try:
            # Save to configuration
            self.config.config.update(self.current_settings)
            self.logger.info("Settings saved to configuration")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
    
    def _refresh_ui_from_settings(self):
        """Refresh UI elements from current settings."""
        try:
            # Update all UI elements to reflect current settings
            self.brightness_var.set(self.current_settings['display']['brightness'])
            self.contrast_var.set(self.current_settings['display']['contrast'])
            self.theme_var.set(self.current_settings['display']['theme'])
            self.language_var.set(self.current_settings['display']['language'])
            self.units_var.set(self.current_settings['display']['units'])
            
            self.volume_var.set(self.current_settings['audio']['volume'])
            self.bass_var.set(self.current_settings['audio']['bass'])
            self.treble_var.set(self.current_settings['audio']['treble'])
            self.balance_var.set(self.current_settings['audio']['balance'])
            self.fade_var.set(self.current_settings['audio']['fade'])
            self.surround_var.set(self.current_settings['audio']['surround'])
            
            self.auto_lock_var.set(self.current_settings['system']['auto_lock'])
            self.power_save_var.set(self.current_settings['system']['power_save'])
            self.updates_var.set(self.current_settings['system']['updates'])
            self.diagnostics_var.set(self.current_settings['system']['diagnostics'])
            self.backup_var.set(self.current_settings['system']['backup'])
            
            self.wifi_var.set(self.current_settings['connectivity']['wifi'])
            self.bluetooth_var.set(self.current_settings['connectivity']['bluetooth'])
            self.cellular_var.set(self.current_settings['connectivity']['cellular'])
            self.hotspot_var.set(self.current_settings['connectivity']['hotspot'])
            
            # Update labels
            self.brightness_label.config(text=f"{self.current_settings['display']['brightness']}%")
            self.contrast_label.config(text=f"{self.current_settings['display']['contrast']}%")
            self.volume_label.config(text=f"{self.current_settings['display']['volume']}%")
            self.bass_label.config(text=str(self.current_settings['audio']['bass']))
            self.treble_label.config(text=str(self.current_settings['audio']['treble']))
            self.balance_label.config(text=str(self.current_settings['audio']['balance']))
            self.fade_label.config(text=str(self.current_settings['audio']['fade']))
            
        except Exception as e:
            self.logger.error(f"Error refreshing UI from settings: {e}")
    
    def update_performance_display(self):
        """Update performance metrics display."""
        try:
            # Update response time
            if self.operation_times:
                latest_response = self.operation_times[-1]
                self.response_time_label.config(text=f"Response Time: {latest_response:.1f}ms")
            
            # Update operation count
            self.operation_count_label.config(text=f"Operations: {len(self.operation_times)}")
            
            # Update settings changed count
            settings_changed = len(self.operation_times)
            self.settings_changed_label.config(text=f"Settings Changed: {settings_changed}")
            
        except Exception as e:
            self.logger.error(f"Error updating performance display: {e}")
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance data for this widget."""
        return {
            'operation_times': self.operation_times,
            'current_settings': self.current_settings,
            'settings_changed': len(self.operation_times)
        } 