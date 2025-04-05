from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import os
from dotenv import load_dotenv
from collections import defaultdict
import numpy as np
from scipy.spatial import distance
from datetime import datetime
import math
from sqlalchemy import func
from sklearn.metrics.pairwise import cosine_similarity
import webbrowser
import threading
import time

load_dotenv()

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL', "mysql+mysqlconnector://oto:0000@localhost/wine_preferences")

# Handle different database URLs depending on environment
if database_url:
    # If using Postgres in production (common for cloud platforms)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    # If using SQLite (easier for initial deployment)
    elif database_url.startswith("sqlite://"):
        sqlite_path = database_url.replace("sqlite:///", "", 1)
        # Make path absolute for SQLite if it's not already
        if not os.path.isabs(sqlite_path):
            sqlite_path = os.path.join(os.path.dirname(__file__), sqlite_path)
        database_url = f"sqlite:///{sqlite_path}"

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    variety = db.Column(db.String(100))  # メイン品種
    variety_sub1 = db.Column(db.String(100))  # サブ品種1
    variety_sub2 = db.Column(db.String(100))  # サブ品種2
    vintage = db.Column(db.Integer)  # 製造年
    wine_type = db.Column(db.String(50))  # ワインタイプ（赤、白、ロゼ、スパークリング）
    price = db.Column(db.Integer)
    acidity = db.Column(db.Float)
    tannin = db.Column(db.Float)
    body = db.Column(db.Float)
    sweetness = db.Column(db.Float)  # 文字列から数値に変更

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wine.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    rated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    wine = db.relationship('Wine', backref=db.backref('preferences', lazy=True))

def convert_sweetness():
    try:
        # すべてのワインを取得
        wines = Wine.query.all()
        app.logger.info(f"Found {len(wines)} wines to update")
        
        for wine in wines:
            # 現在の値を確認
            old_value = wine.sweetness
            
            # SWEET1-SWEET5を1-5に変換
            if isinstance(wine.sweetness, str):
                if wine.sweetness == 'SWEET1':
                    wine.sweetness = 1.0
                elif wine.sweetness == 'SWEET2':
                    wine.sweetness = 2.0
                elif wine.sweetness == 'SWEET3':
                    wine.sweetness = 3.0
                elif wine.sweetness == 'SWEET4':
                    wine.sweetness = 4.0
                elif wine.sweetness == 'SWEET5':
                    wine.sweetness = 5.0
                else:
                    wine.sweetness = 3.0  # デフォルト値
                app.logger.info(f"Updated wine {wine.id} sweetness from {old_value} to {wine.sweetness}")
        
        # 変更を保存
        db.session.commit()
        app.logger.info("Sweetness values updated successfully")
    except Exception as e:
        app.logger.error(f"Error updating sweetness values: {str(e)}")
        db.session.rollback()

