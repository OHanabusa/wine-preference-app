"""
Direct database setup script for Render deployment.
This script explicitly creates tables and sample data.
"""
from app import app, db, Wine, UserPreference
from datetime import datetime

def setup_database():
    """Set up the database from scratch with explicit table creation."""
    with app.app_context():
        print("Dropping all tables to ensure clean setup...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Adding sample wine data...")
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
            Wine(name="ブルゴーニュ ピノ・ノワール 2020", variety="Pinot Noir", vintage=2020, 
                 wine_type="red", price=5000, acidity=4.0, tannin=3.0, body=3.5, sweetness=1.5),
            Wine(name="シャブリ グラン・クリュ 2019", variety="Chardonnay", vintage=2019, 
                 wine_type="white", price=8000, acidity=4.2, tannin=1.0, body=3.0, sweetness=1.0),
            Wine(name="バローロ 2016", variety="Nebbiolo", vintage=2016, 
                 wine_type="red", price=12000, acidity=4.0, tannin=4.5, body=4.5, sweetness=1.0),
            Wine(name="モエ・エ・シャンドン ブリュット", variety="Chardonnay", vintage=2018, 
                 wine_type="sparkling", price=7000, acidity=4.0, tannin=1.0, body=2.5, sweetness=2.0),
            Wine(name="シャトーヌフ・デュ・パプ 2017", variety="Grenache", vintage=2017, 
                 wine_type="red", price=9000, acidity=3.5, tannin=3.8, body=4.5, sweetness=1.8)
        ]
        
        for wine in sample_wines:
            db.session.add(wine)
        
        # Create some sample user preferences
        print("Adding sample user preferences...")
        sample_preferences = [
            UserPreference(wine_id=1, rating=5, rated_at=datetime.now()),
            UserPreference(wine_id=3, rating=4, rated_at=datetime.now()),
            UserPreference(wine_id=5, rating=3, rated_at=datetime.now())
        ]
        
        for pref in sample_preferences:
            db.session.add(pref)
        
        # Commit all changes
        db.session.commit()
        print("Database setup complete with sample data!")

if __name__ == "__main__":
    setup_database()
