# ワイン好み分析アプリケーション

このアプリケーションは、ユーザーのワイン評価に基づいて好みを分析し、おすすめのワインを提案するWebアプリケーションです。CSVファイルから様々な種類のワインデータを自動的にロードし、ユーザーの好みに基づいたレコメンデーションを提供します。

## 機能

- ワイン検索
- ワインの評価（5段階）
- 好みの分析（レーダーチャート）
- ワインのレコメンデーション
- 評価履歴の表示

## 技術スタック

- Backend: Python (Flask)
- Frontend: HTML, JavaScript, Bootstrap
- Database: PostgreSQL（本番環境）/ SQLite（開発環境）
- 分析: scikit-learn, Pandas
- デプロイ: Render

## セットアップ

### 1. 環境構築

```bash
# Conda環境の作成と有効化
conda create -n wine-app python=3.9
conda activate wine-app

# 依存パッケージのインストール
pip install -r requirements.txt

# Flask-Migrateのインストール
pip install flask-migrate
```

### 2. データベース設定

#### 開発環境（SQLite）
`.env`ファイルを作成し、以下の環境変数を設定
```
DATABASE_URL=sqlite:///wineapp.db
```

#### 本番環境（PostgreSQL）
Renderなどのホスティングサービスで自動的に`DATABASE_URL`環境変数が設定されます。
```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### 3. データベースの初期化

```bash
# データベースの初期化と初期データのロード
python initialize_db.py
```

このコマンドは以下の処理を実行します：
1. データベーステーブルの作成
2. CSVファイルからワインデータのロード
3. サンプルユーザーと好み設定の作成

## 起動方法

```bash
# アプリケーションの起動
flask run
```

```bash
# アプリケーションの確認
ps aux | grep app.py | grep -v grep

# アプリケーションを停止
kill 1234
```

アプリケーションは http://localhost:5000 でアクセスできます。

## データの管理

### ワインデータのCSVインポート

ワインデータは`/Users/oto/CascadeProjects/windsurf-project/archive/wine_info.csv`ファイルから自動的にロードされます。CSVファイルには以下の列が必要です：

- name: ワイン名
- producer: 生産者
- variety: 主要品種
- variety_sub1: 副品種1（オプション）
- variety_sub2: 副品種2（オプション）
- price: 価格
- vintage: 製造年
- wine_type: ワインタイプ（red/white/rose/sparkling）
- acidity: 酸味（ACIDITY1～ACIDITY5）
- tannin: タンニン（TANNIN1～TANNIN5）
- body: ボディ（BODY1～BODY5）
- sweetness: 甘み（SWEET1～SWEET5）

### ワインデータのバランス

CSVからのデータロード時、以下のバランスでワインを取得します：
- 赤ワイン: 最大1000本
- 白ワイン: 最大500本
- スパークリングワイン: 最大200本
- ロゼワイン: 最大100本
- その他のワイン: 最大200本

これにより、様々な種類のワインがバランスよくデータベースに登録されます。

### データベースの更新

データベースを手動で更新するには以下のコマンドを実行します：

```bash
python initialize_db.py
```

### データベースのリセット

データベースをリセットする場合は以下の手順を実行します：

#### 開発環境（SQLite）
1. データベースファイルの削除
```bash
rm wineapp.db
```

2. データベースの再初期化
```bash
python initialize_db.py
```

#### 本番環境（PostgreSQL）
Renderダッシュボードから：
1. PostgreSQLデータベースサービスをリセット
2. アプリケーションを再デプロイ

## SQLによるデータ操作

### PostgreSQL/SQLiteへの接続

#### PostgreSQL（本番環境）
```bash
# PostgreSQLに接続（Renderダッシュボードから接続情報を取得）
psql postgresql://username:password@host:port/database_name
```

#### SQLite（開発環境）
```bash
# SQLiteに接続
sqlite3 wineapp.db
```

### 基本的なデータ検索

```sql
-- 全てのワインを表示
SELECT * FROM wine;

-- ワイン名で検索
SELECT * FROM wine WHERE name LIKE '%シャブリ%';

-- 価格帯で検索（3000円から5000円）
SELECT name, price, vintage FROM wine 
WHERE price BETWEEN 3000 AND 5000 
ORDER BY price;

-- ワインタイプ別の集計
SELECT wine_type, COUNT(*) as count, AVG(price) as avg_price 
FROM wine 
GROUP BY wine_type;

