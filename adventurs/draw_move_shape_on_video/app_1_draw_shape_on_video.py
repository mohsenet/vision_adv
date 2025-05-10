import cv2

# Input and output file paths
input_video = 'input.mp4'
output_video = 'output.mp4'

# Define multiple shape overlays with timing and styling
shape_events = [
    {
        "type": "rectangle",
        "start_time": 1.0,
        "end_time": 4.0,
        "start_point": (100, 100),
        "end_point": (300, 300),
        "color": (0, 255, 0),     # Green
        "thickness": 2
    },
    {
        "type": "circle",
        "start_time": 2.0,
        "end_time": 6.0,
        "center": (400, 200),
        "radius": 50,
        "color": (255, 0, 0),     # Blue
        "thickness": 1           # Negative thickness fills the circle
    },
    {
        "type": "line",
        "start_time": 5.0,
        "end_time": 8.0,
        "start_point": (100, 480),
        "end_point": (640, 480),
        "color": (0, 0, 255),     # Red
        "thickness": 3
    }
]

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

    # Loop through all shape events and draw if active
    for event in shape_events:
        if event["start_time"] <= current_time <= event["end_time"]:
            shape_type = event["type"]
            if shape_type == "rectangle":
                cv2.rectangle(
                    frame,
                    event["start_point"],
                    event["end_point"],
                    event["color"],
                    event["thickness"]
                )
            elif shape_type == "circle":
                cv2.circle(
                    frame,
                    event["center"],
                    event["radius"],
                    event["color"],
                    event["thickness"]
                )
            elif shape_type == "line":
                cv2.line(
                    frame,
                    event["start_point"],
                    event["end_point"],
                    event["color"],
                    event["thickness"]
                )

    # Write the frame to output video
    out.write(frame)
    frame_idx += 1

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print("Shapes added successfully.")
