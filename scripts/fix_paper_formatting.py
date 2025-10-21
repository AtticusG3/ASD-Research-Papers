#!/usr/bin/env python3
"""
Fix formatting issues in research papers to make them human-readable.
"""

import os
import re
import yaml

def clean_and_format_content(content):
    """Clean and format research paper content for better readability."""
    
    # Split into front matter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return content  # Can't process if no proper front matter
    
    front_matter = parts[1]
    main_content = parts[2]
    
    # Parse front matter
    try:
        metadata = yaml.safe_load(front_matter)
    except:
        metadata = {}
    
    # Clean the main content
    cleaned_content = clean_main_content(main_content)
    
    # Reconstruct the file
    new_content = f"---\n{front_matter}---\n\n{cleaned_content}"
    
    return new_content

def clean_main_content(content):
    """Clean the main content section."""
    
    # Remove duplicate sections
    content = remove_duplicate_sections(content)
    
    # Clean up HTML artifacts
    content = clean_html_artifacts(content)
    
    # Fix section headers
    content = fix_section_headers(content)
    
    # Clean up whitespace
    content = clean_whitespace(content)
    
    # Structure the content properly
    content = structure_content(content)
    
    return content

def remove_duplicate_sections(content):
    """Remove duplicate sections in the content."""
    
    # Split into lines
    lines = content.split('\n')
    seen_sections = set()
    cleaned_lines = []
    
    for line in lines:
        # Check if this is a section header
        if re.match(r'^##\s+', line):
            section_name = line.strip().lower()
            if section_name in seen_sections:
                # Skip this duplicate section
                continue
            else:
                seen_sections.add(section_name)
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def clean_html_artifacts(content):
    """Remove HTML artifacts and website content."""
    
    # Remove common HTML patterns
    html_patterns = [
        r'googletag\.cmd\.push\([^)]*\);',
        r'http://creativecommons\.org/licenses/[^\s]*',
        r'https://doi\.org/[^\s]*',
        r'statistics from altmetric\.com',
        r'you will be able to get a quick price and instant permission[^.]*\.',
        r'read the full text or download the pdf:',
        r'subscribe log in[^.]*\.',
        r'forgot your log in details\?',
        r'register a new account\?',
        r'forgot your user name or password\?',
        r'trendmd\.register\([^)]*\);',
        r'content latest content archive[^.]*\.',
        r'browse by collection[^.]*\.',
        r'most read articles[^.]*\.',
        r'top cited articles[^.]*\.',
        r'responses journal about[^.]*\.',
        r'editorial board[^.]*\.',
        r'sign up for email alerts[^.]*\.',
        r'thank you to our reviewers[^.]*\.',
        r'authors instructions for authors[^.]*\.',
        r'submit an article[^.]*\.',
        r'editorial policies[^.]*\.',
        r'open access at bmj[^.]*\.',
        r'instructions for reviewers[^.]*\.',
        r'bmj author hub[^.]*\.',
        r'help contact us[^.]*\.',
        r'reprints permissions[^.]*\.',
        r'advertising feedback form[^.]*\.',
        r'rss twitter facebook[^.]*\.',
        r'blog website[^.]*\.',
        r'terms & conditions[^.]*\.',
        r'privacy & cookies[^.]*\.',
        r'contact bmj[^.]*\.',
        r'cookie settings[^.]*\.',
        r'online issn:[^.]*\.',
        r'print issn:[^.]*\.',
        r'copyright ©[^.]*\.',
        r'all rights, including for text and data mining[^.]*\.',
        r'are reserved[^.]*\.',
        r'## Full Text##',
        r'## Introduction##',
        r'## Methods##',
        r'## Results##',
        r'## Discussion##',
        r'## Conclusion##',
        r'## References##',
        r'## Scraping Notes[^.]*\.',
    ]
    
    for pattern in html_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    return content

def fix_section_headers(content):
    """Fix section headers to be properly formatted."""
    
    # Fix headers that are missing spaces or have extra characters
    content = re.sub(r'^##([^#\s])', r'## \1', content, flags=re.MULTILINE)
    content = re.sub(r'^###([^#\s])', r'### \1', content, flags=re.MULTILINE)
    
    # Remove headers that are just "##" or "###"
    content = re.sub(r'^##\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^###\s*$', '', content, flags=re.MULTILINE)
    
    return content

