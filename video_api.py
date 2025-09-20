# File: C:\New Project\viral-ai-content\video_api.py

from flask import Flask, request, jsonify
import json
import asyncio
from datetime import datetime
import os
import sys

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your video creator
from create_video_pillow import VideoCreator

app = Flask(__name__)

@app.route('/create-video', methods=['POST'])
def create_video():
    try:
        # Get script from n8n
        script_data = request.json
        
        # DEBUG: Print the raw received data
        print("=" * 50)
        print("RAW DATA FROM n8n:")
        print(json.dumps(script_data, indent=2))
        print("=" * 50)
        
        # If data is wrapped, unwrap it
        if 'content' in script_data:
            # Data might be in 'content' field
            actual_data = json.loads(script_data['content'])
            script_data = actual_data
        elif '0' in script_data:
            # Data might be indexed
            script_data = script_data['0']
        
        print(f"Processed script ID: {script_data.get('id', 'unknown')}")
        
        # Ensure required fields exist
        if 'video_details' not in script_data:
            script_data['video_details'] = {"title": "AI News Update"}
        if 'voiceover' not in script_data:
            # Create voiceover from components
            components = script_data.get('script_components', {})
            script_data['voiceover'] = f"{components.get('hook', '')} {' '.join(components.get('main_points', []))} {components.get('cta', '')}"
        
        # Generate video filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"C:\\New Project\\viral-ai-content\\output\\videos\\video_{timestamp}.mp4"
        
        # Create directories
        os.makedirs("C:\\New Project\\viral-ai-content\\output\\videos", exist_ok=True)
        
        # Create video
        print("Creating video...")
        creator = VideoCreator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        video_path = loop.run_until_complete(
            creator.create_video(script_data, output_path)
        )
        
        print(f"✅ Video created: {video_path}")
        
        return jsonify({
            "success": True, 
            "video_path": video_path,
            "message": "Video created successfully!"
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "API is working!"})

if __name__ == '__main__':
    print("🚀 Video API running at http://localhost:5000")
    print("📝 Test at: http://localhost:5000/test")
    app.run(host='0.0.0.0', port=5000)