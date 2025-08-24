import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

# Mission segment labels and durations (in hours)
segment_labels = ["Hover", "Climb", "Cruise", "Loiter", "Descent", "Hover (2)", "Landing"]
durations_hr = [0.033, 0.028, 0.1, 0.5, 0.046, 0.033, 0.005]
durations_min = np.array(durations_hr) * 60
time_cumulative = np.cumsum(durations_min)
time_midpoints = np.insert(time_cumulative[:-1], 0, 0) + durations_min / 2

# Mission data
power_kW = [0.91, 1.25, 0.82, 0.64, 0.30, 0.91, 0.91]
energy_kWh = [0.03, 0.03, 0.08, 0.32, 0.01, 0.03, 0.00]
thrust_N = [107.91, 109.94, 108.54, 107.99, 107.06, 107.91, 107.91]

# Smooth interpolation
time_smooth = np.linspace(time_midpoints[0], time_midpoints[-1], 300)
power_interp = interp1d(time_midpoints, power_kW, kind='cubic')
energy_interp = interp1d(time_midpoints, energy_kWh, kind='cubic')
thrust_interp = interp1d(time_midpoints, thrust_N, kind='cubic')

def smart_label_positioning(ax, xvals, yvals, labels, base_offset=0.05):
    """
    Smart label positioning to avoid overlaps with collision detection
    """
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0]
    
    # Calculate initial positions
    positions = []
    for i, (x, y, label) in enumerate(zip(xvals, yvals, labels)):
        # Determine if label should go above or below based on curve direction
        if i == 0:
            offset_direction = 1  # First point, go above
        elif i == len(xvals) - 1:
            offset_direction = 1  # Last point, go above
        else:
            # Check if point is local max/min
            prev_y, next_y = yvals[i-1], yvals[i+1]
            if y > prev_y and y > next_y:  # Local maximum
                offset_direction = 1  # Above
            elif y < prev_y and y < next_y:  # Local minimum
                offset_direction = -1  # Below
            else:
                offset_direction = 1  # Default above
        
        # Calculate position
        y_offset = offset_direction * y_range * base_offset
        label_y = y + y_offset
        
        # Ensure label stays within plot bounds
        if label_y > ylim[1]:
            label_y = y - y_range * base_offset
            offset_direction = -1
        elif label_y < ylim[0]:
            label_y = y + y_range * base_offset
            offset_direction = 1
            
        positions.append((x, y, label_y, offset_direction, label))
    
    # Collision detection and adjustment
    for i in range(len(positions)):
        x, y, label_y, direction, label = positions[i]
        
        # Check for collisions with nearby labels
        for j in range(len(positions)):
            if i == j:
                continue
            x2, y2, label_y2, direction2, label2 = positions[j]
            
            # If labels are close horizontally and vertically
            if abs(x - x2) < 5 and abs(label_y - label_y2) < y_range * 0.08:
                # Adjust current label position
                if direction == 1:  # Currently above
                    new_label_y = label_y + y_range * 0.06
                else:  # Currently below
                    new_label_y = label_y - y_range * 0.06
                
                # Update if within bounds
                if ylim[0] <= new_label_y <= ylim[1]:
                    positions[i] = (x, y, new_label_y, direction, label)
    
    # Draw labels and connection lines
    for x, y, label_y, direction, label in positions:
        # Draw connection line
        ax.plot([x, x], [y, label_y], 'k--', alpha=0.3, linewidth=0.8)
        
        # Draw label with background
        ax.annotate(label,
                   xy=(x, label_y),
                   ha='center', va='center',
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", 
                           facecolor='white', 
                           edgecolor='gray', 
                           alpha=0.9,
                           linewidth=1))

# Set up the plotting style
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

# Plot 1: Power
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(time_smooth, power_interp(time_smooth), color='#2E86AB', linewidth=3, alpha=0.8)
ax.scatter(time_midpoints, power_kW, color='#F24236', s=80, zorder=5, edgecolor='white', linewidth=2)
ax.set_title("Power Required vs Time", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Time (min)", fontsize=12, fontweight='bold')
ax.set_ylabel("Power (kW)", fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)
ax.set_facecolor('#FAFAFA')

# Apply smart labeling
smart_label_positioning(ax, time_midpoints, power_kW, segment_labels, base_offset=0.08)

plt.tight_layout()
plt.savefig("power_vs_time_improved.png", dpi=300, bbox_inches='tight')
plt.show()

# Plot 2: Energy
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(time_smooth, energy_interp(time_smooth), color='#A23B72', linewidth=3, alpha=0.8)
ax.scatter(time_midpoints, energy_kWh, color='#F18F01', s=80, zorder=5, edgecolor='white', linewidth=2)
ax.set_title("Energy Consumption vs Time", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Time (min)", fontsize=12, fontweight='bold')
ax.set_ylabel("Energy (kWh)", fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)
ax.set_facecolor('#FAFAFA')

# Apply smart labeling
smart_label_positioning(ax, time_midpoints, energy_kWh, segment_labels, base_offset=0.12)

plt.tight_layout()
plt.savefig("energy_vs_time_improved.png", dpi=300, bbox_inches='tight')
plt.show()

# Plot 3: Thrust
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(time_smooth, thrust_interp(time_smooth), color='#C73E1D', linewidth=3, alpha=0.8)
ax.scatter(time_midpoints, thrust_N, color='#F24236', s=80, zorder=5, edgecolor='white', linewidth=2)
ax.set_title("Thrust Required vs Time", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Time (min)", fontsize=12, fontweight='bold')
ax.set_ylabel("Thrust (N)", fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)
ax.set_facecolor('#FAFAFA')

# Apply smart labeling
smart_label_positioning(ax, time_midpoints, thrust_N, segment_labels, base_offset=0.04)

plt.tight_layout()
plt.savefig("thrust_vs_time_improved.png", dpi=300, bbox_inches='tight')
plt.show()

print("All plots generated successfully with improved label positioning!")
print("Features added:")
print("- Smart collision detection and avoidance")
print("- Adaptive label positioning (above/below based on curve)")
print("- Connection lines from points to labels")
print("- Enhanced visual styling with better colors and contrast")
print("- Higher resolution output (300 DPI)")
print("- Improved readability with bold fonts and backgrounds")