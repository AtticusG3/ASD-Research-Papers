#!/usr/bin/env python3
"""
Script to find papers from the CSV that need webscraping.
Identifies papers with DOIs that haven't been scraped yet.
"""

import pandas as pd
import yaml
import os
from pathlib import Path

def load_scraping_logs():
    """Load existing scraping logs to see what's already been processed."""
    scraped_dois = set()
    
    # Load HTML scraping log
    html_log_path = "acquired_papers/html_scraping_log_20251021_174632.yaml"
    if os.path.exists(html_log_path):
        with open(html_log_path, 'r', encoding='utf-8') as f:
            html_log = yaml.safe_load(f)
            for paper in html_log.get('scraped_papers', []):
                # Extract DOI from title or other fields if available
                title = paper.get('title', '')
                # We'll need to match by title since DOIs aren't in the log
                scraped_dois.add(title.lower().strip())
    
    # Load search results scraping log
    search_log_path = "acquired_papers/search_results_scraping_log_20251021_175035.yaml"
    if os.path.exists(search_log_path):
        with open(search_log_path, 'r', encoding='utf-8') as f:
            search_log = yaml.safe_load(f)
            for paper in search_log.get('scraped_papers', []):
                title = paper.get('title', '')
                scraped_dois.add(title.lower().strip())
    
    return scraped_dois

def find_papers_to_scrape():
    """Find papers with DOIs that haven't been scraped yet."""
    # Load the CSV
    csv_path = "acquired_papers/acquired_papers_20251021_161222.csv"
    df = pd.read_csv(csv_path)
    
    print(f"Total papers in CSV: {len(df)}")
    print(f"Papers with DOIs: {len(df[df['doi'].notna()])}")
    print(f"Papers without DOIs: {len(df[df['doi'].isna()])}")
    
    # Get already scraped papers
    scraped_titles = load_scraping_logs()
    print(f"Already scraped papers: {len(scraped_titles)}")
    
    # Find papers with DOIs that haven't been scraped
    papers_with_dois = df[df['doi'].notna()].copy()
    
    # Filter out already scraped papers
    papers_to_scrape = []
    for idx, row in papers_with_dois.iterrows():
        title = str(row['title']).lower().strip()
        if title not in scraped_titles:
            papers_to_scrape.append(row)
    
    print(f"Papers with DOIs that need scraping: {len(papers_to_scrape)}")
    
    # Show first 20 papers that need scraping
    print("\nFirst 20 papers that need scraping:")
    for i, paper in enumerate(papers_to_scrape[:20]):
        print(f"{i+1:2d}. {paper['title'][:80]}...")
        print(f"    DOI: {paper['doi']}")
        print(f"    Journal: {paper['journal']}")
        print(f"    Date: {paper['date']}")
        print()
    
    return papers_to_scrape[:20]  # Return first 20

if __name__ == "__main__":
    papers_to_scrape = find_papers_to_scrape()
    
    # Save the list to a file for the scraping script
    output_data = []
    for paper in papers_to_scrape:
        output_data.append({
            'title': paper['title'],
            'doi': paper['doi'],
            'journal': paper['journal'],
            'date': paper['date'],
            'authors': paper['authors'],
            'abstract': paper['abstract'],
            'category': paper['category']
        })
    
    with open('papers_to_scrape_next_20.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True)
    
    print(f"Saved {len(output_data)} papers to scrape to 'papers_to_scrape_next_20.yaml'")
