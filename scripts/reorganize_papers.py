#!/usr/bin/env python3
"""
Reorganize existing papers into the new folder structure
"""

import os
import shutil
import re
from pathlib import Path

def categorize_paper(filename, content):
    """Categorize a paper based on its filename and content"""
    filename_lower = filename.lower()
    content_lower = content.lower()
    
    # Primary condition detection
    if any(term in filename_lower or term in content_lower for term in ['tourette', 'tic', 'gilles']):
        if any(term in filename_lower or term in content_lower for term in ['adhd', 'attention', 'deficit', 'hyperactivity']):
            return 'comorbidity'
        return 'tourette'
    
    if any(term in filename_lower or term in content_lower for term in ['adhd', 'attention', 'deficit', 'hyperactivity']):
        if any(term in filename_lower or term in content_lower for term in ['autism', 'asperger', 'spectrum']):
            return 'comorbidity'
        return 'adhd'
    
    if any(term in filename_lower or term in content_lower for term in ['autism', 'asperger', 'spectrum']):
        return 'asd'
    
    # Check for related disorders
    if any(term in filename_lower or term in content_lower for term in ['ocd', 'obsessive', 'compulsive']):
        return 'related-disorders/ocd'
    
    if any(term in filename_lower or term in content_lower for term in ['anxiety', 'anxious']):
        return 'related-disorders/anxiety'
    
    if any(term in filename_lower or term in content_lower for term in ['depression', 'depressive']):
        return 'related-disorders/depression'
    
    # Check for neurochemistry
    if any(term in filename_lower or term in content_lower for term in ['dopamine', 'dopaminergic']):
        return 'neurochemistry/dopamine'
    
    if any(term in filename_lower or term in content_lower for term in ['serotonin', 'serotonergic']):
        return 'neurochemistry/serotonin'
    
    if any(term in filename_lower or term in content_lower for term in ['norepinephrine', 'noradrenaline']):
        return 'neurochemistry/norepinephrine'
    
    if any(term in filename_lower or term in content_lower for term in ['glutamate', 'gaba', 'gamma-aminobutyric']):
        return 'neurochemistry/glutamate-gaba'
    
    # Check for hormones
    if any(term in filename_lower or term in content_lower for term in ['cortisol', 'stress', 'hpa']):
        return 'hormones-endocrine/cortisol-stress'
    
    if any(term in filename_lower or term in content_lower for term in ['thyroid', 'thyroxine', 'tsh']):
        return 'hormones-endocrine/thyroid'
    
    if any(term in filename_lower or term in content_lower for term in ['testosterone', 'estrogen', 'progesterone', 'sex hormone']):
        return 'hormones-endocrine/sex-hormones'
    
    # Default to comorbidity if multiple conditions detected
    condition_count = 0
    if any(term in content_lower for term in ['tourette', 'tic']):
        condition_count += 1
    if any(term in content_lower for term in ['adhd', 'attention deficit']):
        condition_count += 1
    if any(term in content_lower for term in ['autism', 'asperger']):
        condition_count += 1
    
    if condition_count > 1:
        return 'comorbidity'
    
    # Default fallback
    return 'tourette'  # Most papers are Tourette-related

def reorganize_papers():
    """Reorganize existing papers into new structure"""
    docs_dir = Path('docs')
    research_dir = docs_dir / 'research'
    
    # Find all existing markdown files in docs root
    existing_papers = list(docs_dir.glob('*.md'))
    
    # Filter out meta files
    meta_files = ['README.md', 'SEARCH_GUIDE.md', 'CONVERSION_SUMMARY.md', 'knowledge_index.yaml']
    papers_to_move = [f for f in existing_papers if f.name not in meta_files]
    
    print(f"Found {len(papers_to_move)} papers to reorganize")
    
    moved_count = 0
    for paper_file in papers_to_move:
        try:
            # Read content to help with categorization
            with open(paper_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Categorize the paper
            category = categorize_paper(paper_file.name, content)
            
            # Determine destination
            if '/' in category:
                dest_dir = research_dir / category
            else:
                dest_dir = research_dir / category
            
            # Create destination directory if it doesn't exist
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            dest_path = dest_dir / paper_file.name
            shutil.move(str(paper_file), str(dest_path))
            
            print(f"Moved {paper_file.name} -> {category}/")
            moved_count += 1
            
        except Exception as e:
            print(f"Error moving {paper_file.name}: {e}")
    
    print(f"Successfully moved {moved_count} papers")

if __name__ == "__main__":
    reorganize_papers()
