#!/usr/bin/env python3
"""
Test Paperscraper API to understand correct parameters
"""

import paperscraper.pubmed as pubmed
import paperscraper.arxiv as arxiv

print("Testing PubMed API...")
try:
    # Test basic PubMed search
    results = pubmed.get_pubmed_papers('tourette syndrome', max_results=5)
    print(f"PubMed basic search: Found {len(results)} results")
    if len(results) > 0:
        print("Columns:", list(results.columns))
        print("Sample result:")
        print(results.iloc[0]['title'])
except Exception as e:
    print(f"PubMed error: {e}")

print("\nTesting ArXiv API...")
try:
    # Test basic ArXiv search
    results = arxiv.get_arxiv_papers_api('tourette syndrome', max_results=5)
    print(f"ArXiv basic search: Found {len(results)} results")
    if len(results) > 0:
        print("Columns:", list(results.columns))
        print("Sample result:")
        print(results.iloc[0]['title'])
except Exception as e:
    print(f"ArXiv error: {e}")

print("\nTesting PubMed with different parameters...")
try:
    # Test PubMed with different parameter combinations
    results = pubmed.get_pubmed_papers('tourette syndrome', max_results=5, date_from='2020-01-01')
    print(f"PubMed with date_from: Found {len(results)} results")
except Exception as e:
    print(f"PubMed with date_from error: {e}")

try:
    results = pubmed.get_pubmed_papers('tourette syndrome', max_results=5, date_to='2024-12-31')
    print(f"PubMed with date_to: Found {len(results)} results")
except Exception as e:
    print(f"PubMed with date_to error: {e}")

print("\nTesting ArXiv with different parameters...")
try:
    results = arxiv.get_arxiv_papers_api('tourette syndrome', max_results=5, categories=['q-bio.NC'])
    print(f"ArXiv with categories: Found {len(results)} results")
except Exception as e:
    print(f"ArXiv with categories error: {e}")

# Check function signatures
print("\nFunction signatures:")
import inspect
print("pubmed.get_pubmed_papers signature:")
print(inspect.signature(pubmed.get_pubmed_papers))
print("\narxiv.get_arxiv_papers_api signature:")
print(inspect.signature(arxiv.get_arxiv_papers_api))
