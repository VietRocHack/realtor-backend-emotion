from flask import Flask
import os, dotenv
from services.pinata_service import PinataService
from services.emotion_service import EmotionService

app = Flask(__name__)
dotenv.load_dotenv()

# Initialize Pinata Services from environment variables
pinata_secret_key = os.getenv("PINATA_API_KEY")
pinata_jwt = os.getenv("PINATA_JWT")
pinata_gateway = os.getenv("PINATA_GATEWAY")
group_id = os.getenv("PINATA_GROUP_ID")

pinata_service = PinataService(pinata_secret_key, pinata_jwt, pinata_gateway)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/analyze/<cid>')
def analyze_from_cid(cid):
    # Get file from IPFS
    file_binary = pinata_service.get_file_public(cid)

    # Write file to local
    local_file_path = f"temp/{cid}.mp4"
    with open(local_file_path, "wb") as file:
        file.write(file_binary)
    
    emotions = EmotionService.analyze_dominant_emotion(local_file_path)
    print(emotions)
    # Analyze emotions from the video
    return {"results": emotions}, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0")