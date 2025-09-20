# File: C:\New Project\viral-ai-content\create_video_pillow.py

import asyncio
import edge_tts
from moviepy.editor import *
from PIL import Image, ImageDraw
import numpy as np
import os
import time
from datetime import datetime

class VideoCreator:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 24
        self.voice = "en-IN-NeerjaNeural"
        
    async def generate_voice(self, text, output_file):
        """Generate voiceover using edge-tts with validation"""
        print(f"🎤 Generating voiceover for text: {text[:50]}...")  # Show first 50 chars
        
        # Validate text
        if not text or len(text.strip()) < 5:
            print("⚠️ Text too short, using default")
            text = "This is an AI generated video about trending topics. Follow for more updates!"
        
        # Delete old file if exists
        if os.path.exists(output_file):
            os.remove(output_file)
            
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)
            
            # Wait for file to be fully written
            time.sleep(2)  # Increased wait time
            
            # Verify file exists and has content
            if not os.path.exists(output_file):
                raise Exception("Voice file was not created")
                
            file_size = os.path.getsize(output_file)
            if file_size < 1000:  # Less than 1KB means something's wrong
                print(f"⚠️ Voice file too small: {file_size} bytes")
                # Try again with simpler text
                simple_text = "Testing voice generation. This is a test video."
                communicate = edge_tts.Communicate(simple_text, self.voice)
                await communicate.save(output_file)
                time.sleep(2)
                file_size = os.path.getsize(output_file)
                
            print(f"✅ Voice file created: {file_size} bytes")
            return output_file
            
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
            # Create a silent audio file as fallback
            return None
    
    async def create_video(self, script_data, output_path):
        """Create simple video from script"""
        print("🎬 Starting video creation...")
        print(f"📝 Script data keys: {script_data.keys()}")
        
        # Fix path handling
        if not os.path.dirname(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
        
        # Create directories if needed
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Use absolute path for voice file
        voice_file = os.path.join(os.getcwd(), f"temp_voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
        
        try:
            # Get voiceover text - try multiple sources
            voiceover_text = script_data.get('voiceover', '')
            
            # If no voiceover, try voiceover_script
            if not voiceover_text:
                voiceover_text = script_data.get('voiceover_script', '')
            
            # If still no voiceover, build from components
            if not voiceover_text:
                components = script_data.get('script_components', {})
                hook = components.get('hook', 'Breaking AI news!')
                points = components.get('main_points', ['Important update'])
                if isinstance(points, list):
                    points_text = ' '.join(points)
                else:
                    points_text = str(points)
                cta = components.get('cta', 'Follow for more!')
                voiceover_text = f"{hook} {points_text} {cta}"
            
            print(f"📢 Voiceover text length: {len(voiceover_text)} characters")
            
            # Generate voice
            voice_result = await self.generate_voice(voiceover_text, voice_file)
            
            # Check if we have audio
            audio = None
            duration = 10  # Default duration
            
            if voice_result and os.path.exists(voice_file):
                try:
                    audio = AudioFileClip(voice_file)
                    duration = audio.duration
                    print(f"📏 Audio duration: {duration:.1f} seconds")
                except Exception as e:
                    print(f"⚠️ Could not load audio: {e}")
                    audio = None
            else:
                print("⚠️ No audio file, creating silent video")
            
            # Create simple video
            background = ColorClip(
                size=(self.width, self.height), 
                color=(50, 20, 80),  # Purple
                duration=duration
            )
            
            # Add audio if available
            if audio:
                final_video = background.set_audio(audio)
            else:
                final_video = background
            
            # Export
            print("📹 Rendering video...")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac' if audio else None,
                preset='ultrafast',
                threads=2,
                logger=None
            )
            
            print(f"✅ Video saved to: {output_path}")
            return output_path
            
        finally:
            # Cleanup
            if os.path.exists(voice_file):
                try:
                    time.sleep(0.5)
                    os.remove(voice_file)
                except:
                    pass

# Test function
async def test_video():
    creator = VideoCreator()
    test_data = {
        "voiceover": "This is a test video creation. Testing the AI content automation system.",
        "video_details": {"title": "Test Video"},
        "script_components": {
            "hook": "Breaking news!",
            "main_points": ["Point 1", "Point 2"],
            "cta": "Follow for more!"
        }
    }
    output_file = "output/videos/test_output.mp4"
    await creator.create_video(test_data, output_file)
    print(f"Test complete! Check: {output_file}")

if __name__ == "__main__":
    asyncio.run(test_video())