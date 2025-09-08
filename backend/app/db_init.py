"""
Database initialization utilities for startup configuration
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import SessionLocal, engine
from . import models


def clear_all_events():
    """Clear all events from the database"""
    with SessionLocal() as db:
        try:
            deleted_count = db.query(models.Event).count()
            db.query(models.Event).delete()
            db.commit()
            print(f"Database initialization: Cleared {deleted_count} events from database")
        except Exception as e:
            db.rollback()
            print(f"Failed to clear events: {e}")
            raise


def reset_database():
    """Drop and recreate all tables"""
    try:
        print("Database initialization: Dropping and recreating all tables...")
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        print("Database initialization: Tables reset successfully")
    except Exception as e:
        print(f"Failed to reset database: {e}")
        raise


def run_database_initialization(init_mode: str | None):
    """
    Run database initialization based on the specified mode
    
    Available modes:
    - "clear_events": Clear all events from the database
    - "reset": Drop and recreate all tables (destructive)
    - None or empty: No initialization
    """
    if not init_mode:
        return
    
    init_mode = init_mode.lower().strip()
    
    if init_mode == "clear_events":
        clear_all_events()
    elif init_mode == "reset":
        reset_database()
    else:
        print(f"Warning: Unknown database initialization mode '{init_mode}'. Skipping initialization.")
        print("Available modes: clear_events, reset")