-- 評価の高いワイン（平均評価4以上）
SELECT w.name, w.vintage, w.wine_type, AVG(up.rating) as avg_rating
FROM wine w
JOIN user_preferences up ON w.id = up.wine_id
GROUP BY w.id
HAVING avg_rating >= 4
ORDER BY avg_rating DESC;
```

### データの更新と追加

```sql
-- ワインの価格を更新
UPDATE wine 
SET price = 3500 
WHERE name = 'シャブリ' AND vintage = 2020;

-- 新しいワインを追加
INSERT INTO wine (name, variety, price, vintage, wine_type, acidity, tannin, body, sweetness) 
VALUES ('新しいワイン', 'シャルドネ', 4000, 2022, 'white', 3, 2, 3, 2);

-- 評価データを追加
INSERT INTO user_preferences (wine_id, rating, rated_at) 
VALUES (1, 5, NOW());
```

### データの削除

```sql
-- 特定のワインを削除
DELETE FROM wine WHERE name = '削除するワイン';

-- 古い評価データを削除（1年以上前）
DELETE FROM user_preferences 
WHERE rated_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### 高度な検索クエリ

```sql
-- ワインと評価の詳細情報を結合して表示
SELECT 
    w.name,
    w.vintage,
    w.wine_type,
    w.price,
    COUNT(up.id) as rating_count,
    AVG(up.rating) as avg_rating,
    MAX(up.rated_at) as last_rated
FROM wine w
LEFT JOIN user_preferences up ON w.id = up.wine_id
GROUP BY w.id
ORDER BY avg_rating DESC;

-- 品種ごとの平均評価
SELECT 
    w.variety,
    COUNT(DISTINCT w.id) as wine_count,
    AVG(up.rating) as avg_rating,
    AVG(w.price) as avg_price
FROM wines w
LEFT JOIN user_preferences up ON w.id = up.wine_id
GROUP BY w.variety
HAVING wine_count > 1
ORDER BY avg_rating DESC;

-- 月別の評価傾向
SELECT 
    DATE_FORMAT(rated_at, '%Y-%m') as month,
    COUNT(*) as rating_count,
    AVG(rating) as avg_rating
FROM user_preferences
GROUP BY month
ORDER BY month DESC;
```

### バックアップとリストア

```bash
# データベースのバックアップ
mysqldump -u your_username -p wine_preference_db > backup.sql

# データベースのリストア
mysql -u your_username -p wine_preference_db < backup.sql
```

これらのSQLコマンドは、MySQLクライアントまたはMySQLワークベンチなどのGUIツールで実行できます。本番環境での実行時は、十分なテストと確認を行ってください。

## ワインの好みとレコメンデーションの仕組み

### 1. ワインの特徴

各ワインは以下の4つの特徴量で表現されています：

- **酸味（Acidity）**: 1-5の値（1: 低い, 5: 高い）
- **タンニン（Tannin）**: 1-5の値（1: 軽い, 5: 強い）
- **ボディ（Body）**: 1-5の値（1: ライト, 5: フル）
- **甘さ（Sweetness）**: 1-5の値（1: 辛口, 5: 甘口）

### 2. 好みの計算方法

ユーザーの好みは、評価したワインの特徴を評価値の二乗で重み付けして平均を取ることで計算されます：

```python
# 評価の二乗を重みとして使用
weights = {wine_id: rating**2 for wine_id, rating in user_ratings.items()}
total_weight = sum(weights.values())

preferences = {
    'acidity': sum(wines[wine_id].acidity * weights[wine_id] for wine_id in weights) / total_weight,
    'tannin': sum(wines[wine_id].tannin * weights[wine_id] for wine_id in weights) / total_weight,
    'body': sum(wines[wine_id].body * weights[wine_id] for wine_id in weights) / total_weight,
    'sweetness': sum(wines[wine_id].sweetness * weights[wine_id] for wine_id in weights) / total_weight
}

# 品種の好みを計算
variety_preferences = defaultdict(float)
for wine_id, weight in weights.items():
    if wines[wine_id].variety:
        variety_preferences[wines[wine_id].variety] += weight
# 重みの正規化
for variety in variety_preferences:
    variety_preferences[variety] /= total_weight
```

評価の重み付け（二次関数）：
- 5点の評価 → 重み25（5²）
- 4点の評価 → 重み16（4²）
- 3点の評価 → 重み9（3²）
- 2点の評価 → 重み4（2²）
- 1点の評価 → 重み1（1²）

