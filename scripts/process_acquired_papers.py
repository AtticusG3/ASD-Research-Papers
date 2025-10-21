#!/usr/bin/env python3
"""
Process acquired papers from CSV into Markdown format
Converts the 959 papers from our acquisition system into properly formatted knowledge base entries
"""

import pandas as pd
import yaml
import re
from pathlib import Path
from datetime import datetime
import html

def clean_text(text):
    """Clean and format text for Markdown"""
    if pd.isna(text) or text == '':
        return ''
    
    # Convert to string and clean
    text = str(text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Clean up common formatting issues
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
    text = text.strip()
    
    return text

def extract_key_topics(abstract, title):
    """Extract key topics from abstract and title"""
    text = f"{title} {abstract}".lower()
    
    topics = []
    
    # Condition-based topics
    if any(term in text for term in ['tourette', 'tic', 'tics', 'gilles']):
        topics.append('tourette_syndrome')
    if any(term in text for term in ['adhd', 'attention deficit', 'hyperactivity']):
        topics.append('adhd')
    if any(term in text for term in ['autism', 'spectrum', 'asperger', 'asd']):
        topics.append('asd')
    if any(term in text for term in ['ocd', 'obsessive', 'compulsive']):
        topics.append('ocd')
    if any(term in text for term in ['anxiety', 'depression']):
        topics.append('mental_health')
    
    # Neurochemistry topics
    if any(term in text for term in ['dopamine', 'dopaminergic']):
        topics.append('dopamine')
    if any(term in text for term in ['serotonin', 'serotonergic']):
        topics.append('serotonin')
    if any(term in text for term in ['norepinephrine', 'noradrenaline']):
        topics.append('norepinephrine')
    if any(term in text for term in ['glutamate', 'gaba', 'gamma-aminobutyric']):
        topics.append('glutamate_gaba')
    
    # Hormone topics
    if any(term in text for term in ['cortisol', 'stress', 'hpa']):
        topics.append('cortisol_stress')
    if any(term in text for term in ['thyroid', 'thyroxine', 'tsh']):
        topics.append('thyroid')
    if any(term in text for term in ['testosterone', 'estrogen', 'progesterone']):
        topics.append('sex_hormones')
    if any(term in text for term in ['growth hormone', 'gh']):
        topics.append('growth_hormones')
    
    # Treatment topics
    if any(term in text for term in ['cbit', 'behavioral', 'intervention', 'habit reversal']):
        topics.append('behavioral_therapy')
    if any(term in text for term in ['medication', 'pharmacological', 'drug', 'haldol', 'risperidone']):
        topics.append('pharmacological')
    if any(term in text for term in ['therapy', 'psychotherapy']):
        topics.append('psychotherapy')
    
    # Study design
    if any(term in text for term in ['randomized', 'controlled trial', 'rct']):
        topics.append('randomized_controlled_trial')
    elif any(term in text for term in ['cohort', 'longitudinal']):
        topics.append('cohort_study')
    elif any(term in text for term in ['cross-sectional', 'survey']):
        topics.append('cross_sectional')
    elif any(term in text for term in ['case report', 'case study']):
        topics.append('case_study')
    
    return topics

def determine_primary_category(category, topics):
    """Determine the primary category for organizing papers"""
    # Use the category from CSV as primary, but refine based on topics
    if category == 'tourette_syndrome':
        return 'tourette'
    elif category == 'adhd':
        return 'adhd'
    elif category == 'asd':
        return 'asd'
    elif category == 'related_disorders':
        # Further categorize based on topics
        if 'ocd' in topics:
            return 'related-disorders/ocd'
        elif 'anxiety' in topics or 'depression' in topics:
            return 'related-disorders/anxiety'
        else:
            return 'related-disorders'
    elif category == 'neurochemistry':
        # Further categorize based on specific neurotransmitters
        if 'dopamine' in topics:
            return 'neurochemistry/dopamine'
        elif 'serotonin' in topics:
            return 'neurochemistry/serotonin'
        elif 'norepinephrine' in topics:
            return 'neurochemistry/norepinephrine'
        elif 'glutamate_gaba' in topics:
            return 'neurochemistry/glutamate-gaba'
        else:
            return 'neurochemistry/other-neurotransmitters'
    elif category == 'hormones':
        # Further categorize based on specific hormones
        if 'cortisol_stress' in topics:
            return 'hormones-endocrine/cortisol-stress'
        elif 'thyroid' in topics:
            return 'hormones-endocrine/thyroid'
        elif 'sex_hormones' in topics:
            return 'hormones-endocrine/sex-hormones'
        elif 'growth_hormones' in topics:
            return 'hormones-endocrine/growth-hormones'
        else:
            return 'hormones-endocrine'
    elif category == 'comorbidity':
        return 'comorbidity'
    else:
        return 'comorbidity'  # Default fallback

def create_safe_filename(title):
    """Create a safe filename from title"""
    # Remove or replace problematic characters
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    safe_title = re.sub(r'[^\w\s-]', '', safe_title)
    safe_title = re.sub(r'\s+', '_', safe_title)
    safe_title = safe_title[:100]  # Limit length
    
    return f"{safe_title}.md"

def process_paper(row, output_dir):
    """Process a single paper row into a Markdown file"""
    try:
        # Extract and clean data
        title = clean_text(row['title'])
        abstract = clean_text(row['abstract'])
        journal = clean_text(row['journal'])
        date = clean_text(row['date'])
        authors = clean_text(row['authors'])
        doi = clean_text(row['doi'])
        category = clean_text(row['category'])
        search_query = clean_text(row['search_query'])
        source = clean_text(row['source'])
        
        # Skip if no title
        if not title:
            return False
        
        # Extract topics and determine primary category
        topics = extract_key_topics(abstract, title)
        primary_category = determine_primary_category(category, topics)
        
        # Create metadata
        metadata = {
            'title': title,
            'authors': authors,
            'journal': journal,
            'publication_date': date,
            'doi': doi,
            'source': f"{source.upper()} via Paperscraper",
            'acquisition_date': datetime.now().isoformat(),
            'type': 'research_paper',
            'content_type': 'research_paper',
            'conditions': [cat for cat in ['tourette_syndrome', 'adhd', 'asd'] if cat in topics],
            'topics': topics,
            'primary_category': primary_category,
            'search_query': search_query,
            'acquisition_method': 'paperscraper_automated',
            'reading_level': 'academic',
            'audience': ['professional', 'researcher'],
            'patient_friendly': False,
            'search_priority': 'standard',
            'keywords': topics + [category, source],
            'search_tags': topics + [category, source, 'research', 'academic']
        }
        
        # Create content
        content = f"# {title}\n\n"
        
        if authors and authors != 'nan':
            content += f"**Authors:** {authors}\n\n"
        
        if journal and journal != 'nan':
            content += f"**Journal:** {journal}\n\n"
        
        if date and date != 'nan':
            content += f"**Publication Date:** {date}\n\n"
        
        if doi and doi != 'nan':
            content += f"**DOI:** {doi}\n\n"
        
        content += "## Abstract\n\n"
        content += f"{abstract}\n\n"
        
        # Add search optimization section
        content += "---\n\n"
        content += "## Research Details\n\n"
        content += f"**Source:** {source.upper()}\n"
        content += f"**Category:** {category}\n"
        content += f"**Primary Topics:** {', '.join(topics[:5])}\n"
        content += f"**Search Query:** {search_query}\n"
        content += f"**Acquisition Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        content += "*This paper was automatically acquired and processed for the neurodevelopmental disorders knowledge base.*\n"
        
        # Create YAML frontmatter
        yaml_content = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        
        # Combine frontmatter and content
        full_content = f"---\n{yaml_content}---\n\n{content}"
        
        # Create output directory
        target_dir = Path(output_dir) / "research" / primary_category
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename and save
        filename = create_safe_filename(title)
        output_file = target_dir / filename
        
        # Handle duplicate filenames
        counter = 1
        original_filename = filename
        while output_file.exists():
            name_part = original_filename.replace('.md', '')
            filename = f"{name_part}_{counter}.md"
            output_file = target_dir / filename
            counter += 1
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return True
        
    except Exception as e:
        print(f"Error processing paper '{title}': {e}")
        return False

def process_acquired_papers(csv_file, output_dir):
    """Process all acquired papers from CSV"""
    print(f"Loading papers from {csv_file}...")
    
    # Load CSV
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} papers")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Process each paper
    processed_count = 0
    failed_count = 0
    
    for index, row in df.iterrows():
        if process_paper(row, output_dir):
            processed_count += 1
            if processed_count % 50 == 0:
                print(f"Processed {processed_count} papers...")
        else:
            failed_count += 1
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {processed_count}")
    print(f"Failed: {failed_count}")
    
    # Create processing log
    log_data = {
        'processing_date': datetime.now().isoformat(),
        'source_file': str(csv_file),
        'total_papers': len(df),
        'processed_successfully': processed_count,
        'failed': failed_count,
        'output_directory': str(output_path)
    }
    
    log_file = output_path / 'processing_log.yaml'
    with open(log_file, 'w', encoding='utf-8') as f:
        yaml.dump(log_data, f, default_flow_style=False)
    
    print(f"Processing log saved to: {log_file}")
    
    return processed_count

def main():
    """Main processing function"""
    csv_file = "acquired_papers/acquired_papers_20251021_161222.csv"
    output_dir = "docs"
    
    if not Path(csv_file).exists():
        print(f"CSV file not found: {csv_file}")
        return
    
    print("Starting paper processing...")
    processed_count = process_acquired_papers(csv_file, output_dir)
    
    print(f"\nSuccessfully converted {processed_count} papers to Markdown format!")
    print("Papers are now organized in the docs/research/ directory structure.")

if __name__ == "__main__":
    main()
