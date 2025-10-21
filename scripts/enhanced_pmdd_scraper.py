#!/usr/bin/env python3
"""
Enhanced PMDD web scraping system with better source handling and retry logic
"""

import os
import re
import yaml
import json
import time
import requests
import pandas as pd
import html
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPMDDScraper:
    def __init__(self, csv_file, output_dir="docs/research/hormones-endocrine/pmdd"):
        self.csv_file = Path(csv_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.scraped_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.results = []
        
        # Track already processed papers to avoid duplicates
        self.processed_dois = set()
        self.load_existing_papers()
    
    def load_existing_papers(self):
        """Load already processed papers to avoid duplicates"""
        try:
            for file_path in self.output_dir.glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract DOI from YAML frontmatter
                    if 'doi:' in content:
                        doi_match = re.search(r'doi:\s*([^\n]+)', content)
                        if doi_match:
                            self.processed_dois.add(doi_match.group(1).strip())
            
            logger.info(f"Found {len(self.processed_dois)} already processed papers")
        except Exception as e:
            logger.warning(f"Could not load existing papers: {e}")
    
    def load_papers(self):
        """Load PMDD papers from CSV"""
        try:
            df = pd.read_csv(self.csv_file)
            logger.info(f"Loaded {len(df)} PMDD papers from {self.csv_file}")
            return df
        except Exception as e:
            logger.error(f"Error loading papers: {e}")
            return None
    
    def get_paper_urls(self, row):
        """Get potential URLs for a paper with enhanced strategies"""
        urls = []
        
        # Try to construct URLs from DOI
        doi = row.get('doi', '')
        if doi and not pd.isna(doi):
            # Enhanced DOI URL patterns
            doi_urls = [
                f"https://doi.org/{doi}",
                f"https://dx.doi.org/{doi}",
                f"https://www.ncbi.nlm.nih.gov/pmc/articles/{doi}",
                f"https://pubmed.ncbi.nlm.nih.gov/{doi}",
            ]
            urls.extend(doi_urls)
        
        # Try PubMed Central if we have PMID
        pmid = row.get('pmid', '')
        if pmid and not pd.isna(pmid):
            urls.extend([
                f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmid}/",
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmid}/"
            ])
        
        # Try to extract URL from existing data
        url = row.get('url', '')
        if url and not pd.isna(url):
            urls.append(url)
        
        # Try alternative sources for common publishers
        if doi and not pd.isna(doi):
            # Springer
            if 'springer' in doi.lower() or '10.1007' in doi:
                urls.append(f"https://link.springer.com/article/{doi}")
            # Elsevier
            elif 'elsevier' in doi.lower() or '10.1016' in doi:
                urls.append(f"https://www.sciencedirect.com/science/article/pii/{doi}")
            # Nature
            elif 'nature' in doi.lower() or '10.1038' in doi:
                urls.append(f"https://www.nature.com/articles/{doi}")
            # Wiley
            elif 'wiley' in doi.lower() or '10.1002' in doi:
                urls.append(f"https://onlinelibrary.wiley.com/doi/full/{doi}")
        
        return urls
    
    def scrape_paper_content(self, url, max_retries=3):
        """Scrape content from a paper URL with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping (attempt {attempt + 1}): {url}")
                
                # Add delay to be respectful
                time.sleep(2 + attempt)  # Increasing delay with retries
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract content based on common academic site patterns
                content = self.extract_academic_content(soup, url)
                
                if content and len(content) > 500:  # Ensure we got substantial content
                    return content
                else:
                    logger.warning(f"Insufficient content from {url} (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        continue
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                    continue
                return None
            except Exception as e:
                logger.error(f"Error scraping {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return None
        
        return None
    
    def extract_academic_content(self, soup, url):
        """Extract content from academic paper pages with enhanced strategies"""
        content_parts = []
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            element.decompose()
        
        # Try different content extraction strategies based on URL domain
        domain = urlparse(url).netloc.lower()
        
        if 'ncbi.nlm.nih.gov' in domain or 'pubmed' in domain:
            content = self.extract_ncbi_content(soup)
        elif 'doi.org' in domain or 'dx.doi.org' in domain:
            content = self.extract_doi_content(soup)
        elif 'springer' in domain or 'link.springer' in domain:
            content = self.extract_springer_content(soup)
        elif 'elsevier' in domain or 'sciencedirect' in domain:
            content = self.extract_elsevier_content(soup)
        elif 'wiley' in domain or 'onlinelibrary.wiley' in domain:
            content = self.extract_wiley_content(soup)
        elif 'nature' in domain:
            content = self.extract_nature_content(soup)
        elif 'mdpi' in domain:
            content = self.extract_mdpi_content(soup)
        elif 'frontiers' in domain:
            content = self.extract_frontiers_content(soup)
        else:
            content = self.extract_generic_content(soup)
        
        return content
    
    def extract_ncbi_content(self, soup):
        """Extract content from NCBI/PubMed pages"""
        content_parts = []
        
        # Try multiple selectors for NCBI content
        selectors = [
            'div#maincontent',
            'div.main-content',
            'div.article-content',
            'div.abstract',
            'section.abstract',
            'div.full-text',
            'section.full-text',
            'article'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def extract_springer_content(self, soup):
        """Extract content from Springer pages"""
        content_parts = []
        
        # Springer specific selectors
        selectors = [
            'section.Abstract',
            'div.abstract',
            'div.main-content',
            'article',
            'div.c-article-body',
            'div.c-article-section'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def extract_elsevier_content(self, soup):
        """Extract content from Elsevier/ScienceDirect pages"""
        content_parts = []
        
        # Elsevier specific selectors
        selectors = [
            'div.abstract',
            'section.abstract',
            'div.article-content',
            'article',
            'div.section-content',
            'div.abstract-content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def extract_wiley_content(self, soup):
        """Extract content from Wiley pages"""
        content_parts = []
        
        # Wiley specific selectors
        selectors = [
            'div.abstract',
            'section.abstract',
            'div.article-content',
            'article',
            'div.section-content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def extract_nature_content(self, soup):
        """Extract content from Nature pages"""
        content_parts = []
        
        # Nature specific selectors
        selectors = [
            'div.abstract',
            'section.abstract',
            'div.article-content',
            'article',
            'div.c-article-body'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def extract_mdpi_content(self, soup):
        """Extract content from MDPI pages"""
        content_parts = []
        
        # MDPI specific selectors
        selectors = [
            'div.abstract',
            'section.abstract',
            'div.article-content',
            'article',
            'div.section-content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def extract_frontiers_content(self, soup):
        """Extract content from Frontiers pages"""
        content_parts = []
        
        # Frontiers specific selectors
        selectors = [
            'div.abstract',
            'section.abstract',
            'div.article-content',
            'article',
            'div.section-content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def extract_doi_content(self, soup):
        """Extract content from DOI redirect pages"""
        return self.extract_generic_content(soup)
    
    def extract_generic_content(self, soup):
        """Generic content extraction for unknown sites"""
        content_parts = []
        
        # Try common academic paper selectors
        selectors = [
            'article',
            '.article-content',
            '.main-content',
            '.content',
            '#content',
            '.paper-content',
            '.full-text',
            '.abstract',
            'section.abstract',
            'div.abstract'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:  # Only include substantial content
                    content_parts.append(text)
        
        # If no specific content found, try to get all text
        if not content_parts:
            body = soup.find('body')
            if body:
                text = body.get_text(separator='\n', strip=True)
                if len(text) > 500:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def clean_content(self, content):
        """Clean and normalize scraped content"""
        if not content:
            return None
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'^\s+|\s+$', '', content, flags=re.MULTILINE)
        
        # Remove common web artifacts
        content = re.sub(r'Cookie Policy.*?Accept', '', content, flags=re.DOTALL)
        content = re.sub(r'Privacy Policy.*?Accept', '', content, flags=re.DOTALL)
        content = re.sub(r'Terms of Service.*?Accept', '', content, flags=re.DOTALL)
        content = re.sub(r'Subscribe.*?Newsletter', '', content, flags=re.DOTALL)
        
        # Remove navigation elements
        content = re.sub(r'Home.*?Contact', '', content, flags=re.DOTALL)
        content = re.sub(r'Search.*?Advanced', '', content, flags=re.DOTALL)
        content = re.sub(r'Login.*?Register', '', content, flags=re.DOTALL)
        
        # Remove common footer content
        content = re.sub(r'Copyright.*?All rights reserved', '', content, flags=re.DOTALL)
        content = re.sub(r'Published by.*?Journal', '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def process_paper(self, row, index, total):
        """Process a single paper"""
        try:
            # Check if already processed
            doi = self.extract_doi(row.get('doi', ''))
            if doi and doi in self.processed_dois:
                logger.info(f"Paper {index + 1} already processed, skipping")
                self.skipped_count += 1
                return None
            
            logger.info(f"Processing paper {index + 1}/{total}: {row.get('title', 'Unknown')[:50]}...")
            
            # Get potential URLs
            urls = self.get_paper_urls(row)
            
            if not urls:
                logger.warning(f"No URLs found for paper {index + 1}")
                self.failed_count += 1
                return None
            
            # Try to scrape content from each URL
            scraped_content = None
            successful_url = None
            
            for url in urls:
                content = self.scrape_paper_content(url)
                if content:
                    scraped_content = self.clean_content(content)
                    successful_url = url
                    break
            
            if not scraped_content:
                logger.warning(f"Could not scrape content for paper {index + 1}")
                self.failed_count += 1
                return None
            
            # Create enhanced metadata
            enhanced_metadata = self.create_enhanced_metadata(row, scraped_content, successful_url)
            
            # Create filename
            filename = self.create_filename(row, enhanced_metadata)
            
            # Create markdown content
            markdown_content = self.create_markdown_content(row, enhanced_metadata, scraped_content)
            
            # Write file
            output_file = self.output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Add to processed DOIs
            if doi:
                self.processed_dois.add(doi)
            
            self.scraped_count += 1
            logger.info(f"Successfully scraped and saved: {filename}")
            
            return {
                'filename': filename,
                'url': successful_url,
                'content_length': len(scraped_content),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error processing paper {index + 1}: {e}")
            self.failed_count += 1
            return None
    
    def create_enhanced_metadata(self, row, content, url):
        """Create enhanced metadata with scraped content"""
        metadata = {
            'title': self.clean_text(row.get('title', '')),
            'authors': self.clean_text(row.get('authors', '')),
            'journal': self.clean_text(row.get('journal', '')),
            'publication_date': str(row.get('year', '')),
            'doi': self.extract_doi(row.get('doi', '')),
            'pmid': self.extract_pmid(row.get('pmid', '')),
            'document_type': 'research_paper',
            'source': row.get('source', ''),
            'search_category': row.get('search_category', ''),
            'search_query': row.get('search_query', ''),
            'scraped_url': url,
            'scraping_date': datetime.now().isoformat(),
            'content_length': len(content),
            'has_full_text': True,
            'tags': self.generate_tags(row, content),
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'content_type': 'research_paper',
            'condition': 'pmdd',
            'topic': 'premenstrual_dysphoric_disorder'
        }
        
        return metadata
    
    def clean_text(self, text):
        """Clean text content"""
        if pd.isna(text) or text == '':
            return ''
        return html.unescape(str(text)).strip()
    
    def extract_doi(self, text):
        """Extract DOI from text"""
        if pd.isna(text):
            return ''
        doi_pattern = r'10\.\d+/[^\s]+'
        match = re.search(doi_pattern, str(text))
        return match.group(0) if match else ''
    
    def extract_pmid(self, text):
        """Extract PMID from text"""
        if pd.isna(text):
            return ''
        pmid_pattern = r'PMID:\s*(\d+)'
        match = re.search(pmid_pattern, str(text))
        return match.group(1) if match else ''
    
    def generate_tags(self, row, content):
        """Generate tags based on content analysis"""
        tags = ['pmdd', 'premenstrual_dysphoric_disorder', 'hormones_endocrine']
        
        # Add category-specific tags
        category = row.get('search_category', '')
        if 'core' in category:
            tags.extend(['diagnosis', 'clinical_features'])
        elif 'symptoms' in category:
            tags.extend(['mood_symptoms', 'emotional_dysregulation'])
        elif 'hormones' in category:
            tags.extend(['estrogen', 'progesterone', 'allopregnanolone'])
        elif 'neurochemistry' in category:
            tags.extend(['serotonin', 'gaba', 'dopamine', 'neurotransmitters'])
        elif 'treatment' in category:
            tags.extend(['ssri', 'therapy', 'medication'])
        elif 'comorbidity' in category:
            tags.extend(['adhd', 'autism', 'anxiety', 'depression'])
        elif 'mechanisms' in category:
            tags.extend(['neuroimaging', 'genetics', 'pathophysiology'])
        
        # Add content-based tags
        content_lower = content.lower()
        if 'ssri' in content_lower or 'selective serotonin' in content_lower:
            tags.append('ssri_treatment')
        if 'cognitive behavioral' in content_lower or 'cbt' in content_lower:
            tags.append('cbt_treatment')
        if 'neuroimaging' in content_lower or 'brain imaging' in content_lower:
            tags.append('neuroimaging')
        if 'genetic' in content_lower or 'gene' in content_lower:
            tags.append('genetics')
        if 'zinc' in content_lower or 'magnesium' in content_lower or 'copper' in content_lower:
            tags.append('minerals')
        if 'supplement' in content_lower or 'vitamin' in content_lower:
            tags.append('supplements')
        
        return list(set(tags))  # Remove duplicates
    
    def create_filename(self, row, metadata):
        """Create a descriptive filename"""
        title = metadata['title']
        authors = metadata['authors']
        year = metadata['publication_date']
        
        # Clean title
        clean_title = re.sub(r'[^\w\s-]', '', str(title))
        clean_title = re.sub(r'\s+', '_', clean_title)
        clean_title = clean_title[:100]
        
        # Get first author's last name
        first_author = ''
        if authors:
            authors_str = str(authors)
            if ',' in authors_str:
                first_author = authors_str.split(',')[0].strip()
            else:
                first_author = authors_str.split()[0] if authors_str.split() else ''
        
        # Clean author name
        first_author = re.sub(r'[^\w\s-]', '', first_author)
        first_author = re.sub(r'\s+', '_', first_author)
        
        # Create filename
        if first_author and year:
            filename = f"{first_author}_{year}_{clean_title}.md"
        elif year:
            filename = f"{year}_{clean_title}.md"
        else:
            filename = f"{clean_title}.md"
        
        return filename.lower()
    
    def create_markdown_content(self, row, metadata, content):
        """Create the complete markdown content"""
        # Create YAML frontmatter
        yaml_frontmatter = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        
        # Create markdown content
        markdown_content = f"""---
{yaml_frontmatter}---

