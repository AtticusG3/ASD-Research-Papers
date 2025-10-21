#!/usr/bin/env python3
"""
Fix content issues in research papers.
"""

import os
import re
import requests
from bs4 import BeautifulSoup

def fix_empty_abstracts():
    """Fix files with empty abstracts by attempting to fetch content."""
    print("=== FIXING EMPTY ABSTRACTS ===")
    
    # Find files with empty abstracts
    empty_abstract_files = []
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for empty abstract
                    if '## Abstract' in content:
                        abstract_section = content.split('## Abstract')[1].split('##')[0] if '## Abstract' in content else ''
                        if len(abstract_section.strip()) < 50:
                            empty_abstract_files.append((filepath, content))
                            
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    print(f"Found {len(empty_abstract_files)} files with empty abstracts")
    
    fixed_count = 0
    for filepath, content in empty_abstract_files:
        # Extract DOI from content
        doi_match = re.search(r'doi:\s*([^\s\n]+)', content, re.IGNORECASE)
        if doi_match:
            doi = doi_match.group(1)
            print(f"Attempting to fix {filepath} with DOI: {doi}")
            
            # Try to fetch abstract from DOI
            abstract = fetch_abstract_from_doi(doi)
            if abstract:
                # Replace empty abstract
                new_content = re.sub(
                    r'(## Abstract\s*\n)\s*\n',
                    f'\\1{abstract}\n\n',
                    content
                )
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  Fixed: {filepath}")
                    fixed_count += 1
                except Exception as e:
                    print(f"  Error writing {filepath}: {e}")
            else:
                print(f"  Could not fetch abstract for {doi}")
        else:
            print(f"  No DOI found in {filepath}")
    
    print(f"Fixed {fixed_count} files with empty abstracts")

def fetch_abstract_from_doi(doi):
    """Fetch abstract from DOI using various methods."""
    try:
        # Method 1: Try Crossref API
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data and 'abstract' in data['message']:
                abstract = data['message']['abstract']
                # Clean up the abstract
                if isinstance(abstract, str):
                    return abstract.strip()
                elif isinstance(abstract, list):
                    return ' '.join(abstract).strip()
        
        # Method 2: Try to get from DOI URL
        doi_url = f"https://doi.org/{doi}"
        response = requests.get(doi_url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common abstract selectors
            abstract_selectors = [
                '.abstract', '.article-abstract', '.abstract-content',
                '[data-testid="abstract"]', '.c-article-section__content'
            ]
            
            for selector in abstract_selectors:
                abstract_elem = soup.select_one(selector)
                if abstract_elem:
                    abstract_text = abstract_elem.get_text().strip()
                    if len(abstract_text) > 50:
                        return abstract_text
        
        return None
        
    except Exception as e:
        print(f"Error fetching abstract for DOI {doi}: {e}")
        return None

def fix_permission_text():
    """Fix files containing permission request text."""
    print("\n=== FIXING PERMISSION TEXT ===")
    
    permission_files = []
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for permission text
                    if any(pattern in content.lower() for pattern in [
                        'request permissions', 'reuse any or all of this article', 
                        'please use the link below', 'copyright notice'
                    ]):
                        permission_files.append((filepath, content))
                        
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    print(f"Found {len(permission_files)} files with permission text")
    
    fixed_count = 0
    for filepath, content in permission_files:
        # Remove permission text sections
        new_content = content
        
        # Remove common permission text patterns
        permission_patterns = [
            r'Request permissions.*?\.',
            r'If you wish to reuse any or all of this article.*?\.',
            r'Please use the link below.*?\.',
            r'Copyright notice.*?\.',
            r'All rights reserved.*?\.'
        ]
        
        for pattern in permission_patterns:
            new_content = re.sub(pattern, '', new_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
        
        if new_content != content:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed: {filepath}")
                fixed_count += 1
            except Exception as e:
                print(f"Error writing {filepath}: {e}")
    
    print(f"Fixed {fixed_count} files with permission text")

def add_missing_metadata():
    """Add missing metadata to files that only have basic content."""
    print("\n=== ADDING MISSING METADATA ===")
    
    metadata_files = []
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file has minimal content
                    lines = content.split('\n')
                    if len(lines) < 20:  # Very short files
                        metadata_files.append((filepath, content))
                        
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    print(f"Found {len(metadata_files)} files with minimal content")
    
    # For now, just report these files
    for filepath, content in metadata_files[:10]:  # Show first 10
        print(f"Minimal content: {filepath}")

def main():
    print("=== FIXING RESEARCH PAPER CONTENT ISSUES ===\n")
    
    # Fix empty abstracts
    fix_empty_abstracts()
    
    # Fix permission text
    fix_permission_text()
    
    # Add missing metadata
    add_missing_metadata()
    
    print("\n=== CONTENT FIXES COMPLETE ===")
    print("Please run the content audit again to verify improvements.")

if __name__ == '__main__':
    main()
