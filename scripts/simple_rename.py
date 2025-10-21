#!/usr/bin/env python3
"""
Simple script to rename research files with descriptive names
"""

import os
import re
import yaml
from pathlib import Path

def clean_title_for_filename(title):
    """Clean and shorten title for use as filename"""
    if not title or title.strip() == '':
        return "untitled_paper"
    
    # Remove common prefixes and suffixes
    title = re.sub(r'^(A|An|The)\s+', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s+(A|An|The)$', '', title, flags=re.IGNORECASE)
    
    # Remove special characters and extra whitespace
    title = re.sub(r'[^\w\s\-]', '', title)
    title = re.sub(r'\s+', '_', title)
    
    # Remove common academic suffixes
    title = re.sub(r'_(DOI|doi|DOI_|doi_)\d+.*$', '', title)
    title = re.sub(r'_(PMC|pmc|PMC_|pmc_)\d+.*$', '', title)
    title = re.sub(r'_(PMID|pmid|PMID_|pmid_)\d+.*$', '', title)
    
    # Limit length
    if len(title) > 80:
        words = title.split('_')
        result = ''
        for word in words:
            if len(result + '_' + word) <= 80:
                result += ('_' if result else '') + word
            else:
                break
        title = result
    
    if not title or title == '_':
        return "untitled_paper"
        
    return title.lower()

def extract_title_from_content(content):
    """Extract title from markdown content"""
    lines = content.split('\n')
    
    # Look for # title in the first 20 lines
    for line in lines[:20]:
        if line.startswith('# ') and len(line.strip()) > 3:
            return line[2:].strip()
    
    # Look for title in the first few lines
    for line in lines[:10]:
        line = line.strip()
        if line and not line.startswith('**') and not line.startswith('---') and len(line) > 10:
            if not any(meta in line.lower() for meta in ['authors:', 'journal:', 'doi:', 'year:', 'scraped']):
                return line
    
    return None

def get_doi_from_content(content):
    """Extract DOI from content"""
    doi_pattern = r'10\.\d+/[^\s<>"\']+'
    doi_match = re.search(doi_pattern, content)
    if doi_match:
        return doi_match.group().replace('/', '_').replace('.', '_')
    return None

def rename_file(file_path):
    """Rename a single research file"""
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Skip if file is too small
        if len(content.strip()) < 100:
            return False
        
        # Try to extract title from YAML frontmatter
        title = None
        if content.startswith('---'):
            try:
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end]
                    frontmatter = yaml.safe_load(yaml_content)
                    title = frontmatter.get('title', '')
            except:
                pass
        
        # If no title in frontmatter, extract from content
        if not title or title.strip() == '' or title == '- professional':
            title = extract_title_from_content(content)
        
        # Clean the title for filename
        clean_title = clean_title_for_filename(title)
        
        # Add DOI if available for uniqueness
        doi = get_doi_from_content(content)
        if doi and len(doi) < 20:
            clean_title += f"_{doi}"
        
        # Ensure filename is unique
        base_name = clean_title
        counter = 1
        while (file_path.parent / f"{base_name}.md").exists() and (file_path.parent / f"{base_name}.md") != file_path:
            base_name = f"{clean_title}_{counter}"
            counter += 1
        
        new_filename = f"{base_name}.md"
        
        # Skip if filename is the same
        if new_filename == file_path.name:
            return False
        
        # Create new file path and rename
        new_path = file_path.parent / new_filename
        file_path.rename(new_path)
        return True
        
    except Exception as e:
        return False

def main():
    research_dir = Path("docs/research")
    subdirs = [d for d in research_dir.iterdir() if d.is_dir() and d.name != "backup_scraped_files"]
    
    total_renamed = 0
    total_skipped = 0
    
    for subdir in subdirs:
        md_files = list(subdir.glob("*.md"))
        if not md_files:
            continue
            
        print(f"\nProcessing {subdir.name} ({len(md_files)} files):")
        renamed = 0
        skipped = 0
        
        for file_path in md_files:
            if rename_file(file_path):
                renamed += 1
            else:
                skipped += 1
        
        print(f"  Renamed: {renamed}, Skipped: {skipped}")
        total_renamed += renamed
        total_skipped += skipped
    
    print(f"\nTotal: Renamed {total_renamed}, Skipped {total_skipped}")

if __name__ == "__main__":
    main()
