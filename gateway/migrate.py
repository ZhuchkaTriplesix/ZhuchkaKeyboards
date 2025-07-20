#!/usr/bin/env python3
"""
Simple migration script for Alembic
"""
import os
import sys
import subprocess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_migrations():
    """Run Alembic migrations"""
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Running migrations from: {current_dir}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Alembic.ini exists: {os.path.exists(os.path.join(current_dir, 'alembic.ini'))}")
    
    try:
        # Change to app directory and run alembic
        result = subprocess.run(
            ["alembic", "-c", os.path.join(current_dir, "alembic.ini"), "upgrade", "head"],
            cwd=current_dir,
            capture_output=True,
            text=True,
            env=dict(os.environ, PYTHONPATH=os.path.join(current_dir, 'src'))
        )
        
        if result.returncode == 0:
            print("Migrations completed successfully!")
            print(result.stdout)
        else:
            print(f"Error running migrations: {result.stderr}")
            print(f"Return code: {result.returncode}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 