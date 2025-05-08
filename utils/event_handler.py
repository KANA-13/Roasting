import pandas as pd
from datetime import datetime

class EventHandler:
    def __init__(self):
        self.events = []
    
    def add_event(self, event_type, details=""):
        """Add a new event to the log"""
        timestamp = datetime.now()
        self.events.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "details": details
        })
    
    def get_events_df(self):
        """Return events as a pandas DataFrame"""
        return pd.DataFrame(self.events)
    
    def clear_events(self):
        """Clear all events"""
        self.events = []
