#!/usr/bin/env python3
"""
Set up repository for GitHub hosting with public access.
"""

import os
import json
import subprocess
import sys

def check_git_status():
    """Check if this is a git repository and its status."""
    print("=== CHECKING GIT STATUS ===")
    
    try:
        # Check if git is available
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        print("Git is available")
        
        # Check if this is a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("This is a git repository")
            return True
        else:
            print("This is not a git repository")
            return False
            
    except subprocess.CalledProcessError:
        print("Git is not available")
        return False
    except FileNotFoundError:
        print("Git is not installed")
        return False

def initialize_git_repo():
    """Initialize git repository if not already initialized."""
    print("\n=== INITIALIZING GIT REPOSITORY ===")
    
    try:
        subprocess.run(['git', 'init'], check=True)
        print("Git repository initialized")
        
        # Set default branch to main
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        print("Default branch set to 'main'")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error initializing git repository: {e}")
        return False

def create_gitignore():
    """Create .gitignore file if it doesn't exist."""
    print("\n=== CREATING .GITIGNORE ===")
    
    if os.path.exists('.gitignore'):
        print(".gitignore already exists")
        return True
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
*.tmp
*.temp

# Backup files
*.bak
*.backup
*~

# Temporary files
*.tmp
*.temp
*.swp
*.swo

# Analysis files (keep for reference but don't commit)
duplicate_analysis.json
cleanup_log.json
patient_docs_audit_report.json
cleanup_report.json

# Scripts output
*.csv
*.yaml
*.json
!docs/meta/master_index.yaml
!docs/meta/knowledge_index.yaml
!config/openwebui_config.yaml

# Large files
*.pdf
*.zip
*.tar.gz
*.rar

# Sensitive data
.env
.env.local
.env.production
.env.staging
secrets/
credentials/

# Node modules (if any)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/
"""
    
    try:
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print(".gitignore created successfully")
        return True
    except Exception as e:
        print(f"Error creating .gitignore: {e}")
        return False

def create_github_workflow():
    """Create GitHub workflow for automated checks."""
    print("\n=== CREATING GITHUB WORKFLOW ===")
    
    workflow_dir = '.github/workflows'
    os.makedirs(workflow_dir, exist_ok=True)
    
    workflow_content = """name: Quality Check

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run quality checks
      run: |
        python scripts/simple_cleanup.py
        python scripts/audit_patient_docs.py
    
    - name: Check for broken links
      run: |
        python scripts/check_links.py
    
    - name: Validate markdown
      run: |
        python scripts/validate_markdown.py
"""
    
    workflow_file = os.path.join(workflow_dir, 'quality-check.yml')
    
    try:
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(workflow_content)
        print("GitHub workflow created successfully")
        return True
    except Exception as e:
        print(f"Error creating GitHub workflow: {e}")
        return False

def create_requirements_txt():
    """Create requirements.txt for Python dependencies."""
    print("\n=== CREATING REQUIREMENTS.TXT ===")
    
    requirements_content = """# Core dependencies
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
PyYAML>=6.0
markdown>=3.4.0

# Development dependencies
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991

# Documentation
mkdocs>=1.4.0
mkdocs-material>=8.5.0
"""
    
    try:
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        print("requirements.txt created successfully")
        return True
    except Exception as e:
        print(f"Error creating requirements.txt: {e}")
        return False

def create_github_issue_templates():
    """Create GitHub issue templates."""
    print("\n=== CREATING GITHUB ISSUE TEMPLATES ===")
    
    templates_dir = '.github/ISSUE_TEMPLATE'
    os.makedirs(templates_dir, exist_ok=True)
    
    # Bug report template
    bug_template = """---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the Bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
- OS: [e.g. Windows, macOS, Linux]
- Browser: [e.g. Chrome, Firefox, Safari]
- Version: [e.g. 22]

**Additional Context**
Add any other context about the problem here.
"""
    
    # Feature request template
    feature_template = """---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
"""
    
    # Documentation template
    docs_template = """---
name: Documentation
about: Help improve documentation
title: '[DOCS] '
labels: documentation
assignees: ''
---

**What needs documentation?**
A clear and concise description of what needs documentation.

