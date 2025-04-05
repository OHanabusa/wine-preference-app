"""
Database initialization script for Render deployment.
This script will initialize the database with the required tables and import data.
"""
from app import app, db, Wine, UserPreference
import pandas as pd
import os
import csv
from datetime import datetime

def init_db():
    """Initialize the database with tables and import data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we have data to import
        if Wine.query.first() is None:
            print("No wine data found. Importing data...")
            
            try:
                # Try to import from backup.sql or wine_database.db if available
                if os.path.exists('wine_database.db'):
                    try:
                        import sqlite3
                        conn = sqlite3.connect('wine_database.db')
                        
                        # Import wines
                        wines_df = pd.read_sql('SELECT * FROM wine', conn)
                        print(f"Found {len(wines_df)} wines to import from SQLite")
                        
                        for _, row in wines_df.iterrows():
                            wine = Wine(
                                id=row['id'],
                                name=row['name'],
                                variety=row['variety'],
                                variety_sub1=row['variety_sub1'] if 'variety_sub1' in row else None,
                                variety_sub2=row['variety_sub2'] if 'variety_sub2' in row else None,
                                vintage=row['vintage'],
                                wine_type=row['wine_type'],
                                price=row['price'],
                                acidity=row['acidity'],
                                tannin=row['tannin'],
                                body=row['body'],
                                sweetness=row['sweetness']
                            )
                            db.session.add(wine)
                        
                        # Try to import user preferences if available
                        try:
                            prefs_df = pd.read_sql('SELECT * FROM user_preferences', conn)
                            print(f"Found {len(prefs_df)} user preferences to import")
                            
                            for _, row in prefs_df.iterrows():
                                pref = UserPreference(
                                    id=row['id'],
                                    wine_id=row['wine_id'],
                                    rating=row['rating'],
                                    rated_at=row['rated_at'] if isinstance(row['rated_at'], datetime) else datetime.now()
                                )
                                db.session.add(pref)
                        except Exception as e:
                            print(f"No user preferences found or error importing them: {str(e)}")
                        
                        db.session.commit()
                        print("Data import from SQLite completed!")
                        conn.close()
                    except Exception as e:
                        print(f"Error importing from SQLite: {str(e)}")
                        db.session.rollback()
                        
                # If no data was imported, create some sample data
                if Wine.query.first() is None:
                    print("Creating sample wine data...")
                    # Create sample wine data
                    sample_wines = [
                        Wine(name="Château Margaux 2015", variety="Cabernet Sauvignon", vintage=2015, 
                             wine_type="red", price=120000, acidity=3.5, tannin=4.0, body=5.0, sweetness=2.0),
                        Wine(name="Dom Pérignon 2010", variety="Chardonnay", vintage=2010, 
                             wine_type="sparkling", price=25000, acidity=4.0, tannin=1.0, body=3.0, sweetness=2.5),
                        Wine(name="Cloudy Bay Sauvignon Blanc 2022", variety="Sauvignon Blanc", vintage=2022, 
                             wine_type="white", price=4000, acidity=4.5, tannin=1.0, body=2.0, sweetness=1.5),
                        Wine(name="シャトー・メルシャン 甲州きいろ香 2022", variety="甲州", vintage=2022, 
                             wine_type="white", price=2500, acidity=3.8, tannin=1.0, body=2.0, sweetness=2.0),
                        Wine(name="Opus One 2018", variety="Cabernet Sauvignon", vintage=2018, 
                             wine_type="red", price=45000, acidity=3.8, tannin=4.5, body=5.0, sweetness=1.5),
                    ]
                    
                    for wine in sample_wines:
                        db.session.add(wine)
                    
                    db.session.commit()
                    print("Sample wine data created successfully!")
            except Exception as e:
                print(f"Error during data initialization: {str(e)}")
                db.session.rollback()
        else:
            print("Database already contains wine data.")

if __name__ == "__main__":
    init_db()
