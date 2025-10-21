#!/usr/bin/env python3
"""
Audit and update patient documentation with current research data.
"""

import os
import json
import re
from pathlib import Path

def audit_patient_docs():
    """Audit patient documentation for completeness and accuracy."""
    print("=== AUDITING PATIENT DOCUMENTATION ===")
    
    audit_results = {
        'total_files': 0,
        'files_with_issues': 0,
        'missing_links': [],
        'outdated_content': [],
        'missing_sections': [],
        'categories': {}
    }
    
    # Check patient guides
    patient_guides_dir = 'docs/patient-guides'
    if os.path.exists(patient_guides_dir):
        for root, dirs, files in os.walk(patient_guides_dir):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    audit_results['total_files'] += 1
                    
                    # Get category
                    rel_path = os.path.relpath(root, patient_guides_dir)
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
                        
                        # Check for research paper links
                        if not re.search(r'\[.*\]\(.*research.*\)', content):
                            audit_results['missing_links'].append(filepath)
                            has_issues = True
                        
                        # Check for outdated content indicators
                        if any(word in content.lower() for word in ['outdated', 'old', 'deprecated', 'obsolete']):
                            audit_results['outdated_content'].append(filepath)
                            has_issues = True
                        
                        # Check for missing sections
                        if len(content.strip()) < 500:
                            audit_results['missing_sections'].append(filepath)
                            has_issues = True
                        
                        if has_issues:
                            audit_results['files_with_issues'] += 1
                            
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
    
    # Check support resources
    support_dir = 'docs/support'
    if os.path.exists(support_dir):
        for root, dirs, files in os.walk(support_dir):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    audit_results['total_files'] += 1
                    
                    # Get category
                    rel_path = os.path.relpath(root, support_dir)
                    if rel_path == '.':
                        category = 'support-root'
                    else:
                        category = f"support-{rel_path.split(os.sep)[0]}"
                    
                    if category not in audit_results['categories']:
                        audit_results['categories'][category] = 0
                    audit_results['categories'][category] += 1
                    
                    # Audit file content
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        has_issues = False
                        
                        # Check for research paper links
                        if not re.search(r'\[.*\]\(.*research.*\)', content):
                            audit_results['missing_links'].append(filepath)
                            has_issues = True
                        
                        # Check for outdated content indicators
                        if any(word in content.lower() for word in ['outdated', 'old', 'deprecated', 'obsolete']):
                            audit_results['outdated_content'].append(filepath)
                            has_issues = True
                        
                        # Check for missing sections
                        if len(content.strip()) < 500:
                            audit_results['missing_sections'].append(filepath)
                            has_issues = True
                        
                        if has_issues:
                            audit_results['files_with_issues'] += 1
                            
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
    
    return audit_results

def get_research_paper_links():
    """Get links to research papers for linking in patient docs."""
    research_dir = 'docs/research'
    paper_links = {}
    
    if os.path.exists(research_dir):
        for root, dirs, files in os.walk(research_dir):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, 'docs')
                    
                    # Get category
                    category = rel_path.split(os.sep)[1]
                    
                    if category not in paper_links:
                        paper_links[category] = []
                    
                    # Get title from filename
                    title = file.replace('.md', '').replace('_', ' ').title()
                    paper_links[category].append({
                        'title': title,
                        'path': rel_path,
                        'filename': file
                    })
    
    return paper_links

def create_missing_directories():
    """Create missing directories for patient documentation."""
    print("\n=== CREATING MISSING DIRECTORIES ===")
    
    missing_dirs = [
        'docs/patient-guides/symptoms',
        'docs/support/relationships',
        'docs/support/school-work'
    ]
    
    for dir_path in missing_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created: {dir_path}")

def update_patient_docs_with_links():
    """Update patient documentation with links to research papers."""
    print("\n=== UPDATING PATIENT DOCS WITH LINKS ===")
    
    # Get research paper links
    paper_links = get_research_paper_links()
    
    # Update each patient doc file
    for root, dirs, files in os.walk('docs/patient-guides'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                update_file_with_links(filepath, paper_links)
    
    for root, dirs, files in os.walk('docs/support'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                update_file_with_links(filepath, paper_links)

def update_file_with_links(filepath, paper_links):
    """Update a single file with relevant research paper links."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file already has research links section
        if '## Research Papers' in content or '## Related Research' in content:
            return
        
        # Determine relevant categories based on file content
        relevant_categories = []
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['adhd', 'attention', 'hyperactivity']):
            relevant_categories.append('adhd')
        if any(word in content_lower for word in ['autism', 'asd', 'spectrum']):
            relevant_categories.append('asd')
        if any(word in content_lower for word in ['tourette', 'tic', 'tics']):
            relevant_categories.append('tourette')
        if any(word in content_lower for word in ['hormone', 'endocrine', 'pmdd']):
            relevant_categories.append('hormones-endocrine')
        if any(word in content_lower for word in ['neurochemistry', 'dopamine', 'serotonin']):
            relevant_categories.append('neurochemistry')
        if any(word in content_lower for word in ['comorbidity', 'comorbid']):
            relevant_categories.append('comorbidity')
        if any(word in content_lower for word in ['related', 'disorder']):
            relevant_categories.append('related-disorders')
        
        # Add research links section
        if relevant_categories:
            research_section = "\n\n## Related Research Papers\n\n"
            research_section += "The following research papers provide scientific evidence and detailed information on this topic:\n\n"
            
            for category in relevant_categories:
                if category in paper_links:
                    research_section += f"### {category.replace('-', ' ').title()}\n\n"
                    for paper in paper_links[category][:5]:  # Limit to 5 papers per category
                        research_section += f"- [{paper['title']}](../research/{paper['path']})\n"
                    research_section += "\n"
            
            # Append to content
            content += research_section
            
            # Write back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Updated: {filepath}")
    
    except Exception as e:
        print(f"Error updating {filepath}: {e}")

def generate_patient_docs_report(audit_results):
    """Generate a report on patient documentation audit."""
    print("\n=== PATIENT DOCS AUDIT REPORT ===")
    
    print(f"Total patient documentation files: {audit_results['total_files']}")
    print(f"Files with issues: {audit_results['files_with_issues']}")
    if audit_results['total_files'] > 0:
        quality_score = ((audit_results['total_files'] - audit_results['files_with_issues']) / audit_results['total_files'] * 100)
        print(f"Quality score: {quality_score:.1f}%")
    
    print("\n=== ISSUES FOUND ===")
    for issue_type, files in audit_results.items():
        if isinstance(files, list) and files:
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
    with open('patient_docs_audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: patient_docs_audit_report.json")

def main():
    print("=== PATIENT DOCUMENTATION AUDIT AND UPDATE ===\n")
    
    # Create missing directories
    create_missing_directories()
    
    # Audit patient documentation
    audit_results = audit_patient_docs()
    
    # Update patient docs with links
    update_patient_docs_with_links()
    
    # Generate report
    generate_patient_docs_report(audit_results)
    
    print("\n=== PATIENT DOCS UPDATE COMPLETE ===")
    print("Patient documentation has been audited and updated with research paper links.")

if __name__ == '__main__':
    main()
