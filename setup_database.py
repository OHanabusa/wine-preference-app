"""
Direct database setup script for Render deployment.
This script explicitly creates tables and sample data.
"""
from app import app, db, Wine, UserPreference
from datetime import datetime
import pandas as pd
import os

def load_from_csv():
    """Load wine data from the wine_info.csv file"""
    # プロジェクトディレクトリ内のCSVファイルを使用
    csv_path = os.path.join(os.path.dirname(__file__), 'wine_info.csv')
    
    # For deployment, we need to check if the file exists in the deployment environment
    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}, using sample data instead")
        return False
        
    try:
        print(f"Loading wine data from {csv_path}...")
        # Read the CSV file
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Limit to 1000 rows to avoid memory issues
        df = df.head(1000)
        
        # Remove duplicate wines by name
        df = df.drop_duplicates(subset=['name'])
        
        print(f"Loaded {len(df)} wines from CSV file")
        
        # Convert dataframe rows to Wine objects
        for _, row in df.iterrows():
            try:
                # Extract wine name and clean up Korean text
                name = ''
                if 'name' in row and pd.notna(row['name']):
                    # ワイン名から韓国語パートを除去（通常は最初の部分）
                    raw_name = str(row['name'])
                    # 韓国語とそれ以外のパートを分離
                    parts = raw_name.split(',')
                    if len(parts) > 1:
                        # カンマで区切られている場合は2番目の部分を使用
                        name = parts[1].strip()
                    else:
                        name = raw_name
                    
                # 品種情報のクリーンアップと抽出
                variety = ''
                variety_sub1 = ''
                variety_sub2 = ''
                
                # カラムの位置ではなく名前で品種を特定
                if 'variety' in row.index and pd.notna(row['variety']):
                    variety = str(row['variety'])
                elif len(row) > 8 and pd.notna(row[8]):
                    variety = str(row[8])
                    
                if 'variety_sub1' in row.index and pd.notna(row['variety_sub1']):
                    variety_sub1 = str(row['variety_sub1'])
                elif len(row) > 9 and pd.notna(row[9]):
                    variety_sub1 = str(row[9])
                    
                if 'variety_sub2' in row.index and pd.notna(row['variety_sub2']):
                    variety_sub2 = str(row['variety_sub2'])
                elif len(row) > 10 and pd.notna(row[10]):
                    variety_sub2 = str(row[10])
                
                # Extract vintage as integer
                vintage = 0
                if 'vintage' in row and pd.notna(row['vintage']):
                    try:
                        vintage = int(row['vintage'])
                    except:
                        vintage = 0
                
                # Extract wine type
                wine_type = 'red'  # Default
                if 'wine_type' in row and pd.notna(row['wine_type']):
                    wine_type = row['wine_type'].lower()
                
                # Extract price
                price = 0
                if 'price' in row and pd.notna(row['price']):
                    try:
                        price = int(row['price'])
                    except:
                        price = 0
                
                # Handle taste attributes
                acidity = 3.0  # Default values
                tannin = 3.0
                body = 3.0
                sweetness = 1.0
                
                # CSVファイルでは 'sweet' という列名で甘さが保存されている
                if 'sweet' in row.index and pd.notna(row['sweet']):
                    sweetness_str = str(row['sweet'])
                    if 'SWEET1' in sweetness_str:
                        sweetness = 1.0
                    elif 'SWEET2' in sweetness_str:
                        sweetness = 2.0
                    elif 'SWEET3' in sweetness_str:
                        sweetness = 3.0
                    elif 'SWEET4' in sweetness_str:
                        sweetness = 4.0
                    elif 'SWEET5' in sweetness_str:
                        sweetness = 5.0
                    print(f"Processed sweetness value: {sweetness_str} -> {sweetness}")
                
                # 'acidity' 列からデータを取得
                if 'acidity' in row.index and pd.notna(row['acidity']):
                    acidity_str = str(row['acidity'])
                    if 'ACIDITY1' in acidity_str:
                        acidity = 1.0
                    elif 'ACIDITY2' in acidity_str:
                        acidity = 2.0
                    elif 'ACIDITY3' in acidity_str:
                        acidity = 3.0
                    elif 'ACIDITY4' in acidity_str:
                        acidity = 4.0
                    elif 'ACIDITY5' in acidity_str:
                        acidity = 5.0
                
                # 'body' 列からデータを取得
                if 'body' in row.index and pd.notna(row['body']):
                    body_str = str(row['body'])
                    if 'BODY1' in body_str:
                        body = 1.0
                    elif 'BODY2' in body_str:
                        body = 2.0
                    elif 'BODY3' in body_str:
                        body = 3.0
                    elif 'BODY4' in body_str:
                        body = 4.0
                    elif 'BODY5' in body_str:
                        body = 5.0
                
                # 'tannin' 列からデータを取得
                if 'tannin' in row.index and pd.notna(row['tannin']):
                    tannin_str = str(row['tannin'])
                    if 'TANNIN1' in tannin_str:
                        tannin = 1.0
                    elif 'TANNIN2' in tannin_str:
                        tannin = 2.0
                    elif 'TANNIN3' in tannin_str:
                        tannin = 3.0
                    elif 'TANNIN4' in tannin_str:
                        tannin = 4.0
                    elif 'TANNIN5' in tannin_str:
                        tannin = 5.0
                
                # 韓国語を含む行は除外するチェック
                if name.strip() == '' or any(ord(c) > 0xAC00 and ord(c) < 0xD7A4 for c in name):
                    # 空の名前または韓国語文字を含む場合はスキップ
                    continue
                    
                # 品種名もクリーンアップ
                def clean_text(text):
                    # 韓国語の範囲はU+AC00-U+D7A3
                    return ''.join([c for c in text if not (ord(c) > 0xAC00 and ord(c) < 0xD7A4)])
                
                variety = clean_text(variety)
                variety_sub1 = clean_text(variety_sub1)
                variety_sub2 = clean_text(variety_sub2)
                
                # Create Wine object
                wine = Wine(
                    name=name,
                    variety=variety,
                    variety_sub1=variety_sub1,
                    variety_sub2=variety_sub2,
                    vintage=vintage,
                    wine_type=wine_type,
                    price=price,
                    acidity=acidity,
                    tannin=tannin,
                    body=body,
                    sweetness=sweetness
                )
                
                # Add to session
                db.session.add(wine)
                
            except Exception as e:
                print(f"Error processing wine row: {e}")
                continue
        
        # Commit changes
        db.session.commit()
        print("CSV data imported successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading wine data from CSV: {e}")
        return False

