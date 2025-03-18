"""
Reset the database for the DockerForge Web UI.

This script drops all tables and recreates them with the correct schema.
"""
from database import drop_db, init_db, create_initial_data

def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    """
    print("Dropping all tables...")
    drop_db()
    
    print("Creating tables...")
    init_db()
    
    print("Creating initial data...")
    create_initial_data()
    
    print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
