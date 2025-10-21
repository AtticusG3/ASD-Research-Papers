#!/usr/bin/env python3
"""
Quick cleanup: Handle professional files and subdirectories
"""

import os
import yaml
from pathlib import Path
import shutil

def safe_print(text):
    """Print text safely handling Unicode"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def move_subdirectories():
    """Move subdirectory files to related-disorders"""
    print("Moving subdirectory files to related-disorders...")
    
    research_dir = Path("docs/research")
    related_dir = research_dir / "related-disorders"
    related_dir.mkdir(exist_ok=True)
    
    # Define subdirectories to move
    subdirs = [
        'cortisol-stress', 'dopamine', 'glutamate-gaba', 'growth-hormones',
        'norepinephrine', 'ocd', 'other-neurotransmitters', 'serotonin',
        'sex-hormones', 'thyroid'
    ]
    
    moved_count = 0
    
    for subdir_name in subdirs:
        subdir_path = research_dir / subdir_name
        if subdir_path.exists():
            print(f"  Moving {subdir_name}...")
            
            for file_path in subdir_path.glob("*.md"):
                try:
                    new_path = related_dir / file_path.name
                    
                    # Handle filename conflicts
                    counter = 1
                    while new_path.exists():
                        name_parts = file_path.stem, counter, file_path.suffix
                        new_path = related_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        counter += 1
                    
                    shutil.move(str(file_path), str(new_path))
                    moved_count += 1
                    safe_print(f"    Moved: {file_path.name}")
                    
                except Exception as e:
                    safe_print(f"    Error moving {file_path}: {str(e)}")
            
            # Remove empty subdirectory
            try:
                subdir_path.rmdir()
                safe_print(f"    Removed: {subdir_name}")
            except:
                pass
    
    print(f"Moved {moved_count} files")
    return moved_count

def check_professional_files():
    """Check professional files for better versions"""
    print("Checking professional files...")
    
    research_dir = Path("docs/research")
    all_files = list(research_dir.rglob("*.md"))
    
    professional_files = []
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end]
                    try:
                        frontmatter = yaml.safe_load(yaml_content)
                        title = frontmatter.get('title', '').strip().lower()
                        if title in ['- professional', 'title_-_professional']:
                            professional_files.append((file_path, frontmatter.get('doi', ''), len(content)))
                    except:
                        pass
        except:
            pass
    
    print(f"Found {len(professional_files)} professional files")
    
    # Check for better versions
    better_versions = 0
    for prof_file, prof_doi, prof_size in professional_files:
        if not prof_doi:
            continue
        
        for file_path in all_files:
            if file_path == prof_file:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end != -1:
                        yaml_content = content[3:yaml_end]
                        try:
                            frontmatter = yaml.safe_load(yaml_content)
                            title = frontmatter.get('title', '').strip().lower()
                            doi = frontmatter.get('doi', '')
                            
                            if doi == prof_doi and title not in ['- professional', 'title_-_professional']:
                                if len(content) > prof_size:
                                    better_versions += 1
                                    safe_print(f"  Better version found for {prof_file.name}")
                                    break
                        except:
                            pass
            except:
                pass
    
    print(f"Found {better_versions} professional files with better versions")
    return professional_files, better_versions

def main():
    print("Quick cleanup starting...")
    
    # Step 1: Move subdirectories
    moved = move_subdirectories()
    
    # Step 2: Check professional files
    prof_files, better_versions = check_professional_files()
    
    # Final count
    research_dir = Path("docs/research")
    all_files = list(research_dir.rglob("*.md"))
    print(f"\nTotal files: {len(all_files)}")
    
    # Directory breakdown
    stats = {}
    for file_path in all_files:
        condition = file_path.parent.name
        if condition not in stats:
            stats[condition] = 0
        stats[condition] += 1
    
    print("\nDirectory breakdown:")
    for condition, count in sorted(stats.items()):
        print(f"  {condition}: {count} files")

if __name__ == "__main__":
    main()
