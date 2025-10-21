#!/usr/bin/env python3
"""
Helper script for agents to locate and work with the tracking system
"""

import os
import json
import sys
from pathlib import Path

def find_tracking_file():
    """Find the agent_tracking.json file"""
    # Try different possible locations
    possible_paths = [
        "agent_tracking.json",  # Root directory
        "../agent_tracking.json",  # One level up
        "../../agent_tracking.json",  # Two levels up
        "scripts/../agent_tracking.json",  # From scripts directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found tracking file at: {os.path.abspath(path)}")
            return path
    
    print("ERROR: Could not find agent_tracking.json")
    print("Current working directory:", os.getcwd())
    print("Files in current directory:", os.listdir("."))
    return None

def load_tracking_data():
    """Load the tracking data"""
    tracking_file = find_tracking_file()
    if not tracking_file:
        return None
    
    try:
        with open(tracking_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded tracking data with {data['papers']['total_papers']} papers")
        return data, tracking_file
    except Exception as e:
        print(f"Error loading tracking file: {e}")
        return None, None

def save_tracking_data(data, tracking_file):
    """Save the tracking data"""
    try:
        with open(tracking_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved tracking data to {tracking_file}")
        return True
    except Exception as e:
        print(f"Error saving tracking file: {e}")
        return False

def get_paper_range(data, start_idx, end_idx):
    """Get a specific range of papers"""
    papers = data['papers']['papers_to_scrape']
    if start_idx >= len(papers):
        print(f"Start index {start_idx} is beyond available papers ({len(papers)})")
        return []
    
    end_idx = min(end_idx, len(papers))
    selected_papers = papers[start_idx:end_idx]
    print(f"Selected papers {start_idx}-{end_idx-1} ({len(selected_papers)} papers)")
    return selected_papers

if __name__ == "__main__":
    print("Agent Helper Script")
    print("==================")
    
    # Test loading
    result = load_tracking_data()
    if result:
        data, tracking_file = result
        print(f"Successfully loaded {data['papers']['total_papers']} papers")
        print(f"First paper title: {data['papers']['papers_to_scrape'][0]['title'][:50]}...")
    else:
        print("Failed to load tracking data")
        sys.exit(1)
