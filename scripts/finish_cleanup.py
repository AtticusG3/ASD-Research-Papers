#!/usr/bin/env python3
"""
Finish the duplicate cleanup process
"""

import os
import yaml
from pathlib import Path
from collections import defaultdict

def safe_print(text):
    """Print text safely handling Unicode"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def finish_cleanup():
    """Finish the cleanup process"""
    research_dir = Path("docs/research")
    backup_dir = Path("duplicate_cleanup_backup")
    
    # Handle the remaining "- professional" files
    print("Handling remaining '- professional' files...")
    
    professional_files = []
    for file_path in research_dir.rglob("*.md"):
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
                            professional_files.append((file_path, len(content)))
                    except:
                        pass
        except:
            pass
    
    print(f"Found {len(professional_files)} '- professional' files")
    
    # Group by DOI and keep only the largest
    doi_groups = defaultdict(list)
    for file_path, size in professional_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end]
                    try:
                        frontmatter = yaml.safe_load(yaml_content)
                        doi = frontmatter.get('doi', '')
                        if doi:
                            doi_groups[doi].append((file_path, size))
                    except:
                        pass
        except:
            pass
    
    removed_count = 0
    for doi, files in doi_groups.items():
        if len(files) > 1:
            # Sort by size and keep the largest
            files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove all but the largest
            for file_path, size in files[1:]:
                try:
                    # Backup
                    backup_path = backup_dir / file_path.relative_to(research_dir)
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    
                    # Remove
                    file_path.unlink()
                    removed_count += 1
                    safe_print(f"  Removed: {file_path.relative_to(research_dir)}")
                except Exception as e:
                    safe_print(f"  Error removing {file_path}: {str(e)}")
    
    print(f"Removed {removed_count} additional duplicate files")
    
    # Final statistics
    all_files = list(research_dir.rglob("*.md"))
    print(f"\nFinal count: {len(all_files)} files")
    
    # Directory breakdown
    stats = {}
    for file_path in all_files:
        condition = file_path.parent.name
        if condition not in stats:
            stats[condition] = 0
        stats[condition] += 1
    
    print("\nFinal directory breakdown:")
    for condition, count in sorted(stats.items()):
        print(f"  {condition}: {count} files")
    
    total = sum(stats.values())
    print(f"\nTotal files: {total}")
    
    return total

if __name__ == "__main__":
    finish_cleanup()
