#!/usr/bin/env python3
"""
Webscraping Agent B for ASD Research Papers
Processes papers 318-634 from agent_tracking.json
"""

import json
import time
import requests
from datetime import datetime
import os
import re
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScrapingAgentB:
    def __init__(self):
        self.base_delay = 2  # 2 seconds between requests
        self.max_retries = 3
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create necessary directories
        os.makedirs('docs/research', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Load tracking data
        self.load_tracking_data()
        
    def load_tracking_data(self):
        """Load the agent_tracking.json file"""
        try:
            with open('agent_tracking.json', 'r') as f:
                self.tracking_data = json.load(f)
            self.papers = self.tracking_data['papers']['papers_to_scrape']
            self.target_papers = self.papers[317:634]  # Papers 318-634
            logger.info(f"Loaded {len(self.target_papers)} papers to process")
        except Exception as e:
            logger.error(f"Error loading tracking data: {e}")
            raise
    
    def save_tracking_data(self):
        """Save updated tracking data back to file"""
        try:
            with open('agent_tracking.json', 'w') as f:
                json.dump(self.tracking_data, f, indent=2)
            logger.info("Tracking data saved successfully")
        except Exception as e:
            logger.error(f"Error saving tracking data: {e}")
            raise
    
    def get_paper_sources(self, doi):
        """Find online sources for a paper given its DOI"""
        sources = []
        
        # Try common academic sources
        potential_urls = [
            f"https://doi.org/{doi}",
            f"https://link.springer.com/article/{doi}",
            f"https://www.nature.com/articles/{doi}",
            f"https://journals.plos.org/plosone/article?id={doi}",
            f"https://www.frontiersin.org/articles/{doi}",
            f"https://www.mdpi.com/1422-0067/23/4/{doi}",
            f"https://www.sciencedirect.com/science/article/pii/{doi}",
            f"https://onlinelibrary.wiley.com/doi/{doi}",
            f"https://www.tandfonline.com/doi/{doi}",
            f"https://www.cambridge.org/core/journals/{doi}",
        ]
        
        for url in potential_urls:
            try:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    sources.append({
                        'url': response.url,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', ''),
                        'source': self.identify_source(url)
                    })
            except Exception as e:
                logger.debug(f"Failed to check {url}: {e}")
                continue
        
        return sources
    
    def identify_source(self, url):
        """Identify the source platform from URL"""
        domain = urlparse(url).netloc.lower()
        if 'springer' in domain:
            return 'Springer'
        elif 'nature' in domain:
            return 'Nature'
        elif 'plos' in domain:
            return 'PLOS'
        elif 'frontiers' in domain:
            return 'Frontiers'
        elif 'mdpi' in domain:
            return 'MDPI'
        elif 'sciencedirect' in domain:
            return 'ScienceDirect'
        elif 'wiley' in domain:
            return 'Wiley'
        elif 'tandfonline' in domain:
            return 'Taylor & Francis'
        elif 'cambridge' in domain:
            return 'Cambridge'
        elif 'doi.org' in domain:
            return 'DOI.org'
        else:
            return 'Unknown'
    
    def scrape_paper_content(self, paper, sources):
        """Scrape full-text content from available sources"""
        content = {
            'title': paper.get('title', ''),
            'doi': paper.get('doi', ''),
            'abstract': paper.get('abstract', ''),
            'authors': paper.get('authors', ''),
            'journal': paper.get('journal', ''),
            'year': paper.get('year', ''),
            'full_text': '',
            'scraped_from': '',
            'scraping_notes': []
        }
        
        for source in sources:
            try:
                logger.info(f"Attempting to scrape from {source['source']}: {source['url']}")
                
                response = self.session.get(source['url'], timeout=30, allow_redirects=True)
                
                if response.status_code == 200:
                    # Try to extract text content
                    text_content = self.extract_text_from_html(response.text)
                    
                    if text_content and len(text_content) > 500:  # Minimum content length
                        content['full_text'] = text_content
                        content['scraped_from'] = source['source']
                        content['scraping_notes'].append(f"Successfully scraped from {source['source']}")
                        logger.info(f"Successfully scraped content from {source['source']}")
                        return content
                    else:
                        content['scraping_notes'].append(f"Content too short from {source['source']}")
                        logger.warning(f"Content too short from {source['source']}")
                else:
                    content['scraping_notes'].append(f"HTTP {response.status_code} from {source['source']}")
                    logger.warning(f"HTTP {response.status_code} from {source['source']}")
                    
            except Exception as e:
                content['scraping_notes'].append(f"Error scraping {source['source']}: {str(e)}")
                logger.error(f"Error scraping {source['source']}: {e}")
                continue
        
        # If no content was scraped, create a basic entry
        if not content['full_text']:
            content['scraping_notes'].append("No full-text content could be scraped from any source")
            logger.warning(f"No content scraped for paper {paper.get('title', 'Unknown')[:50]}...")
        
        return content
    
    def extract_text_from_html(self, html_content):
        """Extract text content from HTML"""
        try:
            # Simple text extraction - remove HTML tags and clean up
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Look for common academic paper sections
            sections = {
                'abstract': self.extract_section(text, ['abstract', 'summary']),
                'introduction': self.extract_section(text, ['introduction', 'background']),
                'methods': self.extract_section(text, ['methods', 'methodology', 'materials and methods']),
                'results': self.extract_section(text, ['results', 'findings']),
                'discussion': self.extract_section(text, ['discussion', 'conclusion']),
            }
            
            # Combine sections if found
            combined_text = []
            for section_name, section_text in sections.items():
                if section_text:
                    combined_text.append(f"## {section_name.title()}\n{section_text}")
            
            if combined_text:
                return '\n\n'.join(combined_text)
            else:
                return text[:5000]  # Return first 5000 characters if no sections found
                
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_section(self, text, keywords):
        """Extract a specific section from text based on keywords"""
        text_lower = text.lower()
        
        for keyword in keywords:
            # Look for the keyword followed by content
            pattern = rf'{keyword}[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z][a-z]+\s*[:\s]|$)'
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def create_markdown_file(self, content, paper_id):
        """Create markdown file for scraped paper"""
        filename = f"docs/research/scraped_{paper_id}.md"
        
        markdown_content = f"""# {content['title']}

**DOI:** {content['doi']}
**Authors:** {content['authors']}
**Journal:** {content['journal']}
**Year:** {content['year']}
**Scraped from:** {content['scraped_from']}
**Scraped by:** agent_b
**Scraping date:** {datetime.now().isoformat()}

## Abstract

{content['abstract']}

## Full Text

{content['full_text']}

## Scraping Notes

{chr(10).join(f"- {note}" for note in content['scraping_notes'])}
"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Created markdown file: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error creating markdown file {filename}: {e}")
            return None
    
    def process_papers(self):
        """Process all assigned papers"""
        results = {
            'agent': 'agent_b',
            'start_time': datetime.now().isoformat(),
            'papers_processed': 0,
            'papers_completed': 0,
            'papers_failed': 0,
            'papers': []
        }
        
        logger.info(f"Starting to process {len(self.target_papers)} papers")
        
        for i, paper in enumerate(self.target_papers):
            paper_id = 318 + i  # Paper ID starts from 318
            logger.info(f"Processing paper {paper_id}/{634}: {paper.get('title', 'Unknown')[:50]}...")
            
            try:
                # Find sources
                sources = self.get_paper_sources(paper['doi'])
                
                if not sources:
                    logger.warning(f"No sources found for paper {paper_id}")
                    self.update_paper_status(paper_id, 'failed', 'No sources found')
                    results['papers_failed'] += 1
                    results['papers'].append({
                        'paper_id': paper_id,
                        'title': paper.get('title', ''),
                        'doi': paper.get('doi', ''),
                        'status': 'failed',
                        'reason': 'No sources found'
                    })
                    continue
                
                # Scrape content
                content = self.scrape_paper_content(paper, sources)
                
                # Create markdown file
                if content['full_text']:
                    filename = self.create_markdown_file(content, paper_id)
                    if filename:
                        self.update_paper_status(paper_id, 'completed', f'Scraped from {content["scraped_from"]}')
                        results['papers_completed'] += 1
                        results['papers'].append({
                            'paper_id': paper_id,
                            'title': paper.get('title', ''),
                            'doi': paper.get('doi', ''),
                            'status': 'completed',
                            'scraped_from': content['scraped_from'],
                            'filename': filename
                        })
                    else:
                        self.update_paper_status(paper_id, 'failed', 'Could not create markdown file')
                        results['papers_failed'] += 1
                        results['papers'].append({
                            'paper_id': paper_id,
                            'title': paper.get('title', ''),
                            'doi': paper.get('doi', ''),
                            'status': 'failed',
                            'reason': 'Could not create markdown file'
                        })
                else:
                    self.update_paper_status(paper_id, 'failed', 'No content scraped')
                    results['papers_failed'] += 1
                    results['papers'].append({
                        'paper_id': paper_id,
                        'title': paper.get('title', ''),
                        'doi': paper.get('doi', ''),
                        'status': 'failed',
                        'reason': 'No content scraped'
                    })
                
                results['papers_processed'] += 1
                
                # Rate limiting
                if i < len(self.target_papers) - 1:  # Don't delay after last paper
                    logger.info(f"Waiting {self.base_delay} seconds before next request...")
                    time.sleep(self.base_delay)
                
            except Exception as e:
                logger.error(f"Error processing paper {paper_id}: {e}")
                self.update_paper_status(paper_id, 'failed', f'Error: {str(e)}')
                results['papers_failed'] += 1
                results['papers'].append({
                    'paper_id': paper_id,
                    'title': paper.get('title', ''),
                    'doi': paper.get('doi', ''),
                    'status': 'failed',
                    'reason': f'Error: {str(e)}'
                })
        
        results['end_time'] = datetime.now().isoformat()
        results['duration_seconds'] = (datetime.fromisoformat(results['end_time']) - 
                                     datetime.fromisoformat(results['start_time'])).total_seconds()
        
        # Save results log
        self.save_results_log(results)
        
        # Save updated tracking data
        self.save_tracking_data()
        
        logger.info(f"Processing complete. Completed: {results['papers_completed']}, Failed: {results['papers_failed']}")
        return results
    
    def update_paper_status(self, paper_id, status, notes=''):
        """Update paper status in tracking data"""
        try:
            # Find the paper in the tracking data (paper_id - 1 for 0-based index)
            paper_index = paper_id - 1
            if 0 <= paper_index < len(self.papers):
                self.papers[paper_index]['status'] = status
                self.papers[paper_index]['scraped_by'] = 'agent_b'
                if notes:
                    self.papers[paper_index]['scraping_notes'] = notes
                logger.info(f"Updated paper {paper_id} status to {status}")
            else:
                logger.error(f"Paper ID {paper_id} out of range")
        except Exception as e:
            logger.error(f"Error updating paper {paper_id} status: {e}")
    
    def save_results_log(self, results):
        """Save results to log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/webscraping_agent_b_{timestamp}.json"
        
        try:
            with open(log_filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results log saved: {log_filename}")
        except Exception as e:
            logger.error(f"Error saving results log: {e}")

def main():
    """Main function"""
    try:
        agent = WebScrapingAgentB()
        results = agent.process_papers()
        
        print(f"\n=== Webscraping Agent B Results ===")
        print(f"Papers processed: {results['papers_processed']}")
        print(f"Papers completed: {results['papers_completed']}")
        print(f"Papers failed: {results['papers_failed']}")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()