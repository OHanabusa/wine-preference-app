from app import app, db, UserPreference
from datetime import datetime

def fix_created_at():
    with app.app_context():
        # created_atがNullのレコードを取得
        preferences = UserPreference.query.filter(UserPreference.created_at.is_(None)).all()
        print(f"Found {len(preferences)} preferences without created_at")
        
        # 現在時刻を設定
        now = datetime.utcnow()
        for pref in preferences:
            pref.created_at = now
            print(f"Setting created_at for preference {pref.id}")
        
        # 変更を保存
        db.session.commit()
        print("All preferences updated successfully")

if __name__ == '__main__':
    fix_created_at()
