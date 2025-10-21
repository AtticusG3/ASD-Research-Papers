#!/usr/bin/env python3
"""
Extract first 317 papers from agent_tracking.json for processing
"""

import json
import sys
from datetime import datetime

def extract_papers():
    """Extract first 317 papers from agent_tracking.json"""
    try:
        with open('agent_tracking.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        papers = data.get('papers', {}).get('papers_to_scrape', [])
        
        # Get first 317 papers
        papers_to_process = papers[:317]
        
        print(f"Extracted {len(papers_to_process)} papers for processing")
        
        # Count papers with DOI
        papers_with_doi = [p for p in papers_to_process if p.get('doi')]
        print(f"Papers with DOI: {len(papers_with_doi)}")
        
        # Show first few papers as examples
        print("\nFirst 5 papers:")
        for i, paper in enumerate(papers_to_process[:5]):
            print(f"{i+1}. {paper.get('title', 'No title')[:80]}...")
            print(f"   DOI: {paper.get('doi', 'No DOI')}")
            print(f"   Status: {paper.get('status', 'unknown')}")
            print()
        
        return papers_to_process
        
    except Exception as e:
        print(f"Error reading agent_tracking.json: {e}")
        return []

if __name__ == "__main__":
    papers = extract_papers()
    print(f"Ready to process {len(papers)} papers")