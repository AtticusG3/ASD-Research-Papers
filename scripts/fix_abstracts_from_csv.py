#!/usr/bin/env python3
"""
Fix truncated abstracts in markdown files using the original CSV data
This is a practical first step in enriching our paper collection
"""

import pandas as pd
import yaml
import re
from pathlib import Path
from datetime import datetime

def extract_metadata_from_markdown(file_path):
    """Extract YAML frontmatter and content from markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        markdown_content = yaml_match.group(2)
        metadata = yaml.safe_load(yaml_content)
        return metadata, markdown_content
    
    return {}, content

def find_abstract_in_csv(doi, title, df):
    """Find the paper in CSV by DOI or title"""
    if doi:
        matches = df[df['doi'] == doi]
        if not matches.empty:
            return matches.iloc[0]['abstract']
    
    # Try fuzzy title match
    if not title or pd.isna(title):
        return None
    
    title_clean = title.lower().strip()
    for idx, row in df.iterrows():
        if pd.isna(row['title']):
            continue
        row_title = str(row['title']).lower().strip()
        if row_title in title_clean or title_clean in row_title:
            return row['abstract']
    
    return None

def check_abstract_truncated(markdown_content):
    """Check if abstract appears truncated"""
    abstract_match = re.search(r'## Abstract\s*\n\s*(.{0,2000}?)(?:\n##|\n---|\Z)', markdown_content, re.DOTALL)
    if not abstract_match:
        return True, ""
    
    abstract_text = abstract_match.group(1).strip()
    
    # Check for truncation indicators
    if len(abstract_text) < 100:
        return True, abstract_text
    if abstract_text.endswith('...'):
        return True, abstract_text
    if not abstract_text:
        return True, abstract_text
    
    # Check if ends abruptly (no period, incomplete sentence)
    if not abstract_text.endswith(('.', '!', '?', '"', ')')):
        return True, abstract_text
    
    return False, abstract_text

def fix_abstract(file_path, csv_df):
    """Fix truncated abstract in a markdown file"""
    metadata, markdown_content = extract_metadata_from_markdown(file_path)
    
    is_truncated, current_abstract = check_abstract_truncated(markdown_content)
    
    if not is_truncated:
        return {'status': 'ok', 'file': str(file_path)}
    
    # Find correct abstract in CSV
    doi = metadata.get('doi', '')
    title = metadata.get('title', '')
    
    correct_abstract = find_abstract_in_csv(doi, title, csv_df)
    
    if not correct_abstract or pd.isna(correct_abstract):
        return {'status': 'not_found', 'file': str(file_path), 'doi': doi}
    
    # Replace abstract in markdown
    abstract_pattern = r'(## Abstract\s*\n\s*)(.{0,2000}?)(\n##|\n---|\Z)'
    
    def replace_abstract(match):
        return match.group(1) + correct_abstract + '\n' + match.group(3)
    
    new_content = re.sub(abstract_pattern, replace_abstract, markdown_content, flags=re.DOTALL)
    
    # Update metadata
    metadata['abstract_fixed'] = True
    metadata['abstract_fix_date'] = datetime.now().isoformat()
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write(yaml.dump(metadata, default_flow_style=False, allow_unicode=True))
        f.write('---\n')
        f.write(new_content)
    
    return {'status': 'fixed', 'file': str(file_path), 'doi': doi}

def main():
    print("[*] Abstract Fixer - Using CSV Data")
    print("[*] Loading CSV data...\n")
    
    csv_path = Path('acquired_papers/acquired_papers_20251021_161222.csv')
    df = pd.read_csv(csv_path)
    print(f"[+] Loaded {len(df)} papers from CSV\n")
    
    # Get all markdown files
    docs_dir = Path('docs/research')
    md_files = list(docs_dir.rglob('*.md'))
    print(f"[+] Found {len(md_files)} markdown files\n")
    
    results = {
        'ok': [],
        'fixed': [],
        'not_found': []
    }
    
    print("[*] Processing files...\n")
    total = len(md_files)
    for i, md_file in enumerate(md_files, 1):
        # Handle Unicode encoding issues on Windows
        try:
            filename_display = md_file.name[:60]
        except:
            filename_display = "file_" + str(i)
        
        if i % 50 == 0 or i == total:
            try:
                print(f"[{i}/{total}] {filename_display}", end='')
            except UnicodeEncodeError:
                print(f"[{i}/{total}] [non-ASCII filename]", end='')
        else:
            try:
                print(f"[{i}/{total}] {filename_display}", end='')
            except UnicodeEncodeError:
                print(f"[{i}/{total}] [non-ASCII filename]", end='')
        
        result = fix_abstract(md_file, df)
        results[result['status']].append(result)
        print(f" ... {result['status'].upper()}")
    
    # Summary
    print(f"\n[*] Summary:")
    print(f"    Already OK: {len(results['ok'])}")
    print(f"    Fixed: {len(results['fixed'])}")
    print(f"    Not Found: {len(results['not_found'])}")
    
    # Save log
    log_file = Path('acquired_papers') / f"abstract_fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    with open(log_file, 'w') as f:
        yaml.dump(results, f, default_flow_style=False)
    
    print(f"\n[*] Log saved to: {log_file}")
    
    return results

if __name__ == '__main__':
    main()

