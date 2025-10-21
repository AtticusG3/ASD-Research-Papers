#!/usr/bin/env python3
"""
Script to webscrape the next 20 papers identified from the CSV.
Finds online sources and scrapes full-text content.
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

def find_paper_sources(doi):
    """Find online sources for a paper using its DOI."""
    sources = []
    
    # Try different DOI resolution services
    doi_urls = [
        f"https://doi.org/{doi}",
        f"https://dx.doi.org/{doi}",
    ]
    
    for doi_url in doi_urls:
        try:
            response = requests.get(doi_url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                final_url = response.url
                sources.append({
                    'url': final_url,
                    'source': 'doi_redirect',
                    'status': 'found'
                })
                
                # Check if it's a known open access source
                domain = urlparse(final_url).netloc.lower()
                if 'pmc.ncbi.nlm.nih.gov' in domain:
                    sources.append({
                        'url': final_url,
                        'source': 'pmc',
                        'status': 'open_access'
                    })
                elif 'frontiersin.org' in domain:
                    sources.append({
                        'url': final_url,
                        'source': 'frontiers',
                        'status': 'open_access'
                    })
                elif 'nature.com' in domain or 'springer.com' in domain:
                    sources.append({
                        'url': final_url,
                        'source': 'publisher',
                        'status': 'may_be_paywalled'
                    })
                
                break
        except Exception as e:
            print(f"Error resolving DOI {doi}: {e}")
            continue
    
    # Try Unpaywall API for open access versions
    try:
        unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email=research@example.com"
        response = requests.get(unpaywall_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('is_oa', False):
                oa_url = data.get('oa_locations', [{}])[0].get('url_for_pdf')
                if oa_url:
                    sources.append({
                        'url': oa_url,
                        'source': 'unpaywall',
                        'status': 'open_access_pdf'
                    })
    except Exception as e:
        print(f"Error checking Unpaywall for {doi}: {e}")
    
    return sources

def scrape_paper_content(url, title):
    """Scrape content from a paper URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find the main content
        content_selectors = [
            'article',
            '.article-content',
            '.main-content',
            '.content',
            '#content',
            '.abstract',
            '.full-text',
            '.paper-content'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            # Fallback to body if no specific content found
            content = soup.find('body')
        
        if content:
            # Extract text and clean it up
            text = content.get_text()
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean up multiple newlines
            text = text.strip()
            
            return text, "success"
        else:
            return None, "no_content_found"
            
    except Exception as e:
        return None, str(e)

def save_scraped_paper(paper_data, content, source_info, output_dir="docs/research"):
    """Save scraped paper content to markdown file."""
    # Create safe filename
    safe_title = re.sub(r'[^\w\s-]', '', paper_data['title'])
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    safe_title = safe_title[:100]  # Limit length
    
    # Determine category directory
    category = paper_data.get('category', 'tourette_syndrome')
    if category == 'tourette_syndrome':
        category_dir = 'tourette'
    elif category == 'adhd':
        category_dir = 'adhd'
    elif category == 'asd':
        category_dir = 'asd'
    else:
        category_dir = 'related-disorders'
    
    # Create directory if it doesn't exist
    paper_dir = Path(output_dir) / category_dir
    paper_dir.mkdir(parents=True, exist_ok=True)
    
    # Create markdown file
    filename = f"{safe_title}.md"
    filepath = paper_dir / filename
    
    # Create markdown content
    markdown_content = f"""---
title: "{paper_data['title']}"
authors: {paper_data['authors']}
journal: "{paper_data['journal']}"
date: "{paper_data['date']}"
doi: "{paper_data['doi']}"
category: "{category}"
source_url: "{source_info['url']}"
scraped_date: "{datetime.now().isoformat()}"
---

## Abstract

{paper_data['abstract']}

## Full Text

{content}

---
*Scraped from: {source_info['url']}*
*Source: {source_info['source']}*
*Status: {source_info['status']}*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return str(filepath)

def main():
    """Main function to scrape the next 20 papers."""
    # Load papers to scrape
    with open('papers_to_scrape_next_20.yaml', 'r', encoding='utf-8') as f:
        papers = yaml.safe_load(f)
    
    print(f"Starting to scrape {len(papers)} papers...")
    
    results = {
        'scraping_date': datetime.now().isoformat(),
        'total_papers': len(papers),
        'successful': 0,
        'failed': 0,
        'scraped_papers': [],
        'failed_papers': []
    }
    
    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}] Processing: {paper['title'][:60]}...")
        print(f"DOI: {paper['doi']}")
        
        # Find sources for this paper
        sources = find_paper_sources(paper['doi'])
        print(f"Found {len(sources)} sources")
        
        if not sources:
            print("No sources found - skipping")
            results['failed'] += 1
            results['failed_papers'].append({
                'title': paper['title'],
                'doi': paper['doi'],
                'reason': 'no_sources_found'
            })
            continue
        
        # Try to scrape from the best available source
        scraped = False
        for source in sources:
            print(f"Trying source: {source['source']} - {source['url']}")
            
            content, status = scrape_paper_content(source['url'], paper['title'])
            
            if content and len(content) > 500:  # Minimum content length
                print(f"Successfully scraped {len(content)} characters")
                
                # Save the scraped content
                filepath = save_scraped_paper(paper, content, source)
                print(f"Saved to: {filepath}")
                
                results['successful'] += 1
                results['scraped_papers'].append({
                    'title': paper['title'],
                    'doi': paper['doi'],
                    'source_url': source['url'],
                    'source_type': source['source'],
                    'filepath': filepath,
                    'content_length': len(content)
                })
                
                scraped = True
                break
            else:
                print(f"Failed to scrape: {status}")
        
        if not scraped:
            print("All sources failed - skipping")
            results['failed'] += 1
            results['failed_papers'].append({
                'title': paper['title'],
                'doi': paper['doi'],
                'reason': 'all_sources_failed',
                'sources_tried': len(sources)
            })
        
        # Be respectful - add delay between requests
        time.sleep(2)
    
    # Save results log
    log_filename = f"acquired_papers/webscraping_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    with open(log_filename, 'w', encoding='utf-8') as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n=== SCRAPING COMPLETE ===")
    print(f"Total papers: {results['total_papers']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Results saved to: {log_filename}")

if __name__ == "__main__":
    main()
