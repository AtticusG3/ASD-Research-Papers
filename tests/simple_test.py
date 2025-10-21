#!/usr/bin/env python3
"""
Simple test to check if AgentManager works
"""

import sys
import os

print("Starting simple test...")
print(f"Current working directory: {os.getcwd()}")

try:
    print("Adding current directory to Python path...")
    sys.path.append('.')
    
    print("Importing AgentManager...")
    from scripts.agent_manager import AgentManager
    print("AgentManager imported successfully")
    
    print("Creating AgentManager instance...")
    manager = AgentManager()
    print("AgentManager instance created successfully")
    
    print("Checking if CSV exists...")
    csv_path = "acquired_papers/acquired_papers_20251021_161222.csv"
    if os.path.exists(csv_path):
        print(f"CSV file exists at: {csv_path}")
        
        print("Testing CSV read...")
        import pandas as pd
        df = pd.read_csv(csv_path)
        print(f"CSV loaded with {len(df)} rows")
        
        print("Testing load_papers_from_csv with first 10 papers only...")
        # Let's test with just a small sample first
        df_sample = df.head(10)
        df_sample.to_csv("test_sample.csv", index=False)
        
        # Create a new manager for testing
        test_manager = AgentManager("test_agent_tracking.json")
        papers_loaded = test_manager.load_papers_from_csv("test_sample.csv")
        print(f"Successfully loaded {papers_loaded} papers into tracking system")
        
        # Clean up test files
        os.remove("test_sample.csv")
        os.remove("test_agent_tracking.json")
        
    else:
        print(f"CSV file not found at: {csv_path}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("Simple test completed")
