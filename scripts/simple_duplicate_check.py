#!/usr/bin/env python3
"""
Simple duplicate check with Unicode handling
"""

import os
import yaml
import hashlib
from pathlib import Path
from collections import defaultdict, Counter

def safe_print(text):
    """Print text safely handling Unicode"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def check_duplicates():
    """Check for duplicates"""
    research_dir = Path("docs/research")
    all_files = list(research_dir.rglob("*.md"))
    
    print(f"Total files to check: {len(all_files)}")
    
    # Check for exact content duplicates
    file_hashes = defaultdict(list)
    for file_path in all_files:
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
                file_hashes[file_hash].append(file_path)
        except:
            pass
    
    content_duplicates = 0
    for file_hash, files in file_hashes.items():
        if len(files) > 1:
            content_duplicates += len(files) - 1
    
    # Check for title duplicates
    title_duplicates = defaultdict(list)
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end]
                    try:
                        frontmatter = yaml.safe_load(yaml_content)
                        title = frontmatter.get('title', '')
                        if title and title.strip():
                            clean_title = title.strip().lower()
                            title_duplicates[clean_title].append(file_path)
                    except:
                        pass
        except:
            pass
    
    title_dup_count = 0
    for title, files in title_duplicates.items():
        if len(files) > 1:
            title_dup_count += len(files) - 1
    
    # Check for DOI duplicates
    doi_duplicates = defaultdict(list)
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end]
                    try:
                        frontmatter = yaml.safe_load(yaml_content)
                        doi = frontmatter.get('doi', '')
                        if doi and doi.strip():
                            clean_doi = doi.strip().lower()
                            doi_duplicates[clean_doi].append(file_path)
                    except:
                        pass
        except:
            pass
    
    doi_dup_count = 0
    for doi, files in doi_duplicates.items():
        if len(files) > 1:
            doi_dup_count += len(files) - 1
    
    # Summary
    print("\n" + "="*50)
    print("DUPLICATE CHECK SUMMARY:")
    print(f"  Total files checked: {len(all_files)}")
    print(f"  Exact content duplicates: {content_duplicates}")
    print(f"  Title duplicates: {title_dup_count}")
    print(f"  DOI duplicates: {doi_dup_count}")
    print("="*50)
    
    # Show some examples
    print("\nTOP TITLE DUPLICATES:")
    title_counts = [(title, len(files)) for title, files in title_duplicates.items() if len(files) > 1]
    title_counts.sort(key=lambda x: x[1], reverse=True)
    
    for title, count in title_counts[:10]:
        safe_print(f"  '{title[:60]}...' - {count} files")
    
    print("\nTOP DOI DUPLICATES:")
    doi_counts = [(doi, len(files)) for doi, files in doi_duplicates.items() if len(files) > 1]
    doi_counts.sort(key=lambda x: x[1], reverse=True)
    
    for doi, count in doi_counts[:10]:
        safe_print(f"  {doi} - {count} files")
    
    return {
        'total_files': len(all_files),
        'content_duplicates': content_duplicates,
        'title_duplicates': title_dup_count,
        'doi_duplicates': doi_dup_count
    }

if __name__ == "__main__":
    results = check_duplicates()
