#!/usr/bin/env python3
"""
Rename research files with more descriptive names based on their content
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

class ResearchFileRenamer:
    def __init__(self, research_dir="docs/research"):
        self.research_dir = Path(research_dir)
        self.renamed_count = 0
        self.skipped_count = 0
        
    def clean_title_for_filename(self, title):
        """Clean and shorten title for use as filename"""
        if not title or title.strip() == '':
            return "untitled_paper"
        
        # Remove common prefixes and suffixes
        title = re.sub(r'^(A|An|The)\s+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+(A|An|The)$', '', title, flags=re.IGNORECASE)
        
        # Remove special characters and extra whitespace, but keep basic Unicode
        title = re.sub(r'[^\w\s\-]', '', title)
        title = re.sub(r'\s+', '_', title)
        
        # Remove common academic suffixes
        title = re.sub(r'_(DOI|doi|DOI_|doi_)\d+.*$', '', title)
        title = re.sub(r'_(PMC|pmc|PMC_|pmc_)\d+.*$', '', title)
        title = re.sub(r'_(PMID|pmid|PMID_|pmid_)\d+.*$', '', title)
        
        # Limit length to reasonable filename size
        if len(title) > 80:
            # Try to break at word boundaries
            words = title.split('_')
            result = ''
            for word in words:
                if len(result + '_' + word) <= 80:
                    result += ('_' if result else '') + word
                else:
                    break
            title = result
        
        # Ensure it's not empty
        if not title or title == '_':
            return "untitled_paper"
            
        return title.lower()
    
    def extract_title_from_content(self, content):
        """Extract title from markdown content if YAML frontmatter is missing title"""
        lines = content.split('\n')
        
        # Look for # title in the first 20 lines
        for line in lines[:20]:
            if line.startswith('# ') and len(line.strip()) > 3:
                return line[2:].strip()
        
        # Look for title in the first few lines
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith('**') and not line.startswith('---') and len(line) > 10:
                # Skip lines that look like metadata
                if not any(meta in line.lower() for meta in ['authors:', 'journal:', 'doi:', 'year:', 'scraped']):
                    return line
        
        return None
    
    def get_doi_from_content(self, content):
        """Extract DOI from content for additional identification"""
        doi_pattern = r'10\.\d+/[^\s<>"\']+'
        doi_match = re.search(doi_pattern, content)
        if doi_match:
            return doi_match.group().replace('/', '_').replace('.', '_')
        return None
    
    def generate_descriptive_filename(self, file_path, content):
        """Generate a descriptive filename for the research paper"""
        try:
            # Try to extract title from YAML frontmatter
            title = None
            if content.startswith('---'):
                try:
                    # Find the end of YAML frontmatter
                    yaml_end = content.find('---', 3)
                    if yaml_end != -1:
                        yaml_content = content[3:yaml_end]
                        frontmatter = yaml.safe_load(yaml_content)
                        title = frontmatter.get('title', '')
                except:
                    pass
            
            # If no title in frontmatter, extract from content
            if not title or title.strip() == '' or title == '- professional':
                title = self.extract_title_from_content(content)
            
            # Clean the title for filename
            clean_title = self.clean_title_for_filename(title)
            
            # Add DOI if available for uniqueness
            doi = self.get_doi_from_content(content)
            if doi and len(doi) < 20:  # Only add if DOI is reasonably short
                clean_title += f"_{doi}"
            
            # Ensure filename is unique
            base_name = clean_title
            counter = 1
            while (file_path.parent / f"{base_name}.md").exists() and (file_path.parent / f"{base_name}.md") != file_path:
                base_name = f"{clean_title}_{counter}"
                counter += 1
            
            return f"{base_name}.md"
            
        except Exception as e:
            print(f"  Error generating filename: {str(e)}")
            return file_path.name
    
    def rename_file(self, file_path):
        """Rename a single research file"""
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip if file is too small
            if len(content.strip()) < 100:
                print(f"  Skipped: File too small")
                self.skipped_count += 1
                return False
            
            # Generate new filename
            new_filename = self.generate_descriptive_filename(file_path, content)
            
            # Skip if filename is the same
            if new_filename == file_path.name:
                print(f"  Skipped: Name unchanged")
                self.skipped_count += 1
                return False
            
            # Create new file path
            new_path = file_path.parent / new_filename
            
            # Rename the file
            file_path.rename(new_path)
            try:
                print(f"  Renamed: {file_path.name} -> {new_filename}")
            except UnicodeEncodeError:
                print(f"  Renamed: [Unicode filename] -> {new_filename}")
            self.renamed_count += 1
            return True
            
        except Exception as e:
            print(f"  Error renaming {file_path.name}: {str(e)}")
            self.skipped_count += 1
            return False
    
    def rename_files_in_directory(self, directory_path):
        """Rename all markdown files in a directory"""
        md_files = list(directory_path.glob("*.md"))
        
        if not md_files:
            print(f"No markdown files found in {directory_path.name}")
            return
        
        print(f"\nProcessing {directory_path.name} ({len(md_files)} files):")
        print("-" * 50)
        
        for file_path in md_files:
            try:
                print(f"Processing: {file_path.name}")
                self.rename_file(file_path)
            except UnicodeEncodeError:
                print(f"Processing: [Unicode filename]")
                self.rename_file(file_path)
    
    def rename_all_research_files(self):
        """Rename all research files in all subdirectories"""
        subdirs = [d for d in self.research_dir.iterdir() if d.is_dir() and d.name != "backup_scraped_files"]
        
        if not subdirs:
            print("No research subdirectories found")
            return
        
        print(f"Found {len(subdirs)} research directories to process")
        
        for subdir in subdirs:
            self.rename_files_in_directory(subdir)
        
        print("\n" + "=" * 50)
        print(f"Renaming complete:")
        print(f"  Renamed: {self.renamed_count}")
        print(f"  Skipped: {self.skipped_count}")
        print(f"  Total: {self.renamed_count + self.skipped_count}")

def main():
    renamer = ResearchFileRenamer()
    
    print("Renaming research files with descriptive names...")
    renamer.rename_all_research_files()

if __name__ == "__main__":
    main()
