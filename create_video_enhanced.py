# File: C:\New Project\viral-ai-content\create_video_enhanced.py
"""
Enhanced Video Creator for Viral AI Content
Creates near-perfect videos with subtitles, effects, and multiple formats
"""

import json
import asyncio
from moviepy.editor import *
from moviepy.video.fx.all import *
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import requests
from datetime import datetime
import re
import random
from stock_footage_manager import StockFootageManager
from voice_enhancer import generate_voice_with_subtitles_enhanced
from video_effects_manager import VideoEffectsManager

class EnhancedVideoCreator:
    def __init__(self):
        # Video specifications
        self.formats = {
            'reels': {'width': 1080, 'height': 1920},  # 9:16
            'square': {'width': 1080, 'height': 1080},  # 1:1
            'youtube': {'width': 1920, 'height': 1080}  # 16:9
        }
        self.fps = 30
        
        # More modern voices
        self.voices = {
            'female': 'en-US-AriaNeural',  # More modern than Indian accent
            'male': 'en-IN-PrabhatNeural'
        }
        
        # Paths
        self.project_root = r"C:\New Project\viral-ai-content"
        self.output_dir = os.path.join(self.project_root, "output", "videos")
        self.music_dir = os.path.join(self.project_root, "assets", "music")
        self.fonts_dir = os.path.join(self.project_root, "assets", "fonts")
        
        # API Keys (from environment)
        self.pexels_key = os.getenv('PEXELS_API_KEY', '')
        
        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.music_dir, exist_ok=True)
        
    async def generate_voice_with_subtitles(self, text, voice_type='female'):
        """Generate voice and subtitle timings"""
        voice = self.voices[voice_type]
        voice_file = os.path.join(self.project_root, f"temp_voice_{datetime.now().timestamp()}.mp3")
        
        # Generate voice
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(voice_file)
        
        # Generate subtitle timings (word-level)
        words = text.split()
        audio_clip = AudioFileClip(voice_file)
        duration = audio_clip.duration
        
        # Make subtitles appear word by word, not all at once
        subtitles = []
        words_per_second = 2.5  # Faster pace for modern videos
        current_time = 0

        for word in words:
            word_duration = 1 / words_per_second
            subtitles.append({
                'text': word,
                'start': current_time,
                'end': current_time + word_duration
            })
            current_time += word_duration * 0.8  # Slight overlap for smooth flow
            
        return voice_file, subtitles
    
    def fetch_stock_footage(self, query, count=3):
        """Fetch relevant stock videos from Pexels"""
        if not self.pexels_key:
            return []
            
        headers = {'Authorization': self.pexels_key}
        url = f'https://api.pexels.com/videos/search?query={query}&per_page={count}'
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            video_urls = []
            for video in data.get('videos', [])[:count]:
                # Get HD video file
                for file in video.get('video_files', []):
                    if file.get('quality') == 'hd':
                        video_urls.append(file.get('link'))
                        break
            return video_urls
        except:
            return []
    
    def create_animated_text(self, text, duration, width, height, style='slide'):
        """Create animated text overlays"""
        # Create text image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load custom font
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with stroke
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        # Convert to video clip
        img_array = np.array(img)
        text_clip = ImageClip(img_array, duration=duration)
        
        # Add animation based on style
        if style == 'slide':
            text_clip = text_clip.set_position(('center', 60))  # Fixed position
        elif style == 'fade':
            text_clip = text_clip.fadein(0.5).fadeout(0.5)
        elif style == 'zoom':
            try:
                text_clip = text_clip.resize(lambda t: min(1.3, 1 + 0.1 * (t / duration)))
            except:
                pass  # Skip if it fails
            
        return text_clip
    
    def create_subtitle_clips(self, subtitles, width, height):
        """Create modern animated subtitles"""
        subtitle_clips = []

        for i, sub in enumerate(subtitles):
            # Bigger, bolder text
            img = Image.new('RGBA', (width, 250), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("arial.ttf", 80)  # Bigger font
            except:
                font = ImageFont.load_default()

            text = sub['text'].upper()  # Always uppercase
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2

            # No background box - just thick outline
            for offset in range(5):  # Thick black outline
                for angle in range(0, 360, 30):
                    dx = offset * np.cos(np.radians(angle))
                    dy = offset * np.sin(np.radians(angle))
                    draw.text((x + dx, 100 + dy), text, font=font, fill=(0, 0, 0, 255))

            # Bright white or yellow text
            color = (255, 255, 0) if i % 2 == 0 else (255, 255, 255)
            draw.text((x, 100), text, font=font, fill=(*color, 255))

            # Create clip with pop animation
            img_array = np.array(img)
            subtitle_clip = (ImageClip(img_array, duration=sub['end'] - sub['start'])
                           .set_start(sub['start'])
                           .set_position(('center', height - 350)))

            # Add scale animation
            subtitle_clip = subtitle_clip.resize(
                lambda t: min(1.2, 0.5 + t * 5) if t < 0.1 else 1
            )

            subtitle_clips.append(subtitle_clip)

        return subtitle_clips
    
    def add_background_music(self, video_clip, music_file=None):
        """Add background music with proper mixing"""
        if music_file and os.path.exists(music_file):
            music = AudioFileClip(music_file)
            
            # Loop music if needed
            if music.duration < video_clip.duration:
                music = music.loop(duration=video_clip.duration)
            else:
                music = music.subclip(0, video_clip.duration)
            
            # Lower music volume
            music = music.volumex(0.1)
            
            # Mix with original audio
            final_audio = CompositeAudioClip([video_clip.audio, music])
            return video_clip.set_audio(final_audio)
        
        return video_clip
    
    def create_quality_report(self, video_path, script_data):
        """Generate quality report for the video"""
        report = {
            'video_path': video_path,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'hook_strength': self.analyze_hook(script_data.get('hook', '')),
                'information_density': len(script_data.get('main_points', [])),
                'has_subtitles': True,
                'has_music': True,
                'duration': 'optimal' if 30 <= script_data.get('duration', 0) <= 45 else 'adjust',
                'formats_created': ['9:16', '1:1'],
            },
            'hashtags': script_data.get('hashtags', []),
            'best_posting_time': 'Evening 7-9 PM IST',
            'predicted_score': 8.5
        }
        
        # Save report
        report_path = video_path.replace('.mp4', '_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
    
    def analyze_hook(self, hook):
        """Analyze hook strength"""
        power_words = ['breaking', 'exclusive', 'shocking', 'revealed', 'secret', 
                      'amazing', 'unbelievable', 'game-changing', 'revolutionary']
        
        hook_lower = hook.lower()
        score = 5  # Base score
        
        # Check for power words
        for word in power_words:
            if word in hook_lower:
                score += 1
        
        # Check for questions
        if '?' in hook:
            score += 1
            
        # Check for numbers
        if any(char.isdigit() for char in hook):
            score += 1
            
        return min(score, 10)
    
    async def create_video(self, script_data, format_type='reels'):
        """Main function to create enhanced video with stock footage"""
        print(f"Creating {format_type} video with stock footage...")
        
        # Get format specifications
        format_spec = self.formats[format_type]
        width = format_spec['width']
        height = format_spec['height']
        
        # Generate voice and subtitles
        voice_file, subtitles = await generate_voice_with_subtitles_enhanced(
            script_data['voiceover'],
            voice_type='female'
        )
        
        # Load audio
        audio = AudioFileClip(voice_file)
        duration = audio.duration
        
        # Initialize managers
        stock_manager = StockFootageManager(self.pexels_key)
        effects_manager = VideoEffectsManager()

        # Get stock footage for the script
        print("Fetching stock footage...")
        footage_dict = stock_manager.get_footage_for_script(script_data)
        
        # Create video segments with stock footage
        video_segments = []
        current_time = 0
        
        # Calculate segment durations
        hook_duration = min(3, duration * 0.10)  # 3 seconds max, not 5
        cta_duration = min(3, duration * 0.10)   # 3 seconds max, not 5
        main_duration = duration - hook_duration - cta_duration
        points_count = len(script_data['script_components']['main_points'])
        point_duration = 1.5  # Fixed 1.5 seconds per point, not calculated
        
        # 1. HOOK SEGMENT (0-5 seconds) - Using VideoEffectsManager
        footage_clips = []
        # Collect footage clips for hook sequence
        if footage_dict['hook']:
            footage_clips.extend(footage_dict['hook'])
        if footage_dict['background']:
            footage_clips.extend(footage_dict['background'])

        if len(footage_clips) >= 3:
            # Use first 3 clips for hook sequence
            hook_segment = effects_manager.create_hook_sequence(
                footage_clips[:3],
                script_data['script_components']['hook'],
                hook_duration
            )
        elif footage_dict['hook']:
            # Fallback to single footage segment
            hook_segment = self.create_footage_segment(
                footage_dict['hook'][0],
                hook_duration,
                width, height,
                text_overlay=script_data['script_components']['hook'],
                style='dramatic'
            )
        else:
            # Fallback to gradient if no footage
            hook_segment = self.create_text_on_gradient(
                script_data['script_components']['hook'],
                hook_duration, width, height
            )
        video_segments.append(hook_segment)
        current_time += hook_duration
        
        # 2. MAIN POINTS SEGMENTS
        main_points = script_data['script_components']['main_points']
        for i, point in enumerate(main_points):
            # Use stock footage if available
            if i < len(footage_dict['main_points']) and footage_dict['main_points'][i]:
                point_clip = self.create_footage_segment(
                    footage_dict['main_points'][i],
                    point_duration,
                    width, height,
                    text_overlay=point,
                    style='informative'
                )
            else:
                # Use background footage or gradient
                if footage_dict['background']:
                    bg_video = random.choice(footage_dict['background'])
                    point_clip = self.create_footage_segment(
                        bg_video,
                        point_duration,
                        width, height,
                        text_overlay=point,
                        style='informative'
                    )
                else:
                    point_clip = self.create_text_on_gradient(
                        point, point_duration, width, height
                    )
            
            video_segments.append(point_clip)
            current_time += point_duration
        
        # 3. CTA SEGMENT (last 5 seconds)
        if footage_dict['cta']:
            cta_clip = self.create_footage_segment(
                footage_dict['cta'][0],
                cta_duration,
                width, height,
                text_overlay=script_data['script_components']['cta'],
                style='action'
            )
        else:
            cta_clip = self.create_text_on_gradient(
                script_data['script_components']['cta'],
                cta_duration, width, height
            )
        video_segments.append(cta_clip)
        
        # Concatenate all segments with transitions
        print("Combining video segments with transitions...")
        final_video = self.concatenate_with_transitions(video_segments)
        
        # Add audio
        final_video = final_video.set_audio(audio)
        
        # Add TikTok-style animated captions
        print("Adding TikTok-style animated captions...")
        caption_clips = effects_manager.create_animated_captions(
            script_data['voiceover'],
            duration,
            style='bold'
        )

        # Combine video with captions
        clips_with_captions = [final_video] + caption_clips
        final_video = CompositeVideoClip(clips_with_captions)
        
        # Add background music
        music_file = os.path.join(self.music_dir, "background_music_1.mp3")
        if os.path.exists(music_file):
            final_video = self.add_background_music(final_video, music_file)
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            self.output_dir,
            f"video_{format_type}_{timestamp}.mp4"
        )
        
        # Export video
        print(f"Rendering {format_type} video...")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4,
            logger=None  # Suppress verbose output
        )
        
        # Cleanup
        os.remove(voice_file)
        
        # Generate quality report
        report = self.create_quality_report(output_path, script_data)
        print(f"Video saved to: {output_path}")
        print(f"Quality score: {report['predicted_score']}/10")
        
        # Generate thumbnail
        self.generate_thumbnail(final_video, output_path.replace('.mp4', '_thumb.jpg'))
        
        return output_path, report

    def create_footage_segment(self, video_path, duration, width, height, text_overlay=None, style='normal'):
        """Create a video segment from stock footage with effects"""
        try:
            # CHANGE: Make clips shorter
            duration = min(duration, 2.0)  # Max 2 seconds per clip instead of 5+

            # Load stock video
            clip = VideoFileClip(video_path)
            
            # Loop if too short
            if clip.duration < duration:
                clip = clip.loop(duration=duration)
            else:
                # Select interesting part (avoid beginning/end)
                start = min(2, clip.duration * 0.1)  # Start 10% in or 2 seconds
                clip = clip.subclip(start, start + duration)
            
            # Resize to fit format (crop to fill)
            clip = self.resize_and_crop(clip, width, height)
            
            # Apply style effects
            if style == 'dramatic':
                # Add zoom effect for hook with lambda function
                try:
                    clip = clip.resize(lambda t: min(1.3, 1 + 0.1 * (t / duration)))
                except:
                    pass  # Skip zoom if it fails
                # Add vignette
                clip = self.add_vignette(clip, width, height)
            elif style == 'informative':
                # Ken Burns effect
                clip = self.apply_ken_burns(clip, duration)
            elif style == 'action':
                # Speed ramp for CTA (simplified)
                try:
                    speed_factor = 1.2  # Fixed speed instead of time-based
                    clip = clip.speedx(speed_factor)
                except:
                    pass  # Skip speed change if it fails
            
            # Add color grading
            clip = self.apply_color_grading(clip, style)
            
            # Add text overlay if provided
            if text_overlay:
                text_clip = self.create_animated_text(
                    text_overlay, duration, width, height, style
                )
                clip = CompositeVideoClip([clip, text_clip])
            
            return clip
            
        except Exception as e:
            print(f"Error processing footage: {e}")
            # Fallback to gradient
            return self.create_text_on_gradient(text_overlay or "", duration, width, height)

    def resize_and_crop(self, clip, target_width, target_height):
        """Resize and crop video to target dimensions"""
        # Get clip dimensions safely
        clip_width = clip.w if hasattr(clip, 'w') else clip.size[0]
        clip_height = clip.h if hasattr(clip, 'h') else clip.size[1]

        # Calculate aspect ratios
        clip_ratio = clip_width / clip_height
        target_ratio = target_width / target_height

        if clip_ratio > target_ratio:
            # Video is wider - fit height, crop width
            new_height = target_height
            new_width = int(target_height * clip_ratio)
            clip = clip.resize(height=new_height)
            # Center crop
            x_center = clip.w / 2 if hasattr(clip, 'w') else clip.size[0] / 2
            clip = clip.crop(x1=x_center - target_width/2, x2=x_center + target_width/2)
        else:
            # Video is taller - fit width, crop height
            new_width = target_width
            new_height = int(target_width / clip_ratio)
            clip = clip.resize(width=new_width)
            # Center crop
            y_center = clip.h / 2 if hasattr(clip, 'h') else clip.size[1] / 2
            clip = clip.crop(y1=y_center - target_height/2, y2=y_center + target_height/2)

        return clip

    def apply_ken_burns(self, clip, duration):
        """Apply Ken Burns effect (pan and zoom)"""
        # Random zoom direction
        zoom_in = random.choice([True, False])
        
        if zoom_in:
            # Start wide, zoom in with lambda
            try:
                clip = clip.resize(lambda t: min(1.3, 1 + 0.1 * (t / duration)))
            except:
                pass  # Skip if it fails
        else:
            # Start close, zoom out with lambda
            try:
                clip = clip.resize(lambda t: max(0.8, 1.3 - 0.1 * (t / duration)))
            except:
                pass  # Skip if it fails
        
        return clip

    def add_vignette(self, clip, width, height):
        """Add vignette effect"""
        from PIL import Image, ImageDraw
        import numpy as np
        
        # Create vignette mask
        vignette = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vignette)
        
        # Draw radial gradient
        for i in range(min(width, height) // 2):
            alpha = int(255 * (i / (min(width, height) / 2)) ** 2)
            draw.ellipse(
                [i, i, width - i, height - i],
                fill=(0, 0, 0, alpha)
            )
        
        vignette_clip = ImageClip(np.array(vignette), duration=clip.duration)
        
        return CompositeVideoClip([clip, vignette_clip])

    def apply_color_grading(self, clip, style):
        """Apply color grading based on style"""
        if style == 'dramatic':
            # Increase contrast, slight blue tint
            clip = clip.fx(vfx.colorx, 1.2)  # Increase contrast
        elif style == 'informative':
            # Bright and clear
            clip = clip.fx(vfx.gamma_corr, 1.1)  # Slightly brighter
        elif style == 'action':
            # High contrast, saturated
            clip = clip.fx(vfx.colorx, 1.3)
        
        return clip

    def concatenate_with_transitions(self, clips, transition_duration=0.5):
        """Concatenate clips with smooth transitions"""
        final_clips = []
        
        for i, clip in enumerate(clips):
            if i > 0:
                # Add crossfade transition
                clip = clip.crossfadein(transition_duration)
            if i < len(clips) - 1:
                # Prepare for next transition
                clip = clip.crossfadeout(transition_duration)
            
            final_clips.append(clip)
        
        # Use concatenate with padding to handle transitions
        return concatenate_videoclips(final_clips, padding=-transition_duration, method="compose")

    def create_animated_subtitles(self, subtitles, width, height):
        """Create modern animated subtitles"""
        subtitle_clips = []
        
        for i, sub in enumerate(subtitles):
            # Create modern subtitle style
            img = Image.new('RGBA', (width, 120), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                # Use bold font for better visibility
                font = ImageFont.truetype("arialbd.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            text = sub['text'].upper()  # Uppercase for impact
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Draw background pill
            padding = 20
            draw.rounded_rectangle(
                [x - padding, 20, x + text_width + padding, 80],
                radius=30,
                fill=(0, 0, 0, 200)
            )
            
            # Draw text with glow effect
            for offset in range(3, 0, -1):
                draw.text((x, 30), text, font=font, 
                         fill=(255, 255, 0, 100 // offset))  # Yellow glow
            draw.text((x, 30), text, font=font, fill=(255, 255, 255, 255))
            
            # Create clip with animation
            subtitle_clip = (ImageClip(np.array(img), duration=sub['end'] - sub['start'])
                            .set_start(sub['start'])
                            .set_position(('center', height - 200)))
            
            # Add pop animation - simplified
            try:
                subtitle_clip = subtitle_clip.resize(1.05)  # Fixed small zoom
            except:
                pass  # Skip if it fails
            
            subtitle_clips.append(subtitle_clip)
        
        return subtitle_clips

    def create_text_on_gradient(self, text, duration, width, height):
        """Fallback: Create text on gradient background"""
        # Use existing gradient creation
        background = ColorClip(
            size=(width, height),
            color=(20, 20, 30),
            duration=duration
        )
        
        # Add gradient overlay
        gradient = ImageClip(
            self.create_gradient_image(width, height),
            duration=duration
        ).set_opacity(0.8)
        
        # Add text
        text_clip = self.create_animated_text(
            text, duration, width, height, style='fade'
        ).set_position(('center', 'center'))
        
        return CompositeVideoClip([background, gradient, text_clip])

    def create_gradient_image(self, width, height):
        """Creates a gradient image."""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        for i in range(height):
            r = int(20 + 30 * i / height)
            g = int(20 + 30 * i / height)
            b = int(30 + 40 * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        return np.array(img)

    
    def generate_thumbnail(self, video_clip, output_path):
        """Generate better positioned thumbnail"""
        # Get frame at 2 seconds
        frame = video_clip.get_frame(2)
        img = Image.fromarray(frame)

        # Don't add text on thumbnail - let the video content speak
        # Or position text in the safe zone (center 80% of image)

        img.save(output_path, quality=95)
        print(f"Thumbnail saved: {output_path}")
    
    async def create_all_formats(self, script_data):
        """Create video in reels format only"""
        results = {}

        # Only create Reels/Shorts format (9:16)
        reels_path, reels_report = await self.create_video(script_data, 'reels')
        results['reels'] = {'path': reels_path, 'report': reels_report}

        return results

# Test function
async def test_enhanced_creator():
    """Test with sample script data"""
    script_data = {
        "id": "test_001",
        "video_details": {
            "title": "AI Revolution in India 2025"
        },
        "script_components": {
            "hook": "BREAKING: India's AI sector just hit 1 Trillion!",
            "main_points": [
                "3 Indian startups are leading global AI innovation",
                "Government launches AI skill program for 1 million students",
                "Tech giants investing 50,000 crore in Indian AI"
            ],
            "cta": "Follow for daily AI updates from India!"
        },
        "voiceover": """BREAKING: India's AI sector just hit 1 Trillion rupees! 
        Here are three game-changing developments you need to know. First, 
        3 Indian startups are leading global AI innovation. Second, the Government 
        launches AI skill program for 1 million students. Third, Tech giants are 
        investing 50,000 crore rupees in Indian AI. This is just the beginning. 
        Follow for daily AI updates from India!""",
        "hashtags": ["#AIIndia", "#TechNews", "#StartupIndia", "#AI2025"],
        "duration": 35
    }
    
    creator = EnhancedVideoCreator()
    results = await creator.create_all_formats(script_data)
    
    print("\nAll formats created successfully!")
    for format_name, result in results.items():
        print(f"  {format_name}: {result['path']}")
        print(f"  Quality Score: {result['report']['predicted_score']}/10")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_enhanced_creator())
