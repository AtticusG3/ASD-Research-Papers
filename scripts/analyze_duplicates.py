#!/usr/bin/env python3
"""
Analyze duplicates and professional files in the research papers collection.
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

def find_doi_duplicates():
    """Find files with duplicate DOIs."""
    doi_files = defaultdict(list)
    total_files = 0
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if file.endswith('.md'):
                total_files += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for DOI patterns
                        doi_match = re.search(r'doi:\s*([^\s\n]+)', content, re.IGNORECASE)
                        if doi_match:
                            doi = doi_match.group(1).strip()
                            # Clean up DOI
                            doi = re.sub(r'[^\w\.\-\/]', '', doi)
                            if doi and len(doi) > 5:  # Valid DOI should be longer
                                doi_files[doi].append(filepath)
                except Exception as e:
                    print(f'Error reading {filepath}: {e}')
    
    # Report duplicates
    duplicates = {doi: files for doi, files in doi_files.items() if len(files) > 1}
    
    print(f'Total files processed: {total_files}')
    print(f'Unique DOIs found: {len(doi_files)}')
    print(f'DOIs with duplicates: {len(duplicates)}')
    print(f'Total duplicate files: {sum(len(files) for files in duplicates.values())}')
    
    return duplicates

def find_professional_files():
    """Find files with 'professional' in the title."""
    professional_files = []
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check if title contains 'professional'
                        if re.search(r'title:\s*.*professional.*', content, re.IGNORECASE):
                            professional_files.append(filepath)
                except Exception as e:
                    print(f'Error reading {filepath}: {e}')
    
    print(f'Professional files found: {len(professional_files)}')
    return professional_files

def find_subdirectories():
    """Find subdirectories that should be moved to main categories."""
    subdirs = []
    
    for root, dirs, files in os.walk('docs/research'):
        # Skip the main research directory itself
        if root == 'docs/research':
            continue
            
        # Check if this is a subdirectory (has a parent that's not the main research dir)
        rel_path = os.path.relpath(root, 'docs/research')
        if '/' in rel_path or '\\' in rel_path:
            subdirs.append(root)
    
    print(f'Subdirectories found: {len(subdirs)}')
    return subdirs

def main():
    print("=== Analyzing Research Papers Collection ===\n")
    
    print("1. Finding DOI duplicates...")
    duplicates = find_doi_duplicates()
    
    print("\n2. Finding professional files...")
    professional_files = find_professional_files()
    
    print("\n3. Finding subdirectories...")
    subdirs = find_subdirectories()
    
    # Save results to JSON for further processing
    results = {
        'duplicates': {doi: files for doi, files in list(duplicates.items())[:50]},  # First 50 for analysis
        'professional_files': professional_files[:50],  # First 50 for analysis
        'subdirectories': subdirs
    }
    
    with open('duplicate_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to duplicate_analysis.json")
    
    # Show some examples
    if duplicates:
        print("\nFirst 5 duplicate DOIs:")
        for i, (doi, files) in enumerate(list(duplicates.items())[:5]):
            print(f'{i+1}. DOI: {doi}')
            for file in files:
                print(f'   - {file}')
            print()
    
    if professional_files:
        print("\nFirst 5 professional files:")
        for i, file in enumerate(professional_files[:5]):
            print(f'{i+1}. {file}')

if __name__ == '__main__':
    main()
