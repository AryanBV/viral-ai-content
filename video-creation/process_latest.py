# File: C:\New Project\viral-ai-content\video-creation\process_latest.py

import json
import asyncio
from create_video import VideoCreator
from datetime import datetime

async def process_latest_script():
    # Read the latest script from n8n output
    # (You'll need to save n8n output to a file or pass it directly)
    
    with open('data/processed/latest_script.json', 'r') as f:
        script_data = json.load(f)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/videos/video_{timestamp}.mp4"
    
    creator = VideoCreator()
    await creator.create_video(script_data, output_file)
    
    return output_file

if __name__ == "__main__":
    video_path = asyncio.run(process_latest_script())
    print(f"✅ Video created: {video_path}")