def create_sample_data():
    """Set up the database with sample data for deployment and testing."""
    with app.app_context():
        print("Dropping all tables to ensure clean setup...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        # Try to load from CSV first
        csv_loaded = load_from_csv()
        
        # If CSV loading failed, use sample data
        if not csv_loaded:
            print("Adding sample wine data...")
            # Create sample wine data based on real entries from wine_info.csv
            sample_wines = [
            # Japanese wines
            Wine(name="シャトー・メルシャン 甲州きいろ香 2022", variety="甲州", vintage=2022, 
                 wine_type="white", price=2500, acidity=3.8, tannin=1.0, body=2.0, sweetness=1.0),
            Wine(name="ジャパンプレミアム 塩尻メルロー 2018", variety="Merlot", vintage=2018, 
                 wine_type="red", price=3800, acidity=3.5, tannin=3.5, body=4.0, sweetness=1.0),
            Wine(name="登美の丘 マスカット・ベリーＡ 2020", variety="Muscat Bailey A", vintage=2020, 
                 wine_type="red", price=5500, acidity=3.2, tannin=2.5, body=3.0, sweetness=1.5),
                 
            # French wines
            Wine(name="Château Margaux 2015", variety="Cabernet Sauvignon", vintage=2015, 
                 wine_type="red", price=120000, acidity=3.5, tannin=4.0, body=5.0, sweetness=1.0),
            Wine(name="Dom Pérignon 2010", variety="Chardonnay", vintage=2010, 
                 wine_type="sparkling", price=25000, acidity=4.0, tannin=1.0, body=3.0, sweetness=2.5),
            Wine(name="シャブリ グラン・クリュ 2019", variety="Chardonnay", vintage=2019, 
                 wine_type="white", price=8000, acidity=4.2, tannin=1.0, body=3.0, sweetness=1.0),
            Wine(name="シャトーヌフ・デュ・パプ 2017", variety="Grenache", vintage=2017, 
                 wine_type="red", price=9000, acidity=3.5, tannin=3.8, body=4.5, sweetness=1.0),
                 
            # Italian wines
            Wine(name="バローロ 2016", variety="Nebbiolo", vintage=2016, 
                 wine_type="red", price=12000, acidity=4.0, tannin=4.5, body=4.5, sweetness=1.0),
            Wine(name="キアンティ クラシコ リゼルヴァ 2017", variety="Sangiovese", vintage=2017, 
                 wine_type="red", price=6000, acidity=3.8, tannin=3.5, body=4.0, sweetness=1.0),
            Wine(name="ガヤ バルバレスコ 2015", variety="Nebbiolo", vintage=2015, 
                 wine_type="red", price=38000, acidity=4.0, tannin=4.0, body=4.0, sweetness=1.0),
                 
            # US wines
            Wine(name="Opus One 2018", variety="Cabernet Sauvignon", variety_sub1="Merlot", vintage=2018, 
                 wine_type="red", price=45000, acidity=3.8, tannin=4.5, body=5.0, sweetness=1.5),
            Wine(name="Cloudy Bay Sauvignon Blanc 2022", variety="Sauvignon Blanc", vintage=2022, 
                 wine_type="white", price=4000, acidity=4.5, tannin=1.0, body=2.0, sweetness=1.5),
            Wine(name="Silver Oak Alexander Valley Cabernet Sauvignon 2016", variety="Cabernet Sauvignon", vintage=2016, 
                 wine_type="red", price=15000, acidity=3.5, tannin=4.0, body=4.5, sweetness=1.0),
                 
            # Spanish & Portuguese wines
            Wine(name="Vega Sicilia Unico 2009", variety="Tempranillo", variety_sub1="Cabernet Sauvignon", vintage=2009, 
                 wine_type="red", price=62000, acidity=3.8, tannin=4.2, body=5.0, sweetness=1.0),
            Wine(name="Cvne Rioja Crianza 2018", variety="Tempranillo", variety_sub1="Garnacha", vintage=2018, 
                 wine_type="red", price=3500, acidity=3.5, tannin=3.5, body=3.5, sweetness=1.0),
            Wine(name="ダウズ ヴィンテージ ポート 2016", variety="Touriga Nacional", vintage=2016, 
                 wine_type="red", price=18000, acidity=3.5, tannin=4.0, body=5.0, sweetness=4.0),
                 
            # Other popular wines
            Wine(name="モエ・エ・シャンドン ブリュット", variety="Chardonnay", variety_sub1="Pinot Noir", vintage=2018, 
                 wine_type="sparkling", price=7000, acidity=4.0, tannin=1.0, body=2.5, sweetness=2.0),
            Wine(name="ヴーヴ・クリコ イエローラベル", variety="Chardonnay", variety_sub1="Pinot Noir", vintage=2019, 
                 wine_type="sparkling", price=7500, acidity=4.2, tannin=1.0, body=2.5, sweetness=1.5),
            Wine(name="ペンフォールズ グランジ 2017", variety="Shiraz", vintage=2017, 
                 wine_type="red", price=98000, acidity=3.5, tannin=4.5, body=5.0, sweetness=1.0),
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
    create_sample_data()
    
# Export additional function for direct CSV loading
def load_csv_data():
    """Function to directly load CSV data without dropping tables"""
    with app.app_context():
        # Check if wines already exist
        existing_count = Wine.query.count()
        print(f"Database currently has {existing_count} wines")
        
        if existing_count == 0:
            # Load from CSV
            if not load_from_csv():
                # Fall back to sample data if CSV loading fails
                print("Adding sample wines instead...")
                create_sample_data()
        else:
            print("Database already contains wines, skipping import")
