#!/usr/bin/env python3
"""
Automated PMDD research paper acquisition using Paperscraper
Searches PubMed and ArXiv for research papers on Premenstrual Dysphoric Disorder
"""

import os
import time
import yaml
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Import Paperscraper modules
try:
    import paperscraper.arxiv as arxiv
    import paperscraper.pubmed as pubmed
    print("[OK] Paperscraper modules imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing Paperscraper: {e}")
    print("Please install Paperscraper: pip install paperscraper")
    exit(1)

def safe_search(func, query, max_results=50, delay=2, **kwargs):
    """Safely search with error handling and rate limiting"""
    try:
        print(f"Searching: {query}")
        results = func(query, max_results=max_results, **kwargs)
        time.sleep(delay)  # Rate limiting
        return results
    except Exception as e:
        print(f"Error searching '{query}': {e}")
        return None

def search_pmdd_papers():
    """Search for PMDD research papers"""
    print("\n[SEARCH] Searching for PMDD research papers...")
    
    # Define comprehensive PMDD search queries
    queries = {
        'pmdd_core': [
            'premenstrual dysphoric disorder',
            'PMDD',
            'premenstrual dysphoric disorder treatment',
            'premenstrual dysphoric disorder diagnosis',
            'premenstrual dysphoric disorder neurobiology'
        ],
        'pmdd_symptoms': [
            'premenstrual mood symptoms',
            'premenstrual anxiety depression',
            'premenstrual irritability',
            'premenstrual emotional dysregulation',
            'premenstrual cognitive symptoms'
        ],
        'pmdd_hormones': [
            'premenstrual hormone sensitivity',
            'estrogen progesterone PMDD',
            'allopregnanolone PMDD',
            'hormonal sensitivity premenstrual',
            'neurosteroid premenstrual'
        ],
        'pmdd_neurochemistry': [
            'serotonin PMDD',
            'GABA PMDD',
            'dopamine premenstrual',
            'neurotransmitter premenstrual',
            'brain chemistry PMDD'
        ],
        'pmdd_treatment': [
            'SSRI premenstrual dysphoric disorder',
            'oral contraceptive PMDD',
            'cognitive behavioral therapy PMDD',
            'lifestyle intervention PMDD',
            'supplement PMDD'
        ],
        'pmdd_comorbidity': [
            'PMDD ADHD',
            'PMDD autism',
            'PMDD anxiety depression',
            'PMDD neurodevelopmental',
            'premenstrual neurodevelopmental'
        ],
        'pmdd_mechanisms': [
            'PMDD pathophysiology',
            'premenstrual brain imaging',
            'PMDD neuroimaging',
            'premenstrual neuroplasticity',
            'PMDD genetic factors'
        ]
    }
    
    all_papers = []
    search_log = []
    
    # Search PubMed for each category
    for category, query_list in queries.items():
        print(f"\n[CATEGORY] {category.upper()}")
        for query in query_list:
            print(f"  Query: {query}")
            
            # Search PubMed
            pubmed_results = safe_search(
                pubmed.get_pubmed_papers,
                query,
                max_results=30,
                delay=1.5
            )
            
            if pubmed_results is not None and len(pubmed_results) > 0:
                pubmed_results['search_category'] = category
                pubmed_results['search_query'] = query
                pubmed_results['source'] = 'PubMed'
                all_papers.append(pubmed_results)
                
                search_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'source': 'PubMed',
                    'category': category,
                    'query': query,
                    'results_found': len(pubmed_results)
                })
                print(f"    Found {len(pubmed_results)} papers")
            else:
                print(f"    No results found")
                search_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'source': 'PubMed',
                    'category': category,
                    'query': query,
                    'results_found': 0
                })
    
    # Search ArXiv for additional research
    print(f"\n[SEARCH] Searching ArXiv for PMDD research...")
    arxiv_queries = [
        'premenstrual dysphoric disorder',
        'PMDD neurobiology',
        'premenstrual mood disorders',
        'hormonal sensitivity brain'
    ]
    
    for query in arxiv_queries:
        print(f"  ArXiv Query: {query}")
        arxiv_results = safe_search(
            arxiv.get_arxiv_papers_api,
            query,
            max_results=20,
            delay=1.5
        )
        
        if arxiv_results is not None and len(arxiv_results) > 0:
            arxiv_results['search_category'] = 'arxiv_general'
            arxiv_results['search_query'] = query
            arxiv_results['source'] = 'ArXiv'
            all_papers.append(arxiv_results)
            
            search_log.append({
                'timestamp': datetime.now().isoformat(),
                'source': 'ArXiv',
                'category': 'arxiv_general',
                'query': query,
                'results_found': len(arxiv_results)
            })
            print(f"    Found {len(arxiv_results)} papers")
        else:
            print(f"    No results found")
            search_log.append({
                'timestamp': datetime.now().isoformat(),
                'source': 'ArXiv',
                'category': 'arxiv_general',
                'query': query,
                'results_found': 0
            })
    
    return all_papers, search_log

def save_results(papers, search_log):
    """Save acquired papers and search log"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save papers to CSV
    if papers:
        # Combine all DataFrames
        combined_df = pd.concat(papers, ignore_index=True)
        papers_file = f"acquired_papers/pmdd_papers_{timestamp}.csv"
        combined_df.to_csv(papers_file, index=False)
        print(f"\n[SAVE] Saved {len(combined_df)} papers to {papers_file}")
        
        # Save search log
        log_file = f"acquired_papers/pmdd_search_log_{timestamp}.yaml"
        with open(log_file, 'w') as f:
            yaml.dump({
                'acquisition_summary': {
                    'total_papers': len(combined_df),
                    'timestamp': timestamp,
                    'search_categories': list(combined_df['search_category'].unique()),
                    'sources': list(combined_df['source'].unique())
                },
                'search_log': search_log
            }, f, default_flow_style=False)
        print(f"[SAVE] Saved search log to {log_file}")
        
        return papers_file, log_file
    else:
        print("\n[WARNING] No papers found to save")
        return None, None

def main():
    """Main acquisition function"""
    print("=" * 60)
    print("PMDD RESEARCH PAPER ACQUISITION")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("acquired_papers", exist_ok=True)
    
    # Search for papers
    papers, search_log = search_pmdd_papers()
    
    # Save results
    papers_file, log_file = save_results(papers, search_log)
    
    # Summary
    print("\n" + "=" * 60)
    print("ACQUISITION SUMMARY")
    print("=" * 60)
    
    if papers:
        combined_df = pd.concat(papers, ignore_index=True)
        print(f"Total papers found: {len(combined_df)}")
        
        sources = combined_df['source'].value_counts().to_dict()
        categories = combined_df['search_category'].value_counts().to_dict()
        
        print(f"Sources: {sources}")
        print(f"Categories: {categories}")
    else:
        print("Total papers found: 0")
    
    print(f"Papers saved to: {papers_file}")
    print(f"Search log saved to: {log_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
