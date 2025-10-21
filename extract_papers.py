#!/usr/bin/env python3
"""
Extract papers from agent_tracking.json for processing
Supports different paper ranges for different agents
"""

import json
import sys
from datetime import datetime

def extract_papers(start_idx=0, end_idx=317):
    """Extract papers from agent_tracking.json for specified range"""
    try:
        with open('agent_tracking.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        papers = data.get('papers', {}).get('papers_to_scrape', [])
        
        # Extract papers in specified range
        target_papers = papers[start_idx:end_idx]
        
        print(f"Total papers in file: {len(papers)}")
        print(f"Extracting papers {start_idx+1}-{end_idx}: {len(target_papers)} papers")
        
        # Count papers with DOI
        papers_with_doi = [p for p in target_papers if p.get('doi')]
        print(f"Papers with DOI: {len(papers_with_doi)}")
        
        # Show first few papers
        for i, paper in enumerate(target_papers[:5]):
            print(f"\nPaper {start_idx + i + 1}:")
            print(f"  Title: {paper.get('title', 'N/A')[:100]}...")
            print(f"  DOI: {paper.get('doi', 'N/A')}")
            print(f"  Status: {paper.get('status', 'N/A')}")
        
        return target_papers
        
    except Exception as e:
        print(f"Error reading agent_tracking.json: {e}")
        return []

def extract_papers_1_317():
    """Extract first 317 papers (Agent A)"""
    return extract_papers(0, 317)

def extract_papers_318_634():
    """Extract papers 318-634 (Agent B)"""
    return extract_papers(317, 634)

def extract_papers_635_950():
    """Extract papers 635-950 (Agent C)"""
    return extract_papers(634, 950)

if __name__ == "__main__":
    # Default to Agent A range
    papers = extract_papers_1_317()
    print(f"Ready to process {len(papers)} papers")
