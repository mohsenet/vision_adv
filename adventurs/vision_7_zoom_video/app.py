import cv2
import numpy as np
import subprocess
import tempfile
import os

def apply_zoom_with_audio_and_coordinates(
        input_path, 
        output_path, 
        zoom_start_time, 
        zoom_duration, 
        hold_duration, 
        zoom_factor,
        zoom_x,  # X coordinate (0-1, left to right)
        zoom_y   # Y coordinate (0-1, top to bottom)
    ):
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    # Open video
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Convert relative coordinates to absolute pixels
    target_x = int(zoom_x * width)
    target_y = int(zoom_y * height)
    
    # Calculate frame numbers
    zoom_start_frame = int(zoom_start_time * fps)
    zoom_in_end_frame = zoom_start_frame + int(zoom_duration * fps)
    hold_end_frame = zoom_in_end_frame + int(hold_duration * fps)
    zoom_out_end_frame = hold_end_frame + int(zoom_duration * fps)
    
    # Process frames
    current_frame = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if current_frame < zoom_start_frame:
            processed_frame = frame
        elif zoom_start_frame <= current_frame < zoom_in_end_frame:
            progress = (current_frame - zoom_start_frame) / (zoom_in_end_frame - zoom_start_frame)
            current_zoom = 1 + (zoom_factor - 1) * progress
            processed_frame = apply_zoom(frame, current_zoom, target_x, target_y, width, height)
        elif zoom_in_end_frame <= current_frame < hold_end_frame:
            processed_frame = apply_zoom(frame, zoom_factor, target_x, target_y, width, height)
        elif hold_end_frame <= current_frame < zoom_out_end_frame:
            progress = (current_frame - hold_end_frame) / (zoom_out_end_frame - hold_end_frame)
            current_zoom = zoom_factor - (zoom_factor - 1) * progress
            processed_frame = apply_zoom(frame, current_zoom, target_x, target_y, width, height)
        else:
            processed_frame = frame
        
        cv2.imwrite(f"{temp_dir}/frame_{current_frame:04d}.png", processed_frame)
        current_frame += 1
    
    cap.release()
    
    # Handle audio
    subprocess.run([
        'ffmpeg', '-i', input_path, '-vn', '-acodec', 'copy', 
        f'{temp_dir}/audio.aac'
    ], check=True)
    
    # Combine video and audio
    subprocess.run([
        'ffmpeg', '-framerate', str(fps), '-i', f'{temp_dir}/frame_%04d.png',
        '-i', f'{temp_dir}/audio.aac', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-shortest', output_path
    ], check=True)
    
    # Cleanup
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)

def apply_zoom(frame, zoom_factor, target_x, target_y, frame_width, frame_height):
    """Zoom towards specific coordinates"""
    # Calculate crop size
    crop_width = int(frame_width / zoom_factor)
    crop_height = int(frame_height / zoom_factor)
    
    # Calculate crop area (ensure it stays within frame bounds)
    x1 = max(0, target_x - crop_width // 2)
    y1 = max(0, target_y - crop_height // 2)
    
    # Adjust if crop would go beyond right/bottom edges
    if x1 + crop_width > frame_width:
        x1 = frame_width - crop_width
    if y1 + crop_height > frame_height:
        y1 = frame_height - crop_height
    
    # Crop and resize
    cropped = frame[y1:y1+crop_height, x1:x1+crop_width]
    return cv2.resize(cropped, (frame_width, frame_height), interpolation=cv2.INTER_LINEAR)

# Example usage - zoom to point at 30% from left, 70% from top
apply_zoom_with_audio_and_coordinates(
    input_path="input.mp4",
    output_path="output.mp4",
    zoom_start_time=10,
    zoom_duration=2,
    hold_duration=5,
    zoom_factor=2.0,  # 2x zoom
    zoom_x=0.3,       # 30% from left
    zoom_y=0.7        # 70% from top
)
