#!/usr/bin/env python3
"""
Analyze remaining files in related-disorders root to suggest new subcategories.
"""

import os

def analyze_remaining_files():
    """Analyze files in related-disorders root for potential new subcategories."""
    related_dir = 'docs/research/related-disorders'
    if not os.path.exists(related_dir):
        print("related-disorders directory not found")
        return
    
    files = [f for f in os.listdir(related_dir) if f.endswith('.md')]
    print(f"Files in related-disorders root: {len(files)}")
    
    print("\n=== RECOMMENDED NEW SUBCATEGORIES ===")
    
    # Potential new subcategories based on DSM-5 and common conditions
    potential_categories = {
        'impulse-control-disorders': {
            'keywords': ['impulse', 'control', 'gambling', 'kleptomania', 'pyromania', 'trichotillomania', 'excoriation'],
            'files': []
        },
        'conduct-disorders': {
            'keywords': ['conduct', 'oppositional', 'defiant', 'aggression', 'violence', 'antisocial'],
            'files': []
        },
        'dissociative-disorders': {
            'keywords': ['dissociative', 'conversion', 'somatic', 'factitious', 'malingering'],
            'files': []
        },
        'psychotic-disorders': {
            'keywords': ['schizophrenia', 'psychosis', 'delusion', 'hallucination', 'catatonia'],
            'files': []
        },
        'mood-disorders': {
            'keywords': ['mania', 'hypomania', 'cyclothymia', 'dysthymia', 'bipolar'],
            'files': []
        },
        'adjustment-disorders': {
            'keywords': ['adjustment', 'grief', 'bereavement', 'stress', 'reactive'],
            'files': []
        },
        'communication-disorders': {
            'keywords': ['communication', 'pragmatic', 'selective', 'mutism', 'stuttering', 'speech', 'language'],
            'files': []
        },
        'movement-disorders': {
            'keywords': ['movement', 'tics', 'stereotypies', 'catatonia', 'negativism', 'echolalia', 'echopraxia'],
            'files': []
        },
        'social-disorders': {
            'keywords': ['social', 'attachment', 'disinhibited', 'reactive', 'social-cognition'],
            'files': []
        }
    }
    
    for file in files:
        file_lower = file.lower()
        for category, data in potential_categories.items():
            for keyword in data['keywords']:
                if keyword in file_lower:
                    data['files'].append(file)
                    break
    
    # Show categories that have files
    found_categories = False
    for category, data in potential_categories.items():
        if data['files']:
            found_categories = True
            print(f"{category}: {len(data['files'])} files")
            for f in data['files']:
                print(f"  - {f}")
            print()
    
    if not found_categories:
        print("No specific patterns found that clearly indicate new personality disorder categories.")
        print("The remaining files appear to be general related disorders research.")
    
    # Show some sample files to understand what's there
    print("\n=== SAMPLE OF REMAINING FILES ===")
    for i, file in enumerate(files[:10]):
        print(f"{i+1:2d}. {file}")
    
    if len(files) > 10:
        print(f"... and {len(files)-10} more files")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total files in root: {len(files)}")
    print("Current subcategories appear comprehensive for personality disorders.")
    print("The remaining files are likely general related disorders research")
    print("that doesn't fit into specific subcategories, which is appropriate.")

if __name__ == '__main__':
    analyze_remaining_files()
