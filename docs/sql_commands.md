# MySQL基本コマンドリファレンス

## データベース操作

### データベースの一覧と選択
```sql
-- データベース一覧の表示
SHOW DATABASES;

-- データベースの選択
USE database_name;

-- 現在のデータベースを表示
SELECT DATABASE();
```

### テーブル操作
```sql
-- テーブル一覧の表示
SHOW TABLES;

-- テーブルの構造を表示
DESCRIBE table_name;
SHOW COLUMNS FROM table_name;

-- テーブルの作成
CREATE TABLE table_name (
    column1 datatype,
    column2 datatype,
    ...
);

-- テーブルの削除
DROP TABLE table_name;

-- テーブル名の変更
RENAME TABLE old_name TO new_name;
```

## データ操作

### データの取得
```sql
-- 全てのカラムを取得
SELECT * FROM table_name;

-- 特定のカラムを取得
SELECT column1, column2 FROM table_name;

-- 条件付き取得
SELECT * FROM table_name WHERE condition;

-- ソート
SELECT * FROM table_name ORDER BY column_name ASC;  -- 昇順
SELECT * FROM table_name ORDER BY column_name DESC; -- 降順

-- 件数制限
SELECT * FROM table_name LIMIT 10;

-- 重複を除外
SELECT DISTINCT column_name FROM table_name;
```

### データの追加・更新・削除
```sql
-- データの追加
INSERT INTO table_name (column1, column2) VALUES (value1, value2);

-- データの更新
UPDATE table_name SET column1 = value1 WHERE condition;

-- データの削除
DELETE FROM table_name WHERE condition;

-- テーブルの全データを削除
TRUNCATE TABLE table_name;
```

### 集計・グループ化
```sql
-- 件数のカウント
SELECT COUNT(*) FROM table_name;
SELECT COUNT(column_name) FROM table_name;

-- グループ化
SELECT column_name, COUNT(*) 
FROM table_name 
GROUP BY column_name;

-- 合計
SELECT SUM(column_name) FROM table_name;

-- 平均
SELECT AVG(column_name) FROM table_name;

-- 最大・最小
SELECT MAX(column_name) FROM table_name;
SELECT MIN(column_name) FROM table_name;
```

### 結合
```sql
-- 内部結合
SELECT * 
FROM table1 
INNER JOIN table2 
ON table1.column = table2.column;

-- 左結合
SELECT * 
FROM table1 
LEFT JOIN table2 
ON table1.column = table2.column;

-- 右結合
SELECT * 
FROM table1 
RIGHT JOIN table2 
ON table1.column = table2.column;
```

## その他の操作

### インデックス
```sql
-- インデックスの作成
CREATE INDEX index_name ON table_name (column_name);

-- インデックスの削除
DROP INDEX index_name ON table_name;

-- テーブルのインデックス一覧
SHOW INDEX FROM table_name;
```

### ユーザー管理
```sql
-- ユーザーの作成
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';

-- 権限の付与
GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';

-- 権限の確認
SHOW GRANTS FOR 'username'@'localhost';

-- 権限の反映
FLUSH PRIVILEGES;
```

### バックアップとリストア
```sql
-- データベースのバックアップ（コマンドライン）
mysqldump -u username -p database_name > backup.sql

-- データベースのリストア（コマンドライン）
mysql -u username -p database_name < backup.sql
```

## MySQLクライアントコマンド

### ヘルプと情報表示
```sql
-- ヘルプの表示
\h
help

-- コマンド一覧の表示
\?

-- ステータスの表示（現在のデータベース、接続情報など）
\s
status
```

### 接続関連
```sql
-- MySQLクライアントの終了
\q
quit
exit

-- データベースを変更
\u database_name
use database_name

-- ホストに接続
\r
connect
```

### クエリ実行
```sql
-- クエリの区切り文字を変更（デフォルトは;）
delimiter //

-- クエリの実行をクリア
\c

-- 前回実行したクエリを再実行
\g
```

### 出力制御
```sql
-- 出力を縦方向に表示
\G

-- 出力をファイルに保存
tee filename.txt
\T filename.txt

-- ファイルへの出力を停止
notee
\t

-- SQLの実行結果をファイルに出力
SELECT * FROM table_name INTO OUTFILE 'filename.csv' 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n';
```

### スクリプト実行
```sql
-- SQLファイルを実行
source filename.sql
\. filename.sql

-- バッチモードでクエリを実行（エラーがあっても続行）
\. filename.sql
```

### 編集
```sql
-- 直前のコマンドを編集
\e

-- SQLファイルを編集
edit filename.sql
```

## トラブルシューティング

### 一般的なエラー
- Table doesn't exist: テーブル名が間違っているか、存在しない
- Access denied: 権限が不足している
- Duplicate entry: 一意制約に違反している
- Syntax error: SQL構文が間違っている

### デバッグ用コマンド
```sql
-- MySQLのバージョン確認
SELECT VERSION();

-- 現在のユーザーを確認
SELECT CURRENT_USER();

-- プロセスリストの確認
SHOW PROCESSLIST;

-- テーブルのステータス確認
SHOW TABLE STATUS;
