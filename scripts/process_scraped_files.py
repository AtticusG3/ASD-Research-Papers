#!/usr/bin/env python3
"""
Process and clean up the scraped_### files in the research directory
"""

import os
import re
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import html

class ScrapedFileProcessor:
    def __init__(self, research_dir="docs/research"):
        self.research_dir = Path(research_dir)
        self.processed_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
    def clean_html_content(self, content):
        """Clean HTML artifacts and JavaScript from content"""
        # Remove JavaScript blocks
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML redirects and tracking code
        content = re.sub(r'Redirecting.*?window\.location.*?;', '', content, flags=re.DOTALL)
        content = re.sub(r'siteCatalyst\.pageDataLoad.*?;', '', content, flags=re.DOTALL)
        content = re.sub(r'var timerStart.*?;', '', content, flags=re.DOTALL)
        content = re.sub(r'function autoRedirectToURL.*?}', '', content, flags=re.DOTALL)
        
        # Remove HTML tags but keep content
        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Clean up extra whitespace
        text_content = re.sub(r'\n\s*\n\s*\n', '\n\n', text_content)
        text_content = re.sub(r'^\s+|\s+$', '', text_content, flags=re.MULTILINE)
        
        return text_content
    
    def extract_metadata_from_content(self, content, filename):
        """Extract metadata from the cleaned content"""
        metadata = {
            'title': '',
            'authors': [],
            'journal': '',
            'doi': '',
            'publication_date': '',
            'abstract': '',
            'source': 'Processed from scraped content',
            'processing_date': datetime.now().isoformat(),
            'original_filename': filename
        }
        
        lines = content.split('\n')
        
        # Extract title (usually first line or after #)
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
                break
            elif line.strip() and not line.startswith('**') and len(line) > 10:
                metadata['title'] = line.strip()
                break
        
        # Extract DOI
        doi_pattern = r'10\.\d+/[^\s<>"\']+'
        doi_match = re.search(doi_pattern, content)
        if doi_match:
            metadata['doi'] = doi_match.group()
        
        # Extract journal
        journal_pattern = r'\*\*Journal:\*\*\s*(.+)'
        journal_match = re.search(journal_pattern, content)
        if journal_match:
            metadata['journal'] = journal_match.group(1).strip()
        
        # Extract authors
        authors_pattern = r'\*\*Authors:\*\*\s*(.+)'
        authors_match = re.search(authors_pattern, content)
        if authors_match:
            authors_str = authors_match.group(1).strip()
            # Parse authors list
            if authors_str.startswith('[') and authors_str.endswith(']'):
                authors_str = authors_str[1:-1]
                metadata['authors'] = [author.strip().strip("'\"") for author in authors_str.split(',')]
            else:
                metadata['authors'] = [authors_str]
        
        # Extract abstract
        abstract_start = content.find('## Abstract')
        if abstract_start != -1:
            abstract_end = content.find('##', abstract_start + 1)
            if abstract_end == -1:
                abstract_end = content.find('## Full Text')
            if abstract_end == -1:
                abstract_end = len(content)
            
            abstract_content = content[abstract_start:abstract_end]
            # Remove the "## Abstract" header
            abstract_content = re.sub(r'^## Abstract\s*\n?', '', abstract_content)
            metadata['abstract'] = abstract_content.strip()
        
        return metadata
    
    def categorize_paper(self, metadata, content):
        """Categorize paper based on content and metadata"""
        categories = []
        conditions = []
        topics = []
        
        # Convert to lowercase for matching
        title_lower = metadata.get('title', '').lower()
        abstract_lower = metadata.get('abstract', '').lower()
        content_lower = content.lower()
        
        # Condition detection
        if any(term in content_lower for term in ['tourette', 'tic disorder', 'gilles de la tourette']):
            conditions.append('tourette_syndrome')
            categories.append('tourette')
        
        if any(term in content_lower for term in ['adhd', 'attention deficit', 'hyperactivity']):
            conditions.append('adhd')
            categories.append('adhd')
        
        if any(term in content_lower for term in ['autism', 'asd', 'autism spectrum']):
            conditions.append('asd')
            categories.append('asd')
        
        if any(term in content_lower for term in ['ocd', 'obsessive compulsive', 'anxiety', 'depression']):
            conditions.append('related_disorders')
            categories.append('related-disorders')
        
        # Topic detection
        if any(term in content_lower for term in ['dopamine', 'neurotransmitter', 'brain chemistry']):
            topics.append('neurochemistry')
            categories.append('neurochemistry')
        
        if any(term in content_lower for term in ['hormone', 'cortisol', 'thyroid', 'endocrine']):
            topics.append('hormones_endocrine')
            categories.append('hormones-endocrine')
        
        if any(term in content_lower for term in ['comorbidity', 'co-occurring', 'multiple conditions']):
            topics.append('comorbidity')
            categories.append('comorbidity')
        
        # Default categorization if none found
        if not categories:
            categories = ['related-disorders']
            conditions = ['related_disorders']
            topics = ['general']
        
        return {
            'categories': categories,
            'conditions': conditions,
            'topics': topics
        }
    
    def create_enriched_markdown(self, content, metadata, categorization):
        """Create properly formatted markdown with YAML frontmatter"""
        # Create YAML frontmatter
        frontmatter = {
            'title': metadata['title'],
            'authors': metadata['authors'],
            'journal': metadata['journal'],
            'doi': metadata['doi'],
            'publication_date': metadata['publication_date'],
            'source': metadata['source'],
            'processing_date': metadata['processing_date'],
            'content_type': 'research_paper',
            'conditions': categorization['conditions'],
            'topics': categorization['topics'],
            'categories': categorization['categories'],
            'reading_level': 'academic',
            'audience': ['professional', 'researcher'],
            'patient_friendly': False,
            'search_priority': 'standard'
        }
        
        # Create search tags
        search_tags = []
        search_tags.extend(categorization['conditions'])
        search_tags.extend(categorization['topics'])
        search_tags.extend(['research', 'academic', 'peer-reviewed'])
        
        # Add keywords from title and abstract
        title_words = re.findall(r'\b\w+\b', metadata['title'].lower())
        abstract_words = re.findall(r'\b\w+\b', metadata['abstract'].lower())
        
        # Filter for relevant keywords
        relevant_keywords = []
        keyword_terms = ['treatment', 'therapy', 'medication', 'behavioral', 'cognitive', 
                        'neurobiology', 'genetic', 'epidemiology', 'quality', 'life',
                        'children', 'adults', 'adolescents', 'clinical', 'trial']
        
        for word in title_words + abstract_words:
            if len(word) > 4 and word in keyword_terms:
                relevant_keywords.append(word)
        
        frontmatter['keywords'] = list(set(relevant_keywords))[:20]  # Limit to 20 keywords
        frontmatter['search_tags'] = list(set(search_tags))
        
        # Create the markdown content
        yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        
        markdown_content = f"---\n{yaml_content}---\n\n"
        
        # Add title
        if metadata['title']:
            markdown_content += f"# {metadata['title']}\n\n"
        
        # Add authors
        if metadata['authors']:
            authors_str = ', '.join(metadata['authors'])
            markdown_content += f"**Authors:** {authors_str}\n\n"
        
        # Add journal and DOI
        if metadata['journal']:
            markdown_content += f"**Journal:** {metadata['journal']}\n\n"
        if metadata['doi']:
            markdown_content += f"**DOI:** {metadata['doi']}\n\n"
        
        # Add abstract
        if metadata['abstract']:
            markdown_content += f"## Abstract\n\n{metadata['abstract']}\n\n"
        
        # Add main content (cleaned)
        main_content = content
        # Remove the title if it's already in the content
        if metadata['title'] and main_content.startswith(f"# {metadata['title']}"):
            main_content = main_content[len(f"# {metadata['title']}"):].strip()
        
        # Remove metadata lines that are now in frontmatter
        main_content = re.sub(r'\*\*Authors:\*\*.*?\n', '', main_content)
        main_content = re.sub(r'\*\*Journal:\*\*.*?\n', '', main_content)
        main_content = re.sub(r'\*\*DOI:\*\*.*?\n', '', main_content)
        main_content = re.sub(r'\*\*Year:\*\*.*?\n', '', main_content)
        main_content = re.sub(r'\*\*Scraped from:\*\*.*?\n', '', main_content)
        main_content = re.sub(r'\*\*Scraped by:\*\*.*?\n', '', main_content)
        main_content = re.sub(r'\*\*Scraping date:\*\*.*?\n', '', main_content)
        
        markdown_content += main_content
        
        return markdown_content
    
    def determine_target_directory(self, categorization):
        """Determine the target directory based on categorization"""
        if 'tourette' in categorization['categories']:
            return self.research_dir / 'tourette'
        elif 'adhd' in categorization['categories']:
            return self.research_dir / 'adhd'
        elif 'asd' in categorization['categories']:
            return self.research_dir / 'asd'
        elif 'neurochemistry' in categorization['categories']:
            return self.research_dir / 'neurochemistry'
        elif 'hormones-endocrine' in categorization['categories']:
            return self.research_dir / 'hormones-endocrine'
        elif 'comorbidity' in categorization['categories']:
            return self.research_dir / 'comorbidity'
        else:
            return self.research_dir / 'related-disorders'
    
    def generate_clean_filename(self, metadata):
        """Generate a clean filename from the title"""
        title = metadata.get('title', 'Untitled Paper')
        
        # Clean the title for filename
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        clean_title = clean_title[:100]  # Limit length
        
        return f"{clean_title}.md"
    
    def process_file(self, file_path):
        """Process a single scraped file"""
        try:
            print(f"Processing: {file_path.name}")
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip if file is too small or empty
            if len(content.strip()) < 100:
                print(f"  Skipped: File too small ({len(content)} chars)")
                self.skipped_count += 1
                return False
            
            # Clean the content
            cleaned_content = self.clean_html_content(content)
            
            # Skip if cleaned content is too small
            if len(cleaned_content.strip()) < 100:
                print(f"  Skipped: Cleaned content too small ({len(cleaned_content)} chars)")
                self.skipped_count += 1
                return False
            
            # Extract metadata
            metadata = self.extract_metadata_from_content(cleaned_content, file_path.name)
            
            # Skip if no title found
            if not metadata['title']:
                print(f"  Skipped: No title found")
                self.skipped_count += 1
                return False
            
            # Categorize the paper
            categorization = self.categorize_paper(metadata, cleaned_content)
            
            # Create enriched markdown
            enriched_content = self.create_enriched_markdown(cleaned_content, metadata, categorization)
            
            # Determine target directory
            target_dir = self.determine_target_directory(categorization)
            target_dir.mkdir(exist_ok=True)
            
            # Generate clean filename
            clean_filename = self.generate_clean_filename(metadata)
            target_path = target_dir / clean_filename
            
            # Handle filename conflicts
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                target_path = target_dir / f"{stem}_{counter}.md"
                counter += 1
            
            # Write the processed file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(enriched_content)
            
            print(f"  Success: Created {target_path}")
            self.processed_count += 1
            return True
            
        except Exception as e:
            print(f"  Error processing {file_path.name}: {str(e)}")
            self.failed_count += 1
            return False
    
    def process_all_scraped_files(self):
        """Process all scraped_### files in the research directory"""
        scraped_files = list(self.research_dir.glob("scraped_*.md"))
        
        if not scraped_files:
            print("No scraped_*.md files found in research directory")
            return
        
        print(f"Found {len(scraped_files)} scraped files to process")
        print("=" * 50)
        
        for file_path in scraped_files:
            self.process_file(file_path)
        
        print("=" * 50)
        print(f"Processing complete:")
        print(f"  Processed: {self.processed_count}")
        print(f"  Failed: {self.failed_count}")
        print(f"  Skipped: {self.skipped_count}")
        print(f"  Total: {len(scraped_files)}")
    
    def cleanup_original_files(self, backup=True):
        """Remove the original scraped files after processing"""
        scraped_files = list(self.research_dir.glob("scraped_*.md"))
        
        if not scraped_files:
            print("No scraped files to clean up")
            return
        
        if backup:
            backup_dir = self.research_dir / "backup_scraped_files"
            backup_dir.mkdir(exist_ok=True)
            print(f"Backing up {len(scraped_files)} files to {backup_dir}")
            
            for file_path in scraped_files:
                backup_path = backup_dir / file_path.name
                shutil.move(str(file_path), str(backup_path))
        else:
            print(f"Removing {len(scraped_files)} scraped files")
            for file_path in scraped_files:
                file_path.unlink()
        
        print("Cleanup complete")

def main():
    processor = ScrapedFileProcessor()
    
    print("Processing scraped files...")
    processor.process_all_scraped_files()
    
    # Ask user if they want to clean up original files
    response = input("\nDo you want to remove the original scraped files? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        backup_response = input("Backup the original files first? (y/n): ").lower().strip()
        backup = backup_response in ['y', 'yes']
        processor.cleanup_original_files(backup=backup)
    else:
        print("Original scraped files kept for review")

if __name__ == "__main__":
    main()
