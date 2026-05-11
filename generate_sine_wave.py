#!/usr/bin/env python3
"""
Generate a sine wave image using matplotlib.
"""

import numpy as np
import matplotlib.pyplot as plt

# Generate x values from 0 to 4π
x = np.linspace(0, 4 * np.pi, 1000)

# Calculate sine values
y = np.sin(x)

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')

# Add labels and title
plt.xlabel('x (radians)', fontsize=12)
plt.ylabel('sin(x)', fontsize=12)
plt.title('Sine Wave', fontsize=14, fontweight='bold')

# Add grid
plt.grid(True, alpha=0.3)

# Add legend
plt.legend(loc='upper right')

# Set axis limits
plt.xlim(0, 4 * np.pi)
plt.ylim(-1.5, 1.5)

# Save the figure
plt.savefig('sine_wave.png', dpi=150, bbox_inches='tight')
print("Sine wave image saved as 'sine_wave.png'")

# Also show the plot (optional, comment out if running on server)
# plt.show()
