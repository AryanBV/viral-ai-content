# File: C:\New Project\viral-ai-content\documentary_style_creator.py
"""
Documentary Style Video Creator
Creates ColdFusion/Aperture style videos - perfect for automation
Slow, cinematic, information-focused content
"""

import json
from moviepy.editor import *
from moviepy.video.fx.all import *
import edge_tts
import asyncio
import os
import random
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import colorsys

class DocumentaryStyleCreator:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        
        # Documentary style voices (authoritative, professional)
        self.voices = {
            'primary': 'en-GB-RyanNeural',           # Deep British male - documentary authority
            'alternative': 'en-US-GuyNeural',        # American documentary narrator
            'backup': 'en-GB-SoniaNeural',          # Professional British female
        }
        
        # Color schemes for different moods
        self.color_schemes = {
            'tech': {'primary': (0, 150, 255), 'secondary': (0, 255, 255), 'text': (255, 255, 255)},
            'serious': {'primary': (20, 20, 30), 'secondary': (50, 50, 70), 'text': (255, 255, 255)},
            'optimistic': {'primary': (255, 200, 0), 'secondary': (255, 150, 0), 'text': (0, 0, 0)},
            'warning': {'primary': (255, 50, 50), 'secondary': (200, 0, 0), 'text': (255, 255, 255)},
        }

        # Style variation schemes for content variety
        self.style_variations = {
            'tech_blue': {
                'color_temp': 'cool',
                'primary_color': (0, 120, 255),
                'secondary_color': (0, 200, 255),
                'mood': 'modern',
                'effects': ['blur', 'glow']
            },
            'warm_human': {
                'color_temp': 'warm',
                'primary_color': (255, 180, 100),
                'secondary_color': (255, 200, 150),
                'mood': 'friendly',
                'effects': ['soft_light', 'warmth']
            },
            'dark_serious': {
                'color_temp': 'neutral',
                'primary_color': (30, 30, 50),
                'secondary_color': (80, 80, 100),
                'mood': 'serious',
                'effects': ['vignette', 'contrast']
            },
            'bright_optimistic': {
                'color_temp': 'bright',
                'primary_color': (255, 220, 100),
                'secondary_color': (200, 255, 150),
                'mood': 'optimistic',
                'effects': ['brightness', 'saturation']
            }
        }
        
        # Load Pexels API
        self.pexels_key = os.getenv('PEXELS_API_KEY', '')

    def get_style_variation(self):
        """Rotate through different visual styles for content variety"""
        styles = [
            'tech_blue',        # Blue tinted, modern
            'warm_human',       # Warm colors, human interest
            'dark_serious',     # Dark, serious topics
            'bright_optimistic' # Bright, positive future
        ]
        return random.choice(styles)

    def apply_style_variation(self, clip, style_name):
        """Apply visual style variation to a video clip"""
        if style_name not in self.style_variations:
            return clip

        style = self.style_variations[style_name]

        try:
            # Apply color temperature adjustments
            if style['color_temp'] == 'cool':
                # Blue tint for tech/modern feel
                clip = clip.fx(vfx.colorx, 1.1).fx(vfx.gamma_corr, 0.9)
            elif style['color_temp'] == 'warm':
                # Warm orange/yellow tint for human interest
                clip = clip.fx(vfx.gamma_corr, 1.1)
            elif style['color_temp'] == 'bright':
                # Increased brightness and saturation
                clip = clip.fx(vfx.colorx, 1.3).fx(vfx.gamma_corr, 1.2)

            # Apply specific effects
            for effect in style.get('effects', []):
                if effect == 'blur':
                    # Subtle motion blur effect
                    pass  # Would need additional libraries
                elif effect == 'glow':
                    # Enhance highlights
                    clip = clip.fx(vfx.colorx, 1.1)
                elif effect == 'vignette':
                    # Dark vignette for serious mood
                    pass  # Could implement custom vignette
                elif effect == 'contrast':
                    # Increase contrast for dramatic effect
                    clip = clip.fx(vfx.colorx, 1.4)
                elif effect == 'brightness':
                    # Increase overall brightness
                    clip = clip.fx(vfx.gamma_corr, 1.3)
                elif effect == 'saturation':
                    # Boost color saturation
                    clip = clip.fx(vfx.colorx, 1.2)

        except Exception as e:
            print(f"Error applying style variation {style_name}: {e}")
            # Return original clip if effects fail
            pass

        return clip

    def get_voice_for_style(self, style_name):
        """Choose appropriate voice based on content style"""
        style = self.style_variations.get(style_name, {})
        mood = style.get('mood', 'modern')

        if mood in ['serious', 'modern']:
            return self.voices['primary']  # Deep British male
        elif mood == 'friendly':
            return self.voices['backup']   # Professional female
        else:
            return self.voices['alternative']  # American narrator

    def create_style_specific_title(self, title, style_name):
        """Modify title presentation based on style"""
        style = self.style_variations.get(style_name, {})

        if style.get('mood') == 'serious':
            # More formal, authoritative
            return title.upper()
        elif style.get('mood') == 'friendly':
            # More casual, approachable
            return title.title()
        elif style.get('mood') == 'optimistic':
            # Add positive framing
            if not any(word in title.lower() for word in ['future', 'breakthrough', 'innovation']):
                return f"The Future of {title}"
            return title
        else:
            return title

    def create_cinematic_opening(self, title, duration=5):
        """Create a cinematic title sequence"""
        
        # Create gradient background
        def make_frame(t):
            # Animated gradient
            img = Image.new('RGB', (self.width, self.height))
            draw = ImageDraw.Draw(img)
            
            # Animate colors
            phase = t / duration
            color1 = (int(20 + 30 * np.sin(phase)), 20, int(30 + 20 * np.sin(phase)))
            color2 = (10, int(10 + 20 * np.sin(phase)), 50)
            
            # Draw gradient
            for y in range(self.height):
                ratio = y / self.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.rectangle([(0, y), (self.width, y + 1)], fill=(r, g, b))
            
            return np.array(img)
        
        background = VideoClip(make_frame, duration=duration)
        
        # Add cinematic bars (letterbox effect)
        bar_height = 200
        top_bar = ColorClip(size=(self.width, bar_height), color=(0, 0, 0), duration=duration)
        bottom_bar = ColorClip(size=(self.width, bar_height), color=(0, 0, 0), duration=duration)
        top_bar = top_bar.set_position(('center', 0))
        bottom_bar = bottom_bar.set_position(('center', self.height - bar_height))
        
        # Create title text with fade in
        title_img = self.create_cinematic_title(title)
        title_clip = (ImageClip(title_img, duration=duration)
                     .set_position('center')
                     .fadein(1.5)
                     .fadeout(0.5))
        
        # Add subtle particle effect
        particles = self.create_particle_overlay(duration)
        
        # Combine all elements
        opening = CompositeVideoClip([background, particles, top_bar, bottom_bar, title_clip])
        
        return opening
    
    def create_cinematic_title(self, title):
        """Create professional title graphic"""
        img = Image.new('RGB', (self.width, 400), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            # Main title font
            title_font = ImageFont.truetype("arial.ttf", 72)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = title_font

        # Split title if too long
        words = title.upper().split()
        if len(words) > 4:
            line1 = ' '.join(words[:len(words)//2])
            line2 = ' '.join(words[len(words)//2:])
        else:
            line1 = title.upper()
            line2 = ""

        # Draw main title
        bbox1 = draw.textbbox((0, 0), line1, font=title_font)
        x1 = (self.width - (bbox1[2] - bbox1[0])) // 2

        # Glow effect
        for offset in range(10, 0, -2):
            alpha_color = (int(100 * (1 - offset/10)), int(200 * (1 - offset/10)), int(255 * (1 - offset/10)))
            draw.text((x1, 150), line1, font=title_font,
                     fill=alpha_color, stroke_width=offset)

        # Main text
        draw.text((x1, 150), line1, font=title_font, fill=(255, 255, 255))

        # Second line if exists
        if line2:
            bbox2 = draw.textbbox((0, 0), line2, font=title_font)
            x2 = (self.width - (bbox2[2] - bbox2[0])) // 2
            draw.text((x2, 230), line2, font=title_font, fill=(255, 255, 255))

        # Add subtle tagline
        tagline = "DOCUMENTARY"
        bbox3 = draw.textbbox((0, 0), tagline, font=subtitle_font)
        x3 = (self.width - (bbox3[2] - bbox3[0])) // 2
        draw.text((x3, 320), tagline, font=subtitle_font, fill=(150, 150, 150))

        return np.array(img)
    
    def create_particle_overlay(self, duration, density=50):
        """Create floating particle effect for atmosphere"""
        def make_frame(t):
            img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Draw floating particles
            random.seed(42)  # Consistent particles
            for i in range(density):
                x = random.randint(0, self.width)
                base_y = random.randint(0, self.height)
                # Float upward
                y = (base_y - t * 50) % self.height
                size = random.randint(1, 3)
                alpha_val = random.randint(30, 100)
                color_intensity = int(255 * alpha_val / 255)

                draw.ellipse([x-size, y-size, x+size, y+size],
                           fill=(color_intensity, color_intensity, color_intensity))

            return np.array(img)

        return VideoClip(make_frame, duration=duration).set_opacity(0.5)
    
    def create_information_card(self, title, points, duration=5):
        """Create clean information display card"""

        # Create background with subtle gradient
        img = Image.new('RGB', (self.width, self.height), (15, 15, 25))
        draw = ImageDraw.Draw(img)

        # Add gradient overlay
        for y in range(self.height):
            gradient_ratio = (1 - y / self.height) * 0.3
            overlay_color = (int(gradient_ratio * 50), int(gradient_ratio * 100), int(gradient_ratio * 150))
            draw.rectangle([(0, y), (self.width, y + 1)], fill=overlay_color)

        try:
            title_font = ImageFont.truetype("arial.ttf", 64)
            point_font = ImageFont.truetype("arial.ttf", 42)
        except:
            title_font = ImageFont.load_default()
            point_font = title_font

        # Draw title
        title_bbox = draw.textbbox((0, 0), title.upper(), font=title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2

        # Title background
        draw.rectangle([50, 200, self.width - 50, 300], fill=(0, 100, 200))
        draw.text((title_x, 220), title.upper(), font=title_font, fill=(255, 255, 255))

        # Draw points with animation markers
        y_offset = 400
        for i, point in enumerate(points[:3]):  # Max 3 points
            # Point background
            draw.rectangle([100, y_offset, self.width - 100, y_offset + 80], fill=(50, 50, 50))

            # Point number
            draw.ellipse([120, y_offset + 15, 170, y_offset + 65], fill=(0, 200, 255))
            draw.text((135, y_offset + 20), str(i + 1), font=point_font, fill=(255, 255, 255))

            # Point text
            draw.text((200, y_offset + 20), point, font=point_font, fill=(255, 255, 255))

            y_offset += 120

        # Convert to clip
        card_clip = ImageClip(np.array(img), duration=duration)

        # Add subtle zoom
        card_clip = card_clip.resize(lambda t: 1 + 0.05 * (t / duration))

        return card_clip
    
    def create_data_visualization(self, data_title, value, unit, duration=3):
        """Create animated data visualization"""

        def make_frame(t):
            img = Image.new('RGB', (self.width, 600), (0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Animated value
            current_value = int(value * min(1, t / 1.5))  # Animate over 1.5 seconds

            try:
                value_font = ImageFont.truetype("arial.ttf", 120)
                label_font = ImageFont.truetype("arial.ttf", 48)
            except:
                value_font = ImageFont.load_default()
                label_font = value_font

            # Draw circular progress
            center_x, center_y = self.width // 2, 300
            radius = 200

            # Background circle
            draw.ellipse([center_x - radius, center_y - radius,
                         center_x + radius, center_y + radius],
                        outline=(50, 50, 50), width=20)

            # Progress arc
            progress = min(1, t / 1.5)
            if progress > 0:
                # Draw arc (simplified - you'd use more complex method in production)
                for angle in range(int(360 * progress)):
                    x = center_x + radius * np.cos(np.radians(angle - 90))
                    y = center_y + radius * np.sin(np.radians(angle - 90))
                    draw.ellipse([x-10, y-10, x+10, y+10], fill=(0, 200, 255))

            # Draw value
            value_text = f"{current_value:,}"
            bbox = draw.textbbox((0, 0), value_text, font=value_font)
            value_x = center_x - (bbox[2] - bbox[0]) // 2
            draw.text((value_x, center_y - 60), value_text,
                     font=value_font, fill=(255, 255, 255))

            # Draw unit
            unit_bbox = draw.textbbox((0, 0), unit, font=label_font)
            unit_x = center_x - (unit_bbox[2] - unit_bbox[0]) // 2
            draw.text((unit_x, center_y + 40), unit,
                     font=label_font, fill=(150, 150, 150))

            # Draw title
            title_bbox = draw.textbbox((0, 0), data_title, font=label_font)
            title_x = center_x - (title_bbox[2] - title_bbox[0]) // 2
            draw.text((title_x, 50), data_title,
                     font=label_font, fill=(255, 255, 255))

            return np.array(img)

        return VideoClip(make_frame, duration=duration).set_position('center')
    
    def process_footage_with_cinematic_style(self, footage_path, duration, style='normal'):
        """Apply cinematic color grading and effects to footage"""
        try:
            clip = VideoFileClip(footage_path)
            
            # Select best part of clip
            if clip.duration > duration * 2:
                # Use middle section for better content
                start = (clip.duration - duration) / 2
                clip = clip.subclip(start, start + duration)
            elif clip.duration < duration:
                clip = clip.loop(duration=duration)
            else:
                clip = clip.subclip(0, duration)
            
            # Resize for mobile maintaining cinematic feel
            clip = self.resize_cinematic(clip)
            
            # Apply color grading
            if style == 'dramatic':
                # Cool, high contrast look
                clip = clip.fx(vfx.colorx, 0.8)  # Reduce saturation
                clip = clip.fx(vfx.lum_contrast, lum=0, contrast=0.3)
            elif style == 'warm':
                # Warm, inviting look
                clip = clip.fx(vfx.colorx, 1.2)
                clip = clip.fx(vfx.gamma_corr, 1.2)
            elif style == 'tech':
                # Blue-tinted, modern look
                def blue_tint(image):
                    image[:,:,2] = np.minimum(255, image[:,:,2] * 1.2)  # Boost blue
                    image[:,:,0] = image[:,:,0] * 0.9  # Reduce red
                    return image
                clip = clip.fl_image(blue_tint)
            
            # Add subtle slow zoom (Ken Burns effect)
            zoom_factor = 1.1
            clip = clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / duration))
            
            # Add vignette for cinematic look
            vignette = self.create_vignette(duration)
            clip = CompositeVideoClip([clip, vignette])
            
            # Add film grain for texture
            if random.random() > 0.5:
                grain = self.create_film_grain(duration)
                clip = CompositeVideoClip([clip, grain])
            
            return clip
            
        except Exception as e:
            print(f"Error processing footage: {e}")
            # Return a stylized color clip as fallback
            return ColorClip(size=(self.width, self.height), 
                           color=(20, 20, 30), duration=duration)
    
    def resize_cinematic(self, clip):
        """Resize with cinematic cropping"""
        # Get aspect ratios
        clip_aspect = clip.w / clip.h
        target_aspect = self.width / self.height
        
        if clip_aspect > target_aspect:
            # Wider than target - scale by height
            clip = clip.resize(height=self.height)
            # Take center crop
            excess = clip.w - self.width
            clip = clip.crop(x1=excess//2, x2=clip.w - excess//2)
        else:
            # Taller than target - scale by width
            clip = clip.resize(width=self.width)
            # Take upper-middle crop (usually more interesting than center)
            excess = clip.h - self.height
            clip = clip.crop(y1=excess//3, y2=clip.h - 2*excess//3)
        
        return clip
    
    def create_vignette(self, duration):
        """Create vignette overlay for cinematic look"""
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Create radial gradient
        center_x, center_y = self.width // 2, self.height // 2
        max_radius = np.sqrt(center_x**2 + center_y**2)

        for i in range(int(max_radius), 0, -5):
            intensity = int(255 * (1 - (i / max_radius) ** 2))
            color = (intensity, intensity, intensity)
            draw.ellipse([center_x - i, center_y - i,
                         center_x + i, center_y + i], fill=color)

        return ImageClip(np.array(img), duration=duration).set_opacity(0.6)
    
    def create_film_grain(self, duration, intensity=0.1):
        """Add subtle film grain texture"""
        def make_frame(t):
            # Create random noise
            grain = np.random.random((self.height, self.width, 3)) * intensity * 255
            grain = grain.astype(np.uint8)

            return grain

        return VideoClip(make_frame, duration=duration).set_opacity(0.2)
    
    def create_lower_third(self, text, subtitle, duration=3):
        """Create professional lower third graphic"""
        img = Image.new('RGB', (self.width, 300), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background bars
        draw.rectangle([0, 50, self.width, 130], fill=(0, 0, 0))
        draw.rectangle([0, 130, 600, 180], fill=(0, 150, 255))

        try:
            main_font = ImageFont.truetype("arial.ttf", 48)
            sub_font = ImageFont.truetype("arial.ttf", 32)
        except:
            main_font = ImageFont.load_default()
            sub_font = main_font

        # Main text
        draw.text((50, 60), text.upper(), font=main_font, fill=(255, 255, 255))

        # Subtitle
        draw.text((50, 135), subtitle, font=sub_font, fill=(200, 200, 200))

        lower_third = ImageClip(np.array(img), duration=duration)

        # Animate in from left
        lower_third = lower_third.set_position(
            lambda t: (min(0, -self.width + t * self.width * 2), self.height - 400)
        )

        return lower_third
    
    def create_transition(self, style='fade'):
        """Create smooth transitions between scenes"""
        if style == 'fade':
            return 0.5  # Duration for crossfade
        elif style == 'cut':
            return 0  # Hard cut
        elif style == 'dissolve':
            return 1.0  # Longer fade
    
    async def create_documentary_video(self, script_data, footage_clips):
        """Create complete documentary-style video"""
        
        print("🎬 Creating documentary-style video...")
        
        # Generate voiceover with professional voice
        voice_file = f"temp_voice_{datetime.now().timestamp()}.mp3"
        voice = self.voices['primary']  # Documentary voice
        
        # Process script for better flow
        voiceover_text = self.process_script_for_documentary(script_data['voiceover'])
        
        communicate = edge_tts.Communicate(voiceover_text, voice, rate="-10%")  # Slightly slower
        await communicate.save(voice_file)
        
        audio = AudioFileClip(voice_file)
        duration = audio.duration
        
        # Create video segments
        segments = []
        
        # 1. Opening sequence (5 seconds)
        opening = self.create_cinematic_opening(
            script_data['video_details']['title'],
            duration=5
        )
        segments.append(opening)
        
        # 2. Hook section with dramatic footage (5-7 seconds)
        if footage_clips and len(footage_clips) > 0:
            hook_footage = self.process_footage_with_cinematic_style(
                footage_clips[0],
                duration=5,
                style='dramatic'
            )
            
            # Add hook text as lower third
            hook_text = self.create_lower_third(
                "BREAKING",
                script_data['script_components']['hook'][:50],
                duration=5
            )
            hook_section = CompositeVideoClip([hook_footage, hook_text])
        else:
            # Fallback to text card
            hook_section = self.create_information_card(
                "KEY INSIGHT",
                [script_data['script_components']['hook']],
                duration=5
            )
        segments.append(hook_section)
        
        # 3. Main points with cinematic footage
        points = script_data['script_components']['main_points']
        point_duration = (duration - 15) / len(points)  # Minus opening and ending
        
        for i, point in enumerate(points):
            if i < len(footage_clips) - 1:
                # Use footage with cinematic treatment
                point_footage = self.process_footage_with_cinematic_style(
                    footage_clips[i + 1],
                    duration=point_duration,
                    style='tech' if i % 2 == 0 else 'warm'
                )
                
                # Add text overlay
                point_text = self.create_lower_third(
                    f"POINT {i + 1}",
                    point[:60],
                    duration=point_duration
                )
                
                point_section = CompositeVideoClip([point_footage, point_text])
            else:
                # Use info card
                point_section = self.create_information_card(
                    f"KEY POINT {i + 1}",
                    [point],
                    duration=point_duration
                )
            
            segments.append(point_section)
        
        # 4. Data visualization (if numbers mentioned)
        if any(char.isdigit() for char in script_data['voiceover']):
            # Extract a number for visualization
            import re
            numbers = re.findall(r'\d+', script_data['voiceover'])
            if numbers:
                data_viz = self.create_data_visualization(
                    "IMPACT",
                    int(numbers[0]),
                    "UNITS",
                    duration=3
                )
                segments.append(data_viz)
        
        # 5. Closing with CTA
        closing_duration = 5
        if footage_clips and len(footage_clips) > 1:
            closing_footage = self.process_footage_with_cinematic_style(
                footage_clips[-1],
                duration=closing_duration,
                style='dramatic'
            )
        else:
            closing_footage = ColorClip(
                size=(self.width, self.height),
                color=(10, 10, 20),
                duration=closing_duration
            )
        
        # Add CTA text
        cta_text = self.create_cinematic_title(script_data['script_components']['cta'])
        cta_clip = (ImageClip(cta_text, duration=closing_duration)
                   .set_position('center')
                   .fadein(0.5))
        
        closing = CompositeVideoClip([closing_footage, cta_clip])
        segments.append(closing)
        
        # Concatenate all segments with smooth transitions
        final_video = concatenate_videoclips(segments, method="compose")
        
        # Add audio
        final_video = final_video.set_audio(audio)
        
        # Add subtle background music (optional)
        # final_video = self.add_ambient_music(final_video)
        
        # Export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            "output", "videos",
            f"documentary_{timestamp}.mp4"
        )
        
        print("📹 Rendering documentary video...")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4
        )
        
        # Cleanup
        os.remove(voice_file)
        
        print(f"✅ Documentary video created: {output_path}")
        return output_path
    
    def process_script_for_documentary(self, script):
        """Adjust script pacing for documentary style"""
        # Add natural pauses
        script = script.replace('. ', '... ')  # Longer pauses between sentences
        script = script.replace('!', '.')  # Less exclamation, more authoritative
        
        # Remove overly casual language
        casual_words = ['guys', 'like', 'you know', 'basically', 'literally']
        for word in casual_words:
            script = script.replace(word, '')
        
        return script

# Test function
async def test_documentary_style():
    creator = DocumentaryStyleCreator()
    
    test_script = {
        "video_details": {"title": "The AI Revolution"},
        "script_components": {
            "hook": "Artificial intelligence is transforming our world",
            "main_points": [
                "AI systems now surpass human performance in many tasks",
                "Investment in AI has reached unprecedented levels",
                "The implications for society are profound"
            ],
            "cta": "Stay informed about the future"
        },
        "voiceover": """Artificial intelligence is transforming our world at an unprecedented pace. 
        AI systems now surpass human performance in many specialized tasks, from medical diagnosis 
        to strategic game playing. Investment in AI has reached unprecedented levels, with billions 
        flowing into research and development. The implications for society are profound and far-reaching. 
        Stay informed about the future that's being built today."""
    }
    
    # Mock footage paths (replace with actual)
    mock_footage = ["path/to/clip1.mp4", "path/to/clip2.mp4", "path/to/clip3.mp4"]
    
    output = await creator.create_documentary_video(test_script, mock_footage)
    print(f"Documentary created: {output}")

if __name__ == "__main__":
    asyncio.run(test_documentary_style())