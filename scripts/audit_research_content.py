#!/usr/bin/env python3
"""
Audit research papers for content completeness and quality.
"""

import os
import re

def audit_research_content():
    """Audit research papers for content quality and completeness."""
    print("=== RESEARCH PAPERS CONTENT AUDIT ===")
    
    research_dir = 'docs/research'
    content_issues = {
        'missing_content': [],
        'permission_text': [],
        'only_metadata': [],
        'incomplete_abstracts': [],
        'good_content': [],
        'empty_abstracts': []
    }
    
    sample_count = 0
    max_samples = 100
    
    for root, dirs, files in os.walk(research_dir):
        for file in files:
            if file.endswith('.md') and sample_count < max_samples:
                filepath = os.path.join(root, file)
                sample_count += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for permission request text
                    permission_patterns = [
                        'request permissions',
                        'reuse any or all of this article',
                        'please use the link below',
                        'copyright notice',
                        'all rights reserved',
                        'permission to reuse'
                    ]
                    
                    has_permission_text = any(pattern in content.lower() for pattern in permission_patterns)
                    
                    if has_permission_text:
                        content_issues['permission_text'].append(filepath)
                        continue
                    
                    # Check if only metadata (no substantial content after front matter)
                    lines = content.split('\n')
                    content_start = -1
                    for i, line in enumerate(lines):
                        if line.strip() == '---' and i > 0:
                            content_start = i + 1
                            break
                    
                    if content_start > 0:
                        actual_content = '\n'.join(lines[content_start:]).strip()
                        
                        # Check for empty abstract
                        if '## Abstract' in actual_content:
                            abstract_section = actual_content.split('## Abstract')[1].split('##')[0] if '## Abstract' in actual_content else ''
                            if len(abstract_section.strip()) < 50:
                                content_issues['empty_abstracts'].append(filepath)
                        
                        if len(actual_content) < 200:
                            content_issues['only_metadata'].append(filepath)
                        elif len(actual_content) > 1000:
                            content_issues['good_content'].append(filepath)
                        else:
                            content_issues['incomplete_abstracts'].append(filepath)
                    else:
                        content_issues['missing_content'].append(filepath)
                        
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return content_issues, sample_count

def analyze_specific_files():
    """Analyze specific files mentioned by user."""
    print("\n=== ANALYZING SPECIFIC FILES ===")
    
    specific_files = [
        'docs/research/related-disorders/a_role_for_the_serotonin_transporter_in_the_largely_unknown_molecular_pathophysiology_of_premenstrua.md',
        'docs/research/related-disorders/autism_therapeutic_approach_and_scientific_evidence.md'
    ]
    
    for filepath in specific_files:
        if os.path.exists(filepath):
            print(f"\n--- {filepath} ---")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                print(f"Total lines: {len(lines)}")
                
                # Find content after front matter
                content_start = -1
                for i, line in enumerate(lines):
                    if line.strip() == '---' and i > 0:
                        content_start = i + 1
                        break
                
                if content_start > 0:
                    actual_content = '\n'.join(lines[content_start:]).strip()
                    print(f"Content length: {len(actual_content)} characters")
                    
                    # Check for abstract
                    if '## Abstract' in actual_content:
                        abstract_section = actual_content.split('## Abstract')[1].split('##')[0] if '## Abstract' in actual_content else ''
                        print(f"Abstract length: {len(abstract_section.strip())} characters")
                        if len(abstract_section.strip()) < 50:
                            print("ISSUE: Empty or very short abstract")
                        else:
                            print("Abstract preview:", abstract_section.strip()[:200] + "...")
                    else:
                        print("ISSUE: No abstract section found")
                    
                    # Check for permission text
                    if 'request permissions' in actual_content.lower():
                        print("ISSUE: Contains permission request text")
                    
                    # Show first few lines of content
                    print("Content preview:")
                    for i, line in enumerate(actual_content.split('\n')[:10]):
                        print(f"  {i+1}: {line}")
                        
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

def generate_content_report(content_issues, sample_count):
    """Generate a comprehensive content report."""
    print(f"\n=== CONTENT AUDIT RESULTS ===")
    print(f"Audited {sample_count} research papers:")
    print(f"Good content: {len(content_issues['good_content'])}")
    print(f"Only metadata: {len(content_issues['only_metadata'])}")
    print(f"Permission text: {len(content_issues['permission_text'])}")
    print(f"Incomplete abstracts: {len(content_issues['incomplete_abstracts'])}")
    print(f"Empty abstracts: {len(content_issues['empty_abstracts'])}")
    print(f"Missing content: {len(content_issues['missing_content'])}")
    
    total_issues = (len(content_issues['only_metadata']) + 
                   len(content_issues['permission_text']) + 
                   len(content_issues['incomplete_abstracts']) + 
                   len(content_issues['empty_abstracts']) + 
                   len(content_issues['missing_content']))
    
    quality_score = ((sample_count - total_issues) / sample_count * 100) if sample_count > 0 else 0
    print(f"\nQuality Score: {quality_score:.1f}%")
    
    print("\n=== EXAMPLES OF PROBLEMATIC FILES ===")
    if content_issues['permission_text']:
        print("\nFiles with permission request text:")
        for f in content_issues['permission_text'][:5]:
            print(f"  - {f}")
    
    if content_issues['only_metadata']:
        print("\nFiles with only metadata:")
        for f in content_issues['only_metadata'][:5]:
            print(f"  - {f}")
    
    if content_issues['empty_abstracts']:
        print("\nFiles with empty abstracts:")
        for f in content_issues['empty_abstracts'][:5]:
            print(f"  - {f}")
    
    return quality_score

def main():
    print("=== RESEARCH PAPERS CONTENT AUDIT ===\n")
    
    # Audit research content
    content_issues, sample_count = audit_research_content()
    
    # Analyze specific files
    analyze_specific_files()
    
    # Generate report
    quality_score = generate_content_report(content_issues, sample_count)
    
    print(f"\n=== SUMMARY ===")
    if quality_score < 50:
        print("CRITICAL: Most research papers are missing actual content!")
        print("The papers appear to contain only metadata and permission text.")
        print("This suggests the scraping process failed to extract the actual research content.")
    elif quality_score < 80:
        print("WARNING: Many research papers have incomplete content.")
        print("Significant improvements needed in content extraction.")
    else:
        print("GOOD: Most research papers have adequate content.")
    
    print(f"\nQuality Score: {quality_score:.1f}%")

if __name__ == '__main__':
    main()
