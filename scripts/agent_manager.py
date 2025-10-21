#!/usr/bin/env python3
"""
Multi-Agent Webscraping Manager

This script manages multiple agents working simultaneously on webscraping tasks.
It provides coordination, locking mechanisms, and progress tracking.
"""

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
import threading
import pandas as pd

class AgentManager:
    def __init__(self, tracking_file="agent_tracking.json"):
        self.tracking_file = Path(tracking_file)
        self.lock = threading.Lock()
        self.load_tracking_data()
    
    def load_tracking_data(self):
        """Load tracking data from JSON file."""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            # Initialize with default structure
            self.data = {
                "project_info": {
                    "name": "ASD Research Papers Webscraping",
                    "version": "1.0.0",
                    "description": "Multi-agent webscraping system for research papers",
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                },
                "agents": {
                    "active_agents": [],
                    "agent_registry": {},
                    "max_concurrent_agents": 5
                },
                "papers": {
                    "total_papers": 0,
                    "papers_to_scrape": [],
                    "scraped_papers": [],
                    "failed_papers": [],
                    "in_progress": []
                },
                "batches": {
                    "current_batch": 1,
                    "batch_size": 20,
                    "batches_completed": 0,
                    "total_batches": 0
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
            self.save_tracking_data()
    
    def save_tracking_data(self):
        """Save tracking data to JSON file."""
        with self.lock:
            self.data["project_info"]["last_updated"] = datetime.now().isoformat()
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def register_agent(self, agent_name, agent_type="webscraper"):
        """Register a new agent."""
        agent_id = str(uuid.uuid4())
        agent_info = {
            "id": agent_id,
            "name": agent_name,
            "type": agent_type,
            "status": "active",
            "registered_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "papers_processed": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0
        }
        
        with self.lock:
            self.data["agents"]["agent_registry"][agent_id] = agent_info
            if len(self.data["agents"]["active_agents"]) < self.data["agents"]["max_concurrent_agents"]:
                self.data["agents"]["active_agents"].append(agent_id)
            self.save_tracking_data()
        
        return agent_id
    
    def unregister_agent(self, agent_id):
        """Unregister an agent."""
        with self.lock:
            if agent_id in self.data["agents"]["active_agents"]:
                self.data["agents"]["active_agents"].remove(agent_id)
            if agent_id in self.data["agents"]["agent_registry"]:
                del self.data["agents"]["agent_registry"][agent_id]
            self.save_tracking_data()
    
    def get_next_paper_batch(self, agent_id, batch_size=None):
        """Get the next batch of papers for an agent to process."""
        if batch_size is None:
            batch_size = self.data["batches"]["batch_size"]
        
        with self.lock:
            # Check if agent is registered and active
            if agent_id not in self.data["agents"]["active_agents"]:
                return []
            
            # Get papers that are not in progress or already processed
            available_papers = [
                paper for paper in self.data["papers"]["papers_to_scrape"]
                if paper["doi"] not in [p["doi"] for p in self.data["papers"]["in_progress"]]
                and paper["doi"] not in [p["doi"] for p in self.data["papers"]["scraped_papers"]]
                and paper["doi"] not in [p["doi"] for p in self.data["papers"]["failed_papers"]]
            ]
            
            # Get next batch
            batch = available_papers[:batch_size]
            
            # Mark papers as in progress
            for paper in batch:
                paper["assigned_agent"] = agent_id
                paper["assigned_at"] = datetime.now().isoformat()
                self.data["papers"]["in_progress"].append(paper)
            
            self.save_tracking_data()
            return batch
    
    def mark_paper_completed(self, agent_id, paper_doi, success=True, content_length=0, filepath=None, error_message=None):
        """Mark a paper as completed (successful or failed)."""
        with self.lock:
            # Find and remove from in_progress
            in_progress_papers = self.data["papers"]["in_progress"]
            paper = None
            for i, p in enumerate(in_progress_papers):
                if p["doi"] == paper_doi and p.get("assigned_agent") == agent_id:
                    paper = in_progress_papers.pop(i)
                    break
            
            if not paper:
                return False
            
            # Add to appropriate list
            if success:
                paper["scraped_at"] = datetime.now().isoformat()
                paper["content_length"] = content_length
                paper["filepath"] = filepath
                self.data["papers"]["scraped_papers"].append(paper)
                self.data["statistics"]["successful_scrapes"] += 1
                self.data["statistics"]["last_successful_scrape"] = datetime.now().isoformat()
            else:
                paper["failed_at"] = datetime.now().isoformat()
                paper["error_message"] = error_message
                self.data["papers"]["failed_papers"].append(paper)
                self.data["statistics"]["failed_scrapes"] += 1
            
            # Update agent stats
            if agent_id in self.data["agents"]["agent_registry"]:
                agent = self.data["agents"]["agent_registry"][agent_id]
                agent["papers_processed"] += 1
                agent["last_activity"] = datetime.now().isoformat()
                if success:
                    agent["successful_scrapes"] += 1
                else:
                    agent["failed_scrapes"] += 1
            
            # Update overall statistics
            self.data["statistics"]["total_attempts"] += 1
            total_attempts = self.data["statistics"]["total_attempts"]
            successful = self.data["statistics"]["successful_scrapes"]
            self.data["statistics"]["success_rate"] = successful / total_attempts if total_attempts > 0 else 0
            
            # Update average content length
            scraped_papers = self.data["papers"]["scraped_papers"]
            if scraped_papers:
                total_length = sum(p.get("content_length", 0) for p in scraped_papers)
                self.data["statistics"]["average_content_length"] = total_length / len(scraped_papers)
            
            self.data["logs"]["last_activity"] = datetime.now().isoformat()
            self.save_tracking_data()
            return True
    
    def load_papers_from_csv(self, csv_path="acquired_papers/acquired_papers_20251021_161222.csv"):
        """Load papers from CSV file into the tracking system."""
        if not os.path.exists(csv_path):
            return False
        
        print(f"Loading CSV from: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"CSV loaded with {len(df)} rows")
        
        papers = []
        current_time = datetime.now().isoformat()  # Get timestamp once instead of for each paper
        
        print("Processing papers...")
        for i, (_, row) in enumerate(df.iterrows()):
            if i % 100 == 0:  # Progress indicator every 100 papers
                print(f"Processed {i} papers...")
                
            if pd.notna(row['doi']):  # Only include papers with DOIs
                paper = {
                    "title": row['title'],
                    "doi": row['doi'],
                    "journal": row['journal'],
                    "date": row['date'],
                    "authors": row['authors'],
                    "abstract": row['abstract'],
                    "category": row['category'],
                    "source": row.get('source', 'pubmed'),
                    "added_to_tracking": current_time
                }
                papers.append(paper)
        
        print(f"Processed {len(papers)} papers with DOIs")
        
        with self.lock:
            print("Saving papers to tracking system...")
            self.data["papers"]["papers_to_scrape"] = papers
            self.data["papers"]["total_papers"] = len(papers)
            self.data["batches"]["total_batches"] = (len(papers) + self.data["batches"]["batch_size"] - 1) // self.data["batches"]["batch_size"]
            self.save_tracking_data()
            print("Papers saved successfully")
        
        return len(papers)
    
    def get_status_report(self):
        """Get a comprehensive status report."""
        with self.lock:
            return {
                "project_info": self.data["project_info"],
                "agents": {
                    "active_count": len(self.data["agents"]["active_agents"]),
                    "total_registered": len(self.data["agents"]["agent_registry"]),
                    "max_concurrent": self.data["agents"]["max_concurrent_agents"]
                },
                "papers": {
                    "total": self.data["papers"]["total_papers"],
                    "to_scrape": len(self.data["papers"]["papers_to_scrape"]),
                    "in_progress": len(self.data["papers"]["in_progress"]),
                    "scraped": len(self.data["papers"]["scraped_papers"]),
                    "failed": len(self.data["papers"]["failed_papers"])
                },
                "statistics": self.data["statistics"],
                "batches": self.data["batches"]
            }
    
    def acquire_lock(self, resource_name, agent_id, timeout=30):
        """Acquire a lock for a specific resource."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.lock:
                if resource_name not in self.data["locks"]["file_locks"]:
                    self.data["locks"]["file_locks"][resource_name] = {
                        "agent_id": agent_id,
                        "acquired_at": datetime.now().isoformat()
                    }
                    self.save_tracking_data()
                    return True
                elif self.data["locks"]["file_locks"][resource_name]["agent_id"] == agent_id:
                    return True  # Already owned by this agent
            
            time.sleep(0.1)  # Wait 100ms before retrying
        
        return False  # Timeout
    
    def release_lock(self, resource_name, agent_id):
        """Release a lock for a specific resource."""
        with self.lock:
            if (resource_name in self.data["locks"]["file_locks"] and 
                self.data["locks"]["file_locks"][resource_name]["agent_id"] == agent_id):
                del self.data["locks"]["file_locks"][resource_name]
                self.save_tracking_data()
                return True
        return False

def main():
    """Example usage of the AgentManager."""
    manager = AgentManager()
    
    # Load papers from CSV
    papers_loaded = manager.load_papers_from_csv()
    print(f"Loaded {papers_loaded} papers from CSV")
    
    # Register an agent
    agent_id = manager.register_agent("test_agent", "webscraper")
    print(f"Registered agent: {agent_id}")
    
    # Get status report
    status = manager.get_status_report()
    print(f"Status: {json.dumps(status, indent=2)}")
    
    # Unregister agent
    manager.unregister_agent(agent_id)
    print("Agent unregistered")

if __name__ == "__main__":
    main()
