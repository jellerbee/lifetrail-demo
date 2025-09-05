"""
Database migration script to add new columns to existing events table
"""
from sqlalchemy import text
from .db import engine

def migrate_database():
    """Add new columns to events table if they don't exist"""
    with engine.connect() as conn:
        # Check if processing_status column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'processing_status'
        """))
        
        if not result.fetchone():
            print("Adding processing_status column...")
            conn.execute(text("""
                ALTER TABLE events 
                ADD COLUMN processing_status VARCHAR(32) DEFAULT 'completed'
            """))
            conn.commit()
        
        # Check if ai_results column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'ai_results'
        """))
        
        if not result.fetchone():
            print("Adding ai_results column...")
            conn.execute(text("""
                ALTER TABLE events 
                ADD COLUMN ai_results JSON
            """))
            conn.commit()
        
        # Check if heic_metadata column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'heic_metadata'
        """))
        
        if not result.fetchone():
            print("Adding heic_metadata column...")
            conn.execute(text("""
                ALTER TABLE events 
                ADD COLUMN heic_metadata JSON
            """))
            conn.commit()
        
        # Check if original_filename column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'original_filename'
        """))
        
        if not result.fetchone():
            print("Adding original_filename column...")
            conn.execute(text("""
                ALTER TABLE events 
                ADD COLUMN original_filename VARCHAR(255)
            """))
            conn.commit()
        
        # Check if photo_taken_at column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'photo_taken_at'
        """))
        
        if not result.fetchone():
            print("Adding photo_taken_at column...")
            conn.execute(text("""
                ALTER TABLE events 
                ADD COLUMN photo_taken_at TIMESTAMPTZ
            """))
            conn.commit()
        
        print("Database migration completed!")

if __name__ == "__main__":
    migrate_database()