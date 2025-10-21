#!/usr/bin/env python3
"""
Organize remaining files in related-disorders into appropriate subdirectories.
"""

import os
import shutil

def categorize_file(filename):
    """Categorize a file based on its filename."""
    file_lower = filename.lower()
    
    # Bipolar disorder
    if any(word in file_lower for word in ['bipolar', 'mania', 'manic', 'hypomania']):
        return 'bipolar'
    
    # Eating disorders
    if any(word in file_lower for word in ['eating', 'anorexia', 'bulimia', 'binge', 'food', 'weight']):
        return 'eating-disorders'
    
    # Sleep disorders
    if any(word in file_lower for word in ['sleep', 'insomnia', 'narcolepsy', 'circadian', 'dream']):
        return 'sleep-disorders'
    
    # Substance use
    if any(word in file_lower for word in ['substance', 'alcohol', 'drug', 'addiction', 'dependence', 'cannabis', 'opioid']):
        return 'substance-use'
    
    # Personality disorders
    if any(word in file_lower for word in ['personality', 'borderline', 'narcissistic', 'antisocial', 'schizoid']):
        return 'personality-disorders'
    
    # Trauma/PTSD
    if any(word in file_lower for word in ['trauma', 'ptsd', 'post-traumatic', 'stress', 'abuse', 'violence']):
        return 'trauma-ptsd'
    
    # Sensory processing
    if any(word in file_lower for word in ['sensory', 'processing', 'sensitivity', 'hypersensitivity', 'tactile', 'auditory']):
        return 'sensory-processing'
    
    # Developmental delays
    if any(word in file_lower for word in ['developmental', 'delay', 'milestone', 'motor', 'speech', 'language']):
        return 'developmental-delays'
    
    # Genetic syndromes
    if any(word in file_lower for word in ['syndrome', 'genetic', 'chromosome', 'fragile', 'down', 'williams', 'angelman']):
        return 'genetic-syndromes'
    
    # Neurological conditions
    if any(word in file_lower for word in ['neurological', 'epilepsy', 'seizure', 'migraine', 'headache', 'stroke']):
        return 'neurological-conditions'
    
    return 'other'

def create_subdirectories():
    """Create the new subdirectories."""
    base_dir = 'docs/research/related-disorders'
    subdirs = [
        'bipolar',
        'eating-disorders',
        'sleep-disorders',
        'substance-use',
        'personality-disorders',
        'trauma-ptsd',
        'sensory-processing',
        'developmental-delays',
        'genetic-syndromes',
        'neurological-conditions'
    ]
    
    for subdir in subdirs:
        full_path = os.path.join(base_dir, subdir)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created: {full_path}")

def organize_files():
    """Organize files into appropriate subdirectories."""
    related_dir = 'docs/research/related-disorders'
    if not os.path.exists(related_dir):
        print("related-disorders directory not found")
        return
    
    files = [f for f in os.listdir(related_dir) if f.endswith('.md')]
    print(f"Organizing {len(files)} files...")
    
    moved_count = 0
    
    for file in files:
        src = os.path.join(related_dir, file)
        
        # Categorize the file
        category = categorize_file(file)
        
        if category == 'other':
            # Keep in related-disorders root
            continue
        
        # Move to appropriate subdirectory
        target_dir = f'docs/research/related-disorders/{category}'
        os.makedirs(target_dir, exist_ok=True)
        
        dst = os.path.join(target_dir, file)
        
        # Handle filename conflicts
        counter = 1
        base_dst = dst
        while os.path.exists(dst):
            name, ext = os.path.splitext(base_dst)
            dst = f"{name}_{counter}{ext}"
            counter += 1
        
        try:
            shutil.move(src, dst)
            moved_count += 1
            print(f"Moved to {category}: {file[:50]}...")
        except Exception as e:
            print(f"Error moving {file[:50]}: {str(e)[:50]}")
    
    print(f"Moved {moved_count} files to subdirectories")

def main():
    print("=== Organizing Related Disorders ===\n")
    
    print("1. Creating subdirectories...")
    create_subdirectories()
    
    print("\n2. Organizing files...")
    organize_files()
    
    print("\n=== Final Related Disorders Structure ===")
    
    # Show final structure
    related_dir = 'docs/research/related-disorders'
    if os.path.exists(related_dir):
        print(f"\n{related_dir}:")
        
        # Count root files
        root_files = [f for f in os.listdir(related_dir) if f.endswith('.md')]
        if root_files:
            print(f"  (root): {len(root_files)} files")
        
        # Count subdirectory files
        for item in sorted(os.listdir(related_dir)):
            item_path = os.path.join(related_dir, item)
            if os.path.isdir(item_path):
                count = len([f for f in os.listdir(item_path) if f.endswith('.md')])
                if count > 0:
                    print(f"  {item}/: {count} files")

if __name__ == '__main__':
    main()
