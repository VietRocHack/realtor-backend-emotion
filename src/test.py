import cv2
from deepface import DeepFace
from collections import Counter

# Load the video
video_path = "./tests/happy.mp4"
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

frame_count = 0
emotion_counts = []

while True:
    # Read the next frame from the video
    ret, frame = cap.read()

    # Break the loop if the frame was not read properly
    if not ret:
        break

    # Process only every 4th frame (i.e., reduce to 15 fps for 60 fps video)
    if frame_count % 4 == 0:
        # Analyze emotions for the current frame
        analysis = DeepFace.analyze(frame, actions=['emotion'])

        # Extract dominant emotion and store it
        dominant_emotion = analysis[0]['dominant_emotion']
        emotion_counts.append(dominant_emotion)

    # Increment the frame counter
    frame_count += 1

# Count the most frequent emotion from processed frames
if emotion_counts:
    most_common_emotion = Counter(emotion_counts).most_common(1)[0][0]
    print(f"Most common emotion in the video: {most_common_emotion}")
else:
    print("No emotions detected.")

# Release video capture
cap.release()
