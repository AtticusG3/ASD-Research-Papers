#!/usr/bin/env python3
import json
import sys

def extract_papers_318_634():
    """Extract papers 318-634 from agent_tracking.json"""
    try:
        with open('agent_tracking.json', 'r') as f:
            data = json.load(f)
        
        papers = data.get('papers', {}).get('papers_to_scrape', [])
        
        # Extract papers 318-634 (0-indexed, so 317-633)
        target_papers = papers[317:634]
        
        print(f"Total papers in file: {len(papers)}")
        print(f"Extracting papers 318-634 (indices 317-633): {len(target_papers)} papers")
        
        # Count papers with DOI
        papers_with_doi = [p for p in target_papers if p.get('doi')]
        print(f"Papers with DOI: {len(papers_with_doi)}")
        
        # Show first few papers
        for i, paper in enumerate(target_papers[:5]):
            print(f"\nPaper {318 + i}:")
            print(f"  Title: {paper.get('title', 'N/A')[:100]}...")
            print(f"  DOI: {paper.get('doi', 'N/A')}")
            print(f"  Status: {paper.get('status', 'N/A')}")
        
        return target_papers
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    papers = extract_papers_318_634()