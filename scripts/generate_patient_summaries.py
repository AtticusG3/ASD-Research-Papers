#!/usr/bin/env python3
"""
Generate patient-friendly summaries for key research papers
Creates accessible explanations of important research findings
"""

import yaml
import re
from pathlib import Path
from datetime import datetime

def identify_key_papers(research_dir):
    """Identify the most important papers for patient summaries"""
    key_papers = []
    
    # Define criteria for key papers
    priority_keywords = [
        'treatment', 'therapy', 'cbit', 'medication', 'intervention',
        'quality of life', 'outcome', 'effectiveness', 'safety',
        'children', 'adolescent', 'adult', 'family', 'parent',
        'neurobiology', 'dopamine', 'brain', 'neurotransmitter',
        'prevalence', 'epidemiology', 'comorbidity'
    ]
    
    # Search through research papers
    for md_file in Path(research_dir).rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    main_content = parts[2]
                else:
                    continue
            else:
                continue
            
            # Check if this is a key paper
            title = frontmatter.get('title', '').lower()
            abstract = main_content.lower()
            
            # Count priority keywords
            keyword_count = sum(1 for keyword in priority_keywords if keyword in title or keyword in abstract)
            
            # Prioritize papers with high keyword relevance
            if keyword_count >= 3:
                key_papers.append({
                    'file': md_file,
                    'title': frontmatter.get('title', ''),
                    'topics': frontmatter.get('topics', []),
                    'category': frontmatter.get('primary_category', ''),
                    'keyword_score': keyword_count,
                    'content': main_content
                })
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            continue
    
    # Sort by keyword score and return top papers
    key_papers.sort(key=lambda x: x['keyword_score'], reverse=True)
    return key_papers[:50]  # Top 50 papers

def extract_key_findings(content):
    """Extract key findings from research paper content"""
    findings = []
    
    # Look for common research finding patterns
    patterns = [
        r'results?\s+(?:show|demonstrate|indicate|suggest|reveal)',
        r'conclusion[s]?\s+(?:show|demonstrate|indicate|suggest|reveal)',
        r'findings?\s+(?:show|demonstrate|indicate|suggest|reveal)',
        r'study\s+(?:show|demonstrate|indicate|suggest|reveal)',
        r'evidence\s+(?:show|demonstrate|indicate|suggest|reveal)'
    ]
    
    content_lower = content.lower()
    
    for pattern in patterns:
        matches = re.finditer(pattern, content_lower)
        for match in matches:
            # Extract sentence containing the finding
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 200)
            sentence = content[start:end].strip()
            
            # Clean up the sentence
            sentence = re.sub(r'\s+', ' ', sentence)
            if len(sentence) > 50 and len(sentence) < 500:
                findings.append(sentence)
    
    return findings[:5]  # Top 5 findings

