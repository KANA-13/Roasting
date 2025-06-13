import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from utils.event_handler import EventHandler
from utils.profile_generator import generate_roast_profile
from utils.visualization import plot_roast_profile
import numpy as np

# Set page config
st.set_page_config(
    page_title="Coffee Roasting Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
if 'first_crack_time' not in st.session_state:
    st.session_state.first_crack_time = None
if 'second_crack_time' not in st.session_state:
    st.session_state.second_crack_time = None

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
        
        # Generate random crack times based on roast level
        if roast_level == "Light":
            st.session_state.first_crack_time = np.random.uniform(7.0, 9.0)
            st.session_state.second_crack_time = None
        elif roast_level == "Medium":
            st.session_state.first_crack_time = np.random.uniform(6.5, 8.0)
            st.session_state.second_crack_time = np.random.uniform(9.5, 11.0)
        else:  # Dark, French, Italian
            st.session_state.first_crack_time = np.random.uniform(5.5, 7.0)
            st.session_state.second_crack_time = np.random.uniform(8.0, 9.5)
        
        event_handler.add_event("Profile Generated", f"{bean_type} {roast_level} profile created")

# Enhanced visualization function
def plot_enhanced_roast_profile(target_profile, actual_data=None):
    fig = go.Figure()
    
    # Plot target profile
    fig.add_trace(go.Scatter(
        x=target_profile['Time'],
        y=target_profile['Temperature'],
        mode='lines',
        name='Target Profile',
        line=dict(color='#6F4E37', width=3, dash='dash'),
        hovertemplate='Time: %{x:.1f} min<br>Temp: %{y:.1f}°C'
    ))
    
    # Plot actual data if available
    if actual_data is not None and not actual_data.empty:
        fig.add_trace(go.Scatter(
            x=actual_data['Time'],
            y=actual_data['Temperature'],
            mode='lines+markers',
            name='Actual Temperature',
            line=dict(color='#C4A484', width=3),
            marker=dict(size=6, color='#6F4E37'),
            hovertemplate='Time: %{x:.1f} min<br>Temp: %{y:.1f}°C'
        ))
        
        # Mark events
        event_data = actual_data[actual_data['Event'] != '']
        if not event_data.empty:
            fig.add_trace(go.Scatter(
                x=event_data['Time'],
                y=event_data['Temperature'],
                mode='markers',
                name='Events',
                marker=dict(
                    color='#FF0000',
                    size=12,
                    symbol='diamond',
                    line=dict(width=2, color='DarkSlateGrey')
                ),
                text=event_data['Event'],
                hovertemplate='<b>%{text}</b><br>Time: %{x:.1f} min<br>Temp: %{y:.1f}°C'
            ))
    
    # Add roast phase annotations
    fig.add_hrect(y0=150, y1=180, line_width=0, fillcolor="yellow", opacity=0.1, 
                 annotation_text="Drying Phase", annotation_position="top left")
    fig.add_hrect(y0=180, y1=210, line_width=0, fillcolor="orange", opacity=0.1, 
                 annotation_text="Maillard Phase", annotation_position="top left")
    fig.add_hrect(y0=210, y1=230, line_width=0, fillcolor="red", opacity=0.1, 
                 annotation_text="Development Phase", annotation_position="top left")
    
    # Add predicted crack times if available
    if st.session_state.first_crack_time:
        fig.add_vline(x=st.session_state.first_crack_time, line_dash="dot", 
                     line_color="green", annotation_text="Predicted 1st Crack")
    
    if st.session_state.second_crack_time:
        fig.add_vline(x=st.session_state.second_crack_time, line_dash="dot", 
                     line_color="brown", annotation_text="Predicted 2nd Crack")
    
    fig.update_layout(
        title='Roast Profile: Target vs Actual',
        xaxis_title='Time (minutes)',
        yaxis_title='Temperature (°C)',
        plot_bgcolor='rgba(240,240,240,0.9)',
        paper_bgcolor='rgba(240,240,240,0.5)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=500
    )
    # Tambahkan RoR jika data aktual tersedia
    if actual_data is not None and len(actual_data) >= 2:
        actual_data_sorted = actual_data.sort_values("Time")
        ror_values = np.gradient(actual_data_sorted['Temperature'], actual_data_sorted['Time'])  # RoR: ΔT/Δt
        fig.add_trace(go.Scatter(
            x=actual_data_sorted['Time'],
            y=ror_values,
            mode='lines',
            name='Rate of Rise (°C/min)',
            yaxis='y2',
            line=dict(color='blue', width=2, dash='dot'),
            hovertemplate='Time: %{x:.1f} min<br>RoR: %{y:.1f}°C/min'
        ))
        fig.update_layout(
            yaxis2=dict(
                title='Rate of Rise (°C/min)',
                overlaying='y',
                side='right',
                showgrid=False
            )
        )

    
    return fig

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Roast Profile Visualization")
    
    if st.session_state.roast_profile is not None:
        fig = plot_enhanced_roast_profile(
            st.session_state.roast_profile,
            st.session_state.roast_data if not st.session_state.roast_data.empty else None
        )
        st.plotly_chart(fig, use_container_width=True)
        # === Fitur Tambahan ===
        st.subheader("🔎 Additional Roast Insights")

        # Estimasi konsumsi energi
        if not st.session_state.roast_in_progress and st.session_state.start_time:
            total_minutes = (datetime.now() - st.session_state.start_time).total_seconds() / 60
            power_kw = 2.5  # asumsi daya
            energy_used = (power_kw * total_minutes) / 60  # kWh
            st.metric("Estimated Energy Used", f"{energy_used:.2f} kWh")

        # Prediksi rasa
        if st.session_state.roast_profile is not None:
            duration = st.session_state.roast_profile['Time'].iloc[-1]
            st.subheader("☕ Predicted Flavor Profile")
            if duration <= 8:
                st.info("Predicted: **Bright and acidic** - Possibly underdeveloped")
            elif duration <= 11:
                st.info("Predicted: **Balanced and sweet** - Good development")
            else:
                st.warning("Predicted: **Bitter and smoky** - Possibly overdeveloped")

        # Download laporan
        if not st.session_state.roast_data.empty:
            st.download_button(
                label="📄 Download CSV Report",
                data=st.session_state.roast_data.to_csv(index=False),
                file_name='roast_report.csv',
                mime='text/csv'
            )

        
        # Display crack predictions
        if st.session_state.first_crack_time:
            st.info(f"**Predicted First Crack**: {st.session_state.first_crack_time:.1f} minutes")
        if st.session_state.second_crack_time:
            st.info(f"**Predicted Second Crack**: {st.session_state.second_crack_time:.1f} minutes")
    else:
        st.info("Generate a roast profile using the sidebar controls to begin")
    
    st.header("Roast Control Panel")
    
    control_col1, control_col2, control_col3 = st.columns(3)
    
    with control_col1:
        if st.button("Start Roast", disabled=st.session_state.roast_in_progress or st.session_state.roast_profile is None):
            st.session_state.roast_in_progress = True
            st.session_state.start_time = datetime.now()
            st.session_state.roast_data = pd.DataFrame(columns=['Time', 'Temperature', 'Event'])
            event_handler.add_event("Roast Started", f"Batch: {batch_size}g {bean_type} from {origin}")
    
    with control_col2:
        if st.button("Add Event", disabled=not st.session_state.roast_in_progress):
            event_type = st.selectbox("Event Type", ["First Crack", "Second Crack", "Fan Adjustment", "Gas Adjustment", "Other"])
            event_note = st.text_input("Event Notes")
            if st.button("Confirm Event"):
                current_time = (datetime.now() - st.session_state.start_time).total_seconds() / 60
                current_temp = st.session_state.roast_profile.iloc[
                    min(int(current_time * 2), len(st.session_state.roast_profile)-1)
                ]['Temperature']
                
                event_handler.add_event(event_type, event_note)
                
                # Update roast data with event
                new_event = pd.DataFrame({
                    'Time': [current_time],
                    'Temperature': [current_temp],
                    'Event': [event_type]
                })
                st.session_state.roast_data = pd.concat([st.session_state.roast_data, new_event])
                st.success(f"Event '{event_type}' added at {current_time:.1f} min!")
    
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
            
            # Auto-detect first crack
            if (st.session_state.first_crack_time and 
                not any(st.session_state.roast_data['Event'] == "First Crack") and
                current_time >= st.session_state.first_crack_time):
                
                event_handler.add_event("First Crack", "Automatically detected")
                new_event = pd.DataFrame({
                    'Time': [current_time],
                    'Temperature': [current_temp],
                    'Event': ["First Crack"]
                })
                st.session_state.roast_data = pd.concat([st.session_state.roast_data, new_event])
                st.success("🔥 First Crack detected automatically!")
            
            # Auto-detect second crack
            if (st.session_state.second_crack_time and 
                not any(st.session_state.roast_data['Event'] == "Second Crack") and
                current_time >= st.session_state.second_crack_time):
                
                event_handler.add_event("Second Crack", "Automatically detected")
                new_event = pd.DataFrame({
                    'Time': [current_time],
                    'Temperature': [current_temp],
                    'Event': ["Second Crack"]
                })
                st.session_state.roast_data = pd.concat([st.session_state.roast_data, new_event])
                st.success("🔥🔥 Second Crack detected automatically!")
            
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
        # Highlight important events
        def highlight_events(row):
            if row['event_type'] == "First Crack":
                return ['background-color: #d4edda'] * len(row)
            elif row['event_type'] == "Second Crack":
                return ['background-color: #f8d7da'] * len(row)
            elif row['event_type'] == "Roast Started":
                return ['background-color: #cce5ff'] * len(row)
            elif row['event_type'] == "Roast Completed":
                return ['background-color: #e2e3e5'] * len(row)
            else:
                return [''] * len(row)
        
        st.dataframe(
            events_df.style.apply(highlight_events, axis=1),
            column_config={
                "timestamp": "Time",
                "event_type": "Event",
                "details": "Details"
            },
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
        if st.button("Clear Events"):
            event_handler.clear_events()
    else:
        st.info("No events recorded yet")
    
    st.header("Roast Statistics")
    
    if not st.session_state.roast_data.empty:
        latest_temp = st.session_state.roast_data['Temperature'].iloc[-1]
        max_temp = st.session_state.roast_data['Temperature'].max()
        
        # Calculate rate of rise
        if len(st.session_state.roast_data) > 5:
            last_30s = st.session_state.roast_data.iloc[-5:]
            ror = (last_30s['Temperature'].iloc[-1] - last_30s['Temperature'].iloc[0]) / 0.5  # °C/min
        
        # Get event times
        first_crack_time = None
        second_crack_time = None
        
        if not events_df.empty:
            if "First Crack" in events_df['event_type'].values:
                first_crack_row = events_df[events_df['event_type'] == "First Crack"].iloc[0]
                first_crack_time = (first_crack_row['timestamp'] - pd.to_datetime(st.session_state.start_time)).total_seconds() / 60
            
            if "Second Crack" in events_df['event_type'].values:
                second_crack_row = events_df[events_df['event_type'] == "Second Crack"].iloc[0]
                second_crack_time = (second_crack_row['timestamp'] - pd.to_datetime(st.session_state.start_time)).total_seconds() / 60
        
        # Display metrics
        col_stat1, col_stat2 = st.columns(2)
        col_stat1.metric("Current Temp", f"{latest_temp:.1f}°C")
        col_stat1.metric("Peak Temp", f"{max_temp:.1f}°C")
        
        if 'ror' in locals():
            col_stat2.metric("Rate of Rise", f"{ror:.1f}°C/min")
        
        if first_crack_time:
            col_stat2.metric("1st Crack Time", f"{first_crack_time:.1f} min")
        if second_crack_time:
            col_stat1.metric("2nd Crack Time", f"{second_crack_time:.1f} min")
    
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
        <p>Coffee Roasting Dashboard v2.0 | Enhanced Roast Simulation</p>
    </div>
""", unsafe_allow_html=True)
