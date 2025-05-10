import cv2
import numpy as np
import os

# File paths
input_video = "input.mp4"
output_video = "output.mp4"
overlay_folder = "frames/"  # Folder containing all PNGs

# Timing and position
start_time = 2.0    # seconds
end_time = 6.0      # seconds
position = (100, 100)  # Top-left corner of the overlay (x, y)

# Open the video
cap = cv2.VideoCapture(input_video)
if not cap.isOpened():
    raise IOError("Error opening input video file.")

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

# Load list of overlay images
overlay_files = sorted(
    [f for f in os.listdir(overlay_folder) if f.endswith('.png')],
    key=lambda x: int(x[6:-4])  # Extract number from 'frame_XXXX.png'
)
overlay_images = [cv2.imread(os.path.join(overlay_folder, f), cv2.IMREAD_UNCHANGED) for f in overlay_files]

for img in overlay_images:
    if img.shape[2] != 4:
        raise ValueError("All overlay images must have an alpha channel.")

total_overlay_frames = len(overlay_images)

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    current_time = frame_idx / fps

    # Only overlay animation during specified time range
    if start_time <= current_time <= end_time:
        # Calculate which overlay frame to use
        anim_duration_seconds = end_time - start_time
        total_anim_frames_needed = int(anim_duration_seconds * fps)
        frame_in_animation = int(((current_time - start_time) / anim_duration_seconds) * total_overlay_frames)

        # Clamp index to valid range
        frame_in_animation = min(frame_in_animation, total_overlay_frames - 1)

        overlay_img = overlay_images[frame_in_animation]
        img_h, img_w = overlay_img.shape[:2]
        x, y = position

        # Clamp position to stay within the video frame
        x = max(0, min(x, frame_width - img_w))
        y = max(0, min(y, frame_height - img_h))

        roi = frame[y:y+img_h, x:x+img_w]

        # Resize overlay if needed
        if roi.shape[0] != overlay_img.shape[0] or roi.shape[1] != overlay_img.shape[1]:
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

print("Animated overlay applied successfully.")
