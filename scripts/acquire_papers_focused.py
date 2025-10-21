#!/usr/bin/env python3
"""
Focused paper acquisition using Paperscraper
Acquires a smaller, targeted set of papers for testing
"""

import os
import time
import yaml
import pandas as pd
from datetime import datetime
from pathlib import Path

# Import Paperscraper modules
try:
    import paperscraper.arxiv as arxiv
    import paperscraper.pubmed as pubmed
    print("[OK] Paperscraper modules imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing Paperscraper: {e}")
    exit(1)

def safe_search(func, query, max_results=10, delay=2):
    """Safely search with error handling and rate limiting"""
    try:
        print(f"Searching: {query}")
        results = func(query, max_results=max_results)
        time.sleep(delay)  # Rate limiting
        return results
    except Exception as e:
        print(f"Error searching '{query}': {e}")
        return None

def acquire_focused_papers():
    """Acquire a focused set of papers for testing"""
    print("[START] Starting focused paper acquisition...")
    
    # Define focused search queries
    queries = {
        'tourette_syndrome': [
            'tourette syndrome',
            'tic disorder',
            'gilles de la tourette'
        ],
        'adhd': [
            'ADHD',
            'attention deficit hyperactivity disorder',
            'attention deficit disorder'
        ],
        'asd': [
            'autism spectrum disorder',
            'autism',
            'asperger syndrome'
        ],
        'neurochemistry': [
            'dopamine neurodevelopmental',
            'serotonin neurodevelopmental',
            'neurotransmitter neurodevelopmental'
        ],
        'hormones': [
            'cortisol neurodevelopmental',
            'thyroid neurodevelopmental',
            'stress hormone neurodevelopmental'
        ]
    }
    
    all_results = []
    
    for category, query_list in queries.items():
        print(f"\n[CATEGORY] {category}")
        category_results = []
        
        for query in query_list:
            # Search PubMed
            results = safe_search(pubmed.get_pubmed_papers, query, max_results=5)
            
            if results is not None and len(results) > 0:
                results['category'] = category
                results['search_query'] = query
                results['source'] = 'pubmed'
                category_results.append(results)
                print(f"  Found {len(results)} papers for: {query}")
            else:
                print(f"  No results for: {query}")
        
        if category_results:
            combined_category = pd.concat(category_results, ignore_index=True)
            all_results.append(combined_category)
    
    # Search ArXiv for a few queries
    print(f"\n[CATEGORY] arxiv_neuroscience")
    arxiv_queries = [
        'tourette syndrome neurobiology',
        'ADHD brain imaging',
        'autism neurochemistry'
    ]
    
    for query in arxiv_queries:
        results = safe_search(arxiv.get_arxiv_papers_api, query, max_results=3)
        
        if results is not None and len(results) > 0:
            results['category'] = 'arxiv_neuroscience'
            results['search_query'] = query
            results['source'] = 'arxiv'
            all_results.append(results)
            print(f"  Found {len(results)} papers for: {query}")
        else:
            print(f"  No results for: {query}")
    
    return all_results

def save_results(results_list, output_dir):
    """Save results to CSV and create acquisition log"""
    if not results_list:
        print("No results to save")
        return
    
    # Combine all results
    combined = pd.concat(results_list, ignore_index=True)
    
    # Remove duplicates based on title
    combined['title_lower'] = combined['title'].str.lower()
    deduplicated = combined.drop_duplicates(subset=['title_lower'], keep='first')
    deduplicated = deduplicated.drop('title_lower', axis=1)
    
    print(f"\n[DEDUP] Deduplication: {len(combined)} -> {len(deduplicated)} papers")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save to CSV
    csv_file = output_path / f"focused_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    deduplicated.to_csv(csv_file, index=False)
    print(f"[SAVE] Saved {len(deduplicated)} papers to: {csv_file}")
    
    # Create acquisition log
    log_data = {
        'acquisition_date': datetime.now().isoformat(),
        'total_papers': len(deduplicated),
        'sources': {
            'pubmed': len(deduplicated[deduplicated['source'] == 'pubmed']),
            'arxiv': len(deduplicated[deduplicated['source'] == 'arxiv'])
        },
        'categories': deduplicated['category'].value_counts().to_dict(),
        'output_file': str(csv_file)
    }
    
    log_file = output_path / 'focused_acquisition_log.yaml'
    with open(log_file, 'w', encoding='utf-8') as f:
        yaml.dump(log_data, f, default_flow_style=False)
    
    print(f"[LOG] Created acquisition log: {log_file}")
    
    # Print summary
    print(f"\n[SUMMARY] Acquisition Summary:")
    print(f"  Total papers: {len(deduplicated)}")
    print(f"  PubMed: {len(deduplicated[deduplicated['source'] == 'pubmed'])}")
    print(f"  ArXiv: {len(deduplicated[deduplicated['source'] == 'arxiv'])}")
    print(f"  Categories:")
    for category, count in deduplicated['category'].value_counts().items():
        print(f"    {category}: {count}")
    
    return deduplicated

def main():
    """Main acquisition function"""
    print("[START] Starting focused paper acquisition...")
    print(f"[INFO] Target: Small focused set for testing")
    
    # Acquire papers
    results = acquire_focused_papers()
    
    if not results:
        print("[ERROR] No papers found")
        return
    
    # Save results
    final_results = save_results(results, 'acquired_papers')
    
    print("\n[COMPLETE] Focused paper acquisition completed!")
    return final_results

if __name__ == "__main__":
    main()
