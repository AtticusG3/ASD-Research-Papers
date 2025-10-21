# ASD Research Papers - Multi-Agent Webscraping System

A comprehensive research paper collection and webscraping system for Autism Spectrum Disorder (ASD), Tourette Syndrome, and related neurodevelopmental conditions.

## Project Overview

This project contains a curated collection of research papers with automated webscraping capabilities for extracting full-text content from online sources. The system supports multi-agent processing for efficient parallel webscraping operations.

## Project Structure

```
ASD Research Papers/
├── docs/                          # Processed research papers (markdown format)
│   ├── research/
│   │   ├── tourette/             # Tourette Syndrome papers
│   │   ├── adhd/                 # ADHD papers
│   │   ├── asd/                  # Autism Spectrum Disorder papers
│   │   └── related-disorders/    # Other related conditions
├── acquired_papers/              # Source data and logs
│   ├── acquired_papers_*.csv     # Paper metadata from PubMed
│   └── *.yaml                    # Processing logs
├── scripts/                      # Automation scripts
│   ├── agent_manager.py          # Multi-agent coordination
│   ├── audit_original_files.py   # File audit and verification
│   ├── webscrape_*.py           # Webscraping utilities
│   └── *.py                     # Other processing scripts
├── backup_originals/             # Backup of original HTML/PDF files
├── agent_tracking.json          # Multi-agent coordination data
├── file_audit_results.json      # File processing audit results
└── *.md                         # Project documentation
```

## Key Features

### 📚 Research Paper Collection
- **959 papers** with abstracts from PubMed
- **147 papers** in Tourette Syndrome category
- **34 papers** with full-text content scraped
- Comprehensive metadata including DOIs, authors, journals, dates

### 🤖 Multi-Agent Webscraping
- Concurrent processing by multiple agents
- Automatic source discovery and content extraction
- Locking mechanisms to prevent conflicts
- Progress tracking and error handling

### 🔍 Content Processing
- HTML to Markdown conversion
- Metadata extraction and preservation
- Source tracking and audit trails
- Quality validation and content verification

### 📊 Tracking and Monitoring
- JSON-based progress tracking
- Comprehensive audit logs
- File integrity verification
- Backup and recovery systems

## Quick Start

### 1. Initialize the System
```bash
# Load papers from CSV into tracking system
python scripts/agent_manager.py

# Run audit to verify file integrity
python scripts/audit_original_files.py
```

### 2. Start Webscraping
```bash
# Register an agent and start scraping
python scripts/webscrape_next_20_papers.py

# Or use the improved scraper for retry attempts
python scripts/improved_webscraper.py
```

### 3. Monitor Progress
```bash
# Check agent status and progress
python -c "
from scripts.agent_manager import AgentManager
manager = AgentManager()
status = manager.get_status_report()
print(json.dumps(status, indent=2))
"
```

## Multi-Agent System

The system supports multiple agents working simultaneously:

### Agent Registration
```python
from scripts.agent_manager import AgentManager

manager = AgentManager()
agent_id = manager.register_agent("agent_name", "webscraper")
```

### Getting Work
```python
# Get next batch of papers to process
batch = manager.get_next_paper_batch(agent_id, batch_size=20)
```

### Reporting Results
```python
# Mark paper as completed
manager.mark_paper_completed(
    agent_id=agent_id,
    paper_doi="10.1234/example",
    success=True,
    content_length=50000,
    filepath="docs/research/tourette/paper.md"
)
```

## Data Sources

### Primary Sources
- **PubMed Central (PMC)** - Open access papers
- **Frontiers Journals** - Open access research
- **Springer Link** - Academic publications
- **Publisher Direct** - Journal websites

### Content Types
- Research articles and reviews
- Case studies and clinical reports
- Meta-analyses and systematic reviews
- Conference proceedings and abstracts

## File Management

### Original Files
- Original HTML and PDF files are backed up in `backup_originals/`
- All content is preserved in markdown format in `docs/`
- Complete audit trail maintained in JSON logs

### Content Verification
- MD5 hash verification for file integrity
- Metadata extraction and validation
- Source URL tracking and preservation
- Content length and quality checks

## Statistics

### Current Status
- **Total Papers**: 959
- **Papers with DOIs**: 950
- **Successfully Scraped**: 34
- **Success Rate**: ~45% (limited by paywall restrictions)
- **Total Content**: ~1.2M characters of research text

### Categories
- **Tourette Syndrome**: 147 papers
- **ADHD**: Papers in development
- **ASD**: Papers in development
- **Related Disorders**: Various conditions

## Technical Details

### Requirements
- Python 3.7+
- Required packages: pandas, requests, beautifulsoup4, pyyaml
- Internet connection for webscraping

### Configuration
- Agent settings in `agent_tracking.json`
- Scraping parameters configurable per agent
- Retry logic and timeout settings
- Rate limiting and respectful scraping

### Error Handling
- Comprehensive error logging
- Automatic retry mechanisms
- Graceful failure handling
- Recovery and continuation support

## Contributing

### Adding New Papers
1. Add paper metadata to CSV file
2. Run audit to verify processing
3. Use webscraping scripts to extract content
4. Verify results and update tracking

### Multi-Agent Development
1. Register new agent with unique name
2. Implement agent-specific processing logic
3. Use locking mechanisms for shared resources
4. Report progress through tracking system

## License

This project is for research and educational purposes. Please respect copyright and terms of service of source websites.

## Contact

For questions about the research collection or technical implementation, please refer to the project documentation and logs.

---

**Last Updated**: October 21, 2025  
**Version**: 1.0.0  
**Status**: Active Development
