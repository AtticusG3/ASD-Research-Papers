#!/usr/bin/env python3
"""
Create agent tracking file for papers 318-634 from the CSV data
"""

import csv
import json
import sys
from datetime import datetime

def create_agent_tracking():
    # Read the CSV file
    papers = []
    with open('acquired_papers/acquired_papers_20251021_161222.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if 318 <= i <= 634:  # Papers 318-634
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
                    "content": None,
                    "error": None,
                    "retry_count": 0
                }
                papers.append(paper)
    
    # Create the tracking structure
    tracking = {
        "project_info": {
            "name": "ASD Research Papers Webscraping",
            "version": "1.0.0",
            "description": "Multi-agent webscraping system for research papers",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "agents": {
            "active_agents": ["agent_b"],
            "agent_registry": {
                "agent_b": {
                    "status": "active",
                    "assigned_papers": list(range(318, 635)),
                    "last_activity": datetime.now().isoformat()
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
            "total_batches": (len(papers) + 19) // 20  # Round up
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
            "last_activity": datetime.now().isoformat(),
            "error_count": 0,
            "warning_count": 0
        }
    }
    
    # Write the tracking file
    with open('agent_tracking.json', 'w', encoding='utf-8') as f:
        json.dump(tracking, f, indent=2, ensure_ascii=False)
    
    print(f"Created agent_tracking.json with {len(papers)} papers (318-634)")
    print(f"Papers with DOI: {sum(1 for p in papers if p['doi'])}")
    print(f"Papers without DOI: {sum(1 for p in papers if not p['doi'])}")

if __name__ == "__main__":
    create_agent_tracking()