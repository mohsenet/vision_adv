import cv2
import numpy as np

# File paths
input_video = "input.mp4"
output_video = "output.mp4"
# overlay_image_path = "transparent.png"  # Must be a PNG with transparency
overlay_image_path = "frames/frame_0000.png"

# Timing and position
start_time = 2.0    # seconds
end_time = 6.0      # seconds
position = (100, 100)  # Top-left corner of the overlay (x, y)

# Load overlay image (with transparency)
overlay_img = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)

if overlay_img is None:
    raise FileNotFoundError(f"Failed to load overlay image: {overlay_image_path}")

if overlay_img.shape[2] != 4:
    raise ValueError("The overlay image must have an alpha channel (i.e., be a PNG with transparency).")

# Open the video
cap = cv2.VideoCapture(input_video)
if not cap.isOpened():
    raise IOError("Error opening input video file.")

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    current_time = frame_idx / fps

    # Only overlay image during specified time range
    if start_time <= current_time <= end_time:
        img_h, img_w = overlay_img.shape[:2]
        x, y = position

        # Clamp position to stay within the video frame
        x = max(0, min(x, frame_width - img_w))
        y = max(0, min(y, frame_height - img_h))

        roi = frame[y:y+img_h, x:x+img_w]

        # Ensure ROI and overlay image have the same size
        if roi.shape[0] != overlay_img.shape[0] or roi.shape[1] != overlay_img.shape[1]:
            # Resize overlay to fit ROI (or vice versa)
            overlay_resized = cv2.resize(overlay_img, (roi.shape[1], roi.shape[0]))
        else:
            overlay_resized = overlay_img

        overlay_bgr = overlay_resized[:, :, :3]
        overlay_alpha = overlay_resized[:, :, 3]

        # Normalize alpha to [0, 1]
        alpha_mask = overlay_alpha.astype(np.float32) / 255.0
        alpha_inv = 1.0 - alpha_mask

        # Blend each color channel separately
        for c in range(3):
            roi[:, :, c] = (alpha_mask * overlay_bgr[:, :, c] + alpha_inv * roi[:, :, c])

        # Replace ROI in original frame
        frame[y:y+img_h, x:x+img_w] = roi

    # Write the frame to output video
    out.write(frame)
    frame_idx += 1

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print("Transparent PNG image overlaid successfully.")
