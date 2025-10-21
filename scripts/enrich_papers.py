#!/usr/bin/env python3
"""
Enrich research papers with full-text content using MCP tools
Retrieves full paper content from arXiv and DOI sources to expand abstract-only documents
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess

class PaperEnricher:
    def __init__(self, test_mode=True, test_limit=50):
        self.test_mode = test_mode
        self.test_limit = test_limit
        self.enrichment_log = {
            'start_time': datetime.now().isoformat(),
            'papers_processed': [],
            'success_count': 0,
            'failure_count': 0,
            'skip_count': 0,
            'retrieval_methods': {
                'arxiv': 0,
                'doi_pdf': 0,
                'alternative_search': 0,
                'failed': 0
            }
        }
        
    def extract_metadata_from_markdown(self, file_path: Path) -> Dict:
        """Extract YAML frontmatter and content from markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            markdown_content = yaml_match.group(2)
            metadata = yaml.safe_load(yaml_content)
            return {
                'metadata': metadata,
                'content': markdown_content,
                'has_yaml': True
            }
        
        return {
            'metadata': {},
            'content': content,
            'has_yaml': False
        }
    
    def check_needs_enrichment(self, file_path: Path) -> Tuple[bool, str]:
        """
        Check if paper needs enrichment
        Returns: (needs_enrichment, reason)
        """
        data = self.extract_metadata_from_markdown(file_path)
        content = data['content']
        
        # Check if already enriched
        if '## Introduction' in content or '## Methods' in content or '## Results' in content:
            return False, "Already has full sections"
        
        # Check if has substantial abstract
        abstract_match = re.search(r'## Abstract\s*\n\s*(.{100,})', content, re.DOTALL)
        if not abstract_match:
            return True, "Missing or minimal abstract"
        
        # Check if only has abstract (no other major sections)
        sections = re.findall(r'^## [A-Z]', content, re.MULTILINE)
        if len(sections) <= 2:  # Only Abstract and Research Details
            return True, "Only has abstract section"
        
        return False, "Appears complete"
    
    def search_arxiv_by_title(self, title: str, doi: Optional[str] = None) -> Optional[str]:
        """
        Search arXiv for paper by title
        Returns arXiv ID if found
        """
        print(f"  [->] Searching arXiv for: {title[:60]}...")
        
        # Use mcp_arxiv_search_papers
        search_query = title.replace(':', ' ').replace('(', '').replace(')', '')
        
        # Create a simple MCP request (this would need to be done via the MCP client)
        # For now, we'll return None and handle this separately
        return None
    
    def download_arxiv_paper(self, arxiv_id: str) -> Optional[str]:
        """
        Download and extract arXiv paper content
        Returns markdown content if successful
        """
        print(f"  [->] Downloading arXiv paper: {arxiv_id}")
        # This would use mcp_arxiv_download_paper and mcp_arxiv_read_paper
        return None
    
    def download_doi_pdf(self, doi: str) -> Optional[str]:
        """
        Download PDF via DOI and extract text
        Returns extracted text if successful
        """
        print(f"  [->] Attempting DOI download: {doi}")
        # This would use mcp_paperscraper_download_paper_pdf
        return None
    
    def search_alternative_sources(self, title: str, authors: List[str]) -> Optional[str]:
        """
        Search alternative sources (Google Scholar, etc.)
        Returns content if found
        """
        print(f"  [->] Searching alternative sources...")
        # This would use mcp_paperscraper_search_scholar
        return None
    
    def parse_full_text_sections(self, full_text: str) -> Dict[str, str]:
        """
        Parse full text into structured sections
        Returns dict of section_name: content
        """
        sections = {}
        
        # Common section patterns
        section_patterns = [
            r'(?:^|\n)#+\s*(Introduction|Background)\s*\n(.*?)(?=\n#+\s*|\Z)',
            r'(?:^|\n)#+\s*(Methods?|Materials? and Methods?|Methodology)\s*\n(.*?)(?=\n#+\s*|\Z)',
            r'(?:^|\n)#+\s*(Results?|Findings?)\s*\n(.*?)(?=\n#+\s*|\Z)',
            r'(?:^|\n)#+\s*(Discussion)\s*\n(.*?)(?=\n#+\s*|\Z)',
            r'(?:^|\n)#+\s*(Conclusion|Conclusions?)\s*\n(.*?)(?=\n#+\s*|\Z)',
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, full_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                section_name = match.group(1).strip()
                section_content = match.group(2).strip()
                if section_content and len(section_content) > 50:
                    sections[section_name] = section_content
        
        return sections
    
    def integrate_content(self, file_path: Path, new_sections: Dict[str, str], 
                         retrieval_method: str) -> bool:
        """
        Integrate retrieved content into existing markdown file
        """
        data = self.extract_metadata_from_markdown(file_path)
        
        # Update metadata
        metadata = data['metadata']
        metadata['enrichment_date'] = datetime.now().isoformat()
        metadata['enrichment_method'] = retrieval_method
        metadata['content_expanded'] = True
        
        # Build new content
        content_lines = data['content'].split('\n')
        
        # Find where to insert new sections (after Abstract section)
        insert_index = -1
        for i, line in enumerate(content_lines):
            if line.strip().startswith('## Research Details') or \
               line.strip().startswith('---') and i > 10:
                insert_index = i
                break
        
        if insert_index == -1:
            insert_index = len(content_lines)
        
        # Build section text
        new_content = []
        for section_name, section_content in new_sections.items():
            new_content.append(f"\n## {section_name}\n")
            new_content.append(section_content)
            new_content.append("\n")
        
        # Insert new sections
        content_lines = content_lines[:insert_index] + new_content + content_lines[insert_index:]
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml.dump(metadata, default_flow_style=False, allow_unicode=True))
            f.write('---\n')
            f.write('\n'.join(content_lines))
        
        return True
    
    def enrich_paper(self, file_path: Path) -> Dict:
        """
        Attempt to enrich a single paper
        Returns result dict with status and details
        """
        result = {
            'file': str(file_path),
            'status': 'pending',
            'method': None,
            'sections_added': [],
            'error': None
        }
        
        print(f"\n[*] Processing: {file_path.name}")
        
        # Check if needs enrichment
        needs_enrichment, reason = self.check_needs_enrichment(file_path)
        if not needs_enrichment:
            print(f"  [SKIP] {reason}")
            result['status'] = 'skipped'
            result['error'] = reason
            self.enrichment_log['skip_count'] += 1
            return result
        
        print(f"  [OK] Needs enrichment: {reason}")
        
        # Extract metadata
        data = self.extract_metadata_from_markdown(file_path)
        metadata = data['metadata']
        
        title = metadata.get('title', '')
        doi = metadata.get('doi', '')
        authors = metadata.get('authors', [])
        
        if isinstance(authors, str):
            try:
                authors = eval(authors)  # Convert string representation of list
            except:
                authors = []
        
        # Try retrieval methods in order
        full_text = None
        retrieval_method = None
        
        # Method 1: arXiv search
        # Note: These would need to be called via MCP client, not directly
        # For now, we'll log what we would do
        
        print(f"  [INFO] Would search arXiv for: {title[:50]}...")
        print(f"  [INFO] Would try DOI: {doi}")
        print(f"  [INFO] Would try alternative sources")
        
        # For this version, we'll mark as needing manual MCP invocation
        result['status'] = 'needs_mcp_invocation'
        result['error'] = 'MCP tools need to be invoked externally'
        result['title'] = title
        result['doi'] = doi
        self.enrichment_log['failure_count'] += 1
        
        return result
    
    def select_papers_for_enrichment(self) -> List[Path]:
        """
        Select papers for enrichment across categories
        """
        docs_dir = Path('docs/research')
        categories = ['tourette', 'asd', 'adhd', 'comorbidity', 'neurochemistry']
        
        papers_per_category = self.test_limit // len(categories)
        selected_papers = []
        
        for category in categories:
            category_dir = docs_dir / category
            if not category_dir.exists():
                continue
            
            # Get all markdown files (recursively for neurochemistry)
            if category == 'neurochemistry':
                md_files = list(category_dir.rglob('*.md'))
            else:
                md_files = list(category_dir.glob('*.md'))
            
            # Take first N papers
            selected = md_files[:papers_per_category]
            selected_papers.extend(selected)
            print(f"[+] Selected {len(selected)} papers from {category}")
        
        return selected_papers[:self.test_limit]
    
    def run(self):
        """Main execution method"""
        print("[*] Paper Enrichment Tool")
        print(f"[*] Mode: {'TEST' if self.test_mode else 'FULL'}")
        print(f"[*] Limit: {self.test_limit} papers\n")
        
        # Select papers
        papers = self.select_papers_for_enrichment()
        print(f"\n[*] Selected {len(papers)} papers for enrichment\n")
        
        # Process each paper
        for paper_path in papers:
            result = self.enrich_paper(paper_path)
            self.enrichment_log['papers_processed'].append(result)
        
        # Finalize log
        self.enrichment_log['end_time'] = datetime.now().isoformat()
        self.enrichment_log['total_processed'] = len(papers)
        
        # Save log
        log_dir = Path('acquired_papers')
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f'enrichment_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
        
        with open(log_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.enrichment_log, f, default_flow_style=False, allow_unicode=True)
        
        print(f"\n[*] Enrichment Complete!")
        print(f"[*] Total processed: {self.enrichment_log['total_processed']}")
        print(f"[*] Successes: {self.enrichment_log['success_count']}")
        print(f"[*] Failures: {self.enrichment_log['failure_count']}")
        print(f"[*] Skipped: {self.enrichment_log['skip_count']}")
        print(f"[*] Log saved to: {log_file}")
        
        return log_file

def main():
    enricher = PaperEnricher(test_mode=True, test_limit=50)
    enricher.run()

if __name__ == '__main__':
    main()

