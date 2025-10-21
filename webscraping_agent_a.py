#!/usr/bin/env python3
"""
Webscraping Agent A for ASD Research Papers
Scrapes papers 1-317 from various online sources
"""

import json
import time
import requests
import yaml
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

class WebscrapingAgentA:
    def __init__(self):
        self.agent_id = "agent_a"
        self.papers_to_scrape = []
        self.scraped_papers = []
        self.failed_papers = []
        self.retry_attempts = 3
        self.delay_between_requests = 2
        self.timeout_seconds = 15
        self.min_content_length = 500
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        Path('docs/research').mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(parents=True, exist_ok=True)
        
        # Load agent tracking
        self.load_agent_tracking()
    
    def load_agent_tracking(self):
        """Load the agent tracking file"""
        try:
            with open('agent_tracking.json', 'r', encoding='utf-8') as f:
                self.tracking_data = json.load(f)
            
            # Get papers assigned to agent_a (1-317)
            self.papers_to_scrape = [p for p in self.tracking_data['papers']['papers_to_scrape'] 
                                   if p['paper_id'] <= 317 and p['status'] == 'pending']
            
            self.logger.info(f"Loaded {len(self.papers_to_scrape)} papers to scrape")
            
        except FileNotFoundError:
            self.logger.error("agent_tracking.json not found!")
            raise
        except Exception as e:
            self.logger.error(f"Error loading agent tracking: {e}")
            raise
    
    def save_agent_tracking(self):
        """Save the updated agent tracking file"""
        try:
            with open('agent_tracking.json', 'w', encoding='utf-8') as f:
                json.dump(self.tracking_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving agent tracking: {e}")
    
    def get_paper_sources(self, doi):
        """Get potential sources for a paper given its DOI"""
        sources = []
        
        if not doi:
            return sources
        
        # Common sources to try
        base_urls = [
            f"https://doi.org/{doi}",
            f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{doi.split('/')[-1]}/" if 'pmc' in doi.lower() else None,
            f"https://pubmed.ncbi.nlm.nih.gov/{doi.split('/')[-1]}/" if 'pubmed' in doi.lower() else None,
        ]
        
        # Remove None values
        sources = [url for url in base_urls if url]
        
        # Try to find additional sources via DOI resolution
        try:
            response = requests.head(f"https://doi.org/{doi}", timeout=10, allow_redirects=True)
            if response.status_code == 200:
                final_url = response.url
                if final_url not in sources:
                    sources.append(final_url)
        except:
            pass
        
        return sources
    
    def scrape_paper_content(self, paper):
        """Scrape content from a paper's online sources"""
        doi = paper.get('doi', '')
        if not doi:
            return None, "No DOI available"
        
        sources = self.get_paper_sources(doi)
        if not sources:
            return None, "No sources found for DOI"
        
        for source_url in sources:
            try:
                self.logger.info(f"Trying source: {source_url}")
                
                # Add delay between requests
                time.sleep(self.delay_between_requests)
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(source_url, headers=headers, timeout=self.timeout_seconds)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract content based on source type
                if 'pubmed' in source_url.lower() or 'ncbi' in source_url.lower():
                    content = self.extract_pubmed_content(soup, paper)
                elif 'doi.org' in source_url.lower():
                    content = self.extract_doi_content(soup, paper)
                else:
                    content = self.extract_generic_content(soup, paper)
                
                if content and len(content.get('full_text', '')) > self.min_content_length:
                    return content, None
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed for {source_url}: {e}")
                continue
            except Exception as e:
                self.logger.warning(f"Parsing failed for {source_url}: {e}")
                continue
        
        return None, "All sources failed"
    
    def extract_pubmed_content(self, soup, paper):
        """Extract content from PubMed/NCBI pages"""
        content = {
            'title': paper.get('title', ''),
            'abstract': paper.get('abstract', ''),
            'authors': paper.get('authors', ''),
            'journal': paper.get('journal', ''),
            'doi': paper.get('doi', ''),
            'full_text': '',
            'sections': {}
        }
        
        # Try to find full text link
        full_text_links = soup.find_all('a', href=re.compile(r'full|pdf|article', re.I))
        for link in full_text_links:
            href = link.get('href')
            if href and ('pdf' in href.lower() or 'full' in href.lower()):
                # This is a link to full text, we'd need to follow it
                # For now, we'll extract what we can from the current page
                pass
        
        # Extract abstract from page
        abstract_elem = soup.find('div', class_='abstract') or soup.find('div', {'id': 'abstract'})
        if abstract_elem:
            content['abstract'] = abstract_elem.get_text(strip=True)
        
        # Extract any available text content
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if main_content:
            content['full_text'] = main_content.get_text(strip=True)
        
        return content
    
    def extract_doi_content(self, soup, paper):
        """Extract content from DOI resolution pages"""
        content = {
            'title': paper.get('title', ''),
            'abstract': paper.get('abstract', ''),
            'authors': paper.get('authors', ''),
            'journal': paper.get('journal', ''),
            'doi': paper.get('doi', ''),
            'full_text': '',
            'sections': {}
        }
        
        # Try to find full text
        full_text_links = soup.find_all('a', href=re.compile(r'pdf|full|article', re.I))
        for link in full_text_links:
            href = link.get('href')
            if href:
                # Try to follow the link
                try:
                    response = requests.get(href, timeout=self.timeout_seconds)
                    if response.status_code == 200:
                        # Check if it's a PDF
                        if 'pdf' in response.headers.get('content-type', '').lower():
                            # For PDFs, we'd need special handling
                            # For now, just note that we found a PDF
                            content['full_text'] = f"[PDF available at: {href}]"
                        else:
                            # Try to parse as HTML
                            pdf_soup = BeautifulSoup(response.content, 'html.parser')
                            main_content = pdf_soup.find('main') or pdf_soup.find('article') or pdf_soup.find('body')
                            if main_content:
                                content['full_text'] = main_content.get_text(strip=True)
                except:
                    pass
        
        # Extract content from current page
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            content['full_text'] = main_content.get_text(strip=True)
        
        return content
    
    def extract_generic_content(self, soup, paper):
        """Extract content from generic web pages"""
        content = {
            'title': paper.get('title', ''),
            'abstract': paper.get('abstract', ''),
            'authors': paper.get('authors', ''),
            'journal': paper.get('journal', ''),
            'doi': paper.get('doi', ''),
            'full_text': '',
            'sections': {}
        }
        
        # Try to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            content['full_text'] = main_content.get_text(strip=True)
        
        return content
    
    def create_markdown_file(self, paper, content):
        """Create a markdown file for the scraped paper"""
        if not content or not content.get('full_text'):
            return None
        
        # Determine category
        category = self.determine_category(paper, content)
        
        # Create filename
        safe_title = re.sub(r'[^\w\s-]', '', paper['title'])
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]  # Limit length
        filename = f"scraped_{paper['paper_id']:03d}_{safe_title}.md"
        
        # Create directory
        output_dir = Path('docs/research') / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create markdown content
        markdown_content = f"""# {paper['title']}

**Authors:** {paper['authors']}
**Journal:** {paper['journal']}
**DOI:** {paper['doi']}
**Publication Date:** {paper['date']}

## Abstract

{paper['abstract']}

## Full Text

{content['full_text']}

---

*Scraped by Agent A on {datetime.now().isoformat()}*
*Source: {paper['source']}*
*Category: {category}*
"""
        
        # Write file
        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(output_file)
    
    def determine_category(self, paper, content):
        """Determine the category for the paper"""
        text = (paper['title'] + ' ' + paper['abstract'] + ' ' + content.get('full_text', '')).lower()
        
        if any(term in text for term in ['tourette', 'tic', 'tics', 'gilles']):
            return 'tourette'
        elif any(term in text for term in ['adhd', 'attention deficit', 'hyperactivity']):
            return 'adhd'
        elif any(term in text for term in ['autism', 'spectrum', 'asperger', 'asd']):
            return 'asd'
        elif any(term in text for term in ['comorbid', 'comorbidity']):
            return 'comorbidity'
        elif any(term in text for term in ['hormone', 'endocrine', 'testosterone', 'estrogen']):
            return 'hormones-endocrine'
        elif any(term in text for term in ['neurochemistry', 'dopamine', 'serotonin', 'neurotransmitter']):
            return 'neurochemistry'
        else:
            return 'related-disorders'
    
    def update_paper_status(self, paper_id, status, error_message=None, markdown_file=None):
        """Update the status of a paper in the tracking file"""
        for paper in self.tracking_data['papers']['papers_to_scrape']:
            if paper['paper_id'] == paper_id:
                paper['status'] = status
                paper['scraped_by'] = self.agent_id
                paper['scraped_at'] = datetime.now().isoformat()
                if error_message:
                    paper['error_message'] = error_message
                if markdown_file:
                    paper['markdown_file'] = markdown_file
                break
    
    def scrape_paper(self, paper):
        """Scrape a single paper with retry logic"""
        paper_id = paper['paper_id']
        self.logger.info(f"Scraping paper {paper_id}: {paper['title'][:50]}...")
        
        for attempt in range(self.retry_attempts):
            try:
                content, error = self.scrape_paper_content(paper)
                
                if content and content.get('full_text'):
                    # Success - create markdown file
                    markdown_file = self.create_markdown_file(paper, content)
                    if markdown_file:
                        self.update_paper_status(paper_id, 'completed', markdown_file=markdown_file)
                        self.scraped_papers.append({
                            'paper_id': paper_id,
                            'title': paper['title'],
                            'markdown_file': markdown_file,
                            'attempt': attempt + 1
                        })
                        self.logger.info(f"Successfully scraped paper {paper_id}")
                        return True
                    else:
                        error = "Failed to create markdown file"
                
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed for paper {paper_id}: {error}. Retrying...")
                    time.sleep(2)  # Wait before retry
                else:
                    # Final attempt failed
                    self.update_paper_status(paper_id, 'failed', error_message=error)
                    self.failed_papers.append({
                        'paper_id': paper_id,
                        'title': paper['title'],
                        'error': error,
                        'attempts': attempt + 1
                    })
                    self.logger.error(f"Failed to scrape paper {paper_id} after {attempt + 1} attempts: {error}")
                    return False
                    
            except Exception as e:
                error = f"Unexpected error: {str(e)}"
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed for paper {paper_id}: {error}. Retrying...")
                    time.sleep(2)
                else:
                    self.update_paper_status(paper_id, 'failed', error_message=error)
                    self.failed_papers.append({
                        'paper_id': paper_id,
                        'title': paper['title'],
                        'error': error,
                        'attempts': attempt + 1
                    })
                    self.logger.error(f"Failed to scrape paper {paper_id} after {attempt + 1} attempts: {error}")
                    return False
        
        return False
    
    def run_scraping(self):
        """Run the scraping process for all assigned papers"""
        self.logger.info(f"Starting scraping process for {len(self.papers_to_scrape)} papers")
        
        for i, paper in enumerate(self.papers_to_scrape, 1):
            self.logger.info(f"Processing paper {i}/{len(self.papers_to_scrape)}")
            
            # Skip papers without DOI
            if not paper.get('doi'):
                self.logger.warning(f"Skipping paper {paper['paper_id']} - no DOI")
                self.update_paper_status(paper['paper_id'], 'failed', error_message="No DOI available")
                continue
            
            # Scrape the paper
            success = self.scrape_paper(paper)
            
            # Save progress after each paper
            self.save_agent_tracking()
            
            # Add delay between papers
            if i < len(self.papers_to_scrape):
                time.sleep(self.delay_between_requests)
        
        self.logger.info("Scraping process completed")
        self.create_log_file()
    
    def create_log_file(self):
        """Create a log file with scraping results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = Path('logs') / f"webscraping_agent_a_{timestamp}.json"
        
        log_data = {
            'agent_id': self.agent_id,
            'scraping_date': datetime.now().isoformat(),
            'total_papers': len(self.papers_to_scrape),
            'successful_scrapes': len(self.scraped_papers),
            'failed_scrapes': len(self.failed_papers),
            'success_rate': len(self.scraped_papers) / len(self.papers_to_scrape) if self.papers_to_scrape else 0,
            'scraped_papers': self.scraped_papers,
            'failed_papers': self.failed_papers,
            'settings': {
                'retry_attempts': self.retry_attempts,
                'delay_between_requests': self.delay_between_requests,
                'timeout_seconds': self.timeout_seconds,
                'min_content_length': self.min_content_length
            }
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Log file created: {log_file}")

def main():
    """Main function"""
    try:
        agent = WebscrapingAgentA()
        agent.run_scraping()
        
        print(f"\nScraping completed!")
        print(f"Successfully scraped: {len(agent.scraped_papers)} papers")
        print(f"Failed: {len(agent.failed_papers)} papers")
        print(f"Success rate: {len(agent.scraped_papers) / len(agent.papers_to_scrape) * 100:.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())