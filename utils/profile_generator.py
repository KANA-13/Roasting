import numpy as np
import pandas as pd

def generate_roast_profile(bean_type, roast_level, charge_temp, development_time):
    """Generate a simulated roast profile based on parameters"""
    # Base parameters based on roast level
    if roast_level == "Light":
        final_temp = 195 + np.random.normal(0, 2)
        duration = 8 + np.random.normal(0, 0.5)
    elif roast_level == "Medium":
        final_temp = 210 + np.random.normal(0, 2)
        duration = 10 + np.random.normal(0, 0.5)
    elif roast_level == "Dark":
        final_temp = 225 + np.random.normal(0, 2)
        duration = 12 + np.random.normal(0, 0.5)
    elif roast_level == "French":
        final_temp = 240 + np.random.normal(0, 2)
        duration = 14 + np.random.normal(0, 0.5)
    else:  # Italian
        final_temp = 250 + np.random.normal(0, 2)
        duration = 16 + np.random.normal(0, 0.5)
    
    # Adjust based on bean type
    if bean_type == "Robusta":
        final_temp += 5
        duration -= 1
    elif bean_type == "Liberica":
        final_temp -= 3
        duration += 1
    
    # Generate time points
    time_points = np.linspace(0, duration, num=100)
    
    # Generate temperature curve (cubic function)
    x = time_points / duration
    temp_curve = charge_temp + (final_temp - charge_temp) * (x**3)
    
    # Add some random noise to make it realistic
    noise = np.random.normal(0, 0.5, size=len(temp_curve))
    temp_curve += noise
    
    # Create DataFrame
    profile = pd.DataFrame({
        'Time': time_points,
        'Temperature': temp_curve
    })
    
    return profile