**Where should it be documented?**
- [ ] README.md
- [ ] Patient guides
- [ ] Support resources
- [ ] Other: 

**Additional context**
Add any other context about the documentation request here.
"""
    
    templates = [
        ('bug_report.md', bug_template),
        ('feature_request.md', feature_template),
        ('documentation.md', docs_template)
    ]
    
    success = True
    for filename, content in templates:
        filepath = os.path.join(templates_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created {filename}")
        except Exception as e:
            print(f"Error creating {filename}: {e}")
            success = False
    
    return success

def create_pull_request_template():
    """Create pull request template."""
    print("\n=== CREATING PULL REQUEST TEMPLATE ===")
    
    pr_template = """## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Content improvement
- [ ] Organization improvement

## Files Changed
- List of files modified/added

## Testing
- [ ] Links tested
- [ ] Content reviewed
- [ ] Accessibility checked
- [ ] Quality checks passed

## Additional Notes
Any additional information about the changes

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
"""
    
    try:
        with open('.github/pull_request_template.md', 'w', encoding='utf-8') as f:
            f.write(pr_template)
        print("Pull request template created successfully")
        return True
    except Exception as e:
        print(f"Error creating pull request template: {e}")
        return False

def create_github_pages_config():
    """Create GitHub Pages configuration."""
    print("\n=== CREATING GITHUB PAGES CONFIG ===")
    
    # Create _config.yml for Jekyll
    config_content = """# GitHub Pages configuration
title: ASD Research Papers Collection
description: A comprehensive collection of research papers on Autism Spectrum Disorder, Tourette Syndrome, ADHD, and related neurodevelopmental conditions
baseurl: ""
url: ""

# Navigation
navigation:
  - title: Home
    url: /
  - title: Research Papers
    url: /docs/research/
  - title: Patient Guides
    url: /docs/patient-guides/
  - title: Support Resources
    url: /docs/support/
  - title: Search Guide
    url: /docs/SEARCH_GUIDE.html

# Collections
collections:
  research:
    output: true
    permalink: /:collection/:name/
  patient-guides:
    output: true
    permalink: /:collection/:name/
  support:
    output: true
    permalink: /:collection/:name/

# Plugins
plugins:
  - jekyll-sitemap
  - jekyll-feed
  - jekyll-seo-tag

# SEO
seo:
  type: "WebSite"
  name: "ASD Research Papers Collection"
  description: "Comprehensive research collection for neurodevelopmental disorders"
  url: "https://your-username.github.io/asd-research-papers"
  image: "/assets/logo.png"

# Exclude files
exclude:
  - README.md
  - LICENSE
  - CONTRIBUTING.md
  - CONTRIBUTORS.md
  - scripts/
  - tests/
  - .gitignore
  - requirements.txt
  - .github/
"""
    
    try:
        with open('_config.yml', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("GitHub Pages configuration created successfully")
        return True
    except Exception as e:
        print(f"Error creating GitHub Pages configuration: {e}")
        return False

def main():
    print("=== SETTING UP GITHUB REPOSITORY ===\n")
    
    # Check git status
    is_git_repo = check_git_status()
    
    if not is_git_repo:
        print("\nInitializing git repository...")
        if not initialize_git_repo():
            print("Failed to initialize git repository")
            return False
    
    # Create necessary files
    success = True
    
    success &= create_gitignore()
    success &= create_github_workflow()
    success &= create_requirements_txt()
    success &= create_github_issue_templates()
    success &= create_pull_request_template()
    success &= create_github_pages_config()
    
    if success:
        print("\n=== GITHUB SETUP COMPLETE ===")
        print("Repository is ready for GitHub hosting!")
        print("\nNext steps:")
        print("1. Add remote repository: git remote add origin https://github.com/your-username/asd-research-papers.git")
        print("2. Add files: git add .")
        print("3. Commit: git commit -m 'Initial commit: ASD Research Papers Collection'")
        print("4. Push: git push -u origin main")
        print("5. Enable GitHub Pages in repository settings")
        print("6. Set repository to public for public access")
    else:
        print("\n=== GITHUB SETUP INCOMPLETE ===")
        print("Some files could not be created. Please check the errors above.")
    
    return success

if __name__ == '__main__':
    main()
