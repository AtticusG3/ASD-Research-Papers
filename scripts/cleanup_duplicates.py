#!/usr/bin/env python3
"""
Clean up duplicate research papers based on size and location criteria
"""

import os
import yaml
import hashlib
from pathlib import Path
from collections import defaultdict
import shutil

class DuplicateCleaner:
    def __init__(self, research_dir="docs/research"):
        self.research_dir = Path(research_dir)
        self.backup_dir = Path("duplicate_cleanup_backup")
        self.removed_files = []
        self.kept_files = []
        
    def get_file_size(self, file_path):
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except:
            return 0
    
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
                            'content': content,
                            'size': len(content)
                        }
                    except yaml.YAMLError:
                        pass
            
            return {
                'title': '',
                'doi': '',
                'authors': [],
                'journal': '',
                'publication_date': '',
                'content': content,
                'size': len(content)
            }
        except:
            return None
    
    def is_failed_scrape(self, metadata):
        """Check if this looks like a failed scrape"""
        if not metadata:
            return True
        
        # Check for generic titles
        title = metadata.get('title', '').strip().lower()
        if title in ['- professional', 'title_-_professional', '']:
            return True
        
        # Check for very small content
        if metadata.get('size', 0) < 2000:  # Less than 2KB
            return True
        
        # Check for missing key metadata
        if not metadata.get('doi') and not metadata.get('journal'):
            return True
        
        return False
    
    def get_priority_directory(self, directories):
        """Determine which directory has priority for keeping files"""
        # Priority order: comorbidity > specific conditions
        if 'comorbidity' in directories:
            return 'comorbidity'
        
        # If no comorbidity, keep in the first directory alphabetically
        return sorted(directories)[0]
    
    def cleanup_duplicates(self):
        """Main cleanup function"""
        print("Starting duplicate cleanup...")
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Group files by DOI
        doi_groups = defaultdict(list)
        all_files = list(self.research_dir.rglob("*.md"))
        
        print(f"Analyzing {len(all_files)} files...")
        
        for file_path in all_files:
            metadata = self.extract_metadata(file_path)
            if metadata and metadata.get('doi'):
                doi = metadata['doi'].strip().lower()
                if doi:
                    doi_groups[doi].append((file_path, metadata))
        
        print(f"Found {len(doi_groups)} unique DOIs")
        
        # Process each DOI group
        for doi, files in doi_groups.items():
            if len(files) > 1:
                self.process_doi_group(doi, files)
        
        # Handle title duplicates (for files without DOI)
        self.handle_title_duplicates()
        
        # Summary
        print("\n" + "="*50)
        print("CLEANUP SUMMARY:")
        print(f"  Files removed: {len(self.removed_files)}")
        print(f"  Files kept: {len(self.kept_files)}")
        print("="*50)
        
        return len(self.removed_files)
    
    def process_doi_group(self, doi, files):
        """Process a group of files with the same DOI"""
        print(f"\nProcessing DOI: {doi} ({len(files)} files)")
        
        # Sort files by size (largest first)
        files.sort(key=lambda x: x[1].get('size', 0), reverse=True)
        
        # Check for failed scrapes
        failed_scrapes = []
        valid_files = []
        
        for file_path, metadata in files:
            if self.is_failed_scrape(metadata):
                failed_scrapes.append((file_path, metadata))
            else:
                valid_files.append((file_path, metadata))
        
        # Remove failed scrapes
        for file_path, metadata in failed_scrapes:
            self.remove_file(file_path, "Failed scrape")
        
        # If we have valid files, keep only the best one
        if valid_files:
            # Get directories for valid files
            directories = [f[0].parent.name for f in valid_files]
            priority_dir = self.get_priority_directory(directories)
            
            # Keep the largest file in the priority directory
            kept_file = None
            for file_path, metadata in valid_files:
                if file_path.parent.name == priority_dir:
                    if not kept_file or metadata.get('size', 0) > kept_file[1].get('size', 0):
                        kept_file = (file_path, metadata)
            
            # If no file in priority directory, keep the largest overall
            if not kept_file:
                kept_file = valid_files[0]  # Already sorted by size
            
            # Remove all other valid files
            for file_path, metadata in valid_files:
                if file_path != kept_file[0]:
                    self.remove_file(file_path, f"Duplicate of {kept_file[0].name}")
            
            self.kept_files.append(kept_file[0])
        else:
            # All files are failed scrapes, keep the largest one
            if failed_scrapes:
                kept_file = failed_scrapes[0]  # Already sorted by size
                for file_path, metadata in failed_scrapes[1:]:
                    self.remove_file(file_path, "Failed scrape duplicate")
                self.kept_files.append(kept_file[0])
    
    def handle_title_duplicates(self):
        """Handle files with duplicate titles but no DOI"""
        print("\nHandling title duplicates...")
        
        # Group files by title
        title_groups = defaultdict(list)
        all_files = list(self.research_dir.rglob("*.md"))
        
        for file_path in all_files:
            metadata = self.extract_metadata(file_path)
            if metadata and metadata.get('title') and not metadata.get('doi'):
                title = metadata['title'].strip().lower()
                if title and title != '- professional':
                    title_groups[title].append((file_path, metadata))
        
        # Process title groups with multiple files
        for title, files in title_groups.items():
            if len(files) > 1:
                self.process_title_group(title, files)
    
    def process_title_group(self, title, files):
        """Process a group of files with the same title"""
        print(f"  Processing title: '{title[:50]}...' ({len(files)} files)")
        
        # Sort by size
        files.sort(key=lambda x: x[1].get('size', 0), reverse=True)
        
        # Get directories
        directories = [f[0].parent.name for f in files]
        priority_dir = self.get_priority_directory(directories)
        
        # Keep the largest file in priority directory
        kept_file = None
        for file_path, metadata in files:
            if file_path.parent.name == priority_dir:
                if not kept_file or metadata.get('size', 0) > kept_file[1].get('size', 0):
                    kept_file = (file_path, metadata)
        
        # If no file in priority directory, keep the largest overall
        if not kept_file:
            kept_file = files[0]
        
        # Remove others
        for file_path, metadata in files:
            if file_path != kept_file[0]:
                self.remove_file(file_path, f"Title duplicate of {kept_file[0].name}")
        
        self.kept_files.append(kept_file[0])
    
    def remove_file(self, file_path, reason):
        """Remove a file and backup it"""
        try:
            # Create backup
            backup_path = self.backup_dir / file_path.relative_to(self.research_dir)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # Remove original
            file_path.unlink()
            
            self.removed_files.append((file_path, reason))
            print(f"    Removed: {file_path.relative_to(self.research_dir)} ({reason})")
            
        except Exception as e:
            print(f"    Error removing {file_path}: {str(e)}")
    
    def get_final_stats(self):
        """Get final statistics after cleanup"""
        all_files = list(self.research_dir.rglob("*.md"))
        
        stats = {}
        for file_path in all_files:
            condition = file_path.parent.name
            if condition not in stats:
                stats[condition] = 0
            stats[condition] += 1
        
        return stats

def main():
    cleaner = DuplicateCleaner()
    
    print("Starting duplicate cleanup process...")
    print("Criteria:")
    print("1. Remove smaller files when larger versions exist")
    print("2. Remove failed scrapes (generic titles, small size)")
    print("3. Keep files in comorbidity directory when duplicates exist across folders")
    print("4. Backup all removed files")
    
    removed_count = cleaner.cleanup_duplicates()
    
    # Final statistics
    final_stats = cleaner.get_final_stats()
    print("\nFINAL DIRECTORY STATS:")
    for condition, count in sorted(final_stats.items()):
        print(f"  {condition}: {count} files")
    
    total_final = sum(final_stats.values())
    print(f"\nTotal files after cleanup: {total_final}")
    print(f"Files removed: {removed_count}")
    
    if removed_count > 0:
        print(f"\nBackup created in: {cleaner.backup_dir}")
        print("You can review the backup and restore files if needed.")

if __name__ == "__main__":
    main()
