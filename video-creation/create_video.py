# File: C:\New Project\viral-ai-content\video-creation\create_video.py

import json
import asyncio
from moviepy.editor import *
from moviepy.video.fx.all import *
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

class VideoCreator:
    def __init__(self):
        self.width = 1080  # Instagram Reels/YouTube Shorts
        self.height = 1920
        self.fps = 30
        self.font_size = 60
        self.voice = "en-IN-NeerjaNeural"
        
    async def generate_voice(self, text, output_file):
        """Generate voiceover using edge-tts"""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)
        return output_file
    
    def create_text_clip(self, text, duration, position='center'):
        """Create text overlay using PIL instead of MoviePy TextClip"""
        # Create text image using PIL
        text_img = self.create_text_image(text, self.font_size)

        # Create ImageClip from PIL image
        txt_clip = ImageClip(text_img).set_duration(duration)

        # Position the text
        if position == 'top':
            txt_clip = txt_clip.set_position(('center', 100))
        elif position == 'bottom':
            txt_clip = txt_clip.set_position(('center', self.height - 200))
        else:
            txt_clip = txt_clip.set_position('center')

        # Add fade in/out effect
        txt_clip = txt_clip.fadein(0.3).fadeout(0.3)
        return txt_clip

    def create_text_image(self, text, font_size):
        """Create text image using PIL"""
        # Calculate text size and create image
        width = int(self.width * 0.9)

        # Create a temporary image to measure text
        temp_img = Image.new('RGBA', (width, 100))
        temp_draw = ImageDraw.Draw(temp_img)

        # Try to use default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Word wrap text
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= width - 40:  # 20px margin each side
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        if current_line:
            lines.append(' '.join(current_line))

        # Calculate total height needed
        line_height = font_size + 10
        total_height = len(lines) * line_height + 40  # 20px margin top/bottom

        # Create final image
        img = Image.new('RGBA', (width, total_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw text with stroke effect
        y_offset = 20
        for line in lines:
            # Get text position for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_offset = (width - text_width) // 2

            # Draw stroke (black outline)
            stroke_width = 2
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x_offset + dx, y_offset + dy), line, font=font, fill=(0, 0, 0, 255))

            # Draw main text (white)
            draw.text((x_offset, y_offset), line, font=font, fill=(255, 255, 255, 255))
            y_offset += line_height

        return np.array(img)
    
    def create_background(self, duration):
        """Create animated gradient background"""
        # Create a simple gradient background
        background = ColorClip(
            size=(self.width, self.height),
            color=(20, 20, 30),  # Dark blue-gray
            duration=duration
        )
        
        # Add subtle gradient overlay
        gradient = ImageClip(
            self.create_gradient_image(),
            duration=duration
        ).set_opacity(0.8)
        
        return CompositeVideoClip([background, gradient])
    
    def create_gradient_image(self):
        """Create gradient image for background"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Create vertical gradient (AI/tech themed colors)
        for i in range(self.height):
            color_value = int(255 * (i / self.height) * 0.3)
            color = (color_value, 0, color_value + 50)  # Purple gradient
            draw.rectangle([(0, i), (self.width, i + 1)], fill=color)
        
        return np.array(img)
    
    async def create_video(self, script_data, output_path):
        """Main function to create video from script"""
        print("🎬 Starting video creation...")
        
        # Generate voiceover
        voice_file = "temp_voice.mp3"
        await self.generate_voice(script_data['voiceover'], voice_file)
        print("✅ Voiceover generated")
        
        # Load audio and get duration
        audio = AudioFileClip(voice_file)
        duration = audio.duration
        
        # Create background
        background = self.create_background(duration)
        
        # Create text overlays for different segments
        clips = [background]
        
        # Hook (0-5 seconds)
        hook_clip = self.create_text_clip(
            script_data['script_components']['hook'],
            min(5, duration),
            'center'
        ).set_start(0)
        clips.append(hook_clip)
        
        # Main points (5 seconds onwards)
        points = script_data['script_components']['main_points']
        point_duration = (duration - 10) / len(points)  # Leave 5s for hook, 5s for CTA
        
        for i, point in enumerate(points):
            start_time = 5 + (i * point_duration)
            point_clip = self.create_text_clip(
                point,
                point_duration,
                'center'
            ).set_start(start_time)
            clips.append(point_clip)
        
        # CTA (last 5 seconds)
        cta_clip = self.create_text_clip(
            script_data['script_components']['cta'],
            5,
            'bottom'
        ).set_start(duration - 5)
        clips.append(cta_clip)
        
        # Title overlay (throughout video)
        title_img = self.create_text_image(script_data['video_details']['title'], 40)
        title_clip = ImageClip(title_img).set_duration(duration).set_position(('center', 50)).set_opacity(0.8)
        clips.append(title_clip)
        
        # Combine all clips
        final_video = CompositeVideoClip(clips)
        final_video = final_video.set_audio(audio)
        
        # Export video
        print("📹 Rendering video...")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium'
        )
        
        # Cleanup
        os.remove(voice_file)
        print(f"✅ Video saved to: {output_path}")
        
        return output_path

# Test function
async def test_with_sample():
    # Sample script data (use your actual generated script)
    script_data = {
        "video_details": {
            "title": "AI News Update"
        },
        "script_components": {
            "hook": "Breaking: Major AI announcement!",
            "main_points": [
                "Point 1: Something important",
                "Point 2: Another key fact",
                "Point 3: Final insight"
            ],
            "cta": "Follow for more AI updates!"
        },
        "voiceover": "Breaking: Major AI announcement! Here are three things you need to know. First, something important. Second, another key fact. Finally, this crucial insight. Follow for more AI updates!"
    }
    
    creator = VideoCreator()
    output = await creator.create_video(
        script_data,
        "C:\\New Project\\viral-ai-content\\output\\videos\\test_video.mp4"
    )
    print(f"Test video created: {output}")

if __name__ == "__main__":
    asyncio.run(test_with_sample())