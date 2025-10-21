#!/usr/bin/env python3
"""
Extract URLs from search results pages and scrape the papers
"""

import requests
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
import yaml
from datetime import datetime

class SearchResultScraper:
    def __init__(self):
        self.scraped_papers = []
        self.failed_papers = []
        self.downloaded_html_files = []
        
    def extract_pmc_urls(self, html_file_path):
        """Extract PMC article URLs from search results page"""
        print(f"[*] Extracting URLs from: {html_file_path.name}")
        
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all PMC article links
        urls = []
        links = soup.find_all('a', href=re.compile(r'pmc\.ncbi\.nlm\.nih\.gov/articles/PMC\d+'))
        
        for link in links:
            url = link.get('href')
            if url and 'PMC' in url:
                urls.append(url)
        
        print(f"  [OK] Found {len(urls)} PMC article URLs")
        return urls
    
    def download_paper_html(self, url, filename):
        """Download HTML content from a paper URL"""
        print(f"  [->] Downloading: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save HTML file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"    [OK] Saved: {filename.name}")
            return True
            
        except Exception as e:
            print(f"    [ERROR] Failed to download {url}: {str(e)}")
            return False
    
    def extract_metadata(self, soup, url):
        """Extract paper metadata from HTML"""
        metadata = {
            'title': '',
            'authors': [],
            'journal': '',
            'doi': '',
            'publication_date': '',
            'abstract': '',
            'source': 'PMC Web Scraping',
            'scraping_date': datetime.now().isoformat(),
            'source_url': url
        }
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            metadata['title'] = title_elem.get_text().strip()
        
        # Extract DOI
        doi_pattern = r'10\.\d+/[^\s<>"\']+'
        doi_match = re.search(doi_pattern, soup.get_text())
        if doi_match:
            metadata['doi'] = doi_match.group()
        
        # Extract journal
        journal_elem = soup.find('meta', {'name': 'citation_journal_title'})
        if journal_elem:
            metadata['journal'] = journal_elem.get('content', '')
        
        # Extract publication date
        date_elem = soup.find('meta', {'name': 'citation_publication_date'})
        if date_elem:
            metadata['publication_date'] = date_elem.get('content', '')
        
        # Extract authors
        author_elems = soup.find_all('meta', {'name': 'citation_author'})
        if author_elems:
            metadata['authors'] = [elem.get('content', '') for elem in author_elems]
        
        return metadata
    
    def extract_abstract(self, soup):
        """Extract abstract content"""
        abstract_section = soup.find('section', class_='abstract')
        if not abstract_section:
            abstract_section = soup.find('div', class_='abstract') or soup.find('div', {'id': 'abstract'})
        
        if abstract_section:
            abstract_header = abstract_section.find('h2')
            if abstract_header:
                abstract_header.decompose()
            
            abstract_text = abstract_section.get_text(separator='\n', strip=True)
            return abstract_text
        
        return ''
    
    def extract_main_content(self, soup):
        """Extract main paper content sections"""
        content_sections = {}
        
        main_content = soup.find('section', class_='body') or soup.find('div', class_='main-content')
        if not main_content:
            main_content = soup.find('article') or soup.find('main')
        
        if not main_content:
            return content_sections
        
        # Extract different sections
        sections = main_content.find_all(['section', 'div'], class_=re.compile(r'(intro|method|result|discussion|conclusion)', re.I))
        
        for section in sections:
            section_title = ''
            section_content = ''
            
            title_elem = section.find(['h1', 'h2', 'h3', 'h4'])
            if title_elem:
                section_title = title_elem.get_text().strip()
            
            section_content = section.get_text(separator='\n', strip=True)
            
            if section_title and section_content:
                section_content = re.sub(r'\n\s*\n', '\n\n', section_content)
                content_sections[section_title] = section_content
        
        # If no structured sections found, try to extract by headings
        if not content_sections:
            headings = main_content.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                section_title = heading.get_text().strip()
                section_content = ''
                
                current = heading.next_sibling
                while current and current.name not in ['h1', 'h2', 'h3', 'h4']:
                    if hasattr(current, 'get_text'):
                        section_content += current.get_text() + '\n'
                    current = current.next_sibling
                
                if section_content.strip():
                    content_sections[section_title] = section_content.strip()
        
        return content_sections
    
    def determine_category(self, title, content):
        """Determine paper category based on content"""
        text = (title + ' ' + content).lower()
        
        if any(term in text for term in ['tourette', 'tic', 'tics', 'gilles']):
            return 'tourette'
        elif any(term in text for term in ['adhd', 'attention deficit', 'hyperactivity']):
            return 'adhd'
        elif any(term in text for term in ['autism', 'spectrum', 'asperger', 'asd']):
            return 'asd'
        elif any(term in text for term in ['comorbid', 'comorbidity']):
            return 'comorbidity'
        else:
            return 'related-disorders'
    
    def create_markdown(self, metadata, abstract, content_sections, category):
        """Create markdown content"""
        frontmatter = {
            'title': metadata['title'],
            'authors': metadata['authors'],
            'journal': metadata['journal'],
            'doi': metadata['doi'],
            'publication_date': metadata['publication_date'],
            'source': metadata['source'],
            'scraping_date': metadata['scraping_date'],
            'source_url': metadata['source_url'],
            'primary_category': category,
            'content_type': 'research_paper',
            'audience': ['professional', 'researcher'],
            'reading_level': 'academic',
            'patient_friendly': False,
            'type': 'research_paper'
        }
        
        markdown_lines = []
        
        # Title
        markdown_lines.append(f"# {metadata['title']}")
        markdown_lines.append("")
        
        # Authors
        if metadata['authors']:
            authors_str = ', '.join(metadata['authors'])
            markdown_lines.append(f"**Authors:** {authors_str}")
            markdown_lines.append("")
        
        # Journal and date
        if metadata['journal']:
            markdown_lines.append(f"**Journal:** {metadata['journal']}")
        if metadata['publication_date']:
            markdown_lines.append(f"**Publication Date:** {metadata['publication_date']}")
        if metadata['doi']:
            markdown_lines.append(f"**DOI:** {metadata['doi']}")
        markdown_lines.append("")
        
        # Abstract
        if abstract:
            markdown_lines.append("## Abstract")
            markdown_lines.append("")
            markdown_lines.append(abstract)
            markdown_lines.append("")
        
        # Content sections
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
        markdown_lines.append(f"**Source:** {metadata['source']}")
        markdown_lines.append(f"**Category:** {category}")
        markdown_lines.append(f"**Source URL:** {metadata['source_url']}")
        markdown_lines.append(f"**Scraping Date:** {metadata['scraping_date']}")
        markdown_lines.append("")
        markdown_lines.append("*This paper was scraped from PMC search results and processed for the neurodevelopmental disorders knowledge base.*")
        
        return frontmatter, '\n'.join(markdown_lines)
    
    def scrape_paper_from_url(self, url):
        """Download and scrape a paper from URL"""
        # Create safe filename from URL
        pmc_id = re.search(r'PMC(\d+)', url)
        if pmc_id:
            filename = f"PMC_{pmc_id.group(1)}.html"
        else:
            filename = f"scraped_{hash(url) % 10000}.html"
        
        html_file = Path(filename)
        
        # Download HTML
        if not self.download_paper_html(url, html_file):
            return False
        
        self.downloaded_html_files.append(html_file)
        
        # Scrape content
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            metadata = self.extract_metadata(soup, url)
            
            # Extract abstract
            abstract = self.extract_abstract(soup)
            
            # Extract main content
            content_sections = self.extract_main_content(soup)
            
            # Determine category
            category = self.determine_category(metadata['title'], abstract + ' '.join(content_sections.values()))
            
            # Create markdown
            frontmatter, markdown_content = self.create_markdown(metadata, abstract, content_sections, category)
            
            # Save markdown file
            output_dir = Path('docs/research') / category
            output_dir.mkdir(parents=True, exist_ok=True)
            
            safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            output_file = output_dir / f"{safe_title}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('---\n')
                f.write(yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True))
                f.write('---\n')
                f.write(markdown_content)
            
            print(f"    [OK] Created: {output_file}")
            self.scraped_papers.append({
                'url': url,
                'html_file': str(html_file),
                'markdown_file': str(output_file),
                'title': metadata['title'],
                'category': category,
                'sections_found': len(content_sections)
            })
            
            return True
            
        except Exception as e:
            print(f"    [ERROR] Failed to scrape {url}: {str(e)}")
            self.failed_papers.append({
                'url': url,
                'html_file': str(html_file),
                'error': str(e)
            })
            return False
    
    def process_search_results(self, search_results_file):
        """Process search results file and scrape all papers"""
        print(f"[*] Processing search results: {search_results_file}")
        
        # Extract URLs
        urls = self.extract_pmc_urls(search_results_file)
        
        if not urls:
            print("  [WARNING] No URLs found in search results")
            return
        
        print(f"[*] Found {len(urls)} papers to scrape")
        print()
        
        # Scrape each paper
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Processing: {url}")
            
            success = self.scrape_paper_from_url(url)
            
            # Be nice to the server
            time.sleep(1)
            
            if not success:
                print(f"  [SKIP] Failed to process {url}")
        
        # Summary
        print(f"\n[*] Scraping Complete!")
        print(f"    Successfully processed: {len(self.scraped_papers)}")
        print(f"    Failed: {len(self.failed_papers)}")
        
        if self.failed_papers:
            print(f"\n[*] Failed papers:")
            for failed in self.failed_papers:
                print(f"    - {failed['url']}: {failed['error']}")
        
        return self.scraped_papers, self.failed_papers

def main():
    scraper = SearchResultScraper()
    
    # Process PMC search results
    pmc_search_file = Path("Tourette - Search Results - PMC.html")
    if pmc_search_file.exists():
        scraped, failed = scraper.process_search_results(pmc_search_file)
        
        # Save log
        log_data = {
            'scraping_date': datetime.now().isoformat(),
            'search_results_file': str(pmc_search_file),
            'total_urls_found': len(scraped) + len(failed),
            'successful': len(scraped),
            'failed': len(failed),
            'scraped_papers': scraped,
            'failed_papers': failed,
            'downloaded_html_files': [str(f) for f in scraper.downloaded_html_files]
        }
        
        log_file = Path('acquired_papers') / f"search_results_scraping_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            yaml.dump(log_data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"\n[*] Log saved to: {log_file}")
    else:
        print(f"[ERROR] Search results file not found: {pmc_search_file}")

if __name__ == '__main__':
    main()
