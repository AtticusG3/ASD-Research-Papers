#!/usr/bin/env python3
"""
Comprehensive audit of research paper content quality.
"""

import os
import re

def audit_all_research_files():
    """Audit all research files for content quality."""
    print("=== COMPREHENSIVE RESEARCH CONTENT AUDIT ===")
    
    research_dir = 'docs/research'
    results = {
        'total_files': 0,
        'full_content': [],      # > 10KB content
        'good_content': [],      # 2-10KB content  
        'short_content': [],     # 500B-2KB content
        'metadata_only': [],     # < 500B content
        'permission_text': [],   # Contains permission requests
        'empty_abstracts': [],   # No abstract content
        'encoding_errors': []    # Files with encoding issues
    }
    
    for root, dirs, files in os.walk(research_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                results['total_files'] += 1
                
                try:
                    # Get file size
                    file_size = os.path.getsize(filepath)
                    
                    # Read content
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find content after front matter
                    lines = content.split('\n')
                    content_start = -1
                    for i, line in enumerate(lines):
                        if line.strip() == '---' and i > 0:
                            content_start = i + 1
                            break
                    
                    if content_start > 0:
                        actual_content = '\n'.join(lines[content_start:]).strip()
                        content_length = len(actual_content)
                        
                        # Check for permission text
                        if any(pattern in actual_content.lower() for pattern in [
                            'request permissions', 'reuse any or all of this article', 
                            'please use the link below', 'copyright notice'
                        ]):
                            results['permission_text'].append((filepath, file_size, content_length))
                            continue
                        
                        # Categorize by content length
                        if content_length > 10000:  # > 10KB
                            results['full_content'].append((filepath, file_size, content_length))
                        elif content_length > 2000:  # 2-10KB
                            results['good_content'].append((filepath, file_size, content_length))
                        elif content_length > 500:   # 500B-2KB
                            results['short_content'].append((filepath, file_size, content_length))
                        else:  # < 500B
                            results['metadata_only'].append((filepath, file_size, content_length))
                        
                        # Check for empty abstracts
                        if '## Abstract' in actual_content:
                            abstract_section = actual_content.split('## Abstract')[1].split('##')[0] if '## Abstract' in actual_content else ''
                            if len(abstract_section.strip()) < 50:
                                results['empty_abstracts'].append((filepath, file_size, content_length))
                    
                except UnicodeDecodeError:
                    results['encoding_errors'].append((filepath, file_size, 0))
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return results

def analyze_content_distribution(results):
    """Analyze the distribution of content quality."""
    print(f"\n=== CONTENT DISTRIBUTION ANALYSIS ===")
    print(f"Total files audited: {results['total_files']}")
    print(f"Full content (>10KB): {len(results['full_content'])}")
    print(f"Good content (2-10KB): {len(results['good_content'])}")
    print(f"Short content (500B-2KB): {len(results['short_content'])}")
    print(f"Metadata only (<500B): {len(results['metadata_only'])}")
    print(f"Permission text: {len(results['permission_text'])}")
    print(f"Empty abstracts: {len(results['empty_abstracts'])}")
    print(f"Encoding errors: {len(results['encoding_errors'])}")
    
    # Calculate quality metrics
    total_with_content = len(results['full_content']) + len(results['good_content']) + len(results['short_content'])
    quality_score = (total_with_content / results['total_files'] * 100) if results['total_files'] > 0 else 0
    
    print(f"\nQuality Score: {quality_score:.1f}%")
    
    return quality_score

def show_examples(results):
    """Show examples of different content types."""
    print(f"\n=== CONTENT EXAMPLES ===")
    
    if results['full_content']:
        print(f"\nFULL CONTENT EXAMPLES (>10KB):")
        for filepath, file_size, content_length in results['full_content'][:3]:
            print(f"  {filepath}")
            print(f"    File size: {file_size:,} bytes, Content: {content_length:,} chars")
    
    if results['metadata_only']:
        print(f"\nMETADATA ONLY EXAMPLES (<500B):")
        for filepath, file_size, content_length in results['metadata_only'][:3]:
            print(f"  {filepath}")
            print(f"    File size: {file_size:,} bytes, Content: {content_length:,} chars")
    
    if results['permission_text']:
        print(f"\nPERMISSION TEXT EXAMPLES:")
        for filepath, file_size, content_length in results['permission_text'][:3]:
            print(f"  {filepath}")
            print(f"    File size: {file_size:,} bytes, Content: {content_length:,} chars")
    
    if results['empty_abstracts']:
        print(f"\nEMPTY ABSTRACT EXAMPLES:")
        for filepath, file_size, content_length in results['empty_abstracts'][:3]:
            print(f"  {filepath}")
            print(f"    File size: {file_size:,} bytes, Content: {content_length:,} chars")

def generate_recommendations(quality_score, results):
    """Generate recommendations based on audit results."""
    print(f"\n=== RECOMMENDATIONS ===")
    
    if quality_score < 30:
        print("CRITICAL: Most research papers are missing actual content!")
        print("RECOMMENDATIONS:")
        print("1. Re-run the scraping process with better content extraction")
        print("2. Check if the original sources are accessible")
        print("3. Implement better content parsing to extract full articles")
        print("4. Consider using different scraping methods or APIs")
        
    elif quality_score < 60:
        print("WARNING: Many research papers have incomplete content.")
        print("RECOMMENDATIONS:")
        print("1. Improve content extraction algorithms")
        print("2. Add validation to ensure abstracts are captured")
        print("3. Implement content quality checks during scraping")
        print("4. Manually review and fix high-priority papers")
        
    elif quality_score < 80:
        print("MODERATE: Some research papers need content improvements.")
        print("RECOMMENDATIONS:")
        print("1. Focus on fixing papers with permission text")
        print("2. Add missing abstracts where possible")
        print("3. Implement automated content validation")
        
    else:
        print("GOOD: Most research papers have adequate content.")
        print("RECOMMENDATIONS:")
        print("1. Fix remaining permission text issues")
        print("2. Add missing abstracts for better accessibility")
        print("3. Implement ongoing content quality monitoring")

def main():
    print("=== COMPREHENSIVE RESEARCH CONTENT AUDIT ===\n")
    
    # Audit all research files
    results = audit_all_research_files()
    
    # Analyze content distribution
    quality_score = analyze_content_distribution(results)
    
    # Show examples
    show_examples(results)
    
    # Generate recommendations
    generate_recommendations(quality_score, results)
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Quality Score: {quality_score:.1f}%")
    if quality_score < 50:
        print("STATUS: CRITICAL - Major content issues detected")
    elif quality_score < 80:
        print("STATUS: NEEDS IMPROVEMENT - Some content issues")
    else:
        print("STATUS: GOOD - Minor content issues only")

if __name__ == '__main__':
    main()