# アプリケーション起動時に実行
with app.app_context():
    try:
        # テーブル作成を確実に
        db.create_all()
        app.logger.info("Database tables created successfully")
        
        # データベースが空なら初期データを投入
        if Wine.query.count() == 0:
            app.logger.info("No wines found in database, loading sample data")
            try:
                from setup_database import create_sample_data
                create_sample_data()
                app.logger.info("Sample data loaded successfully")
            except Exception as setup_e:
                app.logger.error(f"Error loading sample data: {str(setup_e)}")
        else:
            app.logger.info(f"Database already contains {Wine.query.count()} wines")
            
        # SWEET形式の甘さデータを数値に変換
        convert_sweetness()
    except Exception as init_e:
        app.logger.error(f"Error during application initialization: {str(init_e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wine/<int:wine_id>')
def get_wine(wine_id):
    wine = Wine.query.get(wine_id)
    if wine is None:
        return jsonify({'error': 'Wine not found'}), 404
    return jsonify({
        'id': wine.id,
        'name': wine.name,
        'variety': wine.variety,
        'price': 'Unknown' if wine.price == 0 else f"{wine.price:,}"
    })

@app.route('/get_wine/<int:wine_id>')
def get_wine_detail(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    return jsonify({
        'id': wine.id,
        'name': wine.name,
        'vintage': wine.vintage,
        'variety': wine.variety,
        'variety_sub1': wine.variety_sub1,
        'variety_sub2': wine.variety_sub2,
        'price': wine.price,
        'wine_type': wine.wine_type,
        'acidity': wine.acidity,
        'tannin': wine.tannin,
        'body': wine.body,
        'sweetness': wine.sweetness
    })

@app.route('/search_wines_by_name')
def search_wines_by_name():
    try:
        query = request.args.get('q', '')
        if not query or len(query) < 2:  # 少なくとも2文字以上のクエリを要求
            return jsonify([])
        
        # デバッグ情報を追加
        app.logger.info(f"Search query: '{query}'")
        
        # 入力値のサニタイズ（特殊文字をエスケープ）
        query = query.replace('%', '\%').replace('_', '\_')
        
        # 簡易的なクエリの場合は応答時間を改善
        try:
            # データベース内のワインが存在するか確認
            wine_count = Wine.query.count()
            app.logger.info(f"Total wines in database: {wine_count}")
            
            if wine_count == 0:
                # サンプルデータを追加
                from setup_database import create_sample_data
                app.logger.info("No wines found, adding sample data")
                create_sample_data()
                wine_count = Wine.query.count()
                app.logger.info(f"Added sample data. Now have {wine_count} wines")
                
            # 名前で検索（大文字小文字を区別しない）
            # タイムアウト防止のため、複雑なクエリは避け、インデックスを活用
            name_query = f"%{query}%"
            wines = Wine.query.filter(Wine.name.ilike(name_query)).limit(10).all()
            
            # 名前での検索結果がなければ、品種でも検索
            if not wines:
                app.logger.info(f"No results by name, trying variety search")
                variety_query = f"%{query}%"
                wines = Wine.query.filter(
                    db.or_(
                        Wine.variety.ilike(variety_query),
                        Wine.variety_sub1.ilike(variety_query),
                        Wine.variety_sub2.ilike(variety_query)
                    )
                ).limit(10).all()
            
            app.logger.info(f"Found {len(wines)} matching wines")
            
            # ただし結果がない場合は空の配列を返す
            if not wines:
                return jsonify([])
                
            # 結果を整形
            results = []
            for wine in wines:
                try:
                    wine_data = {
                        'id': wine.id,
                        'name': wine.name or '',
                        'variety': wine.variety or '',
                        'variety_sub1': wine.variety_sub1 or '',
                        'variety_sub2': wine.variety_sub2 or '',
                        'vintage': wine.vintage or 0,
                        'wine_type': wine.wine_type or 'other',
                        'price': wine.price or 0
                    }
                    # オプションのデータ（NULLの場合があるため）
                    if hasattr(wine, 'acidity') and wine.acidity is not None:
                        wine_data['acidity'] = wine.acidity
                    if hasattr(wine, 'tannin') and wine.tannin is not None:
                        wine_data['tannin'] = wine.tannin
                    if hasattr(wine, 'body') and wine.body is not None:
                        wine_data['body'] = wine.body
                    if hasattr(wine, 'sweetness') and wine.sweetness is not None:
                        wine_data['sweetness'] = wine.sweetness
                    
                    results.append(wine_data)
                except Exception as item_e:
                    app.logger.warning(f"Error processing wine item {wine.id}: {str(item_e)}")
                    continue
            
            return jsonify(results)
            
        except Exception as db_e:
            app.logger.error(f"Database error: {str(db_e)}")
            # エラーでもクラッシュせず、空の結果を返す
            return jsonify([])
            
    except Exception as e:
        app.logger.error(f"Error searching wines: {str(e)}")
        # クライアントにはシンプルなエラーメッセージを返す
        return jsonify([]), 200  # エラーでも200を返してフロントエンドでのエラー処理を避ける

@app.route('/get_preferences')
def get_preferences():
    try:
        # ユーザーの評価履歴を取得
        rated_wines = []
        preferences = {
            'acidity': 0,
            'tannin': 0,
            'body': 0,
            'sweetness': 0,
            'total_weight': 0  # 重みの合計を追加
        }
        
        ratings = UserPreference.query.order_by(UserPreference.rated_at.desc()).all()
        
        for rating in ratings:
            wine = Wine.query.get(rating.wine_id)
            if wine:
                rated_wines.append({
                    'id': wine.id,
                    'name': wine.name,
                    'variety': wine.variety,
                    'variety_sub1': wine.variety_sub1,
                    'variety_sub2': wine.variety_sub2,
                    'vintage': wine.vintage,
                    'wine_type': wine.wine_type or 'other',
                    'price': wine.price,
                    'rating': rating.rating,
                    'rated_at': rating.rated_at.isoformat()
                })
                
                # 重みを二次関数で計算（rating^2）
                weight = rating.rating ** 2
                
                # 好みの集計（重み付き）
                preferences['acidity'] += wine.acidity * weight
                preferences['tannin'] += wine.tannin * weight
                preferences['body'] += wine.body * weight
                preferences['sweetness'] += wine.sweetness * weight
                preferences['total_weight'] += weight
        
        # 平均を計算（重み付き）
        if preferences['total_weight'] > 0:
            for key in ['acidity', 'tannin', 'body', 'sweetness']:
                preferences[key] = round(preferences[key] / preferences['total_weight'], 2)
        
        # total_weightは不要なので削除
        del preferences['total_weight']
        
        return jsonify({
            'preferences': preferences,
            'rated_wines': rated_wines
        })
        
    except Exception as e:
        print(f"Error getting preferences: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/add_preference', methods=['POST'])
def add_preference():
    try:
        data = request.get_json()
        wine_id = data.get('wine_id')
        rating = data.get('rating')
        
        app.logger.info(f"Received preference data: wine_id={wine_id}, rating={rating}")
        
        if not wine_id or not rating:
            app.logger.error("Missing wine_id or rating")
            return jsonify({'error': 'Missing wine_id or rating'}), 400
        
        # 既存の評価を確認
        existing_preference = UserPreference.query.filter_by(wine_id=wine_id).first()
        if existing_preference:
            app.logger.info(f"Updating existing preference for wine_id={wine_id}")
            existing_preference.rating = rating
            existing_preference.rated_at = datetime.utcnow()
        else:
            app.logger.info(f"Creating new preference for wine_id={wine_id}")
            preference = UserPreference(wine_id=wine_id, rating=rating, rated_at=datetime.utcnow())
            db.session.add(preference)
        
        db.session.commit()
        app.logger.info("Preference saved successfully")

        # 更新された好みと評価済みワインを返す
        return get_preferences()

    except Exception as e:
        app.logger.error(f"Error saving preference: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_variety_similarity(user_wines, target_wine):
    """品種の類似度を計算"""
    # ユーザーが評価したワインの品種をカウント
    user_varieties = defaultdict(float)
    total_weight = 0
    
    for pref in user_wines:
        wine = pref.wine
        weight = pref.rating ** 2
        # メイン品種のカウント
        if wine.variety:
            user_varieties[wine.variety] += weight
        total_weight += weight
    
    # 各品種の重みを正規化
    if total_weight > 0:
        for variety in user_varieties:
            user_varieties[variety] /= total_weight
    
    # 対象ワインの品種との類似度を計算
    similarity = 0
    if target_wine.variety and target_wine.variety in user_varieties:
        similarity = user_varieties[target_wine.variety]
    
    return similarity

@app.route('/get_recommendations')
def get_recommendations():
    try:
        # ユーザーの好みを取得
        user_preferences = UserPreference.query.join(Wine).all()
        
        if not user_preferences:
            return jsonify({
                'red': [],
                'white': [],
                'sparkling': [],
                'other': []
            })

        # 評価済みワインのIDを取得
        rated_wine_ids = {pref.wine_id for pref in user_preferences}

        # ユーザーの好みの特徴量の平均を計算
        weights = {}
        total_weight = 0
        
        for pref in user_preferences:
            wine = pref.wine
            if wine.acidity is not None and wine.tannin is not None and wine.body is not None and wine.sweetness is not None:
                weights[wine.id] = pref.rating ** 2
                total_weight += weights[wine.id]

        if total_weight > 0:
            # ユーザーの好みを計算
            user_prefs = {
                'acidity': sum(pref.wine.acidity * weights[pref.wine_id] for pref in user_preferences) / total_weight,
                'tannin': sum(pref.wine.tannin * weights[pref.wine_id] for pref in user_preferences) / total_weight,
                'body': sum(pref.wine.body * weights[pref.wine_id] for pref in user_preferences) / total_weight,
                'sweetness': sum(pref.wine.sweetness * weights[pref.wine_id] for pref in user_preferences) / total_weight
            }

            # 特徴量の重要度
            feature_weights = {
                'acidity': 1.5,    # 酸味（重要）
                'tannin': 1.5,     # タンニン（重要）
                'body': 1.0,       # ボディ（標準）
                'sweetness': 1.0   # 甘さ（標準）
            }

            def calculate_feature_similarity(user_prefs, wine):
                # 1-5の範囲を0-1に正規化
                normalized_user = {k: (v - 1) / 4 for k, v in user_prefs.items()}
                normalized_wine = {
                    'acidity': (wine.acidity - 1) / 4,
                    'tannin': (wine.tannin - 1) / 4,
                    'body': (wine.body - 1) / 4,
                    'sweetness': (wine.sweetness - 1) / 4
                }
                
                # 重み付きユークリッド距離
                weighted_diff_sum = sum(
                    feature_weights[feature] * (normalized_user[feature] - normalized_wine[feature])**2
                    for feature in feature_weights
                )
                total_weight = sum(feature_weights.values())
                
                distance = math.sqrt(weighted_diff_sum / total_weight)
                return 1 - distance  # 距離を類似度に変換（0-1の範囲）

            # 未評価のワインを取得
            unrated_wines = Wine.query.filter(Wine.id.notin_(rated_wine_ids)).all()
            
            # 各ワインタイプごとのレコメンデーション
            recommendations = {
                'red': [],
                'white': [],
                'sparkling': [],
                'other': []
            }

            for wine in unrated_wines:
                if wine.acidity is None or wine.tannin is None or wine.body is None or wine.sweetness is None:
                    continue

                # 特徴量の類似度を計算（90%）
                feature_sim = calculate_feature_similarity(user_prefs, wine)
                
                # 品種の類似度を計算（10%）
                variety_sim = calculate_variety_similarity(user_preferences, wine)
                
                # 特徴量と品種の類似度を9:1で線形結合
                similarity = 0.9 * feature_sim + 0.1 * variety_sim
                
                wine_type = wine.wine_type.lower() if wine.wine_type else 'other'
                if wine_type not in recommendations:
                    wine_type = 'other'

                recommendations[wine_type].append({
                    'id': wine.id,
                    'name': wine.name,
                    'vintage': wine.vintage,
                    'variety': wine.variety,
                    'variety_sub1': wine.variety_sub1,
                    'variety_sub2': wine.variety_sub2,
                    'price': wine.price,
                    'wine_type': wine.wine_type,
                    'similarity': float(similarity),
                    'acidity': wine.acidity,
                    'tannin': wine.tannin,
                    'body': wine.body,
                    'sweetness': wine.sweetness
                })

            # 各タイプで類似度の高い順にソートして上位5件を取得
            for wine_type in recommendations:
                recommendations[wine_type] = sorted(
                    recommendations[wine_type],
                    key=lambda x: x['similarity'],
                    reverse=True
                )[:5]

            return jsonify(recommendations)

        return jsonify({
            'red': [],
            'white': [],
            'sparkling': [],
            'other': []
        })

    except Exception as e:
        app.logger.error(f"Error in get_recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_rated_wines')
def get_rated_wines():
    try:
        ratings = UserPreference.query.order_by(UserPreference.rated_at.desc()).all()
        rated_wines = []
        
        for rating in ratings:
            wine = Wine.query.get(rating.wine_id)
            if wine:
                rated_wines.append({
                    'id': wine.id,
                    'name': wine.name,
                    'variety': wine.variety,
                    'variety_sub1': wine.variety_sub1,
                    'variety_sub2': wine.variety_sub2,
                    'vintage': wine.vintage,
                    'wine_type': wine.wine_type or 'other',
                    'price': wine.price,
                    'rating': rating.rating,
                    'rated_at': rating.rated_at.isoformat()
                })
        
        return jsonify(rated_wines)
        
    except Exception as e:
        print(f"Error getting rated wines: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/rate_wine', methods=['POST'])
def rate_wine():
    try:
        data = request.get_json()
        wine_id = data.get('wine_id')
        rating = data.get('rating')

        if not wine_id or not rating:
            return jsonify({'error': '必要なパラメータが不足しています'}), 400

        # 既存の評価を確認
        existing_rating = UserPreference.query.filter_by(wine_id=wine_id).first()
        if existing_rating:
            # 既存の評価を更新
            existing_rating.rating = rating
            existing_rating.rated_at = datetime.utcnow()
        else:
            # 新しい評価を作成
            new_rating = UserPreference(
                wine_id=wine_id,
                rating=rating,
                rated_at=datetime.utcnow()
            )
            db.session.add(new_rating)

        db.session.commit()
        return jsonify({'message': '評価を保存しました'})

    except Exception as e:
        print(f"Error rating wine: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/update_sweetness')
def update_sweetness():
    try:
        # すべてのワインを取得
        wines = Wine.query.all()
        app.logger.info(f"Found {len(wines)} wines to update")
        
        for wine in wines:
            # 現在の値を確認
            old_value = wine.sweetness
            
            # 値を更新
            if old_value == 0 or old_value is None:
                wine.sweetness = 3.0  # デフォルト値
            elif old_value < 1:
                wine.sweetness = 1.0
            elif old_value > 5:
                wine.sweetness = 5.0
            else:
                wine.sweetness = round(old_value)
            
            app.logger.info(f"Updated wine {wine.id} sweetness from {old_value} to {wine.sweetness}")
        
        # 変更を保存
        db.session.commit()
        app.logger.info("Sweetness values updated successfully")
        return jsonify({'message': 'Sweetness values updated successfully'})

    except Exception as e:
        app.logger.error(f"Error updating sweetness values: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delete_rating/<int:wine_id>', methods=['DELETE'])
def delete_rating(wine_id):
    try:
        rating = UserPreference.query.filter_by(wine_id=wine_id).first()
        if rating:
            db.session.delete(rating)
            db.session.commit()
            return jsonify({'message': '評価を削除しました'})
        else:
            return jsonify({'error': '評価が見つかりません'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """アプリケーションを終了するエンドポイント"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

def open_browser():
    """アプリケーションのURLをブラウザで開く"""
    # サーバーが起動するのを少し待つ
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # ブラウザを別スレッドで開く
    # threading.Thread(target=open_browser).start()
    # アプリケーションを起動
    app.run(debug=False)
