#!/usr/bin/env python3
"""
Create agent_tracking.json from CSV data for papers 1-317
"""

import json
import csv
import sys
from datetime import datetime

def create_agent_tracking():
    # Read the CSV file
    papers = []
    
    with open('temp_papers_1_317.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            paper = {
                "paper_id": i,
                "title": row['title'],
                "abstract": row['abstract'],
                "journal": row['journal'],
                "date": row['date'],
                "authors": row['authors'],
                "doi": row['doi'],
                "category": row['category'],
                "search_query": row['search_query'],
                "source": row['source'],
                "status": "pending",
                "scraped_by": None,
                "scraped_at": None,
                "retry_count": 0,
                "error_message": None
            }
            papers.append(paper)
    
    # Create the agent tracking structure
    agent_tracking = {
        "project_info": {
            "name": "ASD Research Papers Webscraping",
            "version": "1.0.0",
            "description": "Multi-agent webscraping system for research papers",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "agents": {
            "active_agents": ["agent_a"],
            "agent_registry": {
                "agent_a": {
                    "assigned_papers": list(range(1, 318)),  # papers 1-317
                    "status": "active",
                    "started_at": datetime.now().isoformat()
                }
            },
            "max_concurrent_agents": 5
        },
        "papers": {
            "total_papers": len(papers),
            "papers_to_scrape": papers,
            "scraped_papers": [],
            "failed_papers": [],
            "in_progress": []
        },
        "batches": {
            "current_batch": 1,
            "batch_size": 20,
            "batches_completed": 0,
            "total_batches": 16  # 317 papers / 20 per batch
        },
        "statistics": {
            "total_attempts": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "success_rate": 0.0,
            "last_successful_scrape": None,
            "average_content_length": 0
        },
        "locks": {
            "global_lock": False,
            "file_locks": {},
            "agent_locks": {}
        },
        "settings": {
            "retry_attempts": 3,
            "delay_between_requests": 2,
            "timeout_seconds": 15,
            "min_content_length": 500,
            "max_concurrent_requests": 3
        },
        "logs": {
            "last_activity": None,
            "error_count": 0,
            "warning_count": 0
        }
    }
    
    # Write to agent_tracking.json
    with open('agent_tracking.json', 'w', encoding='utf-8') as f:
        json.dump(agent_tracking, f, indent=2, ensure_ascii=False)
    
    print(f"Created agent_tracking.json with {len(papers)} papers (1-317)")
    print(f"Papers with DOI: {sum(1 for p in papers if p['doi'])}")
    print(f"Papers without DOI: {sum(1 for p in papers if not p['doi'])}")

if __name__ == "__main__":
    create_agent_tracking()