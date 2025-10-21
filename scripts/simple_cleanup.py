#!/usr/bin/env python3
"""
Simple project cleanup and research papers audit.
"""

import os
import json
import shutil
import glob

def cleanup_temporary_files():
    """Remove temporary files and logs."""
    print("=== CLEANING UP TEMPORARY FILES ===")
    
    # Files to remove
    files_to_remove = [
        'duplicate_analysis.json',
        'cleanup_log.json',
        '*.tmp',
        '*.temp',
        '*.log',
        '*.bak',
        '*.backup',
        '*~',
        '*.swp'
    ]
    
    removed_count = 0
    
    for pattern in files_to_remove:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            try:
                if os.path.isfile(match):
                    os.remove(match)
                    print(f"Removed: {match}")
                    removed_count += 1
            except Exception as e:
                print(f"Error removing {match}: {e}")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    print(f"Removed directory: {dir_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {dir_path}: {e}")
    
    print(f"Removed {removed_count} temporary files/directories")

def remove_empty_directories():
    """Remove empty directories (except important ones)."""
    print("\n=== REMOVING EMPTY DIRECTORIES ===")
    
    # Directories to keep even if empty
    keep_dirs = {
        '.git',
        'docs/patient-guides/symptoms',
        'docs/support/relationships', 
        'docs/support/school-work'
    }
    
    removed_count = 0
    
    # Walk through directories and remove empty ones
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(dir_path, '.')
            
            # Skip if we want to keep this directory
            if any(keep_dir in rel_path for keep_dir in keep_dirs):
                continue
            
            try:
                if not os.listdir(dir_path):  # Directory is empty
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                    removed_count += 1
            except Exception as e:
                print(f"Error removing {dir_path}: {e}")
    
    print(f"Removed {removed_count} empty directories")

def audit_research_papers():
    """Audit research papers for quality and completeness."""
    print("\n=== AUDITING RESEARCH PAPERS ===")
    
    research_dir = 'docs/research'
    if not os.path.exists(research_dir):
        print("Research directory not found")
        return
    
    audit_results = {
        'total_files': 0,
        'files_with_issues': 0,
        'issues': {
            'missing_title': [],
            'missing_doi': [],
            'missing_authors': [],
            'missing_abstract': [],
            'empty_content': [],
            'malformed_metadata': []
        },
        'categories': {}
    }
    
    for root, dirs, files in os.walk(research_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                audit_results['total_files'] += 1
                
                # Get relative path for category
                rel_path = os.path.relpath(root, research_dir)
                if rel_path == '.':
                    category = 'root'
                else:
                    category = rel_path.split(os.sep)[0]
                
                if category not in audit_results['categories']:
                    audit_results['categories'][category] = 0
                audit_results['categories'][category] += 1
                
                # Audit file content
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    has_issues = False
                    
                    # Check for title
                    if 'title:' not in content:
                        audit_results['issues']['missing_title'].append(filepath)
                        has_issues = True
                    
                    # Check for DOI
                    if 'doi:' not in content:
                        audit_results['issues']['missing_doi'].append(filepath)
                        has_issues = True
                    
                    # Check for authors
                    if 'authors:' not in content:
                        audit_results['issues']['missing_authors'].append(filepath)
                        has_issues = True
                    
                    # Check for abstract
                    if '## Abstract' not in content and '**Abstract**' not in content:
                        audit_results['issues']['missing_abstract'].append(filepath)
                        has_issues = True
                    
                    # Check for empty content
                    if len(content.strip()) < 100:
                        audit_results['issues']['empty_content'].append(filepath)
                        has_issues = True
                    
                    # Check for malformed metadata
                    if content.count('---') < 2:
                        audit_results['issues']['malformed_metadata'].append(filepath)
                        has_issues = True
                    
                    if has_issues:
                        audit_results['files_with_issues'] += 1
                        
                except Exception as e:
                    print(f"Error reading {filepath}: {str(e)[:50]}")
    
    return audit_results

def generate_cleanup_report(audit_results):
    """Generate a comprehensive cleanup report."""
    print("\n=== CLEANUP REPORT ===")
    
    print(f"Total research papers: {audit_results['total_files']}")
    print(f"Files with issues: {audit_results['files_with_issues']}")
    if audit_results['total_files'] > 0:
        quality_score = ((audit_results['total_files'] - audit_results['files_with_issues']) / audit_results['total_files'] * 100)
        print(f"Quality score: {quality_score:.1f}%")
    
    print("\n=== ISSUES FOUND ===")
    for issue_type, files in audit_results['issues'].items():
        if files:
            print(f"{issue_type}: {len(files)} files")
            if len(files) <= 5:
                for f in files:
                    print(f"  - {f}")
            else:
                print(f"  - {files[0]} (and {len(files)-1} more)")
            print()
    
    print("=== CATEGORY BREAKDOWN ===")
    for category, count in sorted(audit_results['categories'].items()):
        print(f"{category}: {count} files")
    
    # Save report
    with open('cleanup_report.json', 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: cleanup_report.json")

def main():
    print("=== PROJECT CLEANUP AND AUDIT ===\n")
    
    # Clean up temporary files
    cleanup_temporary_files()
    
    # Remove empty directories
    remove_empty_directories()
    
    # Audit research papers
    audit_results = audit_research_papers()
    
    # Generate report
    generate_cleanup_report(audit_results)
    
    print("\n=== CLEANUP COMPLETE ===")
    print("Project folder has been cleaned up and research papers audited.")

if __name__ == '__main__':
    main()
