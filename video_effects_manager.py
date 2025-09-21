# File: C:\New Project\viral-ai-content\video_effects_manager.py
"""
Professional Video Effects for Viral Content
Makes videos look manually edited, not AI-generated
"""

from moviepy.editor import *
from moviepy.video.fx.all import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

class VideoEffectsManager:
    def __init__(self):
        self.transitions = ['fade', 'slide', 'zoom', 'glitch', 'wipe']
        
    def create_hook_sequence(self, footage_clips, hook_text, duration=5):
        """Create dramatic hook with multiple quick cuts"""
        
        # Split hook duration into quick cuts (0.5-1 second each)
        cuts = []
        cut_duration = 0.5
        
        for i in range(int(duration / cut_duration)):
            if i < len(footage_clips):
                clip = footage_clips[i]
                
                # Quick cut from footage
                segment = clip.subclip(
                    random.uniform(0, max(0, clip.duration - cut_duration)),
                    min(clip.duration, random.uniform(0, max(0, clip.duration - cut_duration)) + cut_duration)
                ).set_duration(cut_duration)
                
                # Add different effect to each cut
                if i == 0:
                    segment = segment.fadein(0.2)
                elif i == 1:
                    segment = self.add_shake_effect(segment, intensity=5)
                elif i == 2:
                    segment = self.add_flash_effect(segment)
                elif i == 3:
                    segment = self.add_zoom_punch(segment)
                
                cuts.append(segment)
        
        # Concatenate with no gaps
        hook_video = concatenate_videoclips(cuts, method="compose")
        
        # Add dramatic text overlay
        text_overlay = self.create_cinematic_text(hook_text, duration)
        
        return CompositeVideoClip([hook_video, text_overlay])
    
    def add_shake_effect(self, clip, intensity=5):
        """Add camera shake effect"""
        def shake_frame(get_frame, t):
            frame = get_frame(t)
            if random.random() < 0.5:  # 50% chance of shake
                dx = random.randint(-intensity, intensity)
                dy = random.randint(-intensity, intensity)
                frame = np.roll(frame, dx, axis=1)
                frame = np.roll(frame, dy, axis=0)
            return frame
        
        return clip.fl(shake_frame)
    
    def add_flash_effect(self, clip, flash_duration=0.1):
        """Add white flash transition"""
        white_flash = ColorClip(
            size=clip.size,
            color=(255, 255, 255),
            duration=flash_duration
        ).set_start(clip.duration - flash_duration).set_opacity(0.8)
        
        return CompositeVideoClip([clip, white_flash])
    
    def add_zoom_punch(self, clip):
        """Quick zoom in and out"""
        return clip.resize(lambda t: 1 + 0.2 * np.sin(2 * np.pi * t * 2))
    
    def create_cinematic_text(self, text, duration):
        """Create movie-trailer style text"""
        
        # Create text with PIL for better control
        img_width = 1080
        img_height = 300
        
        # Create text image with glow effect
        base_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        
        # Create glow layer
        glow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        
        try:
            font = ImageFont.truetype("impact.ttf", 80)
        except:
            font = ImageFont.truetype("arial.ttf", 80)
        
        # Center text
        text = text.upper()
        bbox = glow_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img_width - text_width) // 2
        y = 100
        
        # Draw glow
        for offset in range(20, 0, -2):
            alpha = int(255 * (1 - offset/20) * 0.3)
            glow_draw.text(
                (x, y), text, 
                font=font, 
                fill=(255, 255, 0, alpha),
                stroke_width=offset,
                stroke_fill=(255, 200, 0, alpha//2)
            )
        
        # Blur the glow
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Draw main text
        main_draw = ImageDraw.Draw(base_img)
        main_draw.text(
            (x, y), text,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=3,
            stroke_fill=(0, 0, 0, 255)
        )
        
        # Composite glow and main text
        final_img = Image.alpha_composite(glow_img, base_img)
        
        # Convert to video clip
        text_clip = ImageClip(np.array(final_img), duration=duration)
        
        # Animate: slide up + fade in + scale
        text_clip = (text_clip
                    .set_position(lambda t: ('center', 800 - t * 100))
                    .fadein(0.5)
                    .resize(lambda t: min(1.2, 0.8 + t * 0.4)))
        
        return text_clip
    
    def create_transition(self, clip1, clip2, transition_type='random', duration=0.5):
        """Create smooth transition between clips"""
        
        if transition_type == 'random':
            transition_type = random.choice(self.transitions)
        
        if transition_type == 'fade':
            # Crossfade
            clip1 = clip1.crossfadeout(duration)
            clip2 = clip2.crossfadein(duration)
        
        elif transition_type == 'slide':
            # Slide transition
            clip2 = clip2.set_position(
                lambda t: (max(0, 1080 - t * 2160), 'center') if t < duration else ('center', 'center')
            )
        
        elif transition_type == 'zoom':
            # Zoom transition
            clip1 = clip1.resize(lambda t: 1 + (t / clip1.duration) * 0.5)
            clip2 = clip2.resize(lambda t: 1.5 - (t / duration) * 0.5 if t < duration else 1)
        
        elif transition_type == 'glitch':
            # Digital glitch effect
            clip1 = self.add_glitch_effect(clip1, start_time=clip1.duration - duration)
            
        elif transition_type == 'wipe':
            # Wipe transition
            mask_clip = ColorClip(clip1.size, color=(255, 255, 255), duration=duration)
            mask_clip = mask_clip.set_position(
                lambda t: (int(-1080 + t * 2160 / duration), 0)
            )
            clip2 = clip2.set_mask(mask_clip)
        
        return clip1, clip2
    
    def add_glitch_effect(self, clip, start_time=0, duration=0.5):
        """Add digital glitch effect"""
        def glitch_frame(get_frame, t):
            frame = get_frame(t)
            if start_time <= t < start_time + duration:
                # Random RGB channel shift
                if random.random() < 0.3:
                    frame[:, :, 0] = np.roll(frame[:, :, 0], random.randint(-20, 20), axis=1)
                if random.random() < 0.3:
                    frame[:, :, 1] = np.roll(frame[:, :, 1], random.randint(-20, 20), axis=1)
                if random.random() < 0.3:
                    frame[:, :, 2] = np.roll(frame[:, :, 2], random.randint(-20, 20), axis=1)
                
                # Random horizontal bars
                if random.random() < 0.2:
                    bar_height = random.randint(10, 50)
                    bar_y = random.randint(0, frame.shape[0] - bar_height)
                    frame[bar_y:bar_y+bar_height] = np.random.randint(0, 255, frame[bar_y:bar_y+bar_height].shape)
            
            return frame
        
        return clip.fl(glitch_frame)
    
    def create_animated_captions(self, text, duration, style='bold'):
        """Create TikTok-style animated captions"""
        
        words = text.split()
        clips = []
        
        # Calculate timing for each word
        word_duration = duration / len(words)
        
        for i, word in enumerate(words):
            # Create word clip
            img = Image.new('RGBA', (1080, 200), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                if style == 'bold':
                    font = ImageFont.truetype("arialbd.ttf", 60)
                else:
                    font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            # Text positioning
            bbox = draw.textbbox((0, 0), word.upper(), font=font)
            text_width = bbox[2] - bbox[0]
            x = (1080 - text_width) // 2
            
            # Background box (TikTok style)
            padding = 15
            if i % 3 == 0:  # Alternate colors
                box_color = (255, 255, 0, 220)  # Yellow
                text_color = (0, 0, 0, 255)  # Black
            elif i % 3 == 1:
                box_color = (255, 0, 255, 220)  # Magenta
                text_color = (255, 255, 255, 255)  # White
            else:
                box_color = (0, 255, 255, 220)  # Cyan
                text_color = (0, 0, 0, 255)  # Black
            
            # Draw box
            draw.rounded_rectangle(
                [x - padding, 60, x + text_width + padding, 140],
                radius=10,
                fill=box_color
            )
            
            # Draw text
            draw.text((x, 70), word.upper(), font=font, fill=text_color)
            
            # Create clip
            word_clip = (ImageClip(np.array(img), duration=word_duration * 1.5)
                        .set_start(i * word_duration)
                        .set_position(('center', 1600)))
            
            # Add pop animation
            word_clip = word_clip.resize(lambda t: min(1.3, 0.5 + t * 6) if t < 0.1 else 1)
            
            clips.append(word_clip)
        
        return clips
    
    def add_progress_bar(self, clip):
        """Add progress bar at bottom"""
        def make_frame(t):
            progress = t / clip.duration
            bar = np.zeros((10, 1080, 4), dtype=np.uint8)
            bar[:, :int(1080 * progress), :] = [255, 255, 0, 255]  # Yellow
            bar[:, int(1080 * progress):, :] = [100, 100, 100, 100]  # Gray
            return bar
        
        progress_bar = VideoClip(make_frame, duration=clip.duration)
        progress_bar = progress_bar.set_position(('center', 1910))
        
        return CompositeVideoClip([clip, progress_bar])
    
    def create_split_screen(self, clips, style='vertical'):
        """Create split screen effect"""
        if style == 'vertical':
            # Side by side
            left_clip = clips[0].resize(width=540).set_position((0, 'center'))
            right_clip = clips[1].resize(width=540).set_position((540, 'center'))
            return CompositeVideoClip([left_clip, right_clip])
        else:
            # Top and bottom
            top_clip = clips[0].resize(height=960).set_position(('center', 0))
            bottom_clip = clips[1].resize(height=960).set_position(('center', 960))
            return CompositeVideoClip([top_clip, bottom_clip])

# Test function
def test_effects():
    manager = VideoEffectsManager()
    
    # Create test clips
    test_clip = ColorClip(size=(1080, 1920), color=(50, 50, 50), duration=5)
    
    # Test hook sequence
    hook_text = "BREAKING NEWS"
    result = manager.create_hook_sequence([test_clip], hook_text, 5)
    
    # Add animated captions
    caption_clips = manager.create_animated_captions(
        "This is amazing new content", 
        5, 
        style='bold'
    )
    
    final = CompositeVideoClip([result] + caption_clips)
    final.write_videofile("test_effects.mp4", fps=30, codec='libx264')
    print("✅ Test effects video created!")

if __name__ == "__main__":
    test_effects()