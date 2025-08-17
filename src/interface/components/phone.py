"""
Phone widget for the infotainment interface.
Simulates phone functionality with performance tracking.
"""

import tkinter as tk
from tkinter import ttk
import time
import random
from typing import Dict, List, Any

from ...utils.logger import get_logger
from ...monitoring.performance_monitor import get_performance_monitor

class PhoneWidget(ttk.Frame):
    """Phone application widget."""
    
    def __init__(self, parent, main_interface):
        super().__init__(parent)
        self.main_interface = main_interface
        self.logger = get_logger("phone")
        self.performance_monitor = get_performance_monitor()
        
        # Phone state
        self.is_connected = False
        self.current_call = None
        self.contacts = self._create_sample_contacts()
        self.call_history = []
        
        # Performance tracking
        self.operation_times = []
        
        self._create_widgets()
        self.logger.info("Phone Widget initialized")
    
    def _create_sample_contacts(self) -> List[Dict[str, str]]:
        """Create sample contacts for testing."""
        return [
            {"name": "John Doe", "number": "+1-555-0101", "category": "Family"},
            {"name": "Jane Smith", "number": "+1-555-0102", "category": "Work"},
            {"name": "Bob Johnson", "number": "+1-555-0103", "category": "Friend"},
            {"name": "Alice Brown", "number": "+1-555-0104", "category": "Family"},
            {"name": "Charlie Wilson", "number": "+1-555-0105", "category": "Work"}
        ]
    
    def _create_widgets(self):
        """Create all phone UI elements."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_container, text="📱 Phone", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Connection status
        self._create_connection_section(main_container)
        
        # Dialer section
        self._create_dialer_section(main_container)
        
        # Contacts section
        self._create_contacts_section(main_container)
        
        # Call controls
        self._create_call_controls(main_container)
        
        # Performance metrics
        self._create_performance_section(main_container)
    
    def _create_connection_section(self, parent):
        """Create the Bluetooth connection section."""
        connection_frame = ttk.LabelFrame(parent, text="Bluetooth Connection", padding=15)
        connection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Connection status
        status_frame = ttk.Frame(connection_frame)
        status_frame.pack(fill=tk.X)
        
        self.connection_label = ttk.Label(status_frame, text="Status: Disconnected", 
                                         foreground='red', font=('Arial', 10, 'bold'))
        self.connection_label.pack(side=tk.LEFT)
        
        self.connect_button = ttk.Button(status_frame, text="🔗 Connect", 
                                        command=self._toggle_connection, width=12)
        self.connect_button.pack(side=tk.RIGHT)
        
        # Device info
        device_frame = ttk.Frame(connection_frame)
        device_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(device_frame, text="Device: iPhone 15 Pro").pack(side=tk.LEFT)
        ttk.Label(device_frame, text="Signal: --").pack(side=tk.RIGHT)
    
    def _create_dialer_section(self, parent):
        """Create the phone dialer section."""
        dialer_frame = ttk.LabelFrame(parent, text="Dialer", padding=15)
        dialer_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Phone number display
        self.phone_var = tk.StringVar()
        phone_display = ttk.Entry(dialer_frame, textvariable=self.phone_var, 
                                 font=('Arial', 16), justify='center', state='readonly')
        phone_display.pack(fill=tk.X, pady=(0, 15))
        
        # Number pad
        number_pad_frame = ttk.Frame(dialer_frame)
        number_pad_frame.pack()
        
        # Create number buttons
        numbers = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['*', '0', '#']
        ]
        
        for row_idx, row in enumerate(numbers):
            row_frame = ttk.Frame(number_pad_frame)
            row_frame.pack(pady=2)
            
            for col_idx, number in enumerate(row):
                btn = ttk.Button(row_frame, text=number, width=8,
                               command=lambda n=number: self._add_number(n))
                btn.pack(side=tk.LEFT, padx=2)
        
        # Call and clear buttons
        call_buttons_frame = ttk.Frame(dialer_frame)
        call_buttons_frame.pack(pady=(15, 0))
        
        self.call_button = ttk.Button(call_buttons_frame, text="📞 Call", 
                                     command=self._make_call, width=12, state='disabled')
        self.call_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(call_buttons_frame, text="⌫ Clear", 
                                      command=self._clear_number, width=12)
        self.clear_button.pack(side=tk.LEFT)
    
    def _create_contacts_section(self, parent):
        """Create the contacts section."""
        contacts_frame = ttk.LabelFrame(parent, text="Contacts", padding=15)
        contacts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Search contacts
        search_frame = ttk.Frame(contacts_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        
        self.contact_search_var = tk.StringVar()
        self.contact_search_entry = ttk.Entry(search_frame, textvariable=self.contact_search_var, width=25)
        self.contact_search_entry.pack(side=tk.LEFT, padx=(10, 10))
        
        self.search_contacts_button = ttk.Button(search_frame, text="🔍", 
                                               command=self._search_contacts)
        self.search_contacts_button.pack(side=tk.LEFT)
        
        # Contacts list
        columns = ('Name', 'Number', 'Category')
        self.contacts_tree = ttk.Treeview(contacts_frame, columns=columns, show='headings', height=6)
        
        # Configure columns
        for col in columns:
            self.contacts_tree.heading(col, text=col)
            self.contacts_tree.column(col, width=120)
        
        # Add contacts
        for contact in self.contacts:
            self.contacts_tree.insert('', 'end', values=(contact['name'], contact['number'], contact['category']))
        
        # Scrollbar
        contacts_scrollbar = ttk.Scrollbar(contacts_frame, orient=tk.VERTICAL, 
                                          command=self.contacts_tree.yview)
        self.contacts_tree.configure(yscrollcommand=contacts_scrollbar.set)
        
        # Pack contacts elements
        self.contacts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        contacts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.contacts_tree.bind('<<TreeviewSelect>>', self._on_contact_selection)
    
    def _create_call_controls(self, parent):
        """Create the call control section."""
        controls_frame = ttk.LabelFrame(parent, text="Call Controls", padding=15)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Call status
        self.call_status_label = ttk.Label(controls_frame, text="No active call", 
                                          font=('Arial', 12))
        self.call_status_label.pack(pady=(0, 15))
        
        # Call control buttons
        controls_buttons_frame = ttk.Frame(controls_frame)
        controls_buttons_frame.pack()
        
        self.answer_button = ttk.Button(controls_buttons_frame, text="📞 Answer", 
                                       command=self._answer_call, width=12, state='disabled')
        self.answer_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.end_call_button = ttk.Button(controls_buttons_frame, text="📵 End", 
                                         command=self._end_call, width=12, state='disabled')
        self.end_call_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.mute_button = ttk.Button(controls_buttons_frame, text="🔇 Mute", 
                                     command=self._toggle_mute, width=12, state='disabled')
        self.mute_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.speaker_button = ttk.Button(controls_buttons_frame, text="🔊 Speaker", 
                                        command=self._toggle_speaker, width=12, state='disabled')
        self.speaker_button.pack(side=tk.LEFT)
    
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
        
        # Call count
        self.call_count_label = ttk.Label(perf_indicators_frame, text="Calls: 0")
        self.call_count_label.pack(side=tk.LEFT)
    
    def _toggle_connection(self):
        """Toggle Bluetooth connection."""
        try:
            start_time = time.time()
            
            if not self.is_connected:
                # Simulate connection delay
                time.sleep(0.5)
                self.is_connected = True
                self.connection_label.config(text="Status: Connected", foreground='green')
                self.connect_button.config(text="🔌 Disconnect")
                self.call_button.config(state='normal')
                self.logger.info("Bluetooth connected")
            else:
                # Simulate disconnection
                time.sleep(0.2)
                self.is_connected = False
                self.connection_label.config(text="Status: Disconnected", foreground='red')
                self.connect_button.config(text="🔗 Connect")
                self.call_button.config(state='disabled')
                self.logger.info("Bluetooth disconnected")
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
        except Exception as e:
            self.logger.error(f"Error toggling connection: {e}")
    
    def _add_number(self, number):
        """Add a number to the phone display."""
        current = self.phone_var.get()
        self.phone_var.set(current + number)
        
        # Enable call button if we have a number
        if len(self.phone_var.get()) > 0:
            self.call_button.config(state='normal')
    
    def _clear_number(self):
        """Clear the phone number display."""
        self.phone_var.set("")
        self.call_button.config(state='disabled')
    
    def _make_call(self):
        """Make a phone call."""
        if not self.is_connected:
            return
        
        try:
            start_time = time.time()
            
            number = self.phone_var.get()
            if not number:
                return
            
            # Simulate call initiation
            time.sleep(0.3)
            
            # Create call object
            self.current_call = {
                'number': number,
                'start_time': time.time(),
                'status': 'dialing'
            }
            
            # Update UI
            self.call_status_label.config(text=f"Calling {number}...")
            self.end_call_button.config(state='normal')
            self.mute_button.config(state='normal')
            self.speaker_button.config(state='normal')
            
            # Simulate call connection
            self.after(2000, self._connect_call)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Call initiated to {number}")
            
        except Exception as e:
            self.logger.error(f"Error making call: {e}")
    
    def _connect_call(self):
        """Simulate call connection."""
        if self.current_call:
            self.current_call['status'] = 'connected'
            self.call_status_label.config(text=f"Connected to {self.current_call['number']}")
            self.logger.info("Call connected")
    
    def _answer_call(self):
        """Answer an incoming call."""
        # This would be used for incoming calls
        pass
    
    def _end_call(self):
        """End the current call."""
        if not self.current_call:
            return
        
        try:
            # Calculate call duration
            duration = time.time() - self.current_call['start_time']
            
            # Add to call history
            self.call_history.append({
                'number': self.current_call['number'],
                'duration': duration,
                'timestamp': time.time()
            })
            
            # Clear call
            self.current_call = None
            
            # Update UI
            self.call_status_label.config(text="No active call")
            self.end_call_button.config(state='disabled')
            self.mute_button.config(state='disabled')
            self.speaker_button.config(state='disabled')
            
            self.logger.info(f"Call ended, duration: {duration:.1f}s")
            
        except Exception as e:
            self.logger.error(f"Error ending call: {e}")
    
    def _toggle_mute(self):
        """Toggle call mute."""
        if self.current_call:
            self.logger.info("Mute toggled")
    
    def _toggle_speaker(self):
        """Toggle speaker mode."""
        if self.current_call:
            self.logger.info("Speaker toggled")
    
    def _search_contacts(self):
        """Search contacts by name."""
        try:
            start_time = time.time()
            
            search_term = self.contact_search_var.get().lower()
            if not search_term:
                # Show all contacts
                self._refresh_contacts_display(self.contacts)
                return
            
            # Filter contacts
            results = [c for c in self.contacts if search_term in c['name'].lower()]
            self._refresh_contacts_display(results)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.performance_monitor.update_response_time(response_time)
            self.operation_times.append(response_time)
            
            self.logger.info(f"Contact search completed for '{search_term}'")
            
        except Exception as e:
            self.logger.error(f"Error searching contacts: {e}")
    
    def _on_contact_selection(self, event):
        """Handle contact selection."""
        try:
            selection = self.contacts_tree.selection()
            if selection:
                item = self.contacts_tree.item(selection[0])
                contact_name = item['values'][0]
                contact_number = item['values'][1]
                
                # Fill in the phone number
                self.phone_var.set(contact_number)
                self.call_button.config(state='normal')
                
                self.logger.info(f"Contact selected: {contact_name}")
            
        except Exception as e:
            self.logger.error(f"Error selecting contact: {e}")
    
    def _refresh_contacts_display(self, contacts):
        """Refresh the contacts display."""
        # Clear existing items
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
        
        # Add filtered contacts
        for contact in contacts:
            self.contacts_tree.insert('', 'end', values=(contact['name'], contact['number'], contact['category']))
    
    def update_performance_display(self):
        """Update performance metrics display."""
        try:
            # Update response time
            if self.operation_times:
                latest_response = self.operation_times[-1]
                self.response_time_label.config(text=f"Response Time: {latest_response:.1f}ms")
            
            # Update operation count
            self.operation_count_label.config(text=f"Operations: {len(self.operation_times)}")
            
            # Update call count
            self.call_count_label.config(text=f"Calls: {len(self.call_history)}")
            
        except Exception as e:
            self.logger.error(f"Error updating performance display: {e}")
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance data for this widget."""
        return {
            'operation_times': self.operation_times,
            'is_connected': self.is_connected,
            'current_call': self.current_call,
            'call_history': self.call_history
        } 