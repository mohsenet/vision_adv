import numpy as np
import matplotlib.pyplot as plt
import os

# Create output directory
output_dir = "frames"
os.makedirs(output_dir, exist_ok=True)

# Parameters
num_frames = 100
x = np.linspace(0, 4 * np.pi, 1000)

# Generate frames
for i in range(num_frames):
    phase = i * 0.1
    y = np.sin(x + phase)

    plt.figure(figsize=(6, 2))
    plt.plot(x, y, color='blue')  # Change color if background is not black
    plt.ylim(-1.5, 1.5)
    plt.axis('off')  # Hide axes
    plt.tight_layout()
    plt.savefig(f"{output_dir}/frame_{i:04d}.png", dpi=100, transparent=True)
    plt.close()

print("Frames generated.")


# After run above code, use following command to genarate .webm file (output_with_overlay.webm)
# ffmpeg -framerate 30 -i output_frames/frame_%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p output_with_overlay.webm
