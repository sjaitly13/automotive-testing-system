"""
Main infotainment interface for the testing system.
Provides a realistic automotive infotainment system interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..monitoring.performance_monitor import get_performance_monitor
from .components.media_player import MediaPlayerWidget
from .components.navigation import NavigationWidget
from .components.settings import SettingsWidget
from .components.phone import PhoneWidget
from .components.climate import ClimateWidget

class InfotainmentInterface:
    """Main infotainment system interface."""
    
    def __init__(self):
        self.logger = get_logger("infotainment_interface")
        self.config = get_config()
        self.performance_monitor = get_performance_monitor()
        
        # Interface configuration
        self.theme = self.config.get('interface.theme', 'dark')
        self.window_size = self.config.get('interface.window_size', '1024x768')
        self.refresh_rate = self.config.get('interface.refresh_rate_hz', 30)
        
        # UI state
        self.current_app = "home"
        self.apps = {}
        self.is_running = False
        
        # Performance tracking
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.response_times = []
        
        # Initialize main window
        self.root = tk.Tk()
        self._setup_main_window()
        self._create_widgets()
        self._setup_performance_monitoring()
        
        self.logger.info("Infotainment Interface initialized")
    
    def _setup_main_window(self):
        """Setup the main application window."""
        self.root.title("Automotive Infotainment System - Performance Testing")
        self.root.geometry(self.window_size)
        self.root.resizable(True, True)
        
        # Configure theme
        if self.theme == "dark":
            self.root.configure(bg='#1e1e1e')
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('TFrame', background='#1e1e1e')
            style.configure('TLabel', background='#1e1e1e', foreground='white')
            style.configure('TButton', background='#404040', foreground='white')
        
        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Key>', self.on_key_press)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create and arrange all UI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with system status
        self._create_header()
        
        # Main content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Navigation bar
        self._create_navigation_bar()
        
        # App content area
        self.app_frame = ttk.Frame(self.content_frame)
        self.app_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Initialize app widgets
        self._initialize_apps()
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create the header section with system status."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="🚗 Automotive Infotainment System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # System status indicators
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        
        # Performance indicator
        self.performance_label = ttk.Label(status_frame, text="Performance: Excellent", 
                                         foreground='green')
        self.performance_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Time display
        self.time_label = ttk.Label(status_frame, text="", font=('Arial', 10))
        self.time_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def _create_navigation_bar(self):
        """Create the main navigation bar."""
        nav_frame = ttk.Frame(self.content_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Home", "home"),
            ("🎵 Media", "media"),
            ("🧭 Navigation", "navigation"),
            ("📱 Phone", "phone"),
            ("❄️ Climate", "climate"),
            ("⚙️ Settings", "settings")
        ]
        
        for text, app_name in nav_buttons:
            btn = ttk.Button(nav_frame, text=text, 
                           command=lambda a=app_name: self.switch_app(a))
            btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Store button reference for styling
            if not hasattr(self, 'nav_buttons'):
                self.nav_buttons = {}
            self.nav_buttons[app_name] = btn
    
    def _create_status_bar(self):
        """Create the status bar with performance metrics."""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Performance metrics
        metrics_frame = ttk.Frame(status_frame)
        metrics_frame.pack(fill=tk.X)
        
        # CPU usage
        self.cpu_label = ttk.Label(metrics_frame, text="CPU: 0%")
        self.cpu_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Memory usage
        self.memory_label = ttk.Label(metrics_frame, text="Memory: 0%")
        self.memory_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Response time
        self.response_label = ttk.Label(metrics_frame, text="Response: 0ms")
        self.response_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Frame rate
        self.fps_label = ttk.Label(metrics_frame, text="FPS: 0")
        self.fps_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # System health
        self.health_label = ttk.Label(metrics_frame, text="Health: 100%", foreground='green')
        self.health_label.pack(side=tk.RIGHT)
    
    def _initialize_apps(self):
        """Initialize all application widgets."""
        # Home app
        self.apps["home"] = self._create_home_widget()
        
        # Media player
        self.apps["media"] = MediaPlayerWidget(self.app_frame, self)
        
        # Navigation
        self.apps["navigation"] = NavigationWidget(self.app_frame, self)
        
        # Phone
        self.apps["phone"] = PhoneWidget(self.app_frame, self)
        
        # Climate
        self.apps["climate"] = ClimateWidget(self.app_frame, self)
        
        # Settings
        self.apps["settings"] = SettingsWidget(self.app_frame, self)
        
        # Show home app by default
        self.switch_app("home")
    
    def _create_home_widget(self):
        """Create the home screen widget."""
        home_frame = ttk.Frame(self.app_frame)
        
        # Welcome message
        welcome_label = ttk.Label(home_frame, text="Welcome to Your Infotainment System", 
                                font=('Arial', 18, 'bold'))
        welcome_label.pack(pady=(50, 20))
        
        # Quick access buttons
        quick_access_frame = ttk.Frame(home_frame)
        quick_access_frame.pack(pady=20)
        
        quick_buttons = [
            ("🎵 Play Music", lambda: self.switch_app("media")),
            ("🧭 Start Navigation", lambda: self.switch_app("navigation")),
            ("📱 Make Call", lambda: self.switch_app("phone")),
            ("⚙️ System Settings", lambda: self.switch_app("settings"))
        ]
        
        for text, command in quick_buttons:
            btn = ttk.Button(quick_access_frame, text=text, command=command, 
                           width=20, style='Accent.TButton')
            btn.pack(pady=5)
        
        # System status summary
        status_summary_frame = ttk.LabelFrame(home_frame, text="System Status", padding=20)
        status_summary_frame.pack(pady=20, fill=tk.X)
        
        self.status_summary_label = ttk.Label(status_summary_frame, 
                                            text="System Status: Initializing...")
        self.status_summary_label.pack()
        
        return home_frame
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring for the interface."""
        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        
        # Add alert callback
        self.performance_monitor.add_alert_callback(self._on_performance_alert)
        
        # Start UI update loop
        self.is_running = True
        self._update_ui()
    
    def _update_ui(self):
        """Update UI elements with current performance data."""
        if not self.is_running:
            return
        
        try:
            # Update time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=current_time)
            
            # Update performance metrics
            metrics = self.performance_monitor.get_current_metrics()
            if metrics:
                # CPU usage
                cpu_text = f"CPU: {metrics.get('cpu_percent', 0):.1f}%"
                self.cpu_label.config(text=cpu_text)
                
                # Memory usage
                memory_text = f"Memory: {metrics.get('memory_percent', 0):.1f}%"
                self.memory_label.config(text=memory_text)
                
                # Response time
                response_text = f"Response: {metrics.get('response_time_ms', 0):.1f}ms"
                self.response_label.config(text=response_text)
                
                # Frame rate
                fps_text = f"FPS: {metrics.get('frame_rate', 0):.1f}"
                self.fps_label.config(text=fps_text)
                
                # System health
                health_score = self.performance_monitor.get_system_health_score()
                health_text = f"Health: {health_score:.0f}%"
                health_color = 'green' if health_score >= 80 else 'orange' if health_score >= 60 else 'red'
                self.health_label.config(text=health_text, foreground=health_color)
                
                # Performance indicator
                if health_score >= 80:
                    perf_text = "Performance: Excellent"
                    perf_color = 'green'
                elif health_score >= 60:
                    perf_text = "Performance: Good"
                    perf_color = 'orange'
                else:
                    perf_text = "Performance: Poor"
                    perf_color = 'red'
                
                self.performance_label.config(text=perf_text, foreground=perf_color)
                
                # Update status summary on home screen
                if self.current_app == "home" and hasattr(self, 'status_summary_label'):
                    status_text = f"System Status: {perf_text} | Health: {health_score:.0f}%"
                    self.status_summary_label.config(text=status_text)
            
            # Calculate frame rate
            current_time = time.time()
            self.frame_count += 1
            
            if current_time - self.last_frame_time >= 1.0:
                fps = self.frame_count / (current_time - self.last_frame_time)
                self.performance_monitor.update_frame_rate(fps)
                self.frame_count = 0
                self.last_frame_time = current_time
            
            # Schedule next update
            self.root.after(int(1000 / self.refresh_rate), self._update_ui)
            
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
            # Continue updating even if there's an error
            self.root.after(1000, self._update_ui)
    
    def switch_app(self, app_name: str):
        """Switch to a different application."""
        try:
            start_time = time.time()
            
            # Hide current app
            if self.current_app in self.apps:
                self.apps[self.current_app].pack_forget()
            
            # Show new app
            if app_name in self.apps:
                self.apps[app_name].pack(fill=tk.BOTH, expand=True)
                self.current_app = app_name
                
                # Update navigation button styling
                self._update_navigation_styling(app_name)
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                self.performance_monitor.update_response_time(response_time)
                self.response_times.append(response_time)
                
                self.logger.info(f"Switched to {app_name} app in {response_time:.2f}ms")
            else:
                self.logger.error(f"Unknown app: {app_name}")
                
        except Exception as e:
            self.logger.error(f"Error switching to app {app_name}: {e}")
    
    def _update_navigation_styling(self, active_app: str):
        """Update navigation button styling to show active app."""
        for app_name, button in self.nav_buttons.items():
            if app_name == active_app:
                button.configure(style='Accent.TButton')
            else:
                button.configure(style='TButton')
    
    def _on_performance_alert(self, alert_type: str, data: Dict[str, Any]):
        """Handle performance alerts."""
        alert_message = f"Performance Alert: {alert_type}"
        if data:
            alert_message += f" - {data}"
        
        self.logger.warning(alert_message)
        
        # Show alert to user
        messagebox.showwarning("Performance Alert", alert_message)
    
    def on_key_press(self, event):
        """Handle keyboard input."""
        # Log key presses for testing
        self.logger.debug(f"Key pressed: {event.keysym}")
        
        # Handle special keys
        if event.keysym == 'Escape':
            self.switch_app("home")
        elif event.keysym == 'F1':
            self.switch_app("media")
        elif event.keysym == 'F2':
            self.switch_app("navigation")
        elif event.keysym == 'F3':
            self.switch_app("phone")
        elif event.keysym == 'F4':
            self.switch_app("climate")
        elif event.keysym == 'F5':
            self.switch_app("settings")
    
    def on_closing(self):
        """Handle application closing."""
        try:
            self.logger.info("Application closing")
            self.is_running = False
            
            # Stop performance monitoring
            self.performance_monitor.stop_monitoring()
            
            # Destroy window
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def run(self):
        """Start the infotainment interface."""
        try:
            self.logger.info("Starting infotainment interface")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error running interface: {e}")
        finally:
            self.on_closing()
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get current performance data for testing."""
        return {
            'current_app': self.current_app,
            'response_times': self.response_times,
            'frame_count': self.frame_count,
            'is_running': self.is_running
        } 