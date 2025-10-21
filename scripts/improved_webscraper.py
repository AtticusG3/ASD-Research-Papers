#!/usr/bin/env python3
"""
Improved webscraper for research papers with better content detection.
"""

import yaml
import requests
from bs4 import BeautifulSoup
import time
import os
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

def scrape_paper_content_improved(url, title):
    """Improved content scraping with better detection."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try multiple content extraction strategies
        content = None
        content_text = ""
        
        # Strategy 1: Look for specific article containers
        article_selectors = [
            'article',
            '.article-content',
            '.main-content',
            '.content',
            '#content',
            '.abstract',
            '.full-text',
            '.paper-content',
            '.article-body',
            '.entry-content',
            '.post-content',
            '.article-text',
            '.paper-text',
            '.research-article',
            '.journal-article'
        ]
        
        for selector in article_selectors:
            content = soup.select_one(selector)
            if content:
                content_text = content.get_text()
                if len(content_text) > 1000:  # Minimum meaningful content
                    break
        
        # Strategy 2: If no article found, try to find the main content area
        if not content or len(content_text) < 1000:
            # Look for divs with lots of text
            all_divs = soup.find_all('div')
            best_div = None
            max_text_length = 0
            
            for div in all_divs:
                text = div.get_text()
                if len(text) > max_text_length and len(text) > 1000:
                    max_text_length = len(text)
                    best_div = div
            
            if best_div:
                content_text = best_div.get_text()
        
        # Strategy 3: If still no good content, try the body
        if len(content_text) < 1000:
            body = soup.find('body')
            if body:
                content_text = body.get_text()
        
        if content_text and len(content_text) > 500:
            # Clean up the text
            content_text = re.sub(r'\n\s*\n', '\n\n', content_text)  # Clean up multiple newlines
            content_text = re.sub(r'\s+', ' ', content_text)  # Normalize whitespace
            content_text = content_text.strip()
            
            return content_text, "success"
        else:
            return None, "insufficient_content"
            
    except Exception as e:
        return None, str(e)

def try_alternative_sources(doi):
    """Try alternative sources for papers that failed initial scraping."""
    alternative_sources = []
    
    # Try PubMed Central directly
    if doi:
        pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{doi.split('.')[-1]}/"
        alternative_sources.append({
            'url': pmc_url,
            'source': 'pmc_direct',
            'status': 'alternative'
        })
    
    # Try Google Scholar
    scholar_url = f"https://scholar.google.com/scholar?q={doi}"
    alternative_sources.append({
        'url': scholar_url,
        'source': 'google_scholar',
        'status': 'alternative'
    })
    
    return alternative_sources

def scrape_failed_papers():
    """Re-attempt scraping for papers that failed in the first run."""
    # Load the previous results
    log_files = list(Path("acquired_papers").glob("webscraping_log_*.yaml"))
    if not log_files:
        print("No previous scraping logs found")
        return
    
    latest_log = max(log_files, key=os.path.getctime)
    print(f"Loading previous results from: {latest_log}")
    
    with open(latest_log, 'r', encoding='utf-8') as f:
        results = yaml.safe_load(f)
    
    failed_papers = results.get('failed_papers', [])
    print(f"Found {len(failed_papers)} failed papers to retry")
    
    # Load the original paper data
    with open('papers_to_scrape_next_20.yaml', 'r', encoding='utf-8') as f:
        all_papers = yaml.safe_load(f)
    
    # Create a lookup for paper data by title
    paper_lookup = {paper['title']: paper for paper in all_papers}
    
    retry_results = {
        'retry_date': datetime.now().isoformat(),
        'total_retried': len(failed_papers),
        'successful': 0,
        'failed': 0,
        'retry_successful': [],
        'retry_failed': []
    }
    
    for i, failed_paper in enumerate(failed_papers, 1):
        title = failed_paper['title']
        doi = failed_paper['doi']
        
        print(f"\n[{i}/{len(failed_papers)}] Retrying: {title[:60]}...")
        print(f"DOI: {doi}")
        
        # Get the full paper data
        paper_data = paper_lookup.get(title)
        if not paper_data:
            print("Paper data not found - skipping")
            continue
        
        # Try alternative sources
        alt_sources = try_alternative_sources(doi)
        print(f"Trying {len(alt_sources)} alternative sources")
        
        scraped = False
        for source in alt_sources:
            print(f"Trying: {source['source']} - {source['url']}")
            
            content, status = scrape_paper_content_improved(source['url'], title)
            
            if content and len(content) > 1000:
                print(f"Successfully scraped {len(content)} characters")
                
                # Save the scraped content
                from webscrape_next_20_papers import save_scraped_paper
                filepath = save_scraped_paper(paper_data, content, source)
                print(f"Saved to: {filepath}")
                
                retry_results['successful'] += 1
                retry_results['retry_successful'].append({
                    'title': title,
                    'doi': doi,
                    'source_url': source['url'],
                    'source_type': source['source'],
                    'filepath': filepath,
                    'content_length': len(content)
                })
                
                scraped = True
                break
            else:
                print(f"Failed: {status}")
        
        if not scraped:
            print("All alternative sources failed")
            retry_results['failed'] += 1
            retry_results['retry_failed'].append({
                'title': title,
                'doi': doi,
                'reason': 'all_alternative_sources_failed'
            })
        
        time.sleep(3)  # Be respectful
    
    # Save retry results
    retry_log = f"acquired_papers/retry_scraping_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    with open(retry_log, 'w', encoding='utf-8') as f:
        yaml.dump(retry_results, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n=== RETRY COMPLETE ===")
    print(f"Total retried: {retry_results['total_retried']}")
    print(f"Successful: {retry_results['successful']}")
    print(f"Failed: {retry_results['failed']}")
    print(f"Results saved to: {retry_log}")

if __name__ == "__main__":
    scrape_failed_papers()
