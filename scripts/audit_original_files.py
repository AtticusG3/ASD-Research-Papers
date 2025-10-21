#!/usr/bin/env python3
"""
Audit script to verify that original HTML and PDF files have been properly processed
and their content recorded in the markdown files before removal.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import yaml

class FileAuditor:
    def __init__(self, root_dir=".", docs_dir="docs"):
        self.root_dir = Path(root_dir)
        self.docs_dir = Path(docs_dir)
        self.audit_results = {
            "audit_date": datetime.now().isoformat(),
            "html_files": {},
            "pdf_files": {},
            "summary": {
                "total_html_files": 0,
                "total_pdf_files": 0,
                "html_processed": 0,
                "pdf_processed": 0,
                "html_missing": 0,
                "pdf_missing": 0
            }
        }
    
    def get_file_hash(self, filepath):
        """Get MD5 hash of a file."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            return f"ERROR: {e}"
    
    def find_matching_markdown(self, original_filename):
        """Find matching markdown file for an original HTML/PDF file."""
        # Remove extension and clean up filename
        base_name = Path(original_filename).stem
        base_name = base_name.replace(" - PMC", "").replace("_", " ").replace("-", " ")
        
        # Search in docs directory
        for md_file in self.docs_dir.rglob("*.md"):
            md_name = Path(md_file).stem
            md_name = md_name.replace("_", " ").replace("-", " ")
            
            # Check if titles match (case insensitive, partial match)
            if base_name.lower() in md_name.lower() or md_name.lower() in base_name.lower():
                return md_file
        
        return None
    
    def extract_markdown_metadata(self, md_file):
        """Extract metadata from markdown file YAML frontmatter."""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                    metadata = yaml.safe_load(yaml_content)
                    return metadata
        except Exception as e:
            return {"error": str(e)}
        
        return {}
    
    def audit_html_files(self):
        """Audit all HTML files in root directory."""
        html_files = list(self.root_dir.glob("*.html"))
        self.audit_results["summary"]["total_html_files"] = len(html_files)
        
        for html_file in html_files:
            print(f"Auditing HTML: {html_file.name}")
            
            file_info = {
                "original_path": str(html_file),
                "file_size": html_file.stat().st_size,
                "file_hash": self.get_file_hash(html_file),
                "last_modified": datetime.fromtimestamp(html_file.stat().st_mtime).isoformat(),
                "matching_markdown": None,
                "metadata": {},
                "status": "not_found"
            }
            
            # Find matching markdown file
            matching_md = self.find_matching_markdown(html_file.name)
            if matching_md:
                file_info["matching_markdown"] = str(matching_md)
                file_info["metadata"] = self.extract_markdown_metadata(matching_md)
                file_info["status"] = "processed"
                self.audit_results["summary"]["html_processed"] += 1
            else:
                file_info["status"] = "missing"
                self.audit_results["summary"]["html_missing"] += 1
            
            self.audit_results["html_files"][html_file.name] = file_info
    
    def audit_pdf_files(self):
        """Audit all PDF files in root directory."""
        pdf_files = list(self.root_dir.glob("*.pdf"))
        self.audit_results["summary"]["total_pdf_files"] = len(pdf_files)
        
        for pdf_file in pdf_files:
            print(f"Auditing PDF: {pdf_file.name}")
            
            file_info = {
                "original_path": str(pdf_file),
                "file_size": pdf_file.stat().st_size,
                "file_hash": self.get_file_hash(pdf_file),
                "last_modified": datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat(),
                "matching_markdown": None,
                "metadata": {},
                "status": "not_found"
            }
            
            # Find matching markdown file
            matching_md = self.find_matching_markdown(pdf_file.name)
            if matching_md:
                file_info["matching_markdown"] = str(matching_md)
                file_info["metadata"] = self.extract_markdown_metadata(matching_md)
                file_info["status"] = "processed"
                self.audit_results["summary"]["pdf_processed"] += 1
            else:
                file_info["status"] = "missing"
                self.audit_results["summary"]["pdf_missing"] += 1
            
            self.audit_results["pdf_files"][pdf_file.name] = file_info
    
    def generate_removal_plan(self):
        """Generate a plan for which files can be safely removed."""
        removal_plan = {
            "safe_to_remove": [],
            "keep_for_review": [],
            "total_size_to_remove": 0
        }
        
        # Check HTML files
        for filename, info in self.audit_results["html_files"].items():
            if info["status"] == "processed":
                removal_plan["safe_to_remove"].append({
                    "file": filename,
                    "type": "html",
                    "size": info["file_size"],
                    "markdown_file": info["matching_markdown"]
                })
                removal_plan["total_size_to_remove"] += info["file_size"]
            else:
                removal_plan["keep_for_review"].append({
                    "file": filename,
                    "type": "html",
                    "reason": f"Status: {info['status']}"
                })
        
        # Check PDF files
        for filename, info in self.audit_results["pdf_files"].items():
            if info["status"] == "processed":
                removal_plan["safe_to_remove"].append({
                    "file": filename,
                    "type": "pdf",
                    "size": info["file_size"],
                    "markdown_file": info["matching_markdown"]
                })
                removal_plan["total_size_to_remove"] += info["file_size"]
            else:
                removal_plan["keep_for_review"].append({
                    "file": filename,
                    "type": "pdf",
                    "reason": f"Status: {info['status']}"
                })
        
        return removal_plan
    
    def run_audit(self):
        """Run the complete audit."""
        print("Starting file audit...")
        print("=" * 50)
        
        self.audit_html_files()
        self.audit_pdf_files()
        
        # Generate removal plan
        removal_plan = self.generate_removal_plan()
        self.audit_results["removal_plan"] = removal_plan
        
        # Save audit results
        audit_file = "file_audit_results.json"
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 50)
        print("AUDIT SUMMARY")
        print("=" * 50)
        print(f"HTML Files: {self.audit_results['summary']['html_processed']}/{self.audit_results['summary']['total_html_files']} processed")
        print(f"PDF Files: {self.audit_results['summary']['pdf_processed']}/{self.audit_results['summary']['total_pdf_files']} processed")
        print(f"Total files safe to remove: {len(removal_plan['safe_to_remove'])}")
        print(f"Total size to be freed: {removal_plan['total_size_to_remove']:,} bytes")
        print(f"Files needing review: {len(removal_plan['keep_for_review'])}")
        
        if removal_plan['keep_for_review']:
            print("\nFiles needing review:")
            for item in removal_plan['keep_for_review']:
                print(f"  - {item['file']} ({item['type']}): {item['reason']}")
        
        print(f"\nDetailed audit results saved to: {audit_file}")
        return self.audit_results

def main():
    auditor = FileAuditor()
    results = auditor.run_audit()
    
    # Ask for confirmation before removal
    removal_plan = results["removal_plan"]
    if removal_plan["safe_to_remove"]:
        print(f"\nReady to remove {len(removal_plan['safe_to_remove'])} files.")
        print("Run the removal script to proceed with cleanup.")

if __name__ == "__main__":
    main()
