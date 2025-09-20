# File: C:\New Project\viral-ai-content\video-creation\test_voice.py

import asyncio
import edge_tts
import json

async def test_voice():
    # Test with a sample script
    text = "BOOM! China just slammed the door on Nvidia's AI chips. This changes everything for the AI race."
    
    # Try different Indian English voices
    voices = [
        "en-IN-NeerjaNeural",  # Female
        "en-IN-PrabhatNeural"  # Male
    ]
    
    for voice in voices:
        output_file = f"test_{voice.split('-')[2]}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        print(f"✅ Generated: {output_file}")

if __name__ == "__main__":
    asyncio.run(test_voice())
    print("Voice generation test complete! Check the MP3 files.")