この二次関数による重み付けにより：
- 高評価（4-5点）のワインの特徴が強く反映される
- 中評価（3点）の影響は中程度
- 低評価（1-2点）の影響は最小限に抑えられる

### 3. レコメンデーションアルゴリズム

ワインの推薦は以下の手順で行われます：

1. **ユーザーの好みベクトルの計算**
```python
weights = {wine_id: rating**2 for wine_id, rating in user_ratings.items()}
total_weight = sum(weights.values())

# ユーザーの好みを計算
user_preferences = {
    'acidity': sum(wines[wine_id].acidity * weights[wine_id] for wine_id in weights) / total_weight,
    'tannin': sum(wines[wine_id].tannin * weights[wine_id] for wine_id in weights) / total_weight,
    'body': sum(wines[wine_id].body * weights[wine_id] for wine_id in weights) / total_weight,
    'sweetness': sum(wines[wine_id].sweetness * weights[wine_id] for wine_id in weights) / total_weight
}

# 品種の好みを計算
variety_preferences = defaultdict(float)
for wine_id, weight in weights.items():
    if wines[wine_id].variety:
        variety_preferences[wines[wine_id].variety] += weight
# 重みの正規化
for variety in variety_preferences:
    variety_preferences[variety] /= total_weight
```

2. **類似度の計算**
```python
# 特徴量の重要度
feature_weights = {
    'acidity': 1.5,    # 酸味（重要）
    'tannin': 1.5,     # タンニン（重要）
    'body': 1.0,       # ボディ（標準）
    'sweetness': 1.0   # 甘さ（標準）
}

def calculate_similarity(user_prefs, variety_prefs, wine):
    # 特徴量の類似度計算
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
    feature_similarity = 1 - sqrt(weighted_diff_sum / total_weight)
    
    # 品種の類似度計算
    variety_similarity = variety_prefs.get(wine.variety, 0) if wine.variety else 0
    
    # 特徴量と品種の類似度を9:1で線形結合
    return 0.9 * feature_similarity + 0.1 * variety_similarity
```

3. **推薦ワインの選択**
- 未評価のワインそれぞれについて類似度を計算
- 特徴量の類似度（90%）と品種の類似度（10%）を組み合わせて最終的な類似度を算出
- 類似度でソートし、上位5本を推薦
- 同じワインタイプ（赤、白、ロゼ、スパークリング）ごとに分けて推薦

4. **類似度の解釈**
- 1.0: 完全一致（理想的な推薦）
- 0.8以上: 非常に類似（強く推薦）
- 0.6-0.8: かなり類似（推薦）
- 0.4-0.6: やや類似（弱い推薦）
- 0.4未満: あまり類似していない（推薦対象外）

### 4. レコメンデーションの改善

システムは以下の方法で継続的に改善されます：

1. **評価データの蓄積**:
   - ユーザーが評価を行うたびに好みのプロファイルが更新されます
   - より多くの評価データにより、より正確なレコメンデーションが可能になります

2. **多様性の確保**:
   - 評価済みのワインは推薦対象から除外されます
   - これにより、新しいワインとの出会いを促進します

3. **特徴量の重み付け**:
   - 現在は4つの特徴量を均等に扱っていますが、将来的には重要度に応じた重み付けを導入する可能性があります

## データモデル

### Wine モデル
ワインの基本情報と特徴を保存します：
```python
class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    variety = db.Column(db.String(100))      # メイン品種
    variety_sub1 = db.Column(db.String(100)) # サブ品種1
    variety_sub2 = db.Column(db.String(100)) # サブ品種2
    vintage = db.Column(db.Integer)          # 製造年
    wine_type = db.Column(db.String(50))     # ワインタイプ（赤、白、ロゼ、スパークリング）
    price = db.Column(db.Integer)
    acidity = db.Column(db.Float)    # 酸味（1-5）
    tannin = db.Column(db.Float)     # タンニン（1-5）
    body = db.Column(db.Float)       # ボディ（1-5）
    sweetness = db.Column(db.Float)  # 甘さ（1-5）
```

### UserPreference モデル
ユーザーの評価履歴を保存します：
```python
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wine.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # ユーザーの評価（1-5）
    rated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    wine = db.relationship('Wine', backref=db.backref('preferences', lazy=True))
```

### データの関係
- 各ワインは複数のユーザー評価を持つことができます（1対多の関係）
- ユーザーの評価は必ず1つのワインに紐づきます
- 評価履歴は時系列で保存され、最新の評価が優先されます

