#!/usr/bin/env python3
"""
Check for duplicate research papers across all directories
"""

import os
import yaml
import hashlib
from pathlib import Path
from collections import defaultdict, Counter

class DuplicateChecker:
    def __init__(self, research_dir="docs/research"):
        self.research_dir = Path(research_dir)
        self.file_hashes = defaultdict(list)
        self.title_duplicates = defaultdict(list)
        self.doi_duplicates = defaultdict(list)
        self.content_duplicates = defaultdict(list)
        
    def get_file_hash(self, file_path):
        """Get MD5 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def extract_metadata(self, file_path):
        """Extract metadata from file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end]
                    try:
                        frontmatter = yaml.safe_load(yaml_content)
                        return {
                            'title': frontmatter.get('title', ''),
                            'doi': frontmatter.get('doi', ''),
                            'authors': frontmatter.get('authors', []),
                            'journal': frontmatter.get('journal', ''),
                            'publication_date': frontmatter.get('publication_date', ''),
                            'content': content
                        }
                    except yaml.YAMLError:
                        pass
            
            return {
                'title': '',
                'doi': '',
                'authors': [],
                'journal': '',
                'publication_date': '',
                'content': content
            }
        except:
            return None
    
    def check_duplicates(self):
        """Check for various types of duplicates"""
        print("Checking for duplicates...")
        
        all_files = list(self.research_dir.rglob("*.md"))
        print(f"Total files to check: {len(all_files)}")
        
        # Check for exact file content duplicates
        print("\n1. Checking for exact file content duplicates...")
        content_duplicates = 0
        
        for file_path in all_files:
            file_hash = self.get_file_hash(file_path)
            if file_hash:
                self.file_hashes[file_hash].append(file_path)
        
        for file_hash, files in self.file_hashes.items():
            if len(files) > 1:
                content_duplicates += len(files) - 1
                print(f"  Found {len(files)} identical files:")
                for file_path in files:
                    print(f"    - {file_path.relative_to(self.research_dir)}")
        
        print(f"  Total content duplicates: {content_duplicates}")
        
        # Check for title duplicates
        print("\n2. Checking for title duplicates...")
        title_duplicates = 0
        
        for file_path in all_files:
            metadata = self.extract_metadata(file_path)
            if metadata and metadata['title']:
                clean_title = metadata['title'].strip().lower()
                if clean_title:
                    self.title_duplicates[clean_title].append((file_path, metadata))
        
        for title, files in self.title_duplicates.items():
            if len(files) > 1:
                title_duplicates += len(files) - 1
                print(f"  Found {len(files)} files with title: '{title[:80]}...'")
                for file_path, metadata in files:
                    print(f"    - {file_path.relative_to(self.research_dir)}")
                    if metadata['doi']:
                        print(f"      DOI: {metadata['doi']}")
        
        print(f"  Total title duplicates: {title_duplicates}")
        
        # Check for DOI duplicates
        print("\n3. Checking for DOI duplicates...")
        doi_duplicates = 0
        
        for file_path in all_files:
            metadata = self.extract_metadata(file_path)
            if metadata and metadata['doi']:
                clean_doi = metadata['doi'].strip().lower()
                if clean_doi:
                    self.doi_duplicates[clean_doi].append((file_path, metadata))
        
        for doi, files in self.doi_duplicates.items():
            if len(files) > 1:
                doi_duplicates += len(files) - 1
                print(f"  Found {len(files)} files with DOI: {doi}")
                for file_path, metadata in files:
                    print(f"    - {file_path.relative_to(self.research_dir)}")
                    print(f"      Title: {metadata['title'][:80]}...")
        
        print(f"  Total DOI duplicates: {doi_duplicates}")
        
        # Check for similar content (first 1000 characters)
        print("\n4. Checking for similar content...")
        content_similarities = 0
        content_hashes = defaultdict(list)
        
        for file_path in all_files:
            metadata = self.extract_metadata(file_path)
            if metadata and metadata['content']:
                # Use first 1000 characters for similarity check
                content_sample = metadata['content'][:1000].strip()
                if content_sample:
                    content_hash = hashlib.md5(content_sample.encode()).hexdigest()
                    content_hashes[content_hash].append((file_path, metadata))
        
        for content_hash, files in content_hashes.items():
            if len(files) > 1:
                content_similarities += len(files) - 1
                print(f"  Found {len(files)} files with similar content:")
                for file_path, metadata in files:
                    print(f"    - {file_path.relative_to(self.research_dir)}")
                    if metadata['title']:
                        print(f"      Title: {metadata['title'][:60]}...")
        
        print(f"  Total content similarities: {content_similarities}")
        
        # Summary
        print("\n" + "="*50)
        print("DUPLICATE CHECK SUMMARY:")
        print(f"  Exact content duplicates: {content_duplicates}")
        print(f"  Title duplicates: {title_duplicates}")
        print(f"  DOI duplicates: {doi_duplicates}")
        print(f"  Content similarities: {content_similarities}")
        print(f"  Total files checked: {len(all_files)}")
        print("="*50)
        
        return {
            'content_duplicates': content_duplicates,
            'title_duplicates': title_duplicates,
            'doi_duplicates': doi_duplicates,
            'content_similarities': content_similarities,
            'total_files': len(all_files)
        }

def main():
    checker = DuplicateChecker()
    results = checker.check_duplicates()
    
    # Save results to file
    with open('duplicate_check_results.txt', 'w') as f:
        f.write("Duplicate Check Results\n")
        f.write("="*50 + "\n")
        f.write(f"Exact content duplicates: {results['content_duplicates']}\n")
        f.write(f"Title duplicates: {results['title_duplicates']}\n")
        f.write(f"DOI duplicates: {results['doi_duplicates']}\n")
        f.write(f"Content similarities: {results['content_similarities']}\n")
        f.write(f"Total files checked: {results['total_files']}\n")

if __name__ == "__main__":
    main()
