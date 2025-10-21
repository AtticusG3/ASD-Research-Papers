#!/usr/bin/env python3
"""
Web scraping agent for ASD Research Papers - Agent C
Scrapes papers 635-950 from various online sources
"""

import os
import json
import time
import requests
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import yaml

class WebScraperAgentC:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_papers = []
        self.failed_papers = []
        self.rate_limit_delay = 2  # 2 seconds between requests
        
    def load_tracking_data(self):
        """Load the agent tracking data"""
        with open('agent_tracking.json', 'r') as f:
            return json.load(f)
    
    def save_tracking_data(self, data):
        """Save the updated tracking data"""
        with open('agent_tracking.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_papers_to_scrape(self, data):
        """Get papers 635-950 from tracking data"""
        papers = data['papers']['papers_to_scrape']
        return papers[634:950]  # papers 635-950 (0-indexed)
    
    def find_paper_urls(self, doi):
        """Find possible URLs for a paper given its DOI"""
        urls = []
        
        # Common patterns for DOI URLs
        if doi:
            # Direct DOI URL
            urls.append(f"https://doi.org/{doi}")
            
            # Try common publisher patterns
            doi_clean = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
            
            # PubMed Central
            urls.append(f"https://www.ncbi.nlm.nih.gov/pmc/articles/{doi_clean}/")
            
            # Try to extract PMC ID from DOI if possible
            if '10.3389' in doi:
                urls.append(f"https://www.frontiersin.org/articles/{doi_clean}")
            elif '10.1371' in doi:
                urls.append(f"https://journals.plos.org/plosone/article?id={doi_clean}")
            elif '10.1038' in doi:
                urls.append(f"https://www.nature.com/articles/{doi_clean}")
            elif '10.1016' in doi:
                urls.append(f"https://www.sciencedirect.com/science/article/pii/{doi_clean}")
        
        return urls
    
    def scrape_paper_content(self, url, paper_data):
        """Scrape content from a paper URL"""
        try:
            print(f"    [*] Trying URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self.extract_title(soup, paper_data)
            
            # Extract authors
            authors = self.extract_authors(soup, paper_data)
            
            # Extract abstract
            abstract = self.extract_abstract(soup, paper_data)
            
            # Extract main content
            content = self.extract_main_content(soup)
            
            # Extract journal info
            journal = self.extract_journal(soup, paper_data)
            
            # Extract publication date
            pub_date = self.extract_publication_date(soup, paper_data)
            
            return {
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'content': content,
                'journal': journal,
                'publication_date': pub_date,
                'url': url,
                'success': True
            }
            
        except Exception as e:
            print(f"    [ERROR] Failed to scrape {url}: {str(e)}")
            return {'success': False, 'error': str(e), 'url': url}
    
    def extract_title(self, soup, paper_data):
        """Extract paper title"""
        # Try multiple selectors for title
        title_selectors = [
            'h1.article-title',
            'h1.c-article-title',
            'h1[data-test-id="article-title"]',
            'h1.ArticleTitle',
            'h1.article__title',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                return title_elem.get_text().strip()
        
        # Fallback to paper data
        return paper_data.get('title', '')
    
    def extract_authors(self, soup, paper_data):
        """Extract paper authors"""
        # Try multiple selectors for authors
        author_selectors = [
            '.c-article-author-list .c-article-author-name',
            '.author-list .author-name',
            '.ArticleAuthor .AuthorName',
            '.authors .author',
            '[data-test-id="author-list"] .author',
            '.author'
        ]
        
        authors = []
        for selector in author_selectors:
            author_elems = soup.select(selector)
            if author_elems:
                authors = [elem.get_text().strip() for elem in author_elems if elem.get_text().strip()]
                break
        
        # Fallback to paper data
        if not authors and 'authors' in paper_data:
            try:
                authors = eval(paper_data['authors']) if isinstance(paper_data['authors'], str) else paper_data['authors']
            except:
                authors = [paper_data['authors']]
        
        return authors
    
    def extract_abstract(self, soup, paper_data):
        """Extract paper abstract"""
        # Try multiple selectors for abstract
        abstract_selectors = [
            '.c-article-section__content .c-article-section__title:contains("Abstract") + .c-article-section__content',
            '.abstract .abstract-content',
            '.ArticleAbstract .AbstractText',
            '.abstract p',
            '.abstract',
            '[data-test-id="abstract"]',
            '.section.abstract'
        ]
        
        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                abstract_text = abstract_elem.get_text(separator='\n', strip=True)
                if abstract_text and len(abstract_text) > 50:  # Ensure it's substantial
                    return abstract_text
        
        # Fallback to paper data
        return paper_data.get('abstract', '')
    
    def extract_main_content(self, soup):
        """Extract main paper content"""
        content_sections = {}
        
        # Try to find main content area
        main_content_selectors = [
            '.c-article-body',
            '.article-content',
            '.ArticleContent',
            '.main-content',
            'article',
            '.content'
        ]
        
        main_content = None
        for selector in main_content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            return content_sections
        
        # Extract sections by headings
        headings = main_content.find_all(['h1', 'h2', 'h3', 'h4'])
        
        for heading in headings:
            section_title = heading.get_text().strip()
            if section_title.lower() in ['abstract', 'references', 'acknowledgments']:
                continue
                
            section_content = []
            current = heading.next_sibling
            
            while current:
                if current.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                if hasattr(current, 'get_text'):
                    text = current.get_text().strip()
                    if text:
                        section_content.append(text)
                current = current.next_sibling
            
            if section_content:
                content_sections[section_title] = '\n'.join(section_content)
        
        return content_sections
    
    def extract_journal(self, soup, paper_data):
        """Extract journal information"""
        # Try multiple selectors for journal
        journal_selectors = [
            '.c-article-info-details .c-article-info-details__value',
            '.journal-title',
            '.ArticleJournal',
            '.publication-title',
            'meta[name="citation_journal_title"]'
        ]
        
        for selector in journal_selectors:
            journal_elem = soup.select_one(selector)
            if journal_elem:
                journal_text = journal_elem.get_text().strip() if journal_elem.name != 'meta' else journal_elem.get('content', '')
                if journal_text:
                    return journal_text
        
        # Fallback to paper data
        return paper_data.get('journal', '')
    
    def extract_publication_date(self, soup, paper_data):
        """Extract publication date"""
        # Try multiple selectors for date
        date_selectors = [
            'meta[name="citation_publication_date"]',
            'meta[name="DC.date.issued"]',
            '.c-article-info-details .c-article-info-details__value',
            '.publication-date',
            '.ArticleDate'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text().strip() if date_elem.name != 'meta' else date_elem.get('content', '')
                if date_text:
                    return date_text
        
        # Fallback to paper data
        return paper_data.get('date', '')
    
    def create_markdown_file(self, paper_data, scraped_content, paper_index):
        """Create markdown file for scraped paper"""
        # Create output directory
        output_dir = Path('docs/research')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = f"scraped_{paper_index + 635}.md"  # paper_index is 0-based, so add 635
        
        # Build frontmatter
        frontmatter = {
            'title': scraped_content.get('title', paper_data.get('title', '')),
            'authors': scraped_content.get('authors', []),
            'journal': scraped_content.get('journal', paper_data.get('journal', '')),
            'doi': paper_data.get('doi', ''),
            'publication_date': scraped_content.get('publication_date', paper_data.get('date', '')),
            'source': 'web_scraping',
            'scraping_date': datetime.now().isoformat(),
            'scraped_by': 'agent_c',
            'original_url': scraped_content.get('url', ''),
            'category': paper_data.get('category', ''),
            'content_type': 'research_paper',
            'audience': ['professional', 'researcher'],
            'reading_level': 'academic',
            'patient_friendly': False,
            'type': 'research_paper'
        }
        
        # Build markdown content
        markdown_lines = []
        
        # Title
        markdown_lines.append(f"# {frontmatter['title']}")
        markdown_lines.append("")
        
        # Authors
        if frontmatter['authors']:
            authors_str = ', '.join(frontmatter['authors'])
            markdown_lines.append(f"**Authors:** {authors_str}")
            markdown_lines.append("")
        
        # Journal and date
        if frontmatter['journal']:
            markdown_lines.append(f"**Journal:** {frontmatter['journal']}")
        if frontmatter['publication_date']:
            markdown_lines.append(f"**Publication Date:** {frontmatter['publication_date']}")
        if frontmatter['doi']:
            markdown_lines.append(f"**DOI:** {frontmatter['doi']}")
        markdown_lines.append("")
        
        # Abstract
        abstract = scraped_content.get('abstract', '')
        if abstract:
            markdown_lines.append("## Abstract")
            markdown_lines.append("")
            markdown_lines.append(abstract)
            markdown_lines.append("")
        
        # Main content sections
        content_sections = scraped_content.get('content', {})
        for section_title, section_content in content_sections.items():
            if section_title.lower() not in ['abstract']:
                markdown_lines.append(f"## {section_title}")
                markdown_lines.append("")
                markdown_lines.append(section_content)
                markdown_lines.append("")
        
        # Research details
        markdown_lines.append("---")
        markdown_lines.append("")
        markdown_lines.append("## Research Details")
        markdown_lines.append("")
        markdown_lines.append(f"**Source:** {frontmatter['source']}")
        markdown_lines.append(f"**Category:** {frontmatter['category']}")
        markdown_lines.append(f"**Scraping Date:** {frontmatter['scraping_date']}")
        markdown_lines.append(f"**Scraped By:** {frontmatter['scraped_by']}")
        if frontmatter['original_url']:
            markdown_lines.append(f"**Original URL:** {frontmatter['original_url']}")
        markdown_lines.append("")
        markdown_lines.append("*This paper was scraped from online sources and processed for the neurodevelopmental disorders knowledge base.*")
        
        # Write file
        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True))
            f.write('---\n')
            f.write('\n'.join(markdown_lines))
        
        return str(output_file)
    
    def scrape_paper(self, paper_data, paper_index):
        """Scrape a single paper"""
        paper_id = paper_index + 635
        print(f"[{paper_id}] Processing: {paper_data.get('title', 'Unknown')[:60]}...")
        
        doi = paper_data.get('doi', '')
        if not doi:
            print(f"    [SKIP] No DOI available")
            return False
        
        # Find possible URLs
        urls = self.find_paper_urls(doi)
        
        # Try each URL
        for url in urls:
            scraped_content = self.scrape_paper_content(url, paper_data)
            
            if scraped_content.get('success', False):
                # Create markdown file
                try:
                    output_file = self.create_markdown_file(paper_data, scraped_content, paper_index)
                    print(f"    [OK] Created: {output_file}")
                    
                    self.scraped_papers.append({
                        'paper_id': paper_id,
                        'title': paper_data.get('title', ''),
                        'doi': doi,
                        'output_file': output_file,
                        'url': url,
                        'content_length': len(scraped_content.get('content', {}))
                    })
                    
                    return True
                    
                except Exception as e:
                    print(f"    [ERROR] Failed to create markdown: {str(e)}")
                    continue
            else:
                print(f"    [FAIL] {scraped_content.get('error', 'Unknown error')}")
        
        # If all URLs failed
        print(f"    [FAILED] Could not scrape from any URL")
        self.failed_papers.append({
            'paper_id': paper_id,
            'title': paper_data.get('title', ''),
            'doi': doi,
            'error': 'All URLs failed'
        })
        
        return False
    
    def update_tracking_data(self, data, paper_index, success):
        """Update tracking data for a paper"""
        papers = data['papers']['papers_to_scrape']
        paper = papers[634 + paper_index]  # papers 635-950 (0-indexed)
        
        paper['status'] = 'completed' if success else 'failed'
        paper['scraped_by'] = 'agent_c'
        paper['last_attempt'] = datetime.now().isoformat()
        paper['attempts'] = paper.get('attempts', 0) + 1
        
        if success:
            paper['filepath'] = f"docs/research/scraped_{paper_index + 635}.md"
            paper['content_length'] = len(self.scraped_papers[-1].get('content', '')) if self.scraped_papers else 0
        else:
            paper['error_message'] = self.failed_papers[-1].get('error', 'Unknown error') if self.failed_papers else 'Unknown error'
    
    def create_log_file(self):
        """Create log file with scraping results"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"webscraping_agent_c_{timestamp}.json"
        
        log_data = {
            'agent': 'agent_c',
            'scraping_date': datetime.now().isoformat(),
            'papers_range': '635-950',
            'total_papers': len(self.scraped_papers) + len(self.failed_papers),
            'successful': len(self.scraped_papers),
            'failed': len(self.failed_papers),
            'scraped_papers': self.scraped_papers,
            'failed_papers': self.failed_papers
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"[*] Log saved to: {log_file}")
        return str(log_file)
    
    def run(self):
        """Main scraping process"""
        print("[*] Starting Web Scraping Agent C")
        print("[*] Processing papers 635-950")
        print()
        
        # Load tracking data
        data = self.load_tracking_data()
        papers_to_scrape = self.get_papers_to_scrape(data)
        
        print(f"[*] Found {len(papers_to_scrape)} papers to process")
        print()
        
        # Process each paper
        for i, paper_data in enumerate(papers_to_scrape):
            try:
                success = self.scrape_paper(paper_data, i)
                self.update_tracking_data(data, i, success)
                
                # Rate limiting
                if i < len(papers_to_scrape) - 1:  # Don't delay after last paper
                    time.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                print(f"    [ERROR] Unexpected error: {str(e)}")
                self.failed_papers.append({
                    'paper_id': i + 635,
                    'title': paper_data.get('title', ''),
                    'doi': paper_data.get('doi', ''),
                    'error': str(e)
                })
                self.update_tracking_data(data, i, False)
        
        # Save updated tracking data
        self.save_tracking_data(data)
        
        # Create log file
        self.create_log_file()
        
        # Summary
        print(f"\n[*] Scraping Complete!")
        print(f"    Successfully scraped: {len(self.scraped_papers)}")
        print(f"    Failed: {len(self.failed_papers)}")
        
        return len(self.scraped_papers), len(self.failed_papers)

def main():
    scraper = WebScraperAgentC()
    successful, failed = scraper.run()
    
    print(f"\n[*] Agent C completed processing papers 635-950")
    print(f"    Results: {successful} successful, {failed} failed")

if __name__ == '__main__':
    main()