# {metadata['title']}

## Authors
{metadata['authors']}

## Journal
{metadata['journal']}

## Publication Information
- **Year**: {metadata['publication_date']}
- **DOI**: {metadata['doi']}
- **PMID**: {metadata['pmid']}
- **Source**: {metadata['source']}
- **Scraped from**: {metadata['scraped_url']}

## Abstract
{self.clean_text(row.get('abstract', ''))}

## Full Text Content

{content}

## Keywords
{', '.join(metadata['tags'])}

## Source Information
- **Search Category**: {metadata['search_category']}
- **Search Query**: {metadata['search_query']}
- **Scraping Date**: {metadata['scraping_date']}
- **Content Length**: {metadata['content_length']} characters

---
*This document was automatically scraped and processed from {metadata['source']} and added to the PMDD research knowledge base.*
"""
        
        return markdown_content
    
    def process_all_papers(self, max_papers=None, start_index=0):
        """Process all PMDD papers"""
        # Load papers
        df = self.load_papers()
        if df is None:
            return
        
        # Limit papers if specified
        if max_papers:
            df = df.iloc[start_index:start_index + max_papers]
        else:
            df = df.iloc[start_index:]
        
        total_papers = len(df)
        logger.info(f"Starting to process {total_papers} PMDD papers (starting from index {start_index})")
        
        # Process each paper
        for index, row in df.iterrows():
            result = self.process_paper(row, index - start_index, total_papers)
            if result:
                self.results.append(result)
            
            # Progress update every 10 papers
            if (index - start_index + 1) % 10 == 0:
                logger.info(f"Progress: {index - start_index + 1}/{total_papers} papers processed")
                logger.info(f"Success: {self.scraped_count}, Failed: {self.failed_count}, Skipped: {self.skipped_count}")
        
        # Final summary
        logger.info(f"\nScraping complete:")
        logger.info(f"Successfully scraped: {self.scraped_count}")
        logger.info(f"Failed: {self.failed_count}")
        logger.info(f"Skipped: {self.skipped_count}")
        logger.info(f"Total processed: {total_papers}")
        
        # Save results log
        self.save_results_log()
    
    def save_results_log(self):
        """Save scraping results log"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"acquired_papers/enhanced_pmdd_scraping_log_{timestamp}.yaml"
        
        log_data = {
            'scraping_summary': {
                'total_papers': len(self.results) + self.failed_count + self.skipped_count,
                'successfully_scraped': self.scraped_count,
                'failed': self.failed_count,
                'skipped': self.skipped_count,
                'success_rate': f"{(self.scraped_count / (self.scraped_count + self.failed_count + self.skipped_count) * 100):.1f}%" if (self.scraped_count + self.failed_count + self.skipped_count) > 0 else "0%",
                'timestamp': timestamp
            },
            'results': self.results
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            yaml.dump(log_data, f, default_flow_style=False)
        
        logger.info(f"Results log saved to: {log_file}")

def main():
    """Main scraping function"""
    # Find the most recent PMDD papers CSV
    acquired_dir = Path("acquired_papers")
    pmdd_files = list(acquired_dir.glob("pmdd_papers_*.csv"))
    
    if not pmdd_files:
        logger.error("No PMDD papers CSV found in acquired_papers directory")
        return
    
    # Use the most recent file
    latest_file = max(pmdd_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Processing PMDD papers from: {latest_file}")
    
    # Create scraper
    scraper = EnhancedPMDDScraper(latest_file)
    
    # Process papers (start from index 50 to continue where we left off)
    scraper.process_all_papers(max_papers=100, start_index=50)

if __name__ == "__main__":
    main()
