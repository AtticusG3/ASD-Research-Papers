#!/usr/bin/env python3
"""
Webscraping Agent C for ASD Research Papers
Scrapes papers 635-950 and creates markdown files
"""

import json
import time
import requests
from datetime import datetime
import os
import re
from urllib.parse import urlparse
import logging
from bs4 import BeautifulSoup
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebscrapingAgentC:
    def __init__(self, tracking_file='agent_tracking.json'):
        self.tracking_file = tracking_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay_between_requests = 2
        self.max_retries = 3
        self.min_content_length = 500
        
    def load_tracking(self):
        """Load the agent tracking file"""
        try:
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Tracking file {self.tracking_file} not found")
            return None
    
    def save_tracking(self, tracking_data):
        """Save the agent tracking file"""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(tracking_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save tracking file: {e}")
            return False
    
    def get_paper_urls(self, doi):
        """Get potential URLs for a paper based on DOI"""
        urls = []
        
        if not doi or doi.strip() == '':
            return urls
            
        # Clean DOI
        doi = doi.strip()
        if not doi.startswith('http'):
            doi = f"https://doi.org/{doi}"
        
        urls.append(doi)
        
        # Try to extract potential publisher URLs
        if '10.3389' in doi:
            # Frontiers
            paper_id = doi.split('/')[-1]
            urls.append(f"https://www.frontiersin.org/articles/{paper_id}/full")
        elif '10.1007' in doi:
            # Springer
            urls.append(doi.replace('https://doi.org/', 'https://link.springer.com/article/'))
        elif '10.1038' in doi:
            # Nature
            urls.append(doi.replace('https://doi.org/', 'https://www.nature.com/articles/'))
        elif '10.1371' in doi:
            # PLOS
            urls.append(doi.replace('https://doi.org/', 'https://journals.plos.org/plosone/article?id='))
        elif '10.1016' in doi:
            # Elsevier
            urls.append(doi.replace('https://doi.org/', 'https://www.sciencedirect.com/science/article/pii/'))
        
        return urls
    
    def scrape_paper_content(self, paper):
        """Scrape content for a single paper"""
        paper_id = paper['id']
        doi = paper['doi']
        title = paper['title']
        
        logger.info(f"Scraping paper {paper_id}: {title[:50]}...")
        
        urls = self.get_paper_urls(doi)
        if not urls:
            logger.warning(f"No URLs found for paper {paper_id}")
            return None, "No DOI or valid URLs found"
        
        for attempt in range(self.max_retries):
            for url in urls:
                try:
                    logger.info(f"Attempt {attempt + 1}: Trying {url}")
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        content = self.extract_content(response.text, url)
                        if content and len(content) >= self.min_content_length:
                            logger.info(f"Successfully scraped paper {paper_id} from {url}")
                            return content, None
                        else:
                            logger.warning(f"Content too short for paper {paper_id} from {url}")
                    else:
                        logger.warning(f"HTTP {response.status_code} for {url}")
                        
                except Exception as e:
                    logger.warning(f"Error scraping {url}: {e}")
                
                # Rate limiting
                time.sleep(self.delay_between_requests)
            
            if attempt < self.max_retries - 1:
                logger.info(f"Retrying paper {paper_id} in 5 seconds...")
                time.sleep(5)
        
        return None, "Failed to scrape after all attempts"
    
    def extract_content(self, html_content, url):
        """Extract meaningful content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'article',
                '.article-content',
                '.content',
                '.main-content',
                '.paper-content',
                '.abstract',
                '.full-text',
                'main',
                '.entry-content'
            ]
            
            content = None
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text() for elem in elements])
                    break
            
            if not content:
                # Fallback to body text
                content = soup.get_text()
            
            # Clean up the content
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Additional cleaning based on URL
            if 'frontiersin.org' in url:
                # Remove Frontiers-specific elements
                content = re.sub(r'Citation:.*?(?=\n|$)', '', content, flags=re.DOTALL)
                content = re.sub(r'Keywords:.*?(?=\n|$)', '', content, flags=re.DOTALL)
            elif 'springer.com' in url:
                # Remove Springer-specific elements
                content = re.sub(r'©.*?(?=\n|$)', '', content, flags=re.DOTALL)
            
            return content if len(content) >= self.min_content_length else None
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return None
    
    def create_markdown_file(self, paper, content):
        """Create markdown file for a paper"""
        paper_id = paper['id']
        filename = f"docs/research/scraped_{paper_id}.md"
        
        try:
            # Create markdown content
            markdown_content = f"""# {paper['title']}

**Authors:** {paper['authors']}
**Journal:** {paper['journal']}
**Date:** {paper['date']}
**DOI:** {paper['doi']}
**Category:** {paper['category']}
**Source:** {paper['source']}

## Abstract

{paper['abstract']}

## Full Text

{content}

---
*Scraped by Agent C on {datetime.now().isoformat()}*
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Created markdown file: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create markdown file for paper {paper_id}: {e}")
            return False
    
    def process_papers(self):
        """Process all assigned papers"""
        tracking_data = self.load_tracking()
        if not tracking_data:
            return False
        
        papers_to_scrape = tracking_data['papers']['papers_to_scrape']
        results = {
            'agent_id': 'agent_c',
            'start_time': datetime.now().isoformat(),
            'papers_processed': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'results': []
        }
        
        logger.info(f"Starting to process {len(papers_to_scrape)} papers (635-950)")
        
        for i, paper in enumerate(papers_to_scrape):
            paper_id = paper['id']
            logger.info(f"Processing paper {i+1}/{len(papers_to_scrape)}: {paper_id}")
            
            # Skip if no DOI
            if not paper['doi'] or paper['doi'].strip() == '':
                logger.warning(f"Paper {paper_id} has no DOI, skipping")
                paper['status'] = 'failed'
                paper['scraped_by'] = 'agent_c'
                paper['scraped_at'] = datetime.now().isoformat()
                paper['error'] = 'No DOI available'
                results['failed_scrapes'] += 1
                results['results'].append({
                    'paper_id': paper_id,
                    'status': 'failed',
                    'error': 'No DOI available'
                })
                continue
            
            # Scrape content
            content, error = self.scrape_paper_content(paper)
            
            if content:
                # Create markdown file
                if self.create_markdown_file(paper, content):
                    paper['status'] = 'completed'
                    paper['scraped_by'] = 'agent_c'
                    paper['scraped_at'] = datetime.now().isoformat()
                    paper['content'] = content[:1000] + "..." if len(content) > 1000 else content
                    results['successful_scrapes'] += 1
                    results['results'].append({
                        'paper_id': paper_id,
                        'status': 'completed',
                        'content_length': len(content)
                    })
                    logger.info(f"Successfully processed paper {paper_id}")
                else:
                    paper['status'] = 'failed'
                    paper['scraped_by'] = 'agent_c'
                    paper['scraped_at'] = datetime.now().isoformat()
                    paper['error'] = 'Failed to create markdown file'
                    results['failed_scrapes'] += 1
                    results['results'].append({
                        'paper_id': paper_id,
                        'status': 'failed',
                        'error': 'Failed to create markdown file'
                    })
            else:
                paper['status'] = 'failed'
                paper['scraped_by'] = 'agent_c'
                paper['scraped_at'] = datetime.now().isoformat()
                paper['error'] = error or 'Unknown error'
                results['failed_scrapes'] += 1
                results['results'].append({
                    'paper_id': paper_id,
                    'status': 'failed',
                    'error': error or 'Unknown error'
                })
                logger.warning(f"Failed to scrape paper {paper_id}: {error}")
            
            results['papers_processed'] += 1
            
            # Update tracking file periodically
            if (i + 1) % 10 == 0:
                self.save_tracking(tracking_data)
                logger.info(f"Progress: {i+1}/{len(papers_to_scrape)} papers processed")
        
        # Final update
        tracking_data['papers']['papers_to_scrape'] = papers_to_scrape
        tracking_data['last_updated'] = datetime.now().isoformat()
        self.save_tracking(tracking_data)
        
        results['end_time'] = datetime.now().isoformat()
        results['success_rate'] = results['successful_scrapes'] / results['papers_processed'] if results['papers_processed'] > 0 else 0
        
        # Save results log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/webscraping_agent_c_{timestamp}.json"
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing complete. Results saved to {log_filename}")
        logger.info(f"Success rate: {results['success_rate']:.2%} ({results['successful_scrapes']}/{results['papers_processed']})")
        
        return True

def main():
    """Main function"""
    agent = WebscrapingAgentC()
    success = agent.process_papers()
    
    if success:
        print("Webscraping completed successfully")
    else:
        print("Webscraping failed")
        exit(1)

if __name__ == "__main__":
    main()