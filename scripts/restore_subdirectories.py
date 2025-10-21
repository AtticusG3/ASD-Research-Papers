#!/usr/bin/env python3
"""
Restore subdirectory structure for better organization of research papers.
"""

import os
import shutil
import re
from pathlib import Path

def categorize_file(filename, content=""):
    """Categorize a file based on its filename and content."""
    file_lower = filename.lower()
    
    # Read content if not provided
    if not content:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().lower()
        except:
            content = file_lower
    
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
        print(f"Created directory: {full_path}")

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
        category = categorize_file(src)
        
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
            print(f"Moved: {file} -> {category}")
        except Exception as e:
            print(f"Error moving {file}: {e}")
    
    print(f"Moved {moved_count} files to subdirectories")

def organize_hormones_endocrine():
    """Organize files in hormones-endocrine directory."""
    hormones_dir = 'docs/research/hormones-endocrine'
    if not os.path.exists(hormones_dir):
        return
    
    files = [f for f in os.listdir(hormones_dir) if f.endswith('.md')]
    print(f"Organizing {len(files)} files in hormones-endocrine...")
    
    moved_count = 0
    
    for file in files:
        src = os.path.join(hormones_dir, file)
        
        # Categorize the file
        category = categorize_file(src)
        
        if category == 'other':
            # Keep in hormones-endocrine root
            continue
        
        # Move to appropriate subdirectory
        target_dir = f'docs/research/hormones-endocrine/{category}'
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
            print(f"Moved: {file} -> {category}")
        except Exception as e:
            print(f"Error moving {file}: {e}")
    
    print(f"Moved {moved_count} files in hormones-endocrine")

def main():
    print("=== Restoring Subdirectory Structure ===\n")
    
    print("1. Creating subdirectories...")
    create_subdirectories()
    
    print("\n2. Organizing files in related-disorders...")
    organize_files()
    
    print("\n3. Organizing files in hormones-endocrine...")
    organize_hormones_endocrine()
    
    print("\n=== Final Directory Structure ===")
    
    # Show final structure
    dirs_to_check = [
        'docs/research/related-disorders',
        'docs/research/hormones-endocrine',
        'docs/research/neurochemistry'
    ]
    
    for base_dir in dirs_to_check:
        if os.path.exists(base_dir):
            print(f"\n{base_dir}:")
            for item in sorted(os.listdir(base_dir)):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path):
                    count = len([f for f in os.listdir(item_path) if f.endswith('.md')])
                    print(f"  {item}/: {count} files")
                elif item.endswith('.md'):
                    # Count root files
                    root_files = len([f for f in os.listdir(base_dir) if f.endswith('.md')])
                    if root_files > 0:
                        print(f"  (root): {root_files} files")
                    break

if __name__ == '__main__':
    main()
