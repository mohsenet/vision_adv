import cv2
import numpy as np

# Input and output file paths
input_video = 'input.mp4'
output_video = 'output.mp4'

# Text properties
text = "Hello, World!"
position = (480, 320)         # (x, y)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.8              # Change this value to resize text
thickness = 2
line_type = cv2.LINE_AA

# Duration settings
start_time = 2.0   # seconds
end_time = 6.0     # seconds

# Text color: Set your desired RGB color here
rgb_color = (255, 0, 0)  # e.g., Blue
font_color = tuple(reversed(rgb_color))  # Convert RGB to BGR for OpenCV

# Open the video
cap = cv2.VideoCapture(input_video)

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    current_time = frame_idx / fps

    # Only add text during specified time range
    if start_time <= current_time <= end_time:
        cv2.putText(frame, text, position, font, font_scale, font_color, thickness, line_type)

    # Write the frame
    out.write(frame)
    frame_idx += 1

# Release everything
cap.release()
out.release()
cv2.destroyAllWindows()

print("Text with custom color added to video successfully.")
