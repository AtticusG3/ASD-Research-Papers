#!/usr/bin/env python3
"""
Final cleanup script to handle remaining professional files and subdirectories.
"""

import os
import re
import shutil
from pathlib import Path

def remove_remaining_professional_files():
    """Remove all remaining professional files."""
    removed_count = 0
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if 'professional' in file.lower():
                filepath = os.path.join(root, file)
                try:
                    os.remove(filepath)
                    removed_count += 1
                    print(f"Removed: {filepath}")
                except Exception as e:
                    print(f"Error removing {filepath}: {e}")
    
    return removed_count

def move_remaining_subdirectories():
    """Move files from any remaining subdirectories."""
    moved_count = 0
    
    # Find all subdirectories
    subdirs = []
    for root, dirs, files in os.walk('docs/research'):
        if root == 'docs/research':
            continue
        rel_path = os.path.relpath(root, 'docs/research')
        if '/' in rel_path or '\\' in rel_path:
            subdirs.append(root)
    
    for subdir in subdirs:
        if not os.path.exists(subdir):
            continue
            
        # Determine target directory
        rel_path = os.path.relpath(subdir, 'docs/research')
        if 'pmdd' in rel_path.lower():
            target_dir = 'docs/research/related-disorders'
        elif 'sex-hormones' in rel_path.lower():
            target_dir = 'docs/research/related-disorders'
        elif 'thyroid' in rel_path.lower():
            target_dir = 'docs/research/related-disorders'
        else:
            target_dir = 'docs/research/related-disorders'  # Default
        
        # Create target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Move files
        for file in os.listdir(subdir):
            if file.endswith('.md'):
                src = os.path.join(subdir, file)
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
                    print(f"Moved: {src} -> {dst}")
                except Exception as e:
                    print(f"Error moving {src}: {e}")
        
        # Remove empty subdirectory
        try:
            if not os.listdir(subdir):
                os.rmdir(subdir)
                print(f"Removed empty directory: {subdir}")
        except Exception as e:
            print(f"Error removing directory {subdir}: {e}")
    
    return moved_count

def main():
    print("=== Final Cleanup ===\n")
    
    print("1. Removing remaining professional files...")
    removed_professional = remove_remaining_professional_files()
    print(f"   Removed {removed_professional} professional files")
    
    print("\n2. Moving remaining subdirectories...")
    moved_files = move_remaining_subdirectories()
    print(f"   Moved {moved_files} files")
    
    print("\n=== Final Statistics ===")
    
    # Count files in each directory
    dirs = ['docs/research/adhd', 'docs/research/asd', 'docs/research/tourette', 
            'docs/research/comorbidity', 'docs/research/related-disorders', 
            'docs/research/neurochemistry', 'docs/research/hormones-endocrine']
    
    total = 0
    for dir_path in dirs:
        if os.path.exists(dir_path):
            count = len([f for f in os.listdir(dir_path) if f.endswith('.md')])
            print(f'{dir_path}: {count} files')
            total += count
        else:
            print(f'{dir_path}: Directory not found')
    
    print(f'\nTotal files: {total}')
    
    # Check for remaining professional files
    professional_count = 0
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if 'professional' in file.lower():
                professional_count += 1
    
    print(f'Remaining professional files: {professional_count}')
    
    # Check for remaining subdirectories
    subdir_count = 0
    for root, dirs, files in os.walk('docs/research'):
        if root == 'docs/research':
            continue
        rel_path = os.path.relpath(root, 'docs/research')
        if '/' in rel_path or '\\' in rel_path:
            subdir_count += 1
    
    print(f'Remaining subdirectories: {subdir_count}')

if __name__ == '__main__':
    main()