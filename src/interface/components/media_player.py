"""
Media player widget for the infotainment interface.
Simulates media playback functionality with performance tracking.
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from typing import Dict, List, Any

from ...utils.logger import get_logger
from ...monitoring.performance_monitor import get_performance_monitor

class MediaPlayerWidget(ttk.Frame):
    """Media player application widget."""
    
    def __init__(self, parent, main_interface):
        super().__init__(parent)
        self.main_interface = main_interface
        self.logger = get_logger("media_player")
        self.performance_monitor = get_performance_monitor()
        
        # Media state
        self.is_playing = False
        self.current_track = 0
        self.volume = 50
        self.playlist = self._create_sample_playlist()
        
        # Performance tracking
        self.playback_start_time = 0
        self.operation_times = []
        
        self._create_widgets()
        self.logger.info("Media Player Widget initialized")
    
    def _create_sample_playlist(self) -> List[Dict[str, str]]:
        """Create a sample playlist for testing."""
        return [
            {"title": "Highway to Hell", "artist": "AC/DC", "duration": "3:28"},
            {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "duration": "5:56"},
            {"title": "Bohemian Rhapsody", "artist": "Queen", "duration": "5:55"},
            {"title": "Stairway to Heaven", "artist": "Led Zeppelin", "duration": "8:02"},
            {"title": "Hotel California", "artist": "Eagles", "duration": "6:30"},
            {"title": "Imagine", "artist": "John Lennon", "duration": "3:03"},
            {"title": "Hey Jude", "artist": "The Beatles", "duration": "7:11"},
            {"title": "Smells Like Teen Spirit", "artist": "Nirvana", "duration": "5:01"}
        ]
    
    def _create_widgets(self):
        """Create all media player UI elements."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_container, text="🎵 Media Player", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Now playing section
        self._create_now_playing_section(main_container)
        
        # Playlist section
        self._create_playlist_section(main_container)
        
        # Controls section
        self._create_controls_section(main_container)
        
        # Volume section
        self._create_volume_section(main_container)
        
        # Performance metrics
        self._create_performance_section(main_container)
    
    def _create_now_playing_section(self, parent):
        """Create the now playing display section."""
        now_playing_frame = ttk.LabelFrame(parent, text="Now Playing", padding=15)
        now_playing_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Track info
        self.track_title_label = ttk.Label(now_playing_frame, text="No track selected", 
                                          font=('Arial', 14, 'bold'))
        self.track_title_label.pack()
        
        self.track_artist_label = ttk.Label(now_playing_frame, text="", 
                                           font=('Arial', 12))
        self.track_artist_label.pack()
        
        # Progress bar
        progress_frame = ttk.Frame(now_playing_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(progress_frame, text="0:00 / 0:00")
        self.time_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Update progress bar
        self._update_progress()
    
    def _create_playlist_section(self, parent):
        """Create the playlist display section."""
        playlist_frame = ttk.LabelFrame(parent, text="Playlist", padding=15)
        playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Playlist treeview
        columns = ('Title', 'Artist', 'Duration')
        self.playlist_tree = ttk.Treeview(playlist_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            self.playlist_tree.heading(col, text=col)
            self.playlist_tree.column(col, width=150)
        
        # Add playlist items
        for i, track in enumerate(self.playlist):
            self.playlist_tree.insert('', 'end', values=(track['title'], track['artist'], track['duration']))
        
        # Scrollbar
        playlist_scrollbar = ttk.Scrollbar(playlist_frame, orient=tk.VERTICAL, 
                                          command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=playlist_scrollbar.set)
        
        # Pack playlist elements
        self.playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.playlist_tree.bind('<<TreeviewSelect>>', self._on_track_selection)
    
    def _create_controls_section(self, parent):
        """Create the playback controls section."""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Control buttons
        self.prev_button = ttk.Button(controls_frame, text="⏮ Previous", 
                                     command=self._previous_track, width=12)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.play_button = ttk.Button(controls_frame, text="▶ Play", 
                                     command=self._toggle_playback, width=12)
        self.play_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_button = ttk.Button(controls_frame, text="⏭ Next", 
                                     command=self._next_track, width=12)
        self.next_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Shuffle and repeat buttons
        self.shuffle_button = ttk.Button(controls_frame, text="🔀 Shuffle", 
                                        command=self._toggle_shuffle, width=12)
        self.shuffle_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.repeat_button = ttk.Button(controls_frame, text="🔁 Repeat", 
                                       command=self._toggle_repeat, width=12)
        self.repeat_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    def _create_volume_section(self, parent):
        """Create the volume control section."""
        volume_frame = ttk.LabelFrame(parent, text="Volume Control", padding=15)
        volume_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Volume slider
        volume_slider_frame = ttk.Frame(volume_frame)
        volume_slider_frame.pack(fill=tk.X)
        
        ttk.Label(volume_slider_frame, text="🔊").pack(side=tk.LEFT)
        
        self.volume_var = tk.IntVar(value=self.volume)
        self.volume_slider = ttk.Scale(volume_slider_frame, from_=0, to=100, 
                                      variable=self.volume_var, orient=tk.HORIZONTAL,
                                      command=self._on_volume_change)
        self.volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.volume_label = ttk.Label(volume_slider_frame, text=f"{self.volume}%")
        self.volume_label.pack(side=tk.RIGHT)
    
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
        
        # Average operation time
        self.avg_op_time_label = ttk.Label(perf_indicators_frame, text="Avg Op Time: 0ms")
        self.avg_op_time_label.pack(side=tk.LEFT)
    
    def _on_track_selection(self, event):
        """Handle track selection from playlist."""
        try:
            start_time = time.time()
            
            selection = self.playlist_tree.selection()
            if selection:
                item = self.playlist_tree.item(selection[0])
                track_index = self.playlist_tree.index(selection[0])
                
                self.current_track = track_index
                self._update_now_playing()
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000
                self.performance_monitor.update_response_time(response_time)
                self.operation_times.append(response_time)
                
                self.logger.info(f"Track selected: {self.playlist[track_index]['title']} in {response_time:.2f}ms")
                
        except Exception as e:
            self.logger.error(f"Error selecting track: {e}")
    
    def _toggle_playback(self):
        """Toggle play/pause functionality."""
        try:
            start_time = time.time()
            
            if self.is_playing:
                self._pause_playback()
            else:
                self._start_playback()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
        except Exception as e:
            self.logger.error(f"Error toggling playback: {e}")
    
    def _start_playback(self):
        """Start playback."""
        self.is_playing = True
        self.play_button.config(text="⏸ Pause")
        self.playback_start_time = time.time()
        self.logger.info("Playback started")
    
    def _pause_playback(self):
        """Pause playback."""
        self.is_playing = False
        self.play_button.config(text="▶ Play")
        self.logger.info("Playback paused")
    
    def _previous_track(self):
        """Go to previous track."""
        try:
            start_time = time.time()
            
            if self.current_track > 0:
                self.current_track -= 1
                self._update_now_playing()
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000
                self.performance_monitor.update_response_time(response_time)
                self.operation_times.append(response_time)
                
        except Exception as e:
            self.logger.error(f"Error going to previous track: {e}")
    
    def _next_track(self):
        """Go to next track."""
        try:
            start_time = time.time()
            
            if self.current_track < len(self.playlist) - 1:
                self.current_track += 1
                self._update_now_playing()
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000
                self.performance_monitor.update_response_time(response_time)
                self.operation_times.append(response_time)
                
        except Exception as e:
            self.logger.error(f"Error going to next track: {e}")
    
    def _toggle_shuffle(self):
        """Toggle shuffle mode."""
        try:
            start_time = time.time()
            
            # Simulate shuffle operation
            import random
            random.shuffle(self.playlist)
            
            # Refresh playlist display
            self._refresh_playlist_display()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info("Playlist shuffled")
            
        except Exception as e:
            self.logger.error(f"Error shuffling playlist: {e}")
    
    def _toggle_repeat(self):
        """Toggle repeat mode."""
        try:
            start_time = time.time()
            
            # Simulate repeat toggle
            self.logger.info("Repeat mode toggled")
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
        except Exception as e:
            self.logger.error(f"Error toggling repeat: {e}")
    
    def _on_volume_change(self, value):
        """Handle volume slider change."""
        try:
            self.volume = int(float(value))
            self.volume_label.config(text=f"{self.volume}%")
            
            # Simulate volume change delay
            time.sleep(0.05)
            
        except Exception as e:
            self.logger.error(f"Error changing volume: {e}")
    
    def _update_now_playing(self):
        """Update the now playing display."""
        if 0 <= self.current_track < len(self.playlist):
            track = self.playlist[self.current_track]
            self.track_title_label.config(text=track['title'])
            self.track_artist_label.config(text=track['artist'])
            
            # Update playlist selection
            self.playlist_tree.selection_set(self.playlist_tree.get_children()[self.current_track])
    
    def _refresh_playlist_display(self):
        """Refresh the playlist display after changes."""
        # Clear existing items
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)
        
        # Add updated playlist items
        for track in self.playlist:
            self.playlist_tree.insert('', 'end', values=(track['title'], track['artist'], track['duration']))
    
    def _update_progress(self):
        """Update the progress bar."""
        if self.is_playing:
            # Simulate progress
            current_progress = self.progress_var.get()
            if current_progress < 100:
                self.progress_var.set(current_progress + 1)
                
                # Update time display
                track = self.playlist[self.current_track]
                duration_parts = track['duration'].split(':')
                total_seconds = int(duration_parts[0]) * 60 + int(duration_parts[1])
                
                current_seconds = int((current_progress / 100) * total_seconds)
                current_time = f"{current_seconds // 60}:{current_seconds % 60:02d}"
                
                self.time_label.config(text=f"{current_time} / {track['duration']}")
            
            # Schedule next update
            self.after(1000, self._update_progress)
    
    def update_performance_display(self):
        """Update performance metrics display."""
        try:
            # Update response time
            if self.operation_times:
                latest_response = self.operation_times[-1]
                self.response_time_label.config(text=f"Response Time: {latest_response:.1f}ms")
            
            # Update operation count
            self.operation_count_label.config(text=f"Operations: {len(self.operation_times)}")
            
            # Update average operation time
            if self.operation_times:
                avg_time = sum(self.operation_times) / len(self.operation_times)
                self.avg_op_time_label.config(text=f"Avg Op Time: {avg_time:.1f}ms")
            
        except Exception as e:
            self.logger.error(f"Error updating performance display: {e}")
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance data for this widget."""
        return {
            'operation_times': self.operation_times,
            'current_track': self.current_track,
            'is_playing': self.is_playing,
            'volume': self.volume
        } 