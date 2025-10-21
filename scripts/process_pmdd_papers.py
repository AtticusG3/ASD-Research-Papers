#!/usr/bin/env python3
"""
Process PMDD research papers from CSV to Markdown format for knowledge base
"""

import os
import re
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime
import html

class PMDDPaperProcessor:
    def __init__(self, csv_file, output_dir="docs/research/hormones-endocrine/pmdd"):
        self.csv_file = Path(csv_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_count = 0
        self.failed_count = 0
        
    def clean_text(self, text):
        """Clean and normalize text content"""
        if pd.isna(text) or text == '':
            return ''
        
        # Decode HTML entities
        text = html.unescape(str(text))
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_doi(self, text):
        """Extract DOI from text"""
        if pd.isna(text):
            return ''
        
        doi_pattern = r'10\.\d+/[^\s]+'
        match = re.search(doi_pattern, str(text))
        return match.group(0) if match else ''
    
    def extract_pmid(self, text):
        """Extract PMID from text"""
        if pd.isna(text):
            return ''
        
        pmid_pattern = r'PMID:\s*(\d+)'
        match = re.search(pmid_pattern, str(text))
        return match.group(1) if match else ''
    
    def create_filename(self, title, authors, year):
        """Create a descriptive filename"""
        # Clean title
        clean_title = re.sub(r'[^\w\s-]', '', str(title))
        clean_title = re.sub(r'\s+', '_', clean_title)
        clean_title = clean_title[:100]  # Limit length
        
        # Get first author's last name
        first_author = ''
        if authors and not pd.isna(authors):
            authors_str = str(authors)
            if ',' in authors_str:
                first_author = authors_str.split(',')[0].strip()
            else:
                first_author = authors_str.split()[0] if authors_str.split() else ''
        
        # Clean author name
        first_author = re.sub(r'[^\w\s-]', '', first_author)
        first_author = re.sub(r'\s+', '_', first_author)
        
        # Create filename
        if first_author and year:
            filename = f"{first_author}_{year}_{clean_title}.md"
        elif year:
            filename = f"{year}_{clean_title}.md"
        else:
            filename = f"{clean_title}.md"
        
        return filename.lower()
    
    def create_metadata(self, row):
        """Create YAML metadata for the paper"""
        # Extract basic information
        title = self.clean_text(row.get('title', ''))
        authors = self.clean_text(row.get('authors', ''))
        journal = self.clean_text(row.get('journal', ''))
        abstract = self.clean_text(row.get('abstract', ''))
        doi = self.extract_doi(row.get('doi', ''))
        pmid = self.extract_pmid(row.get('pmid', ''))
        year = row.get('year', '')
        
        # Determine document type
        doc_type = 'research_paper'
        if 'review' in title.lower() or 'review' in journal.lower():
            doc_type = 'review'
        elif 'case' in title.lower():
            doc_type = 'case_study'
        elif 'meta' in title.lower():
            doc_type = 'meta_analysis'
        
        # Create search tags
        tags = ['pmdd', 'premenstrual_dysphoric_disorder', 'hormones_endocrine']
        
        # Add category-specific tags
        category = row.get('search_category', '')
        if 'core' in category:
            tags.extend(['diagnosis', 'clinical_features'])
        elif 'symptoms' in category:
            tags.extend(['mood_symptoms', 'emotional_dysregulation'])
        elif 'hormones' in category:
            tags.extend(['estrogen', 'progesterone', 'allopregnanolone'])
        elif 'neurochemistry' in category:
            tags.extend(['serotonin', 'gaba', 'dopamine', 'neurotransmitters'])
        elif 'treatment' in category:
            tags.extend(['ssri', 'therapy', 'medication'])
        elif 'comorbidity' in category:
            tags.extend(['adhd', 'autism', 'anxiety', 'depression'])
        elif 'mechanisms' in category:
            tags.extend(['neuroimaging', 'genetics', 'pathophysiology'])
        
        # Add source-specific tags
        source = row.get('source', '')
        if source == 'PubMed':
            tags.append('clinical_research')
        elif source == 'ArXiv':
            tags.append('preprint')
        
        metadata = {
            'title': title,
            'authors': authors,
            'journal': journal,
            'publication_date': str(year) if year else '',
            'doi': doi,
            'pmid': pmid,
            'document_type': doc_type,
            'source': source,
            'search_category': category,
            'search_query': row.get('search_query', ''),
            'tags': list(set(tags)),  # Remove duplicates
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'content_type': 'research_paper',
            'condition': 'pmdd',
            'topic': 'premenstrual_dysphoric_disorder'
        }
        
        return metadata
    
    def create_markdown_content(self, row, metadata):
        """Create the markdown content for the paper"""
        title = metadata['title']
        authors = metadata['authors']
        journal = metadata['journal']
        abstract = self.clean_text(row.get('abstract', ''))
        doi = metadata['doi']
        pmid = metadata['pmid']
        year = metadata['publication_date']
        
        # Create markdown content
        content = f"""# {title}

## Authors
{authors}

## Journal
{journal}

## Publication Information
- **Year**: {year}
- **DOI**: {doi}
- **PMID**: {pmid}

## Abstract
{abstract}

## Keywords
{', '.join(metadata['tags'])}

## Source Information
- **Source**: {metadata['source']}
- **Search Category**: {metadata['search_category']}
- **Search Query**: {metadata['search_query']}

---
*This document was automatically processed from {metadata['source']} and added to the PMDD research knowledge base.*
"""
        
        return content
    
    def process_paper(self, row):
        """Process a single paper row"""
        try:
            # Create metadata
            metadata = self.create_metadata(row)
            
            # Create filename
            filename = self.create_filename(
                metadata['title'],
                metadata['authors'],
                metadata['publication_date']
            )
            
            # Create markdown content
            content = self.create_markdown_content(row, metadata)
            
            # Create YAML frontmatter
            yaml_frontmatter = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
            
            # Combine frontmatter and content
            full_content = f"---\n{yaml_frontmatter}---\n\n{content}"
            
            # Write file
            output_file = self.output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            self.processed_count += 1
            return True
            
        except Exception as e:
            print(f"Error processing paper: {e}")
            self.failed_count += 1
            return False
    
    def process_all_papers(self):
        """Process all papers from the CSV file"""
        print(f"Loading papers from {self.csv_file}")
        
        # Load CSV
        df = pd.read_csv(self.csv_file)
        print(f"Found {len(df)} papers to process")
        
        # Process each paper
        for index, row in df.iterrows():
            if index % 50 == 0:
                print(f"Processing paper {index + 1}/{len(df)}")
            
            self.process_paper(row)
        
        print(f"\nProcessing complete:")
        print(f"  Successfully processed: {self.processed_count}")
        print(f"  Failed: {self.failed_count}")
        print(f"  Output directory: {self.output_dir}")

def main():
    """Main processing function"""
    # Find the most recent PMDD papers CSV
    acquired_dir = Path("acquired_papers")
    pmdd_files = list(acquired_dir.glob("pmdd_papers_*.csv"))
    
    if not pmdd_files:
        print("No PMDD papers CSV found in acquired_papers directory")
        return
    
    # Use the most recent file
    latest_file = max(pmdd_files, key=lambda x: x.stat().st_mtime)
    print(f"Processing PMDD papers from: {latest_file}")
    
    # Process papers
    processor = PMDDPaperProcessor(latest_file)
    processor.process_all_papers()

if __name__ == "__main__":
    main()
