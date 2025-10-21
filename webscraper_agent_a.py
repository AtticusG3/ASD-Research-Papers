#!/usr/bin/env python3
"""
Webscraping Agent A for ASD Research Papers
Scrapes papers 1-317 from agent_tracking.json
"""

import json
import time
import requests
import os
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebscrapingAgentA:
    def __init__(self):
        self.agent_id = "agent_a"
        self.papers_to_process = []
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def load_papers(self):
        """Load first 317 papers from agent_tracking.json"""
        try:
            with open('agent_tracking.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            all_papers = data.get('papers', {}).get('papers_to_scrape', [])
            self.papers_to_process = all_papers[:317]
            
            logger.info(f"Loaded {len(self.papers_to_process)} papers for processing")
            return True
        except Exception as e:
            logger.error(f"Error loading papers: {e}")
            return False
    
    def get_paper_sources(self, doi):
        """Find online sources for a paper using its DOI"""
        sources = []
        
        # Try common academic sources
        potential_urls = [
            f"https://doi.org/{doi}",
            f"https://pubmed.ncbi.nlm.nih.gov/?term={doi}",
            f"https://scholar.google.com/scholar?q={doi}",
            f"https://www.ncbi.nlm.nih.gov/pmc/?term={doi}",
        ]
        
        for url in potential_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    sources.append({
                        'url': url,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', ''),
                        'content_length': len(response.content)
                    })
            except Exception as e:
                logger.debug(f"Failed to access {url}: {e}")
                continue
        
        return sources
    
    def scrape_paper_content(self, paper, sources):
        """Scrape full-text content from available sources"""
        content = ""
        successful_source = None
        
        for source in sources:
            try:
                response = self.session.get(source['url'], timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Try to extract main content
                    content_selectors = [
                        'article',
                        '.article-content',
                        '.abstract',
                        '.full-text',
                        '.content',
                        'main',
                        '.main-content'
                    ]
                    
                    for selector in content_selectors:
                        elements = soup.select(selector)
                        if elements:
                            content = ' '.join([elem.get_text(strip=True) for elem in elements])
                            if len(content) > 500:  # Ensure we got substantial content
                                successful_source = source['url']
                                break
                    
                    if content:
                        break
                        
            except Exception as e:
                logger.debug(f"Failed to scrape {source['url']}: {e}")
                continue
        
        return content, successful_source
    
    def create_markdown_file(self, paper, content, source_url):
        """Create markdown file for scraped paper"""
        try:
            # Create docs/research directory if it doesn't exist
            os.makedirs('docs/research', exist_ok=True)
            
            # Generate filename
            paper_id = paper.get('title', 'unknown')[:50].replace(' ', '_').replace('/', '_')
            paper_id = re.sub(r'[^\w\-_]', '', paper_id)
            filename = f"scraped_{paper_id}.md"
            filepath = f"docs/research/{filename}"
            
            # Create markdown content
            markdown_content = f"""# {paper.get('title', 'No Title')}

**DOI:** {paper.get('doi', 'No DOI')}
**Journal:** {paper.get('journal', 'Unknown')}
**Date:** {paper.get('date', 'Unknown')}
**Authors:** {paper.get('authors', 'Unknown')}
**Category:** {paper.get('category', 'Unknown')}
**Source:** {paper.get('source', 'Unknown')}
**Scraped by:** {self.agent_id}
**Scraped at:** {datetime.now().isoformat()}
**Source URL:** {source_url or 'No source URL'}

## Abstract

{paper.get('abstract', 'No abstract available')}

## Full Text Content

{content if content else 'No full text content could be scraped'}

---
*This content was automatically scraped by Webscraping Agent A*
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return filepath, len(content)
            
        except Exception as e:
            logger.error(f"Error creating markdown file: {e}")
            return None, 0
    
    def update_tracking_file(self, paper_index, status, filepath=None, content_length=0, error_message=None):
        """Update agent_tracking.json with paper status"""
        try:
            with open('agent_tracking.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if paper_index < len(data['papers']['papers_to_scrape']):
                paper = data['papers']['papers_to_scrape'][paper_index]
                paper['status'] = status
                paper['scraped_by'] = self.agent_id
                paper['last_attempt'] = datetime.now().isoformat()
                paper['attempts'] = paper.get('attempts', 0) + 1
                
                if filepath:
                    paper['filepath'] = filepath
                if content_length > 0:
                    paper['content_length'] = content_length
                if error_message:
                    paper['error_message'] = error_message
                
                # Write back to file
                with open('agent_tracking.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                return True
        except Exception as e:
            logger.error(f"Error updating tracking file: {e}")
            return False
    
    def process_paper(self, paper, paper_index):
        """Process a single paper"""
        logger.info(f"Processing paper {paper_index + 1}: {paper.get('title', 'No title')[:60]}...")
        
        doi = paper.get('doi')
        if not doi:
            logger.warning(f"Paper {paper_index + 1} has no DOI, skipping")
            self.update_tracking_file(paper_index, 'failed', error_message='No DOI available')
            return False
        
        # Find sources
        sources = self.get_paper_sources(doi)
        if not sources:
            logger.warning(f"No sources found for paper {paper_index + 1}")
            self.update_tracking_file(paper_index, 'failed', error_message='No sources found')
            return False
        
        # Scrape content
        content, source_url = self.scrape_paper_content(paper, sources)
        if not content:
            logger.warning(f"No content scraped for paper {paper_index + 1}")
            self.update_tracking_file(paper_index, 'failed', error_message='No content could be scraped')
            return False
        
        # Create markdown file
        filepath, content_length = self.create_markdown_file(paper, content, source_url)
        if not filepath:
            logger.error(f"Failed to create markdown file for paper {paper_index + 1}")
            self.update_tracking_file(paper_index, 'failed', error_message='Failed to create markdown file')
            return False
        
        # Update tracking
        self.update_tracking_file(paper_index, 'completed', filepath, content_length)
        
        logger.info(f"Successfully processed paper {paper_index + 1}")
        return True
    
    def run(self):
        """Main execution function"""
        logger.info("Starting Webscraping Agent A")
        
        if not self.load_papers():
            logger.error("Failed to load papers")
            return
        
        successful = 0
        failed = 0
        
        for i, paper in enumerate(self.papers_to_process):
            try:
                if self.process_paper(paper, i):
                    successful += 1
                else:
                    failed += 1
                
                # Rate limiting - 2 second delay between requests
                time.sleep(2)
                
                # Progress update every 10 papers
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i + 1}/{len(self.papers_to_process)} papers processed")
                
            except Exception as e:
                logger.error(f"Unexpected error processing paper {i + 1}: {e}")
                self.update_tracking_file(i, 'failed', error_message=str(e))
                failed += 1
        
        logger.info(f"Processing complete. Successful: {successful}, Failed: {failed}")
        
        # Create log file
        self.create_log_file(successful, failed)
    
    def create_log_file(self, successful, failed):
        """Create log file with results"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"logs/webscraping_agent_a_{timestamp}.json"
            
            os.makedirs('logs', exist_ok=True)
            
            log_data = {
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat(),
                'papers_processed': len(self.papers_to_process),
                'successful': successful,
                'failed': failed,
                'papers_range': '1-317',
                'results': self.results
            }
            
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Log file created: {log_filename}")
            
        except Exception as e:
            logger.error(f"Error creating log file: {e}")

if __name__ == "__main__":
    agent = WebscrapingAgentA()
    agent.run()