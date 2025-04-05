"""
Database initialization script for Render deployment.
This script will initialize the database with the required tables and import data.
"""
from app import app, db, Wine, UserPreference
import pandas as pd
import os

def init_db():
    """Initialize the database with tables and import data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we have data to import
        if Wine.query.first() is None:
            print("No wine data found. Importing from SQL dump...")
            
            # If a SQL dump file exists, you can restore it
            # For Render with PostgreSQL, we'll need to adapt this
            # to import from the existing SQLite database
            
            try:
                # Using pandas to read from SQLite and write to PostgreSQL
                if os.path.exists('wine_database.db'):
                    import sqlite3
                    conn = sqlite3.connect('wine_database.db')
                    
                    # Import wines
                    wines_df = pd.read_sql('SELECT * FROM wine', conn)
                    print(f"Found {len(wines_df)} wines to import")
                    
                    for _, row in wines_df.iterrows():
                        wine = Wine(
                            id=row['id'],
                            name=row['name'],
                            variety=row['variety'],
                            variety_sub1=row['variety_sub1'],
                            variety_sub2=row['variety_sub2'],
                            vintage=row['vintage'],
                            wine_type=row['wine_type'],
                            price=row['price'],
                            acidity=row['acidity'],
                            tannin=row['tannin'],
                            body=row['body'],
                            sweetness=row['sweetness']
                        )
                        db.session.add(wine)
                    
                    # Import user preferences
                    prefs_df = pd.read_sql('SELECT * FROM user_preferences', conn)
                    print(f"Found {len(prefs_df)} user preferences to import")
                    
                    for _, row in prefs_df.iterrows():
                        pref = UserPreference(
                            id=row['id'],
                            wine_id=row['wine_id'],
                            rating=row['rating'],
                            rated_at=row['rated_at']
                        )
                        db.session.add(pref)
                    
                    db.session.commit()
                    print("Data import completed successfully!")
                    conn.close()
                else:
                    print("No SQLite database found for import.")
            except Exception as e:
                print(f"Error importing data: {str(e)}")
                db.session.rollback()
        else:
            print("Database already contains data.")

if __name__ == "__main__":
    init_db()
