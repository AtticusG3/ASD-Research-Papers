#!/usr/bin/env python3
"""
Comprehensive cleanup script for research papers collection.
Handles:
1. Professional files (failed scrapes with generic titles)
2. DOI duplicates (keeping best version)
3. Subdirectory reorganization
"""

import os
import re
import json
import shutil
from collections import defaultdict
from pathlib import Path
import hashlib

def get_file_quality_score(filepath):
    """Score file quality based on content length, title quality, etc."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        score = 0
        
        # Check title quality
        title_match = re.search(r'title:\s*([^\n]+)', content)
        if title_match:
            title = title_match.group(1).strip()
            if title and title != '- professional' and len(title) > 10:
                score += 100
            else:
                score -= 50  # Penalty for bad titles
        
        # Check content length
        content_length = len(content)
        if content_length > 5000:
            score += 50
        elif content_length > 2000:
            score += 25
        elif content_length > 1000:
            score += 10
        
        # Check for abstract
        if '## Abstract' in content or '**Abstract**' in content:
            score += 25
        
        # Check for proper metadata
        if 'doi:' in content and 'authors:' in content:
            score += 25
        
        # Check for professional title (penalty)
        if 'title_-_professional' in filepath or '- professional' in content:
            score -= 100
        
        return score
    except Exception as e:
        print(f"Error scoring {filepath}: {e}")
        return -1000

def find_duplicates():
    """Find all duplicate files by DOI."""
    doi_files = defaultdict(list)
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        doi_match = re.search(r'doi:\s*([^\s\n]+)', content, re.IGNORECASE)
                        if doi_match:
                            doi = doi_match.group(1).strip()
                            doi = re.sub(r'[^\w\.\-\/]', '', doi)
                            if doi and len(doi) > 5:
                                doi_files[doi].append(filepath)
                except Exception as e:
                    print(f'Error reading {filepath}: {e}')
    
    return {doi: files for doi, files in doi_files.items() if len(files) > 1}

def find_professional_files():
    """Find files with 'professional' in title."""
    professional_files = []
    
    for root, dirs, files in os.walk('docs/research'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if re.search(r'title:\s*.*professional.*', content, re.IGNORECASE):
                            professional_files.append(filepath)
                except Exception as e:
                    print(f'Error reading {filepath}: {e}')
    
    return professional_files

def find_subdirectories():
    """Find subdirectories that need reorganization."""
    subdirs = []
    
    for root, dirs, files in os.walk('docs/research'):
        if root == 'docs/research':
            continue
            
        rel_path = os.path.relpath(root, 'docs/research')
        if '/' in rel_path or '\\' in rel_path:
            subdirs.append(root)
    
    return subdirs

def cleanup_duplicates(duplicates, dry_run=True):
    """Remove duplicate files, keeping the best version."""
    removed_files = []
    kept_files = []
    
    for doi, files in duplicates.items():
        # Score each file
        scored_files = [(get_file_quality_score(f), f) for f in files]
        scored_files.sort(reverse=True)  # Best first
        
        # Keep the best file
        best_score, best_file = scored_files[0]
        kept_files.append(best_file)
        
        # Remove the rest
        for score, file in scored_files[1:]:
            if not dry_run:
                try:
                    os.remove(file)
                    removed_files.append(file)
                    print(f"Removed duplicate: {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")
            else:
                removed_files.append(file)
                print(f"Would remove duplicate: {file}")
    
    return removed_files, kept_files

def cleanup_professional_files(professional_files, dry_run=True):
    """Remove professional files that are likely failed scrapes."""
    removed_files = []
    
    for file in professional_files:
        # Check if this file has a good duplicate elsewhere
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for DOI
            doi_match = re.search(r'doi:\s*([^\s\n]+)', content, re.IGNORECASE)
            if doi_match:
                doi = doi_match.group(1).strip()
                doi = re.sub(r'[^\w\.\-\/]', '', doi)
                
                # Check if there's a better version elsewhere
                better_found = False
                for root, dirs, files in os.walk('docs/research'):
                    for other_file in files:
                        if other_file.endswith('.md') and other_file != os.path.basename(file):
                            other_path = os.path.join(root, other_file)
                            try:
                                with open(other_path, 'r', encoding='utf-8') as f2:
                                    other_content = f2.read()
                                if doi in other_content and get_file_quality_score(other_path) > get_file_quality_score(file):
                                    better_found = True
                                    break
                            except:
                                continue
                    if better_found:
                        break
                
                if better_found:
                    if not dry_run:
                        try:
                            os.remove(file)
                            removed_files.append(file)
                            print(f"Removed professional file (better version exists): {file}")
                        except Exception as e:
                            print(f"Error removing {file}: {e}")
                    else:
                        removed_files.append(file)
                        print(f"Would remove professional file (better version exists): {file}")
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    return removed_files

def reorganize_subdirectories(subdirs, dry_run=True):
    """Move files from subdirectories to appropriate main categories."""
    moved_files = []
    
    for subdir in subdirs:
        if not os.path.exists(subdir):
            continue
            
        # Determine target directory based on subdir name
        rel_path = os.path.relpath(subdir, 'docs/research')
        if 'cortisol-stress' in rel_path or 'stress' in rel_path:
            target_dir = 'docs/research/related-disorders'
        elif 'dopamine' in rel_path:
            target_dir = 'docs/research/neurochemistry'
        elif 'serotonin' in rel_path:
            target_dir = 'docs/research/neurochemistry'
        elif 'anxiety' in rel_path:
            target_dir = 'docs/research/related-disorders'
        elif 'depression' in rel_path:
            target_dir = 'docs/research/related-disorders'
        elif 'ocd' in rel_path:
            target_dir = 'docs/research/related-disorders'
        elif 'learning-disabilities' in rel_path:
            target_dir = 'docs/research/related-disorders'
        else:
            target_dir = 'docs/research/related-disorders'  # Default
        
        # Create target directory if it doesn't exist
        if not dry_run and not os.path.exists(target_dir):
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
                
                if not dry_run:
                    try:
                        shutil.move(src, dst)
                        moved_files.append((src, dst))
                        print(f"Moved: {src} -> {dst}")
                    except Exception as e:
                        print(f"Error moving {src}: {e}")
                else:
                    moved_files.append((src, dst))
                    print(f"Would move: {src} -> {dst}")
        
        # Remove empty subdirectory
        if not dry_run:
            try:
                if not os.listdir(subdir):
                    os.rmdir(subdir)
                    print(f"Removed empty directory: {subdir}")
            except Exception as e:
                print(f"Error removing directory {subdir}: {e}")
    
    return moved_files

def main():
    print("=== Comprehensive Research Papers Cleanup ===\n")
    
    # Find issues
    print("1. Finding duplicates...")
    duplicates = find_duplicates()
    print(f"   Found {len(duplicates)} DOIs with duplicates")
    
    print("\n2. Finding professional files...")
    professional_files = find_professional_files()
    print(f"   Found {len(professional_files)} professional files")
    
    print("\n3. Finding subdirectories...")
    subdirs = find_subdirectories()
    print(f"   Found {len(subdirs)} subdirectories")
    
    # Ask user for confirmation
    print(f"\n=== CLEANUP SUMMARY ===")
    print(f"DOIs with duplicates: {len(duplicates)}")
    print(f"Professional files to check: {len(professional_files)}")
    print(f"Subdirectories to reorganize: {len(subdirs)}")
    
    response = input("\nProceed with cleanup? (y/n): ").lower().strip()
    if response != 'y':
        print("Cleanup cancelled.")
        return
    
    # Perform cleanup
    print("\n=== PERFORMING CLEANUP ===")
    
    print("\n1. Cleaning up duplicates...")
    removed_duplicates, kept_duplicates = cleanup_duplicates(duplicates, dry_run=False)
    print(f"   Removed {len(removed_duplicates)} duplicate files")
    print(f"   Kept {len(kept_duplicates)} best versions")
    
    print("\n2. Cleaning up professional files...")
    removed_professional = cleanup_professional_files(professional_files, dry_run=False)
    print(f"   Removed {len(removed_professional)} professional files")
    
    print("\n3. Reorganizing subdirectories...")
    moved_files = reorganize_subdirectories(subdirs, dry_run=False)
    print(f"   Moved {len(moved_files)} files")
    
    # Save cleanup log
    cleanup_log = {
        'removed_duplicates': removed_duplicates,
        'kept_duplicates': kept_duplicates,
        'removed_professional': removed_professional,
        'moved_files': moved_files,
        'summary': {
            'duplicates_removed': len(removed_duplicates),
            'professional_removed': len(removed_professional),
            'files_moved': len(moved_files)
        }
    }
    
    with open('cleanup_log.json', 'w', encoding='utf-8') as f:
        json.dump(cleanup_log, f, indent=2, ensure_ascii=False)
    
    print(f"\nCleanup completed! Log saved to cleanup_log.json")
    print(f"Total files removed: {len(removed_duplicates) + len(removed_professional)}")
    print(f"Total files moved: {len(moved_files)}")

if __name__ == '__main__':
    main()