def clean_whitespace(content):
    """Clean up excessive whitespace."""
    
    # Remove excessive blank lines
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # Remove trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Remove leading whitespace from lines (except for indented content)
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Don't remove indentation from list items or code blocks
        if re.match(r'^\s*[-*+]\s', line) or re.match(r'^\s*\d+\.\s', line):
            cleaned_lines.append(line)
        else:
            cleaned_lines.append(line.lstrip())
    
    return '\n'.join(cleaned_lines)

def structure_content(content):
    """Structure the content with proper sections."""
    
    # Define the expected structure
    sections = {
        'abstract': r'##\s*abstract',
        'introduction': r'##\s*introduction',
        'methods': r'##\s*methods',
        'results': r'##\s*results',
        'discussion': r'##\s*discussion',
        'conclusion': r'##\s*conclusion',
        'references': r'##\s*references',
        'keywords': r'##\s*keywords',
        'authors': r'##\s*authors',
        'journal': r'##\s*journal',
        'publication': r'##\s*publication'
    }
    
    # Find existing sections
    found_sections = {}
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        for section_name, pattern in sections.items():
            if re.search(pattern, line, re.IGNORECASE):
                found_sections[section_name] = i
                break
    
    # If we have a good structure, return as is
    if len(found_sections) >= 3:
        return content
    
    # Otherwise, try to organize the content better
    return organize_unstructured_content(content)

def organize_unstructured_content(content):
    """Organize content that doesn't have clear structure."""
    
    lines = content.split('\n')
    organized_lines = []
    
    # Look for the title (usually the first non-empty line after front matter)
    title_found = False
    abstract_started = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            organized_lines.append('')
            continue
        
        # Skip if this looks like a title we've already processed
        if not title_found and len(line) > 10 and not line.startswith('#'):
            organized_lines.append(f"# {line}")
            title_found = True
            continue
        
        # Look for abstract content
        if 'abstract' in line.lower() and not abstract_started:
            organized_lines.append("## Abstract")
            abstract_started = True
            continue
        
        # Look for other section indicators
        if any(keyword in line.lower() for keyword in ['introduction', 'background', 'objective']):
            if not any('## Introduction' in prev_line for prev_line in organized_lines[-5:]):
                organized_lines.append("## Introduction")
                continue
        
        if any(keyword in line.lower() for keyword in ['methods', 'methodology', 'study design']):
            if not any('## Methods' in prev_line for prev_line in organized_lines[-5:]):
                organized_lines.append("## Methods")
                continue
        
        if any(keyword in line.lower() for keyword in ['results', 'findings', 'outcomes']):
            if not any('## Results' in prev_line for prev_line in organized_lines[-5:]):
                organized_lines.append("## Results")
                continue
        
        if any(keyword in line.lower() for keyword in ['discussion', 'conclusion', 'implications']):
            if not any('## Discussion' in prev_line for prev_line in organized_lines[-5:]):
                organized_lines.append("## Discussion")
                continue
        
        # Add the line as is
        organized_lines.append(line)
    
    return '\n'.join(organized_lines)

def process_research_files():
    """Process all research files to fix formatting."""
    
    print("=== FIXING RESEARCH PAPER FORMATTING ===")
    
    research_dir = 'docs/research'
    processed_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(research_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                
                try:
                    # Read the file
                    with open(filepath, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    # Skip if file is too short (likely already well-formatted)
                    if len(original_content) < 1000:
                        continue
                    
                    # Clean and format the content
                    cleaned_content = clean_and_format_content(original_content)
                    
                    # Only write if content changed significantly
                    if len(cleaned_content) < len(original_content) * 0.8:  # Significant reduction
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        
                        print(f"Fixed: {filepath}")
                        processed_count += 1
                    
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    error_count += 1
    
    print(f"\nProcessed {processed_count} files")
    print(f"Errors: {error_count} files")
    
    return processed_count, error_count

def main():
    print("=== RESEARCH PAPER FORMATTING FIX ===\n")
    
    # Process all research files
    processed_count, error_count = process_research_files()
    
    print(f"\n=== FORMATTING FIX COMPLETE ===")
    print(f"Files processed: {processed_count}")
    print(f"Errors: {error_count}")
    
    if processed_count > 0:
        print("\nResearch papers have been reformatted for better readability!")
        print("Key improvements:")
        print("- Removed duplicate content")
        print("- Cleaned HTML artifacts")
        print("- Fixed section headers")
        print("- Improved content structure")
        print("- Cleaned up whitespace")

if __name__ == '__main__':
    main()
