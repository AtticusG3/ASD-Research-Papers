#!/usr/bin/env python3
"""
Simple script to restore subdirectory structure without Unicode issues.
"""

import os
import shutil

def create_subdirectories():
    """Create the subdirectory structure."""
    base_dir = 'docs/research'
    subdirs = [
        'related-disorders/anxiety',
        'related-disorders/depression', 
        'related-disorders/ocd',
        'related-disorders/learning-disabilities',
        'hormones-endocrine/stress-cortisol',
        'hormones-endocrine/pmdd',
        'hormones-endocrine/sex-hormones',
        'hormones-endocrine/thyroid',
        'hormones-endocrine/growth-hormones'
    ]
    
    for subdir in subdirs:
        full_path = os.path.join(base_dir, subdir)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created: {full_path}")

def categorize_file(filename):
    """Categorize a file based on its filename."""
    file_lower = filename.lower()
    
    # PMDD and menstrual-related
    if any(word in file_lower for word in ['pmdd', 'premenstrual', 'menstrual', 'luteal', 'ovulation']):
        return 'pmdd'
    
    # Stress and cortisol
    if any(word in file_lower for word in ['stress', 'cortisol', 'adrenal', 'hpa', 'glucocorticoid']):
        return 'stress-cortisol'
    
    # Sex hormones
    if any(word in file_lower for word in ['sex', 'hormone', 'estrogen', 'testosterone', 'progesterone', 'androgen']):
        return 'sex-hormones'
    
    # Thyroid
    if any(word in file_lower for word in ['thyroid', 'hypothyroid', 'hyperthyroid', 'tsh', 't3', 't4']):
        return 'thyroid'
    
    # Growth hormones
    if any(word in file_lower for word in ['growth', 'hormone', 'igf', 'somatotropin', 'gh']):
        return 'growth-hormones'
    
    # Anxiety
    if any(word in file_lower for word in ['anxiety', 'anxious', 'panic', 'worry']):
        return 'anxiety'
    
    # Depression
    if any(word in file_lower for word in ['depression', 'depressive', 'mood', 'suicidal']):
        return 'depression'
    
    # OCD
    if any(word in file_lower for word in ['ocd', 'obsessive', 'compulsive', 'ritual']):
        return 'ocd'
    
    # Learning disabilities
    if any(word in file_lower for word in ['learning', 'disability', 'cognitive', 'intellectual']):
        return 'learning-disabilities'
    
    return 'other'

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
        
        # Determine target directory
        if category in ['anxiety', 'depression', 'ocd', 'learning-disabilities']:
            target_dir = f'docs/research/related-disorders/{category}'
        else:
            target_dir = f'docs/research/hormones-endocrine/{category}'
        
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Move file
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
    print("=== Restoring Subdirectory Structure ===\n")
    
    print("1. Creating subdirectories...")
    create_subdirectories()
    
    print("\n2. Organizing files...")
    organize_files()
    
    print("\n=== Final Directory Structure ===")
    
    # Show final structure
    dirs_to_check = [
        'docs/research/related-disorders',
        'docs/research/hormones-endocrine'
    ]
    
    for base_dir in dirs_to_check:
        if os.path.exists(base_dir):
            print(f"\n{base_dir}:")
            for item in sorted(os.listdir(base_dir)):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path):
                    count = len([f for f in os.listdir(item_path) if f.endswith('.md')])
                    print(f"  {item}/: {count} files")

if __name__ == '__main__':
    main()
