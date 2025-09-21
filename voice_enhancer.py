# File: C:\New Project\viral-ai-content\voice_enhancer.py
"""
Enhanced Voice Generator with Natural Pauses and Human-like Speech
Makes AI voices sound more natural and engaging
"""

import edge_tts
import asyncio
import re
import os
import random
from datetime import datetime
from moviepy.editor import AudioFileClip

class NaturalVoiceGenerator:
    def __init__(self):
        self.voices = {
            'female': 'en-GB-LibbyNeural',  # British female - sounds most natural
            'male': 'en-IN-PrabhatNeural',
            'female_alt': 'en-IN-NeerjaNeural',  # Indian accent backup
        }

    async def generate_natural_voice(self, text, voice_type='female', output_file='temp_voice.mp3'):
        """Generate voice with natural pauses and emphasis"""

        # Use clean text without SSML markup - the British voice sounds natural already
        clean_text = text.strip()

        # Generate voice with edge-tts
        voice = self.voices[voice_type]
        communicate = edge_tts.Communicate(clean_text, voice)  # No SSML markup needed
        await communicate.save(output_file)

        return output_file

    def add_speech_markup(self, text):
        """Add SSML markup for natural pauses and emphasis"""

        # Add pauses after sentences
        text = text.replace('. ', '. <break time="500ms"/> ')
        text = text.replace('! ', '! <break time="600ms"/> ')
        text = text.replace('? ', '? <break time="600ms"/> ')

        # Add slight pauses after commas
        text = text.replace(', ', ', <break time="200ms"/> ')

        # Add emphasis to key words (based on common patterns)
        emphasis_words = [
            'breaking', 'exclusive', 'amazing', 'revolutionary',
            'shocking', 'incredible', 'massive', 'billion',
            'first', 'never', 'always', 'must', 'need'
        ]

        for word in emphasis_words:
            # Case-insensitive replacement with emphasis
            pattern = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
            text = pattern.sub(lambda m: f'<emphasis level="strong">{m.group()}</emphasis>', text)

        # Add dramatic pause before big reveals
        text = text.replace('Here are', '<break time="300ms"/>Here are')
        text = text.replace('First,', '<break time="200ms"/>First,')
        text = text.replace('Second,', '<break time="200ms"/>Second,')
        text = text.replace('Third,', '<break time="200ms"/>Third,')
        text = text.replace('Finally,', '<break time="300ms"/>Finally,')

        # Vary speech rate for different sections
        # Hook - slightly faster for excitement
        if text.startswith('Breaking') or text.startswith('BREAKING'):
            text = f'<prosody rate="1.1">{text[:50]}</prosody>{text[50:]}'

        # CTA - slightly slower for clarity
        if 'Follow for' in text:
            cta_start = text.index('Follow for')
            text = f'{text[:cta_start]}<prosody rate="0.95">{text[cta_start:]}</prosody>'

        # Wrap in speak tags for SSML
        return f'<speak>{text}</speak>'

    def enhance_audio(self, audio_file):
        """Post-process audio for better quality - Disabled due to FFmpeg dependency"""
        # This function is disabled to avoid FFmpeg dependency
        # The SSML markup in add_speech_markup provides natural speech improvements
        pass

    def create_conversational_script(self, script_data):
        """Rewrite script to be more conversational and natural"""
        original = script_data['voiceover']

        # Make it more conversational and natural
        conversational = original

        # Replace formal phrases with casual ones
        replacements = {
            "It is": "It's",
            "We are": "We're",
            "They are": "They're",
            "Cannot": "Can't",
            "Will not": "Won't",
            "Do not": "Don't",
            "Here are three": "Here's three",
            "You need to know": "you need to know",
            "This is": "This is",
            "According to": "Apparently,",
            "First,": "First...",
            "Second,": "Second...",
            "Third,": "And third...",
        }

        for formal, casual in replacements.items():
            conversational = conversational.replace(formal, casual)

        # Add natural pauses with periods for the British voice
        conversational = conversational.replace("!", ".")
        conversational = conversational.replace("?", ".")

        # Clean up multiple periods
        conversational = conversational.replace("...", ".")
        conversational = conversational.replace("..", ".")

        return conversational

# Integration function for your existing code
async def generate_voice_with_subtitles_enhanced(text, voice_type='female'):
    """Enhanced version to replace your existing function"""
    generator = NaturalVoiceGenerator()

    # Make text more conversational
    script_data = {'voiceover': text}
    conversational_text = generator.create_conversational_script(script_data)

    # Generate natural voice
    voice_file = f"temp_voice_{datetime.now().timestamp()}.mp3"
    await generator.generate_natural_voice(conversational_text, voice_type, voice_file)

    # Generate subtitle timings with improved word timing
    words = conversational_text.split()

    # Try to get actual audio duration, fallback to estimation
    try:
        audio_clip = AudioFileClip(voice_file)
        duration = audio_clip.duration
        audio_clip.close()  # Clean up
    except:
        # Fallback: estimate duration (roughly 3 words per second)
        duration = len(words) / 3.0

    # More realistic word timing with variable speeds
    subtitles = []
    current_time = 0

    for i, word in enumerate(words):
        # Variable word duration based on word length and punctuation
        base_duration = len(word) * 0.08  # Base on word length

        # Add extra time for punctuation
        if any(p in word for p in ['.', '!', '?']):
            base_duration += 0.3
        elif ',' in word:
            base_duration += 0.15

        # Add natural variation
        word_duration = base_duration * random.uniform(0.9, 1.1)

        subtitles.append({
            'text': word,
            'start': current_time,
            'end': current_time + word_duration
        })
        current_time += word_duration

    # Normalize timing to match actual audio duration
    if current_time > 0:
        scale_factor = duration / current_time
        for sub in subtitles:
            sub['start'] *= scale_factor
            sub['end'] *= scale_factor

    return voice_file, subtitles

# Test function
async def test_natural_voice():
    generator = NaturalVoiceGenerator()

    test_text = """BREAKING: India's AI sector just hit 1 Trillion rupees.
    Here's three game-changing developments. First... Indian startups
    are leading global innovation. Second... the government launched
    a massive skill program. And third... tech giants are investing billions.
    This is huge for India's future. Follow for daily updates."""

    output_file = "test_natural_voice.mp3"
    await generator.generate_natural_voice(test_text, 'female', output_file)
    print(f"Natural voice saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(test_natural_voice())