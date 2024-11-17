import av, io
from deepface import DeepFace
from collections import Counter
import numpy as np
import cv2

class EmotionService:
    def analyze_video_emotions(video_binary_data, skip_frames=4):
        """
        Analyzes emotions from a video binary stream.
        
        Args:
            video_binary_data (bytes): Binary data of the MP4 video.
            skip_frames (int): Process every nth frame.
            
        Returns:
            str: The most common emotion detected in the video.
        """
        # Open the binary stream with PyAV
        container = av.open(io.BytesIO(video_binary_data))
        
        emotion_counts = []
        frame_count = 0

        for frame in container.decode(video=0):  # Decode the first video stream
            if frame_count % 10 == 0:
                print(f"Processing frame {frame_count}...")
            
            if frame_count % skip_frames == 0:
                # Convert frame to a numpy array (DeepFace requires a numpy array)
                frame_array = frame.to_ndarray(format="bgr24")

                # Analyze emotions for the current frame
                analysis = DeepFace.analyze(frame_array, actions=['emotion'], enforce_detection=False)

                # Extract dominant emotion and store it
                dominant_emotion = analysis[0]['dominant_emotion']
                emotion_counts.append(dominant_emotion)

            frame_count += 1

        for counter in emotion_counts:
            print(counter)
        
        # Count the most frequent emotion from processed frames
        if emotion_counts:
            most_common_emotion = Counter(emotion_counts).most_common(1)[0][0]
            # print(f"Most common emotion in the video: {most_common_emotion}")
            return most_common_emotion
        else:
            # print("No emotions detected.")
            return None
        
    def analyze_emotions_from_binary(video_binary_data, skip_frames=4, display_result=True):
        """
        Analyzes emotions from a video binary stream using OpenCV and DeepFace.

        Args:
            video_binary_data (bytes): Binary data of the MP4 video.
            skip_frames (int): Process every nth frame (default: 4).
            display_result (bool): Whether to display the video with emotion overlay (default: True).

        Returns:
            str: The most common emotion detected in the video.
        """
        # Convert binary data to a temporary file-like object for OpenCV to read
        # Write binary data to a temporary file
        with open('temp_video.mp4', 'wb') as temp_video_file:
            temp_video_file.write(video_binary_data)
        
        # Open the temporary file with OpenCV
        video_stream = cv2.VideoCapture('temp_video.mp4')

        if not video_stream.isOpened():
            print("Error: Could not open video stream.")
            return None

        frame_count = 0
        emotion_counts = []
        output_frame = None

        while True:
            # Read the next frame from the video
            ret, frame = video_stream.read()

            # Break the loop if no frame is returned
            if not ret:
                break

            # Process only every nth frame
            if frame_count % skip_frames == 0:
                try:
                    # Analyze emotions for the current frame
                    analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

                    # Extract and store the dominant emotion
                    dominant_emotion = analysis[0]['dominant_emotion']
                    emotion_counts.append(dominant_emotion)

                    # Overlay text on the frame
                    text = f"Dominant Emotion: {dominant_emotion}"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, text, (10, 30), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

                    # Store the last frame with text
                    output_frame = frame

                    if display_result:
                        # Display the frame
                        cv2.imshow('Emotion Analysis', frame)

                        # Exit on 'q' key press
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                except Exception as e:
                    # Handle frames where DeepFace might fail
                    print(f"Error processing frame {frame_count}: {e}")

            frame_count += 1

        # Release the video stream
        video_stream.release()
        cv2.destroyAllWindows()

        # Aggregate and find the most common emotion
        if emotion_counts:
            top_two_emotions = Counter(emotion_counts).most_common(2)
            if top_two_emotions[0][0] == 'neutral':
                most_common_emotion = top_two_emotions[1][0]
            else:
                most_common_emotion = top_two_emotions[0][0]
            return most_common_emotion
        else:
            return "No emotions detected"

    def analyze_dominant_emotion(video_path):
        """
        Analyzes a video to determine the dominant emotion.
        
        Parameters:
            video_path (str): Path to the MP4 video file.
        
        Returns:
            str: The dominant emotion excluding "neutral".
        """
        # Open video file
        cap = cv2.VideoCapture(video_path)
        
        frame_skip = 1  # Analyze every frame
        total_analysis = []
        aggregate_count = 10 # Aggregate emotions every 10 frames
        emotions_count = Counter()
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Analyze every nth frame
            if frame_idx % frame_skip == 0:
                try:
                    # Analyze the frame with DeepFace
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    emotion = result[0]['dominant_emotion']
                    # print(emotion)
                    # if emotion != "neutral":
                    emotions_count[emotion] += 1
                except Exception as e:
                    print(f"Error processing frame {frame_idx}: {e}")

            frame_idx += 1

            if frame_idx % aggregate_count == 9:
                if emotions_count:
                    print(emotions_count)
                    dominant_emotion = emotions_count.most_common(1)[0]
                    if dominant_emotion[0] != "neutral":
                        total_analysis.append(dominant_emotion[0])
                    else:
                        if len(emotions_count) > 1:
                            secondary_emotion = emotions_count.most_common(2)[1]
                            neutral_reduced = dominant_emotion[1] // 3
                            print(dominant_emotion[1], secondary_emotion[1])
                            if neutral_reduced <= secondary_emotion[1]:
                                total_analysis.append(secondary_emotion[0])
                            else:
                                total_analysis.append(dominant_emotion[0])
                        else:
                            total_analysis.append(dominant_emotion[0])
                else:
                    total_analysis.append("none")
                emotions_count = Counter()

        cap.release()
        return total_analysis
        # # Get the most frequent non-neutral emotion
        # if emotions_count:
        #     dominant_emotion = emotions_count.most_common(1)[0][0]
        #     return dominant_emotion
        # else:
        #     return "No significant emotions detected"