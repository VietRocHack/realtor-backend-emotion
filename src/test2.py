import time
from services.emotion_service import EmotionService
    
def emotion_test(file_path):
    start_time = time.time()
    with open(file_path, "rb") as f:
        video_binary_data = f.read()
    # Call the function with the binary data
    result = EmotionService.analyze_emotions_from_binary(video_binary_data, skip_frames=3)
    print(f"{file_path}: {result}")
    print(f"Time taken: {time.time() - start_time} seconds")

    # Save the video into a new file
    with open(f"./tests/output/output.mp4", "wb") as f:
        f.write(video_binary_data)
    return

emotion_test("./tests/happy.mp4")
emotion_test("./tests/sad.mp4")
# emotion_test("./tests/happy_compressed_2.mp4")
# emotion_test("./tests/sad_compressed_2.mp4")
