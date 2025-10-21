#!/usr/bin/env python3
"""
Webscraping Agent B for ASD Research Papers
Scrapes papers 318-634 with rate limiting and retry logic
"""

import json
import time
import requests
from datetime import datetime
import re
from urllib.parse import urlparse
import os
from bs4 import BeautifulSoup

class WebscrapingAgentB:
    def __init__(self):
        self.agent_id = "agent_b"
        self.tracking_file = "agent_tracking.json"
        self.log_file = f"logs/webscraping_agent_b_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.delay_between_requests = 2  # seconds
        self.max_retries = 3
        self.min_content_length = 500
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize log
        self.log_data = {
            "agent_id": self.agent_id,
            "start_time": datetime.now().isoformat(),
            "papers_processed": 0,
            "papers_successful": 0,
            "papers_failed": 0,
            "papers_skipped": 0,
            "errors": [],
            "papers": []
        }
    
    def load_tracking(self):
        """Load the agent tracking file"""
        try:
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.tracking_file} not found")
            return None
    
    def save_tracking(self, tracking):
        """Save the updated tracking file"""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(tracking, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tracking file: {e}")
    
    def get_paper_sources(self, doi):
        """Find online sources for a paper given its DOI"""
        sources = []
        
        # Try common academic sources
        if doi:
            # PubMed
            pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={doi}"
            sources.append(("pubmed", pubmed_url))
            
            # Direct DOI resolution
            doi_url = f"https://doi.org/{doi}"
            sources.append(("doi", doi_url))
            
            # Try to find publisher-specific URLs
            # This is a simplified approach - in practice, you'd want more sophisticated DOI resolution
            sources.append(("direct", doi_url))
        
        return sources
    
    def scrape_content(self, url, source_type):
        """Scrape content from a given URL"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Check if content is substantial enough
            if len(text) < self.min_content_length:
                return None, f"Content too short: {len(text)} characters"
            
            return text, None
            
        except requests.exceptions.RequestException as e:
            return None, f"Request error: {str(e)}"
        except Exception as e:
            return None, f"Parsing error: {str(e)}"
    
    def process_paper(self, paper, tracking):
        """Process a single paper"""
        paper_id = paper['paper_id']
        print(f"Processing paper {paper_id}: {paper['title'][:80]}...")
        
        # Skip if already processed
        if paper['status'] in ['completed', 'failed']:
            print(f"Paper {paper_id} already processed (status: {paper['status']})")
            return
        
        # Skip if no DOI
        if not paper['doi']:
            paper['status'] = 'failed'
            paper['error'] = 'No DOI available'
            paper['scraped_by'] = self.agent_id
            paper['scraped_at'] = datetime.now().isoformat()
            self.log_data['papers_skipped'] += 1
            print(f"Paper {paper_id} skipped: No DOI")
            return
        
        # Get potential sources
        sources = self.get_paper_sources(paper['doi'])
        
        content = None
        error = None
        
        # Try each source
        for source_type, url in sources:
            print(f"  Trying {source_type}: {url}")
            content, error = self.scrape_content(url, source_type)
            
            if content:
                print(f"  Successfully scraped from {source_type}")
                break
            else:
                print(f"  Failed to scrape from {source_type}: {error}")
                time.sleep(1)  # Brief delay between attempts
        
        # Update paper status
        if content:
            paper['status'] = 'completed'
            paper['content'] = content
            paper['scraped_by'] = self.agent_id
            paper['scraped_at'] = datetime.now().isoformat()
            paper['error'] = None
            self.log_data['papers_successful'] += 1
            print(f"Paper {paper_id} completed successfully")
        else:
            paper['status'] = 'failed'
            paper['error'] = error or 'All sources failed'
            paper['scraped_by'] = self.agent_id
            paper['scraped_at'] = datetime.now().isoformat()
            self.log_data['papers_failed'] += 1
            print(f"Paper {paper_id} failed: {paper['error']}")
        
        # Update tracking statistics
        tracking['statistics']['total_attempts'] += 1
        if paper['status'] == 'completed':
            tracking['statistics']['successful_scrapes'] += 1
            tracking['statistics']['last_successful_scrape'] = datetime.now().isoformat()
        else:
            tracking['statistics']['failed_scrapes'] += 1
        
        # Calculate success rate
        total_attempts = tracking['statistics']['total_attempts']
        successful = tracking['statistics']['successful_scrapes']
        tracking['statistics']['success_rate'] = (successful / total_attempts) * 100 if total_attempts > 0 else 0
        
        # Log paper result
        paper_log = {
            "paper_id": paper_id,
            "title": paper['title'],
            "doi": paper['doi'],
            "status": paper['status'],
            "error": paper['error'],
            "content_length": len(paper.get('content', '')),
            "scraped_at": paper['scraped_at']
        }
        self.log_data['papers'].append(paper_log)
        self.log_data['papers_processed'] += 1
    
    def create_markdown_file(self, paper):
        """Create markdown file for a successfully scraped paper"""
        if paper['status'] != 'completed' or not paper.get('content'):
            return
        
        filename = f"docs/research/scraped_{paper['paper_id']}.md"
        
        # Create markdown content
        markdown_content = f"""# {paper['title']}

**Authors:** {paper['authors']}  
**Journal:** {paper['journal']}  
**Date:** {paper['date']}  
**DOI:** {paper['doi']}  
**Category:** {paper['category']}  
**Source:** {paper['source']}  
**Scraped by:** {paper['scraped_by']}  
**Scraped at:** {paper['scraped_at']}  

## Abstract

{paper['abstract']}

## Full Text

{paper['content']}
"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Created markdown file: {filename}")
        except Exception as e:
            print(f"Error creating markdown file {filename}: {e}")
    
    def run(self):
        """Main execution loop"""
        print(f"Starting {self.agent_id} - Processing papers 318-634")
        
        # Load tracking data
        tracking = self.load_tracking()
        if not tracking:
            return
        
        # Get papers to process (318-634)
        papers_to_process = [p for p in tracking['papers']['papers_to_scrape'] 
                           if 318 <= p['paper_id'] <= 634 and p['status'] == 'pending']
        
        print(f"Found {len(papers_to_process)} papers to process")
        
        # Process each paper
        for i, paper in enumerate(papers_to_process, 1):
            print(f"\n--- Processing paper {i}/{len(papers_to_process)} ---")
            
            # Process the paper
            self.process_paper(paper, tracking)
            
            # Create markdown file if successful
            if paper['status'] == 'completed':
                self.create_markdown_file(paper)
            
            # Save tracking after each paper
            self.save_tracking(tracking)
            
            # Rate limiting delay
            if i < len(papers_to_process):  # Don't delay after the last paper
                print(f"Waiting {self.delay_between_requests} seconds before next request...")
                time.sleep(self.delay_between_requests)
        
        # Final log update
        self.log_data['end_time'] = datetime.now().isoformat()
        self.log_data['duration_seconds'] = (
            datetime.fromisoformat(self.log_data['end_time']) - 
            datetime.fromisoformat(self.log_data['start_time'])
        ).total_seconds()
        
        # Save final log
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.log_data, f, indent=2, ensure_ascii=False)
            print(f"\nLog saved to: {self.log_file}")
        except Exception as e:
            print(f"Error saving log file: {e}")
        
        # Print summary
        print(f"\n=== SUMMARY ===")
        print(f"Papers processed: {self.log_data['papers_processed']}")
        print(f"Papers successful: {self.log_data['papers_successful']}")
        print(f"Papers failed: {self.log_data['papers_failed']}")
        print(f"Papers skipped: {self.log_data['papers_skipped']}")
        print(f"Success rate: {(self.log_data['papers_successful'] / max(self.log_data['papers_processed'], 1)) * 100:.1f}%")

if __name__ == "__main__":
    agent = WebscrapingAgentB()
    agent.run()