# File: C:\New Project\viral-ai-content\stock_footage_manager.py
"""
Stock Footage Manager for Viral AI Content
Fetches and manages stock videos from Pexels
"""

import os
import requests
import json
import hashlib
from typing import List, Dict
import time
import random

class StockFootageManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com"
        self.headers = {"Authorization": api_key}
        
        # Cache directory for downloaded videos
        self.cache_dir = r"C:\New Project\viral-ai-content\assets\stock_videos"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache index file
        self.cache_index_file = os.path.join(self.cache_dir, "cache_index.json")
        self.load_cache_index()
    
    def load_cache_index(self):
        """Load cache index to avoid re-downloading"""
        if os.path.exists(self.cache_index_file):
            with open(self.cache_index_file, 'r') as f:
                self.cache_index = json.load(f)
        else:
            self.cache_index = {}
    
    def save_cache_index(self):
        """Save cache index"""
        with open(self.cache_index_file, 'w') as f:
            json.dump(self.cache_index, f, indent=2)
    
    def search_videos(self, query: str, count: int = 5, orientation: str = "portrait") -> List[Dict]:
        """
        Search for videos on Pexels
        orientation: portrait (9:16), landscape (16:9), square (1:1)
        """
        search_url = f"{self.base_url}/videos/search"
        params = {
            "query": query,
            "per_page": count,
            "orientation": orientation,
            "size": "medium"
        }
        
        try:
            print(f"🔍 Searching Pexels for: {query}")
            response = requests.get(search_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for video in data.get("videos", []):
                    video_info = {
                        "id": video["id"],
                        "url": video["url"],
                        "duration": video["duration"],
                        "width": video["width"],
                        "height": video["height"],
                        "files": []
                    }
                    
                    # Get the best quality file (HD preferred)
                    for file in video["video_files"]:
                        if file["quality"] == "hd" and file["width"] >= 1920:
                            video_info["files"].append({
                                "link": file["link"],
                                "quality": file["quality"],
                                "width": file["width"],
                                "height": file["height"]
                            })
                            break
                    
                    # Fallback to any HD file
                    if not video_info["files"]:
                        for file in video["video_files"]:
                            if file["quality"] == "hd":
                                video_info["files"].append({
                                    "link": file["link"],
                                    "quality": file["quality"],
                                    "width": file["width"],
                                    "height": file["height"]
                                })
                                break
                    
                    if video_info["files"]:
                        videos.append(video_info)
                
                print(f"✅ Found {len(videos)} videos")
                return videos
            else:
                print(f"❌ Pexels API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching videos: {e}")
            return []
    
    def download_video(self, video_url: str, video_id: str) -> str:
        """Download video and cache it locally"""
        # Check if already cached
        cache_key = hashlib.md5(video_url.encode()).hexdigest()
        
        if cache_key in self.cache_index:
            cached_path = self.cache_index[cache_key]
            if os.path.exists(cached_path):
                print(f"📦 Using cached video: {video_id}")
                return cached_path
        
        # Download video
        try:
            print(f"⬇️ Downloading video {video_id}...")
            response = requests.get(video_url, stream=True)
            
            if response.status_code == 200:
                file_path = os.path.join(self.cache_dir, f"pexels_{video_id}_{cache_key[:8]}.mp4")
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Update cache index
                self.cache_index[cache_key] = file_path
                self.save_cache_index()
                
                print(f"✅ Downloaded: {file_path}")
                return file_path
            else:
                print(f"❌ Download failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            return None
    
    def get_footage_for_script(self, script_data: Dict, count_per_scene: int = 2) -> Dict:
        """
        Get relevant footage for entire script
        Returns dict with footage for each section
        """
        footage = {
            "hook": [],
            "main_points": [],
            "cta": [],
            "background": []
        }

        # CHANGE: Don't search for literal keywords, search for visuals

        # Generic tech/modern footage that works for any AI topic
        generic_searches = [
            "technology abstract",
            "data visualization",
            "coding screen",
            "futuristic city",
            "neon lights",
            "server room",
            "circuit board close up"
        ]

        # Use generic searches instead of specific keywords
        for i, search in enumerate(generic_searches[:4]):
            videos = self.search_videos(search, count=1, orientation="portrait")
            for video in videos:
                if video["files"]:
                    video_path = self.download_video(video["files"][0]["link"], str(video["id"]))
                    if video_path:
                        footage["hook"].append(video_path)
        
        # Search for main points footage using remaining generic searches
        main_points = script_data.get("script_components", {}).get("main_points", [])
        remaining_searches = generic_searches[4:]  # Use remaining searches

        for i, point in enumerate(main_points[:3]):  # Max 3 points
            if i < len(remaining_searches):
                search = remaining_searches[i]
            else:
                # Cycle through available searches
                search = generic_searches[i % len(generic_searches)]

            videos = self.search_videos(search, count=1, orientation="portrait")
            for video in videos:
                if video["files"]:
                    video_path = self.download_video(video["files"][0]["link"], str(video["id"]))
                    if video_path:
                        footage["main_points"].append(video_path)
        
        # Search for CTA footage (cinematic/engaging)
        cta_queries = [
            "futuristic interface digital",
            "technology innovation bright",
            "data streams flowing"
        ]
        videos = self.search_videos(random.choice(cta_queries), count=1, orientation="portrait")
        for video in videos:
            if video["files"]:
                video_path = self.download_video(video["files"][0]["link"], str(video["id"]))
                if video_path:
                    footage["cta"].append(video_path)
        
        # Get cinematic background footage
        bg_queries = [
            f"{' '.join(title_keywords[:2])} abstract background",
            "technology particles floating",
            "digital network connections",
            "space stars cosmos",
            "nature forest cinematic"
        ]
        bg_query = random.choice(bg_queries)
        videos = self.search_videos(bg_query, count=2, orientation="portrait")
        for video in videos:
            if video["files"]:
                video_path = self.download_video(video["files"][0]["link"], str(video["id"]))
                if video_path:
                    footage["background"].append(video_path)
        
        print(f"📊 Footage collected: Hook={len(footage['hook'])}, "
              f"Points={len(footage['main_points'])}, "
              f"CTA={len(footage['cta'])}, "
              f"BG={len(footage['background'])}")
        
        return footage
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been', 'be',
                     'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might',
                     'just', 'now', 'here', 'there', 'this', 'that', 'these', 'those'}
        
        # Convert to lowercase and split
        words = text.lower().split()
        
        # Filter keywords
        keywords = []
        for word in words:
            # Clean punctuation
            word = word.strip('.,!?;:"\'')
            
            # Skip stop words and short words
            if word not in stop_words and len(word) > 2:
                keywords.append(word)
        
        # Prioritize important tech/AI keywords
        priority_words = ['ai', 'artificial', 'intelligence', 'technology', 'digital',
                         'startup', 'innovation', 'future', 'data', 'robot', 'automation',
                         'india', 'billion', 'investment', 'breakthrough']
        
        # Sort keywords by priority
        sorted_keywords = []
        for word in keywords:
            if word in priority_words:
                sorted_keywords.insert(0, word)
            else:
                sorted_keywords.append(word)
        
        return sorted_keywords[:5]  # Return top 5 keywords

# Test function
def test_stock_manager():
    """Test the stock footage manager"""
    from dotenv import load_dotenv
    load_dotenv(encoding='utf-16')
    
    api_key = os.getenv('PEXELS_API_KEY')
    if not api_key:
        print("❌ Please add PEXELS_API_KEY to your .env file")
        return
    
    manager = StockFootageManager(api_key)
    
    # Test script data
    test_script = {
        "video_details": {"title": "AI Revolution in India"},
        "script_components": {
            "hook": "Breaking: India's AI boom shocks the world!",
            "main_points": [
                "Startups raise billion dollars",
                "Government launches AI program",
                "Tech giants expand operations"
            ],
            "cta": "Follow for more updates!"
        }
    }
    
    footage = manager.get_footage_for_script(test_script)
    
    print("\n📹 Footage Results:")
    for section, videos in footage.items():
        print(f"  {section}: {len(videos)} videos")
        for video in videos:
            print(f"    - {os.path.basename(video)}")

if __name__ == "__main__":
    test_stock_manager()