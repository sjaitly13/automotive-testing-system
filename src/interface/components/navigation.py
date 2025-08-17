"""
Navigation widget for the infotainment interface.
Simulates GPS navigation functionality with performance tracking.
"""

import tkinter as tk
from tkinter import ttk
import time
import random
from typing import Dict, List, Any

from ...utils.logger import get_logger
from ...monitoring.performance_monitor import get_performance_monitor

class NavigationWidget(ttk.Frame):
    """Navigation application widget."""
    
    def __init__(self, parent, main_interface):
        super().__init__(parent)
        self.main_interface = main_interface
        self.logger = get_logger("navigation")
        self.performance_monitor = get_performance_monitor()
        
        # Navigation state
        self.is_navigating = False
        self.current_destination = None
        self.estimated_time = 0
        self.distance = 0
        self.route_points = []
        self.current_location = {"lat": 37.7749, "lng": -122.4194}  # San Francisco
        
        # Performance tracking
        self.operation_times = []
        self.map_rendering_times = []
        
        # Sample destinations
        self.destinations = self._create_sample_destinations()
        
        self._create_widgets()
        self.logger.info("Navigation Widget initialized")
    
    def _create_sample_destinations(self) -> List[Dict[str, Any]]:
        """Create sample destinations for testing."""
        return [
            {"name": "Golden Gate Bridge", "lat": 37.8199, "lng": -122.4783, "category": "Landmark"},
            {"name": "Fisherman's Wharf", "lat": 37.8080, "lng": -122.4177, "category": "Tourist"},
            {"name": "Alcatraz Island", "lat": 37.8270, "lng": -122.4230, "category": "Tourist"},
            {"name": "Chinatown", "lat": 37.7941, "lng": -122.4079, "category": "Cultural"},
            {"name": "Golden Gate Park", "lat": 37.7694, "lng": -122.4862, "category": "Park"},
            {"name": "Pier 39", "lat": 37.8087, "lng": -122.4098, "category": "Shopping"},
            {"name": "Coit Tower", "lat": 37.8024, "lng": -122.4058, "category": "Landmark"},
            {"name": "Lombard Street", "lat": 37.8021, "lng": -122.4189, "category": "Tourist"}
        ]
    
    def _create_widgets(self):
        """Create all navigation UI elements."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_container, text="🧭 Navigation", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Search section
        self._create_search_section(main_container)
        
        # Map section
        self._create_map_section(main_container)
        
        # Route info section
        self._create_route_section(main_container)
        
        # Controls section
        self._create_controls_section(main_container)
        
        # Performance metrics
        self._create_performance_section(main_container)
    
    def _create_search_section(self, parent):
        """Create the destination search section."""
        search_frame = ttk.LabelFrame(parent, text="Destination Search", padding=15)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Search input
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_input_frame, text="Search:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_input_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(10, 10))
        
        self.search_button = ttk.Button(search_input_frame, text="🔍 Search", 
                                       command=self._search_destination)
        self.search_button.pack(side=tk.LEFT)
        
        # Quick destinations
        quick_dest_frame = ttk.Frame(search_frame)
        quick_dest_frame.pack(fill=tk.X)
        
        ttk.Label(quick_dest_frame, text="Quick Destinations:").pack(anchor=tk.W)
        
        # Create quick destination buttons
        quick_buttons_frame = ttk.Frame(quick_dest_frame)
        quick_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        for i, dest in enumerate(self.destinations[:4]):  # Show first 4 destinations
            btn = ttk.Button(quick_buttons_frame, text=dest['name'], 
                           command=lambda d=dest: self._select_destination(d),
                           width=15)
            btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def _create_map_section(self, parent):
        """Create the map display section."""
        map_frame = ttk.LabelFrame(parent, text="Map View", padding=15)
        map_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Map canvas (simulated)
        self.map_canvas = tk.Canvas(map_frame, bg='#87CEEB', height=300)
        self.map_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Map controls
        map_controls_frame = ttk.Frame(map_frame)
        map_controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.zoom_in_btn = ttk.Button(map_controls_frame, text="🔍+", 
                                     command=self._zoom_in, width=8)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.zoom_out_btn = ttk.Button(map_controls_frame, text="🔍-", 
                                      command=self._zoom_out, width=8)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.center_btn = ttk.Button(map_controls_frame, text="🎯 Center", 
                                    command=self._center_map, width=10)
        self.center_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.satellite_btn = ttk.Button(map_controls_frame, text="🛰️ Satellite", 
                                       command=self._toggle_satellite, width=12)
        self.satellite_btn.pack(side=tk.RIGHT)
        
        # Draw initial map
        self._draw_map()
    
    def _create_route_section(self, parent):
        """Create the route information section."""
        route_frame = ttk.LabelFrame(parent, text="Route Information", padding=15)
        route_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Route details
        route_details_frame = ttk.Frame(route_frame)
        route_details_frame.pack(fill=tk.X)
        
        # Destination
        dest_frame = ttk.Frame(route_details_frame)
        dest_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dest_frame, text="Destination:").pack(side=tk.LEFT)
        self.dest_label = ttk.Label(dest_frame, text="None selected", font=('Arial', 10, 'bold'))
        self.dest_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Distance and time
        info_frame = ttk.Frame(route_details_frame)
        info_frame.pack(fill=tk.X)
        
        # Distance
        distance_frame = ttk.Frame(info_frame)
        distance_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        ttk.Label(distance_frame, text="Distance:").pack(side=tk.LEFT)
        self.distance_label = ttk.Label(distance_frame, text="0.0 km")
        self.distance_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Time
        time_frame = ttk.Frame(info_frame)
        time_frame.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="ETA:").pack(side=tk.LEFT)
        self.time_label = ttk.Label(time_frame, text="0 min")
        self.time_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Route options
        route_options_frame = ttk.Frame(route_frame)
        route_options_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(route_options_frame, text="Route Options:").pack(anchor=tk.W)
        
        options_buttons_frame = ttk.Frame(route_options_frame)
        options_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.fastest_btn = ttk.Button(options_buttons_frame, text="🚗 Fastest", 
                                     command=lambda: self._set_route_type("fastest"))
        self.fastest_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.shortest_btn = ttk.Button(options_buttons_frame, text="📏 Shortest", 
                                      command=lambda: self._set_route_type("shortest"))
        self.shortest_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.eco_btn = ttk.Button(options_buttons_frame, text="🌱 Eco", 
                                 command=lambda: self._set_route_type("eco"))
        self.eco_btn.pack(side=tk.LEFT)
    
    def _create_controls_section(self, parent):
        """Create the navigation controls section."""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Main control buttons
        self.start_nav_btn = ttk.Button(controls_frame, text="🚀 Start Navigation", 
                                       command=self._start_navigation, width=20)
        self.start_nav_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_nav_btn = ttk.Button(controls_frame, text="⏹️ Stop Navigation", 
                                      command=self._stop_navigation, width=20, state='disabled')
        self.stop_nav_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.recalculate_btn = ttk.Button(controls_frame, text="🔄 Recalculate", 
                                         command=self._recalculate_route, width=15)
        self.recalculate_btn.pack(side=tk.LEFT)
        
        # Voice guidance toggle
        voice_frame = ttk.Frame(controls_frame)
        voice_frame.pack(side=tk.RIGHT)
        
        self.voice_var = tk.BooleanVar(value=True)
        self.voice_check = ttk.Checkbutton(voice_frame, text="🗣️ Voice Guidance", 
                                          variable=self.voice_var)
        self.voice_check.pack()
    
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
        
        # Map rendering time
        self.render_time_label = ttk.Label(perf_indicators_frame, text="Map Render: 0ms")
        self.render_time_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Operation count
        self.operation_count_label = ttk.Label(perf_indicators_frame, text="Operations: 0")
        self.operation_count_label.pack(side=tk.LEFT)
    
    def _search_destination(self):
        """Search for a destination."""
        try:
            start_time = time.time()
            
            search_term = self.search_var.get().lower()
            if not search_term:
                return
            
            # Simulate search delay
            time.sleep(0.1)
            
            # Filter destinations
            results = [d for d in self.destinations if search_term in d['name'].lower()]
            
            if results:
                # Select first result
                self._select_destination(results[0])
                self.logger.info(f"Search completed for '{search_term}' in {((time.time() - start_time) * 1000):.2f}ms")
            else:
                self.logger.info(f"No results found for '{search_term}'")
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
        except Exception as e:
            self.logger.error(f"Error searching destination: {e}")
    
    def _select_destination(self, destination):
        """Select a destination and calculate route."""
        try:
            start_time = time.time()
            
            self.current_destination = destination
            self.dest_label.config(text=destination['name'])
            
            # Calculate route (simulated)
            self._calculate_route()
            
            # Update map
            self._draw_route()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Destination selected: {destination['name']}")
            
        except Exception as e:
            self.logger.error(f"Error selecting destination: {e}")
    
    def _calculate_route(self):
        """Calculate route to destination (simulated)."""
        if not self.current_destination:
            return
        
        # Simulate route calculation
        time.sleep(0.05)
        
        # Generate random route data
        self.distance = random.uniform(2.0, 25.0)
        self.estimated_time = int(self.distance * 2.5)  # Rough estimate
        
        # Update labels
        self.distance_label.config(text=f"{self.distance:.1f} km")
        self.time_label.config(text=f"{self.estimated_time} min")
        
        # Generate route points (simplified)
        self.route_points = [
            self.current_location,
            {"lat": (self.current_location["lat"] + self.current_destination["lat"]) / 2,
             "lng": (self.current_location["lng"] + self.current_destination["lng"]) / 2},
            self.current_destination
        ]
    
    def _draw_map(self):
        """Draw the base map."""
        try:
            start_time = time.time()
            
            # Clear canvas
            self.map_canvas.delete("all")
            
            # Draw grid lines (simulated map)
            for i in range(0, 300, 30):
                self.map_canvas.create_line(0, i, 400, i, fill='#4682B4', width=1)
                self.map_canvas.create_line(i, 0, i, 300, fill='#4682B4', width=1)
            
            # Draw current location
            self.map_canvas.create_oval(190, 140, 210, 160, fill='blue', tags='current_location')
            self.map_canvas.create_text(200, 180, text="You are here", font=('Arial', 8))
            
            # Calculate map rendering time
            render_time = (time.time() - start_time) * 1000
            self.map_rendering_times.append(render_time)
            
        except Exception as e:
            self.logger.error(f"Error drawing map: {e}")
    
    def _draw_route(self):
        """Draw the calculated route on the map."""
        if not self.route_points:
            return
        
        try:
            # Clear existing route
            self.map_canvas.delete("route")
            
            # Draw route line
            points = []
            for point in self.route_points:
                # Convert lat/lng to canvas coordinates (simplified)
                x = 200 + (point["lng"] - self.current_location["lng"]) * 1000
                y = 150 + (point["lat"] - self.current_location["lat"]) * 1000
                points.extend([x, y])
            
            if len(points) >= 4:
                self.map_canvas.create_line(points, fill='red', width=3, tags='route')
            
            # Draw destination marker
            if self.current_destination:
                dest_x = 200 + (self.current_destination["lng"] - self.current_location["lng"]) * 1000
                dest_y = 150 + (self.current_destination["lat"] - self.current_location["lat"]) * 1000
                
                self.map_canvas.create_oval(dest_x-10, dest_y-10, dest_x+10, dest_y+10, 
                                          fill='red', tags='route')
                self.map_canvas.create_text(dest_x, dest_y-20, 
                                          text=self.current_destination["name"], 
                                          font=('Arial', 8), tags='route')
            
        except Exception as e:
            self.logger.error(f"Error drawing route: {e}")
    
    def _start_navigation(self):
        """Start turn-by-turn navigation."""
        if not self.current_destination:
            return
        
        try:
            start_time = time.time()
            
            self.is_navigating = True
            self.start_nav_btn.config(state='disabled')
            self.stop_nav_btn.config(state='normal')
            
            # Start navigation simulation
            self._simulate_navigation()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info("Navigation started")
            
        except Exception as e:
            self.logger.error(f"Error starting navigation: {e}")
    
    def _stop_navigation(self):
        """Stop navigation."""
        try:
            self.is_navigating = False
            self.start_nav_btn.config(state='normal')
            self.stop_nav_btn.config(state='disabled')
            
            self.logger.info("Navigation stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping navigation: {e}")
    
    def _simulate_navigation(self):
        """Simulate turn-by-turn navigation."""
        if not self.is_navigating:
            return
        
        # Simulate navigation updates
        self.logger.info("Navigation update: Continue straight for 2.5 km")
        
        # Schedule next update
        self.after(5000, self._simulate_navigation)
    
    def _recalculate_route(self):
        """Recalculate the current route."""
        if not self.current_destination:
            return
        
        try:
            start_time = time.time()
            
            self._calculate_route()
            self._draw_route()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info("Route recalculated")
            
        except Exception as e:
            self.logger.error(f"Error recalculating route: {e}")
    
    def _set_route_type(self, route_type):
        """Set the route calculation type."""
        try:
            start_time = time.time()
            
            # Simulate route recalculation
            time.sleep(0.1)
            self._calculate_route()
            self._draw_route()
            
            self.logger.info(f"Route type changed to: {route_type}")
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
        except Exception as e:
            self.logger.error(f"Error setting route type: {e}")
    
    def _zoom_in(self):
        """Zoom in on the map."""
        self._map_operation("zoom_in")
    
    def _zoom_out(self):
        """Zoom out on the map."""
        self._map_operation("zoom_out")
    
    def _center_map(self):
        """Center the map on current location."""
        self._map_operation("center")
    
    def _toggle_satellite(self):
        """Toggle satellite view."""
        self._map_operation("satellite")
    
    def _map_operation(self, operation):
        """Perform a map operation."""
        try:
            start_time = time.time()
            
            # Simulate map operation
            time.sleep(0.05)
            
            # Update map display
            self._draw_map()
            if self.route_points:
                self._draw_route()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Map operation completed: {operation}")
            
        except Exception as e:
            self.logger.error(f"Error in map operation {operation}: {e}")
    
    def update_performance_display(self):
        """Update performance metrics display."""
        try:
            # Update response time
            if self.operation_times:
                latest_response = self.operation_times[-1]
                self.response_time_label.config(text=f"Response Time: {latest_response:.1f}ms")
            
            # Update map rendering time
            if self.map_rendering_times:
                latest_render = self.map_rendering_times[-1]
                self.render_time_label.config(text=f"Map Render: {latest_render:.1f}ms")
            
            # Update operation count
            self.operation_count_label.config(text=f"Operations: {len(self.operation_times)}")
            
        except Exception as e:
            self.logger.error(f"Error updating performance display: {e}")
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance data for this widget."""
        return {
            'operation_times': self.operation_times,
            'map_rendering_times': self.map_rendering_times,
            'is_navigating': self.is_navigating,
            'current_destination': self.current_destination,
            'route_points': self.route_points
        } 