### 評価の保存プロセス
1. ユーザーがワインを評価すると、以下の情報が保存されます：
   - 評価対象のワインID
   - 評価値（1-5）
   - 評価日時

2. 同じワインに対する再評価の場合：
   - 既存の評価レコードを更新
   - 評価値を新しい値に更新
   - 評価日時を現在時刻に更新

3. 評価データの利用：
   - レコメンデーションの計算に使用
   - ユーザーの好み分析に使用
   - 評価履歴の表示に使用

## 特徴量間の関係

ワインの特徴量には以下のような関係性があります：

1. **甘さとタンニンの関係**:
   - 甘さが高いワインは通常タンニンが控えめ
   - タンニンが強いワインは通常辛口
   - この逆相関関係は好みの計算に反映されます

2. **酸味とボディの関係**:
   - 高い酸味は軽めのボディと相性が良い
   - フルボディのワインは適度な酸味とバランスを取る
   - この相関関係も考慮されます

3. **タンニンとボディの関係**:
   - 強いタンニンはフルボディと親和性が高い
   - ライトボディには穏やかなタンニンが適している

## レコメンデーションアルゴリズム

特徴量間の関係を考慮するため、マハラノビス距離を使用しています：

```python
# すべてのワインから特徴量間の相関を学習
covariance = np.cov([
    [wine.acidity, wine.tannin, wine.body, wine.sweetness]
    for wine in all_wines
])

# 専門家の知識による重み付け
weights = [1.5, 1.5, 1.0, 1.0]  # 酸味、タンニン、ボディ、甘さ
weighted_covariance = covariance * weights * weights.T

# 類似度計算（特徴量間の関係を考慮）
diff = user_features - wine_features
similarity = 1 / (1 + sqrt(diff @ inv(weighted_covariance) @ diff))
```

この方法により：
- 特徴量間の自然な関係性を反映
- 専門家の知識による重み付けも考慮
- より現実的なレコメンデーションを実現

## 具体例

1. **赤ワインの場合**:
   - タンニンと酸味が高いユーザーには、同様の特徴を持つ他の赤ワインを推薦
   - ただし、これらの特徴は通常セットで変化するため、その相関を考慮

2. **白ワインの場合**:
   - 酸味と甘さのバランスを重視
   - ボディの好みに応じて適切な組み合わせを推薦

3. **ロゼワインの場合**:
   - 赤ワインと白ワインの特徴のバランスを考慮
   - 特徴量間の中間的な関係性を反映

## 使用方法

1. **ワインの検索と評価**
   - 検索バーでワインを検索
   - ワインを選択して星評価（1-5）を付ける
   - 「評価を送信」をクリック

2. **好みの分析**
   - レーダーチャートで自分の好みを確認
   - 酸味、タンニン、ボディ、甘さの4要素で表示

3. **レコメンデーション**
   - 評価したワインに基づいて類似のワインを推薦
   - 各ワインの詳細情報を確認可能

4. **評価履歴**
   - 過去に評価したワインの一覧を表示
   - 評価日、評価点数、ワイン情報を確認可能

## トラブルシューティング

### よくある問題と解決方法

1. データベース接続エラー
   - `.env`ファイルの設定を確認
   - MySQLサービスが起動しているか確認

2. インポートエラー
   - Conda環境が有効化されているか確認
   - 必要なパッケージがインストールされているか確認

3. アプリケーションが起動しない
   - ポート5000が使用可能か確認
   - 必要なパッケージがすべてインストールされているか確認

## 開発者向け情報

### プロジェクト構造

```
wine-preference-app/
├── app.py              # メインアプリケーション
├── import_data.py      # データインポートスクリプト
├── requirements.txt    # 依存パッケージ
├── .env               # 環境変数
├── migrations/        # データベースマイグレーション
├── templates/         # HTMLテンプレート
│   └── index.html    # メインページ
└── wine_info.csv     # ワインデータ
```

### データベーススキーマ

**Wines テーブル**
- id: 主キー
- name: ワイン名
- variety: 主要品種
- variety_sub1: 副品種1
- variety_sub2: 副品種2
- price: 価格
- vintage: 製造年
- wine_type: ワインタイプ
- acidity: 酸味
- tannin: タンニン
- body: ボディ
- sweetness: 甘さ

**UserPreferences テーブル**
- id: 主キー
- wine_id: ワインID（外部キー）
- rating: 評価（1-5）
- rated_at: 評価日時
