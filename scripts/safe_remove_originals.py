#!/usr/bin/env python3
"""
Safe removal script for original HTML and PDF files after audit verification.
Creates a backup log and removes files only if they have been properly processed.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

def safe_remove_original_files(audit_file="file_audit_results.json", backup_dir="backup_originals"):
    """Safely remove original files after audit verification."""
    
    # Load audit results
    if not os.path.exists(audit_file):
        print(f"Audit file {audit_file} not found. Run audit first.")
        return False
    
    with open(audit_file, 'r', encoding='utf-8') as f:
        audit_results = json.load(f)
    
    removal_plan = audit_results.get("removal_plan", {})
    safe_to_remove = removal_plan.get("safe_to_remove", [])
    
    if not safe_to_remove:
        print("No files marked as safe to remove.")
        return True
    
    # Create backup directory
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    # Create removal log
    removal_log = {
        "removal_date": datetime.now().isoformat(),
        "audit_file": audit_file,
        "backup_directory": str(backup_path),
        "files_removed": [],
        "errors": []
    }
    
    print(f"Starting safe removal of {len(safe_to_remove)} files...")
    print(f"Backup directory: {backup_path}")
    
    removed_count = 0
    total_size_freed = 0
    
    for file_info in safe_to_remove:
        filename = file_info["file"]
        file_type = file_info["type"]
        file_size = file_info["size"]
        markdown_file = file_info["markdown_file"]
        
        print(f"Processing {file_type.upper()}: {filename}")
        
        try:
            # Verify markdown file exists
            if not os.path.exists(markdown_file):
                error_msg = f"Markdown file not found: {markdown_file}"
                print(f"  ERROR: {error_msg}")
                removal_log["errors"].append({
                    "file": filename,
                    "error": error_msg
                })
                continue
            
            # Create backup
            backup_file = backup_path / filename
            shutil.copy2(filename, backup_file)
            
            # Remove original file
            os.remove(filename)
            
            # Log successful removal
            removal_log["files_removed"].append({
                "original_file": filename,
                "file_type": file_type,
                "file_size": file_size,
                "markdown_file": markdown_file,
                "backup_file": str(backup_file),
                "removed_at": datetime.now().isoformat()
            })
            
            removed_count += 1
            total_size_freed += file_size
            print(f"  SUCCESS: Removed and backed up")
            
        except Exception as e:
            error_msg = f"Failed to remove {filename}: {str(e)}"
            print(f"  ERROR: {error_msg}")
            removal_log["errors"].append({
                "file": filename,
                "error": error_msg
            })
    
    # Save removal log
    log_file = f"removal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(removal_log, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 50)
    print("REMOVAL SUMMARY")
    print("=" * 50)
    print(f"Files successfully removed: {removed_count}/{len(safe_to_remove)}")
    print(f"Total size freed: {total_size_freed:,} bytes ({total_size_freed/1024/1024:.1f} MB)")
    print(f"Backup directory: {backup_path}")
    print(f"Removal log saved to: {log_file}")
    
    if removal_log["errors"]:
        print(f"\nErrors encountered: {len(removal_log['errors'])}")
        for error in removal_log["errors"]:
            print(f"  - {error['file']}: {error['error']}")
    
    return removed_count == len(safe_to_remove)

def main():
    """Main function to execute safe removal."""
    print("Safe Original Files Removal Script")
    print("=" * 50)
    
    # Check if audit file exists
    if not os.path.exists("file_audit_results.json"):
        print("ERROR: file_audit_results.json not found.")
        print("Please run the audit script first: python scripts/audit_original_files.py")
        return
    
    # Auto-confirm removal since audit has verified safety
    print("This will remove original HTML and PDF files that have been processed.")
    print("Files will be backed up before removal.")
    print("Proceeding automatically based on audit results...")
    
    # Execute removal
    success = safe_remove_original_files()
    
    if success:
        print("\nAll files successfully removed and backed up!")
    else:
        print("\nSome files could not be removed. Check the log for details.")

if __name__ == "__main__":
    main()
