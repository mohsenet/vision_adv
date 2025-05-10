import cv2

# Input and output file paths
input_video = 'input.mp4'
output_video = 'output.mp4'

# Define multiple text overlays with timing and styling
text_events = [
    {
        "text": "Welcome!",
        "start_time": 1.0,
        "end_time": 3.0,
        "position": (380, 480),
        "font_color": (0, 0, 255),   # Red
        "font_scale": 1.5
    },
    {
        "text": "This is part one.",
        "start_time": 2.0,
        "end_time": 5.0,
        "position": (480, 380),
        "font_color": (255, 0, 0),   # Blue
        "font_scale": 1.0
    },
    {
        "text": "Now we are in part two.",
        "start_time": 6.0,
        "end_time": 9.0,
        "position": (700, 500),
        "font_color": (0, 255, 0),   # Green
        "font_scale": 1.0
    },
]

# Font settings
font = cv2.FONT_HERSHEY_SIMPLEX
thickness = 2
line_type = cv2.LINE_AA

# Open the video
cap = cv2.VideoCapture(input_video)

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

    # Loop through all text events and draw if active
    for event in text_events:
        if event["start_time"] <= current_time <= event["end_time"]:
            cv2.putText(
                frame,
                event["text"],
                event["position"],
                font,
                event["font_scale"],
                event["font_color"],
                thickness,
                line_type
            )

    # Write the frame to output video
    out.write(frame)
    frame_idx += 1

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print("Multiple texts added successfully.")
