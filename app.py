import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
from utils.event_handler import EventHandler
from utils.profile_generator import generate_roast_profile
from utils.visualization import plot_roast_profile
import time
import os

# Set page config
st.set_page_config(
    page_title="Coffee Roasting Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/styles.css")

# Initialize event handler
event_handler = EventHandler()

# Session state initialization
if 'roast_data' not in st.session_state:
    st.session_state.roast_data = pd.DataFrame(columns=['Time', 'Temperature', 'Event'])
if 'roast_in_progress' not in st.session_state:
    st.session_state.roast_in_progress = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'roast_profile' not in st.session_state:
    st.session_state.roast_profile = None

# Header
st.title("☕ Coffee Roasting Dashboard")
st.markdown("""
    <div class="header">
        <p>Simulate and analyze your coffee roasting process with event-driven tracking</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("assets/sample_beans.jpg", use_column_width=True)
    st.header("Roast Parameters")
    
    bean_type = st.selectbox("Bean Type", ["Arabica", "Robusta", "Liberica", "Excelsa", "Blend"])
    origin = st.selectbox("Origin", ["Colombia", "Ethiopia", "Brazil", "Vietnam", "Indonesia", "Kenya", "Guatemala"])
    batch_size = st.slider("Batch Size (g)", 100, 1000, 250, 50)
    
    roast_level = st.select_slider(
        "Target Roast Level",
        options=['Light', 'Medium', 'Dark', 'French', 'Italian'],
        value='Medium'
    )
    
    charge_temp = st.slider("Charge Temperature (°C)", 150, 250, 190, 5)
    development_time = st.slider("Development Time (%)", 10, 40, 20, 1)
    
    if st.button("Generate Roast Profile", key="generate_profile"):
        st.session_state.roast_profile = generate_roast_profile(
            bean_type, roast_level, charge_temp, development_time
        )
        event_handler.add_event("Profile Generated", f"{bean_type} {roast_level} profile created")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Roast Profile Visualization")
    
    if st.session_state.roast_profile is not None:
        fig = plot_roast_profile(st.session_state.roast_profile)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Generate a roast profile using the sidebar controls to begin")
    
    st.header("Roast Control Panel")
    
    control_col1, control_col2, control_col3 = st.columns(3)
    
    with control_col1:
        if st.button("Start Roast", disabled=st.session_state.roast_in_progress or st.session_state.roast_profile is None):
            st.session_state.roast_in_progress = True
            st.session_state.start_time = datetime.now()
            event_handler.add_event("Roast Started", f"Batch: {batch_size}g {bean_type} from {origin}")
    
    with control_col2:
        if st.button("Add Event", disabled=not st.session_state.roast_in_progress):
            event_type = st.selectbox("Event Type", ["First Crack", "Second Crack", "Temperature Adjustment", "Other"])
            event_note = st.text_input("Event Notes")
            if st.button("Confirm Event"):
                event_handler.add_event(event_type, event_note)
    
    with control_col3:
        if st.button("End Roast", disabled=not st.session_state.roast_in_progress):
            st.session_state.roast_in_progress = False
            duration = datetime.now() - st.session_state.start_time
            event_handler.add_event("Roast Completed", f"Duration: {duration.total_seconds()/60:.1f} minutes")
    
    if st.session_state.roast_in_progress:
        st.warning("Roast in progress - monitor temperature and events carefully!")
        
        # Simulate temperature readings
        if st.session_state.roast_profile is not None:
            current_time = (datetime.now() - st.session_state.start_time).total_seconds() / 60
            current_temp = st.session_state.roast_profile.iloc[
                min(int(current_time * 2), len(st.session_state.roast_profile)-1)
            ]['Temperature']
            
            st.metric("Current Temperature", f"{current_temp:.1f}°C")
            st.metric("Elapsed Time", f"{current_time:.1f} minutes")
            
            # Update roast data
            new_data = pd.DataFrame({
                'Time': [current_time],
                'Temperature': [current_temp],
                'Event': ['']
            })
            st.session_state.roast_data = pd.concat([st.session_state.roast_data, new_data])

with col2:
    st.header("Roast Events Log")
    events_df = event_handler.get_events_df()
    
    if not events_df.empty:
        st.dataframe(
            events_df,
            column_config={
                "timestamp": "Time",
                "event_type": "Event",
                "details": "Details"
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("Clear Events"):
            event_handler.clear_events()
    else:
        st.info("No events recorded yet")
    
    st.header("Roast Statistics")
    
    if not st.session_state.roast_data.empty:
        latest_temp = st.session_state.roast_data['Temperature'].iloc[-1]
        max_temp = st.session_state.roast_data['Temperature'].max()
        time_to_first_crack = "N/A"
        
        if not events_df.empty and "First Crack" in events_df['event_type'].values:
            first_crack_time = events_df[
                events_df['event_type'] == "First Crack"
            ]['timestamp'].iloc[0]
            start_time = pd.to_datetime(st.session_state.start_time)
            time_to_first_crack = (first_crack_time - start_time).total_seconds() / 60
        
        st.metric("Current Temperature", f"{latest_temp:.1f}°C")
        st.metric("Peak Temperature", f"{max_temp:.1f}°C")
        st.metric("Time to First Crack", 
                 f"{time_to_first_crack:.1f} min" if isinstance(time_to_first_crack, float) else time_to_first_crack)
    
    st.header("Roast Recommendations")
    
    if st.session_state.roast_profile is not None:
        if roast_level == "Light":
            st.info("""
            **Light Roast Tips**:
            - Drop at first crack
            - Aim for 15-20% development
            - Expect bright acidity
            """)
        elif roast_level == "Medium":
            st.info("""
            **Medium Roast Tips**:
            - Drop 30-45 seconds after first crack
            - Aim for 20-25% development
            - Balanced acidity and body
            """)
        elif roast_level in ["Dark", "French", "Italian"]:
            st.warning("""
            **Dark Roast Tips**:
            - Watch for second crack
            - Reduce heat as you approach target
            - Expect heavy body and smoky notes
            """)

# Footer
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>Coffee Roasting Dashboard v1.0 | Event-Driven Roast Simulation</p>
    </div>
""", unsafe_allow_html=True)
