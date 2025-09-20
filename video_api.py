# File: C:\New Project\viral-ai-content\video_api.py
"""
Fixed Flask API Server for Video Creation
Handles data properly from n8n workflow
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import asyncio
import os
import sys
from datetime import datetime
import logging
import traceback

# Add project to path
sys.path.append(r"C:\New Project\viral-ai-content")

# Import video creators
from create_video_enhanced import EnhancedVideoCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r"C:\New Project\viral-ai-content\api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for n8n

@app.route('/create-video', methods=['POST'])
def create_video():
    """Main endpoint for video creation"""
    try:
        # Log incoming request
        logger.info("=" * 50)
        logger.info("NEW VIDEO REQUEST RECEIVED")
        
        # Get and log raw data
        raw_data = request.get_json()
        logger.info(f"Raw data type: {type(raw_data)}")
        logger.info(f"Raw data keys: {raw_data.keys() if isinstance(raw_data, dict) else 'Not a dict'}")
        
        # Debug: Save raw data for inspection
        debug_file = r"C:\New Project\viral-ai-content\data\processed\debug_last_request.json"
        os.makedirs(os.path.dirname(debug_file), exist_ok=True)
        with open(debug_file, 'w') as f:
            json.dump(raw_data, f, indent=2)
        logger.info(f"Debug data saved to: {debug_file}")
        
        # Parse script data properly
        script_data = parse_script_data(raw_data)
        
        # Validate required fields
        if not validate_script_data(script_data):
            logger.error("Script validation failed")
            return jsonify({
                "success": False,
                "error": "Invalid script data - missing required fields"
            }), 400
        
        # Log parsed data
        logger.info(f"Script ID: {script_data.get('id', 'unknown')}")
        logger.info(f"Title: {script_data['video_details']['title']}")
        logger.info(f"Voiceover length: {len(script_data['voiceover'])} chars")
        logger.info(f"Main points: {len(script_data['script_components']['main_points'])}")
        
        # Create output directory
        output_dir = r"C:\New Project\viral-ai-content\output\videos"
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize video creator
        creator = EnhancedVideoCreator()
        
        # Create event loop for async functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create video in all formats
        logger.info("Starting video creation...")
        results = loop.run_until_complete(
            creator.create_all_formats(script_data)
        )
        loop.close()
        
        # Prepare response
        response = {
            "success": True,
            "message": "Videos created successfully!",
            "videos": {}
        }
        
        for format_name, result in results.items():
            response["videos"][format_name] = {
                "path": result['path'],
                "thumbnail": result['path'].replace('.mp4', '_thumb.jpg'),
                "quality_score": result['report']['predicted_score']
            }
            logger.info(f"Created {format_name}: {result['path']}")
        
        # Save successful script for reference
        script_file = os.path.join(
            r"C:\New Project\viral-ai-content\data\processed",
            f"script_{script_data.get('id', datetime.now().strftime('%Y%m%d_%H%M%S'))}.json"
        )
        with open(script_file, 'w') as f:
            json.dump(script_data, f, indent=2)
        
        logger.info("✅ Video creation successful!")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ Error in video creation: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

def parse_script_data(raw_data):
    """Parse and structure script data from various formats"""
    
    # If data is already properly structured
    if all(key in raw_data for key in ['video_details', 'script_components', 'voiceover']):
        return raw_data
    
    # If data is wrapped in another object
    if 'json' in raw_data:
        return parse_script_data(raw_data['json'])
    
    # If data is in array format from n8n
    if '0' in raw_data:
        return parse_script_data(raw_data['0'])
    
    # Try to extract from nested structure
    if 'content' in raw_data:
        try:
            content = raw_data['content']
            if isinstance(content, str):
                return json.loads(content)
            return parse_script_data(content)
        except:
            pass
    
    # Build structure from available fields
    script_data = {
        'id': raw_data.get('id', f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
        'timestamp': raw_data.get('timestamp', datetime.now().isoformat()),
        'video_details': {},
        'script_components': {},
        'voiceover': '',
        'hashtags': []
    }
    
    # Extract video details
    if 'video_details' in raw_data:
        script_data['video_details'] = raw_data['video_details']
    elif 'title' in raw_data:
        script_data['video_details']['title'] = raw_data['title']
    else:
        script_data['video_details']['title'] = "AI Update"
    
    # Extract script components
    if 'script_components' in raw_data:
        script_data['script_components'] = raw_data['script_components']
    else:
        script_data['script_components'] = {
            'hook': raw_data.get('hook', ''),
            'main_points': raw_data.get('main_points', []),
            'cta': raw_data.get('cta', '')
        }
    
    # Extract voiceover
    if 'voiceover' in raw_data:
        script_data['voiceover'] = raw_data['voiceover']
    else:
        # Build from components
        components = script_data['script_components']
        voiceover_parts = [
            components.get('hook', ''),
            ' '.join(components.get('main_points', [])),
            components.get('cta', '')
        ]
        script_data['voiceover'] = ' '.join(filter(None, voiceover_parts))
    
    # Extract hashtags
    script_data['hashtags'] = raw_data.get('hashtags', ['#AI', '#Tech', '#India'])
    
    return script_data

def validate_script_data(script_data):
    """Validate that script has all required fields"""
    
    # Check main structure
    required_keys = ['video_details', 'script_components', 'voiceover']
    if not all(key in script_data for key in required_keys):
        logger.error(f"Missing required keys. Found: {script_data.keys()}")
        return False
    
    # Check video details
    if not script_data['video_details'].get('title'):
        logger.error("Missing video title")
        return False
    
    # Check script components
    components = script_data['script_components']
    if not components.get('hook'):
        logger.error("Missing hook")
        return False
    
    if not components.get('main_points'):
        logger.error("Missing main points")
        return False
    
    if not components.get('cta'):
        logger.error("Missing CTA")
        return False
    
    # Check voiceover
    if not script_data['voiceover'] or len(script_data['voiceover']) < 50:
        logger.error(f"Voiceover too short: {len(script_data.get('voiceover', ''))} chars")
        return False
    
    return True

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify API is running"""
    return jsonify({
        "status": "✅ Video API is running!",
        "version": "2.0",
        "endpoints": [
            "/test - This endpoint",
            "/create-video - Create video from script (POST)",
            "/health - Health check"
        ],
        "project_path": r"C:\New Project\viral-ai-content",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    
    # Check if required directories exist
    checks = {
        "api": "running",
        "output_dir": os.path.exists(r"C:\New Project\viral-ai-content\output\videos"),
        "data_dir": os.path.exists(r"C:\New Project\viral-ai-content\data"),
        "ffmpeg": os.system("ffmpeg -version > nul 2>&1") == 0
    }
    
    all_healthy = all(checks.values())
    
    return jsonify({
        "healthy": all_healthy,
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }), 200 if all_healthy else 503

@app.route('/test-video', methods=['POST'])
def test_video():
    """Create a test video with sample data"""
    
    sample_script = {
        "id": "test_" + datetime.now().strftime('%Y%m%d_%H%M%S'),
        "video_details": {
            "title": "Test: AI News India"
        },
        "script_components": {
            "hook": "Breaking: Major AI announcement from India!",
            "main_points": [
                "Indian AI startups raise $1 billion",
                "New government AI policy launched",
                "Tech giants expand in Bangalore"
            ],
            "cta": "Follow for more AI updates!"
        },
        "voiceover": """Breaking: Major AI announcement from India! 
        Three things you need to know right now. First, Indian AI startups 
        have raised over 1 billion dollars in funding. Second, the government 
        just launched a new AI policy for digital transformation. Third, 
        major tech giants are expanding their AI centers in Bangalore. 
        This is huge for India's tech future. Follow for more AI updates!""",
        "hashtags": ["#AIIndia", "#TechNews", "#Startups"]
    }
    
    # Use provided data or sample
    script_data = request.get_json() if request.is_json else sample_script
    
    # Create video
    request.json = script_data
    return create_video()

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(encoding='utf-8-sig')
    print("=" * 50)
    print("🚀 VIRAL AI VIDEO API SERVER")
    print("=" * 50)
    print("📍 Running at: http://localhost:5000")
    print("📂 Project: C:\\New Project\\viral-ai-content")
    print("🔧 Endpoints:")
    print("   - GET  /test         - Test API")
    print("   - GET  /health       - Health check")
    print("   - POST /create-video - Create video")
    print("   - POST /test-video   - Test with sample")
    print("=" * 50)
    print("📝 Logs saved to: C:\\New Project\\viral-ai-content\\api.log")
    print("🎬 Videos output to: C:\\New Project\\viral-ai-content\\output\\videos")
    print("=" * 50)
    print("\n⏳ Starting server...\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)