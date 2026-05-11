#!/usr/bin/env python3
"""
Generate an SVG image of a cylinder.
"""

# SVG parameters
width = 400
height = 300
cx = width / 2  # center x
cy = height / 2  # center y
radius = 80  # cylinder radius
height_cyl = 150  # cylinder height

# Calculate ellipse centers
top_ellipse_y = cy - height_cyl / 2
bottom_ellipse_y = cy + height_cyl / 2

# Create SVG content
svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     width="{width}" 
     height="{height}" 
     viewBox="0 0 {width} {height}">
  
  <!-- Define gradients for 3D effect -->
  <defs>
    <linearGradient id="cylinderGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#a8d5ff;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#e0f0ff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#a8d5ff;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="topGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#b0d8ff;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Back side of top ellipse (hidden part) -->
  <ellipse cx="{cx}" cy="{top_ellipse_y}" rx="{radius}" ry="{radius * 0.3}" 
           fill="none" stroke="#6ba3c7" stroke-width="2" />
  
  <!-- Cylinder body (rectangle with gradient) -->
  <rect x="{cx - radius}" y="{top_ellipse_y}" 
        width="{radius * 2}" height="{height_cyl}" 
        fill="url(#cylinderGradient)" stroke="#6ba3c7" stroke-width="2" />
  
  <!-- Bottom ellipse -->
  <ellipse cx="{cx}" cy="{bottom_ellipse_y}" rx="{radius}" ry="{radius * 0.3}" 
           fill="url(#cylinderGradient)" stroke="#6ba3c7" stroke-width="2" />
  
  <!-- Top ellipse (visible part) -->
  <ellipse cx="{cx}" cy="{top_ellipse_y}" rx="{radius}" ry="{radius * 0.3}" 
           fill="url(#topGradient)" stroke="#6ba3c7" stroke-width="2" />
  
  <!-- Side lines for depth -->
  <line x1="{cx - radius}" y1="{top_ellipse_y}" 
        x2="{cx - radius}" y2="{bottom_ellipse_y}" 
        stroke="#6ba3c7" stroke-width="2" opacity="0.5" />
  <line x1="{cx + radius}" y1="{top_ellipse_y}" 
        x2="{cx + radius}" y2="{bottom_ellipse_y}" 
        stroke="#6ba3c7" stroke-width="2" opacity="0.5" />
  
</svg>
'''

# Save to file
with open('cylinder.svg', 'w') as f:
    f.write(svg_content)

print("SVG cylinder saved as 'cylinder.svg'")
