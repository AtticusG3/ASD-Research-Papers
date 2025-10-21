#!/usr/bin/env python3
"""
Automated paper acquisition using Paperscraper
Searches PubMed and ArXiv for research papers on neurodevelopmental disorders
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

def search_pubmed_papers():
    """Search PubMed for medical/clinical research papers"""
    print("\n[SEARCH] Searching PubMed...")
    
    # Define search queries for different conditions and topics
    queries = {
        'tourette_syndrome': [
            '("tourette syndrome"[Title/Abstract]) OR ("gilles de la tourette"[Title/Abstract])',
            '("tic disorder"[Title/Abstract]) OR ("chronic tic"[Title/Abstract])',
            '("tourette"[Title/Abstract]) AND ("treatment"[Title/Abstract])',
            '("tourette"[Title/Abstract]) AND ("neurobiology"[Title/Abstract])',
            '("tourette"[Title/Abstract]) AND ("dopamine"[Title/Abstract])'
        ],
        'adhd': [
            '("attention deficit hyperactivity disorder"[Title/Abstract]) OR ("ADHD"[Title/Abstract])',
            '("attention deficit disorder"[Title/Abstract]) OR ("ADD"[Title/Abstract])',
            '("ADHD"[Title/Abstract]) AND ("treatment"[Title/Abstract])',
            '("ADHD"[Title/Abstract]) AND ("neurobiology"[Title/Abstract])',
            '("ADHD"[Title/Abstract]) AND ("dopamine"[Title/Abstract])'
        ],
        'asd': [
            '("autism spectrum disorder"[Title/Abstract]) OR ("ASD"[Title/Abstract])',
            '("autism"[Title/Abstract]) OR ("asperger syndrome"[Title/Abstract])',
            '("autism"[Title/Abstract]) AND ("treatment"[Title/Abstract])',
            '("autism"[Title/Abstract]) AND ("neurobiology"[Title/Abstract])'
        ],
        'related_disorders': [
            '("obsessive compulsive disorder"[Title/Abstract]) OR ("OCD"[Title/Abstract])',
            '("anxiety disorder"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("depression"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("sensory processing disorder"[Title/Abstract])',
            '("learning disability"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])'
        ],
        'neurochemistry': [
            '("dopamine"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("serotonin"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("norepinephrine"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("glutamate"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("GABA"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("neurotransmitter"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])'
        ],
        'hormones': [
            '("cortisol"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("stress hormone"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("thyroid"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("testosterone"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("estrogen"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("growth hormone"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])'
        ],
        'comorbidity': [
            '("comorbidity"[Title/Abstract]) AND ("neurodevelopmental"[Title/Abstract])',
            '("tourette"[Title/Abstract]) AND ("ADHD"[Title/Abstract])',
            '("tourette"[Title/Abstract]) AND ("autism"[Title/Abstract])',
            '("ADHD"[Title/Abstract]) AND ("autism"[Title/Abstract])',
            '("neurodevelopmental disorders"[Title/Abstract]) AND ("comorbidity"[Title/Abstract])'
        ]
    }
    
    all_results = []
    
    for category, query_list in queries.items():
        print(f"\n📂 Category: {category}")
        category_results = []
        
        for query in query_list:
            # Search with date filter (1970-2025)
            results = safe_search(
                pubmed.get_pubmed_papers,
                query,
                max_results=30,
                date_from='1970-01-01',
                date_to='2025-12-31'
            )
            
            if results is not None and len(results) > 0:
                results['category'] = category
                results['search_query'] = query
                results['source'] = 'pubmed'
                category_results.append(results)
                print(f"  Found {len(results)} papers for: {query[:50]}...")
            else:
                print(f"  No results for: {query[:50]}...")
        
        if category_results:
            combined_category = pd.concat(category_results, ignore_index=True)
            all_results.append(combined_category)
    
    return all_results

def search_arxiv_papers():
    """Search ArXiv for neuroscience/computational papers"""
    print("\n🔍 Searching ArXiv...")
    
    queries = [
        'tourette syndrome neurobiology',
        'ADHD brain imaging',
        'autism spectrum disorder neurochemistry',
        'neurodevelopmental disorders dopamine',
        'tic disorders neural networks',
        'attention deficit brain structure',
        'neurotransmitter neurodevelopmental'
    ]
    
    all_results = []
    
    for query in queries:
        results = safe_search(
            arxiv.get_arxiv_papers_api,
            query,
            max_results=20,
            categories=['q-bio.NC', 'q-bio.NEU', 'stat.AP']  # Neuroscience, Neuroimaging, Applied Statistics
        )
        
        if results is not None and len(results) > 0:
            results['source'] = 'arxiv'
            results['search_query'] = query
            all_results.append(results)
            print(f"  Found {len(results)} papers for: {query}")
        else:
            print(f"  No results for: {query}")
    
    return all_results

def deduplicate_papers(all_results):
    """Remove duplicate papers based on title"""
    if not all_results:
        return pd.DataFrame()
    
    # Combine all results
    combined = pd.concat(all_results, ignore_index=True)
    
    # Remove duplicates based on title (case-insensitive)
    combined['title_lower'] = combined['title'].str.lower()
    deduplicated = combined.drop_duplicates(subset=['title_lower'], keep='first')
    
    # Remove the helper column
    deduplicated = deduplicated.drop('title_lower', axis=1)
    
    print(f"\n📊 Deduplication: {len(combined)} -> {len(deduplicated)} papers")
    return deduplicated

def save_results(results_df, output_dir):
    """Save results to CSV and create acquisition log"""
    if results_df.empty:
        print("No results to save")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save to CSV
    csv_file = output_path / f"acquired_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(csv_file, index=False)
    print(f"💾 Saved {len(results_df)} papers to: {csv_file}")
    
    # Create acquisition log
    log_data = {
        'acquisition_date': datetime.now().isoformat(),
        'total_papers': len(results_df),
        'sources': {
            'pubmed': len(results_df[results_df['source'] == 'pubmed']),
            'arxiv': len(results_df[results_df['source'] == 'arxiv'])
        },
        'categories': results_df['category'].value_counts().to_dict() if 'category' in results_df.columns else {},
        'date_range': '1970-2025',
        'output_file': str(csv_file)
    }
    
    log_file = output_path / 'acquisition_log.yaml'
    with open(log_file, 'w', encoding='utf-8') as f:
        yaml.dump(log_data, f, default_flow_style=False)
    
    print(f"📝 Created acquisition log: {log_file}")
    
    # Print summary
    print(f"\n📈 Acquisition Summary:")
    print(f"  Total papers: {len(results_df)}")
    if 'source' in results_df.columns:
        print(f"  PubMed: {len(results_df[results_df['source'] == 'pubmed'])}")
        print(f"  ArXiv: {len(results_df[results_df['source'] == 'arxiv'])}")
    if 'category' in results_df.columns:
        print(f"  Categories:")
        for category, count in results_df['category'].value_counts().items():
            print(f"    {category}: {count}")

def main():
    """Main acquisition function"""
    print("🚀 Starting automated paper acquisition...")
    print(f"📅 Date range: 1970-2025")
    print(f"🔧 Using Paperscraper v0.3.2")
    
    # Search PubMed
    pubmed_results = search_pubmed_papers()
    
    # Search ArXiv
    arxiv_results = search_arxiv_papers()
    
    # Combine and deduplicate
    all_results = []
    if pubmed_results:
        all_results.extend(pubmed_results)
    if arxiv_results:
        all_results.extend(arxiv_results)
    
    if not all_results:
        print("❌ No papers found")
        return
    
    # Deduplicate
    final_results = deduplicate_papers(all_results)
    
    # Save results
    save_results(final_results, 'acquired_papers')
    
    print("\n✅ Paper acquisition completed!")

if __name__ == "__main__":
    main()
