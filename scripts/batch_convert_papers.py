#!/usr/bin/env python3
"""
Batch convert papers with enhanced metadata extraction
Processes papers in the research directories and adds enhanced metadata
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

def extract_enhanced_metadata(content, filename):
    """Extract enhanced metadata from paper content"""
    content_lower = content.lower()
    
    # Determine document type
    doc_type = "research_paper"
    if any(term in content_lower for term in ['case report', 'case study']):
        doc_type = "case_study"
    elif any(term in content_lower for term in ['review', 'meta-analysis']):
        doc_type = "review"
    elif any(term in content_lower for term in ['treatment', 'therapy', 'intervention']):
        doc_type = "treatment_guide"
    elif any(term in content_lower for term in ['epidemiology', 'prevalence', 'survey']):
        doc_type = "epidemiology_study"
    
    # Extract key topics
    topics = []
    if any(term in content_lower for term in ['tourette', 'tic', 'tics', 'gilles']):
        topics.append('tourette_syndrome')
    if any(term in content_lower for term in ['adhd', 'attention', 'deficit', 'hyperactivity']):
        topics.append('adhd')
    if any(term in content_lower for term in ['autism', 'spectrum', 'developmental', 'asperger']):
        topics.append('asd')
    if any(term in content_lower for term in ['ocd', 'obsessive', 'compulsive']):
        topics.append('ocd')
    if any(term in content_lower for term in ['anxiety', 'depression']):
        topics.append('mental_health')
    
    # Extract age groups
    age_groups = []
    if any(term in content_lower for term in ['children', 'child', 'pediatric']):
        age_groups.append('children')
    if any(term in content_lower for term in ['adolescent', 'teen', 'youth']):
        age_groups.append('adolescents')
    if any(term in content_lower for term in ['adult', 'adults']):
        age_groups.append('adults')
    
    # Extract treatment types
    treatments = []
    if any(term in content_lower for term in ['cbit', 'behavioral', 'intervention', 'habit reversal']):
        treatments.append('behavioral_therapy')
    if any(term in content_lower for term in ['medication', 'pharmacological', 'drug', 'haldol', 'risperidone']):
        treatments.append('pharmacological')
    if any(term in content_lower for term in ['therapy', 'psychotherapy']):
        treatments.append('psychotherapy')
    
    # Extract neurochemistry topics
    neurochemistry = []
    if any(term in content_lower for term in ['dopamine', 'dopaminergic']):
        neurochemistry.append('dopamine')
    if any(term in content_lower for term in ['serotonin', 'serotonergic']):
        neurochemistry.append('serotonin')
    if any(term in content_lower for term in ['norepinephrine', 'noradrenaline']):
        neurochemistry.append('norepinephrine')
    if any(term in content_lower for term in ['glutamate', 'gaba', 'gamma-aminobutyric']):
        neurochemistry.append('glutamate_gaba')
    
    # Extract hormone topics
    hormones = []
    if any(term in content_lower for term in ['cortisol', 'stress', 'hpa']):
        hormones.append('cortisol_stress')
    if any(term in content_lower for term in ['thyroid', 'thyroxine', 'tsh']):
        hormones.append('thyroid')
    if any(term in content_lower for term in ['testosterone', 'estrogen', 'progesterone', 'sex hormone']):
        hormones.append('sex_hormones')
    if any(term in content_lower for term in ['growth hormone', 'gh']):
        hormones.append('growth_hormones')
    
    # Extract study design
    study_design = "unknown"
    if any(term in content_lower for term in ['randomized', 'controlled trial', 'rct']):
        study_design = "randomized_controlled_trial"
    elif any(term in content_lower for term in ['cohort', 'longitudinal']):
        study_design = "cohort_study"
    elif any(term in content_lower for term in ['cross-sectional', 'survey']):
        study_design = "cross_sectional"
    elif any(term in content_lower for term in ['case report', 'case study']):
        study_design = "case_study"
    
    # Extract key findings
    key_findings = []
    if 'prevalence' in content_lower:
        key_findings.append('prevalence_data')
    if 'comorbidity' in content_lower:
        key_findings.append('comorbidity_analysis')
    if 'quality of life' in content_lower:
        key_findings.append('quality_of_life')
    if 'treatment' in content_lower:
        key_findings.append('treatment_outcomes')
    if 'neurobiology' in content_lower or 'brain' in content_lower:
        key_findings.append('neurobiological_insights')
    
    # Determine patient relevance
    patient_relevance = "low"
    if any(term in content_lower for term in ['treatment', 'therapy', 'quality of life', 'coping', 'support']):
        patient_relevance = "high"
    elif any(term in content_lower for term in ['symptoms', 'diagnosis', 'prevalence']):
        patient_relevance = "medium"
    
    # Extract publication year if available
    year_match = re.search(r'\b(19|20)\d{2}\b', content)
    publication_year = year_match.group() if year_match else "unknown"
    
    return {
        'document_type': doc_type,
        'topics': topics,
        'age_groups': age_groups,
        'treatments': treatments,
        'neurochemistry': neurochemistry,
        'hormones': hormones,
        'study_design': study_design,
        'key_findings': key_findings,
        'patient_relevance': patient_relevance,
        'publication_year': publication_year,
        'search_tags': topics + age_groups + treatments + neurochemistry + hormones + [study_design] + key_findings
    }

def process_paper(file_path):
    """Process a single paper file and add enhanced metadata"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract existing frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                existing_metadata = yaml.safe_load(parts[1]) or {}
                main_content = parts[2]
            else:
                existing_metadata = {}
                main_content = content
        else:
            existing_metadata = {}
            main_content = content
        
        # Extract enhanced metadata
        enhanced_metadata = extract_enhanced_metadata(main_content, file_path.name)
        
        # Merge metadata
        optimized_metadata = {
            'title': existing_metadata.get('title', file_path.stem),
            'authors': existing_metadata.get('authors', ''),
            'source': existing_metadata.get('source', ''),
            'filename': existing_metadata.get('filename', file_path.name),
            'keywords': existing_metadata.get('keywords', ''),
            'type': existing_metadata.get('type', 'research_paper'),
            'created': datetime.now().isoformat(),
            'optimized_for_search': True,
            **enhanced_metadata
        }
        
        # Create optimized content
        optimized_content = "---\n"
        optimized_content += yaml.dump(optimized_metadata, default_flow_style=False, allow_unicode=True)
        optimized_content += "---\n\n"
        optimized_content += main_content
        
        # Add search optimization section at the end
        search_section = f"""

---

## Search Optimization

**Document Type**: {optimized_metadata['document_type']}
**Primary Topics**: {', '.join(optimized_metadata['topics'])}
**Age Groups**: {', '.join(optimized_metadata['age_groups'])}
**Treatment Types**: {', '.join(optimized_metadata['treatments'])}
**Neurochemistry**: {', '.join(optimized_metadata['neurochemistry'])}
**Hormones**: {', '.join(optimized_metadata['hormones'])}
**Study Design**: {optimized_metadata['study_design']}
**Key Findings**: {', '.join(optimized_metadata['key_findings'])}
**Patient Relevance**: {optimized_metadata['patient_relevance']}
**Publication Year**: {optimized_metadata['publication_year']}

**Search Tags**: {', '.join(optimized_metadata['search_tags'])}

*This document has been optimized for searchability in OpenWebUI knowledge base.*
"""
        
        optimized_content += search_section
        
        # Write optimized content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def batch_convert_papers():
    """Process all papers in the research directories"""
    research_dir = Path('docs/research')
    
    if not research_dir.exists():
        print("Research directory not found!")
        return
    
    # Find all markdown files in research subdirectories
    markdown_files = []
    for subdir in research_dir.rglob('*.md'):
        markdown_files.append(subdir)
    
    print(f"Found {len(markdown_files)} papers to process")
    
    processed_count = 0
    for md_file in markdown_files:
        if process_paper(md_file):
            processed_count += 1
            print(f"Processed: {md_file.name}")
    
    print(f"Successfully processed {processed_count}/{len(markdown_files)} papers")

if __name__ == "__main__":
    batch_convert_papers()
