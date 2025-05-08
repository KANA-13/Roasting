import plotly.express as px

def plot_roast_profile(profile_df):
    """Create an interactive plot of the roast profile"""
    fig = px.line(
        profile_df, 
        x='Time', 
        y='Temperature',
        title='Roast Profile',
        labels={'Time': 'Time (minutes)', 'Temperature': 'Temperature (°C)'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(240,240,240,0.9)',
        paper_bgcolor='rgba(240,240,240,0.5)',
        xaxis=dict(gridcolor='white'),
        yaxis=dict(gridcolor='white'),
        hovermode='x unified'
    )
    
    fig.update_traces(
        line=dict(color='#6F4E37', width=3),
        hovertemplate='Time: %{x:.1f} min<br>Temp: %{y:.1f}°C'
    )
    
    return fig
