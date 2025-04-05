import pandas as pd
from app import app, db, Wine, UserPreference
import os
import csv
import mysql.connector

def clean_numeric(value, default=0.0):
    try:
        # Remove any non-numeric characters and convert to float
        cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.' or c == '-')
        return float(cleaned) if cleaned else default
    except (ValueError, TypeError):
        return default

def won_to_yen(won_price):
    # 1 KRW = 0.0892 JPY (approximate rate)
    if won_price == 0 or pd.isna(won_price):
        return 0
    return round(float(won_price) * 0.0892)

def import_wine_data():
    try:
        with app.app_context():
            # 既存のデータを削除（外部キー制約を考慮）
            UserPreference.query.delete()
            Wine.query.delete()
            db.session.commit()
            
            # CSVファイルを読み込む
            df = pd.read_csv('../archive/wine_info.csv')
            
            # 各行をデータベースに挿入
            for _, row in df.iterrows():
                # 品種情報を取得（NaNを除外）
                varieties = [
                    str(row['varieties1']) if pd.notna(row['varieties1']) else None,
                    str(row['varieties2']) if pd.notna(row['varieties2']) else None,
                    str(row['varieties3']) if pd.notna(row['varieties3']) else None
                ]
                # NaNでない品種のみをフィルタリング
                varieties = [v for v in varieties if v is not None and v.lower() != 'nan']
                
                # Convert price from KRW to JPY
                price_won = clean_numeric(row.get('price', 0))
                price_yen = won_to_yen(price_won)
                
                # Convert sweetness to numeric value
                sweetness_map = {
                    'SWEET1': 1,  # Very Dry
                    'SWEET2': 2,  # Dry
                    'SWEET3': 3,  # Medium
                    'SWEET4': 4,  # Sweet
                    'SWEET5': 5   # Very Sweet
                }
                
                sweet_value = row.get('sweet')
                if pd.isna(sweet_value):
                    # ワインタイプに基づいてデフォルトの甘さを設定
                    wine_type = str(row.get('type', '')).lower()
                    if wine_type == 'red':
                        sweetness = 1  # 赤ワインは通常辛口
                    elif wine_type == 'white':
                        sweetness = 2  # 白ワインは通常やや辛口
                    elif wine_type == 'sparkling':
                        sweetness = 3  # スパークリングは中程度
                    else:
                        sweetness = 2  # その他は辛口をデフォルトに
                    print(f"Warning: Missing sweetness value for wine {row.get('name')} ({wine_type}). Using default: {sweetness}")
                else:
                    sweetness = sweetness_map.get(sweet_value)
                    if sweetness is None:
                        print(f"Warning: Invalid sweetness value for wine {row.get('name')}: {sweet_value}")
                        sweetness = 2  # 不明な場合は辛口をデフォルトに
                
                # 製造年を取得（NaNの場合はNone）
                vintage = None
                if 'year' in row and pd.notna(row['year']):
                    try:
                        vintage = int(row['year'])
                    except (ValueError, TypeError):
                        vintage = None
                
                # ワインタイプを取得
                wine_type = str(row['type']).lower() if pd.notna(row.get('type')) else 'unknown'
                # タイプを標準化
                if 'red' in wine_type:
                    wine_type = 'red'
                elif 'white' in wine_type:
                    wine_type = 'white'
                elif 'rose' in wine_type or 'rosé' in wine_type:
                    wine_type = 'rose'
                elif 'sparkling' in wine_type:
                    wine_type = 'sparkling'
                else:
                    wine_type = 'other'
                
                # Wineオブジェクトを作成
                wine = Wine(
                    name=row['name'],
                    variety=varieties[0] if len(varieties) > 0 else None,
                    variety_sub1=varieties[1] if len(varieties) > 1 else None,
                    variety_sub2=varieties[2] if len(varieties) > 2 else None,
                    vintage=vintage,
                    wine_type=wine_type,
                    price=price_yen,
                    acidity=clean_numeric(row.get('acidity', 0.0)),
                    tannin=clean_numeric(row.get('tannin', 0.0)),
                    body=clean_numeric(row.get('body', 0.0)),
                    sweetness=sweetness
                )
                db.session.add(wine)

                # 進捗表示
                if _ % 100 == 0:
                    print(f"Processed {_} wines")
            
            # 変更を保存
            db.session.commit()
            print("ワインデータのインポートが完了しました")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        import_wine_data()