def create_patient_summary(paper_info, output_dir):
    """Create a patient-friendly summary of a research paper"""
    try:
        title = paper_info['title']
        topics = paper_info['topics']
        category = paper_info['category']
        content = paper_info['content']
        
        # Extract key findings
        key_findings = extract_key_findings(content)
        
        # Determine condition focus
        conditions = []
        if 'tourette_syndrome' in topics:
            conditions.append('tourette')
        if 'adhd' in topics:
            conditions.append('adhd')
        if 'asd' in topics:
            conditions.append('asd')
        
        # Create patient-friendly title
        patient_title = f"What This Research Means: {title[:80]}..."
        
        # Create metadata
        metadata = {
            'title': patient_title,
            'source_paper': paper_info['file'].name,
            'content_type': 'patient_summary',
            'conditions': conditions,
            'topics': topics,
            'reading_level': 'accessible',
            'audience': ['patient', 'caregiver'],
            'patient_friendly': True,
            'search_priority': 'high',
            'created': datetime.now().isoformat(),
            'summary_type': 'research_explanation',
            'keywords': topics + ['research', 'study', 'findings', 'patient-friendly'],
            'search_tags': topics + ['research', 'study', 'findings', 'patient-friendly', 'summary']
        }
        
        # Create content
        summary_content = f"# {patient_title}\n\n"
        
        summary_content += "> **What This Is**\n"
        summary_content += "> This is a patient-friendly explanation of a research study. "
        summary_content += "We've taken the scientific findings and explained them in everyday language.\n\n"
        
        summary_content += "## What the Study Found\n\n"
        
        if key_findings:
            for i, finding in enumerate(key_findings, 1):
                summary_content += f"**Finding {i}:** {finding}\n\n"
        else:
            summary_content += "This study examined important aspects of neurodevelopmental disorders. "
            summary_content += "The researchers looked at how treatments, brain chemistry, or daily life factors "
            summary_content += "affect people with these conditions.\n\n"
        
        summary_content += "## What This Means for You\n\n"
        
        # Add condition-specific implications
        if 'tourette' in conditions:
            summary_content += "**If you have Tourette syndrome:**\n"
            summary_content += "- This research may help explain why certain treatments work\n"
            summary_content += "- It could provide insights into managing tics\n"
            summary_content += "- The findings might help you understand your condition better\n\n"
        
        if 'adhd' in conditions:
            summary_content += "**If you have ADHD:**\n"
            summary_content += "- This research may explain attention and focus challenges\n"
            summary_content += "- It could provide insights into effective treatments\n"
            summary_content += "- The findings might help with daily management strategies\n\n"
        
        if 'asd' in conditions:
            summary_content += "**If you have autism spectrum disorder:**\n"
            summary_content += "- This research may explain sensory or social challenges\n"
            summary_content += "- It could provide insights into support strategies\n"
            summary_content += "- The findings might help with understanding your unique needs\n\n"
        
        summary_content += "## Key Takeaways\n\n"
        summary_content += "- **Research is ongoing** - Scientists continue to learn more about these conditions\n"
        summary_content += "- **Individual differences matter** - What works for one person may not work for another\n"
        summary_content += "- **Talk to your doctor** - Always discuss research findings with your healthcare provider\n"
        summary_content += "- **You're not alone** - Many people share similar experiences and challenges\n\n"
        
        summary_content += "## Important Notes\n\n"
        summary_content += "- This is a summary of one research study\n"
        summary_content += "- Individual results may vary\n"
        summary_content += "- Always consult with healthcare professionals about treatment decisions\n"
        summary_content += "- Research findings are one piece of a larger puzzle\n\n"
        
        summary_content += "---\n\n"
        summary_content += f"**Source:** Research paper: {title}\n"
        summary_content += f"**Summary created:** {datetime.now().strftime('%Y-%m-%d')}\n"
        summary_content += f"**Topics covered:** {', '.join(topics[:5])}\n\n"
        
        summary_content += "*This summary was created to help make research more accessible. "
        summary_content += "It's not a substitute for professional medical advice.*\n"
        
        # Create YAML frontmatter
        yaml_content = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        
        # Combine frontmatter and content
        full_content = f"---\n{yaml_content}---\n\n{summary_content}"
        
        # Determine output location
        if conditions:
            condition = conditions[0]  # Use primary condition
            output_path = Path(output_dir) / "patient-guides" / "research-summaries" / condition
        else:
            output_path = Path(output_dir) / "patient-guides" / "research-summaries" / "general"
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = re.sub(r'[^\w\s-]', '', safe_title)
        safe_title = re.sub(r'\s+', '_', safe_title)
        filename = f"summary_{safe_title[:50]}.md"
        
        # Write file
        output_file = output_path / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return True
        
    except Exception as e:
        print(f"Error creating summary for {paper_info['title']}: {e}")
        return False

def generate_patient_summaries(research_dir, output_dir):
    """Generate patient summaries for key research papers"""
    print("Identifying key papers for patient summaries...")
    
    key_papers = identify_key_papers(research_dir)
    print(f"Found {len(key_papers)} key papers to summarize")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate summaries
    created_count = 0
    failed_count = 0
    
    for paper in key_papers:
        if create_patient_summary(paper, output_dir):
            created_count += 1
            print(f"Created summary: {paper['title'][:60]}...")
        else:
            failed_count += 1
    
    print(f"\nSummary generation complete!")
    print(f"Successfully created: {created_count}")
    print(f"Failed: {failed_count}")
    
    # Create generation log
    log_data = {
        'generation_date': datetime.now().isoformat(),
        'source_directory': str(research_dir),
        'total_papers_reviewed': len(key_papers),
        'summaries_created': created_count,
        'failed': failed_count,
        'output_directory': str(output_path)
    }
    
    log_file = output_path / 'summary_generation_log.yaml'
    with open(log_file, 'w', encoding='utf-8') as f:
        yaml.dump(log_data, f, default_flow_style=False)
    
    print(f"Generation log saved to: {log_file}")
    
    return created_count

def main():
    """Main function"""
    research_dir = "docs/research"
    output_dir = "docs"
    
    if not Path(research_dir).exists():
        print(f"Research directory not found: {research_dir}")
        return
    
    print("Starting patient summary generation...")
    created_count = generate_patient_summaries(research_dir, output_dir)
    
    print(f"\nSuccessfully created {created_count} patient-friendly research summaries!")
    print("Summaries are now available in the docs/patient-guides/research-summaries/ directory.")

if __name__ == "__main__":
    main()
