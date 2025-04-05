#!/bin/bash

# アプリケーションのディレクトリに移動
cd "$(dirname "$0")"

# クリーンアップ関数
cleanup() {
    if [ -f .app.pid ]; then
        pid=$(cat .app.pid)
        kill $pid 2>/dev/null
        rm .app.pid
    fi
    exit 0
}

# 強制クリーンアップ関数
force_cleanup() {
    if lsof -i:5000 > /dev/null 2>&1; then
        echo "Forcing cleanup of port 5000..."
        sudo lsof -i:5000 -t | xargs kill -9 2>/dev/null
    fi
    rm -f .app.pid
}

# シグナルハンドラーを設定
trap cleanup SIGINT SIGTERM

# 既存のプロセスをチェック
if [ -f .app.pid ]; then
    pid=$(cat .app.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "Application is already running (PID: $pid)"
        open http://127.0.0.1:5000
        exit 0
    else
        # 古いPIDファイルを削除
        rm .app.pid
    fi
fi

# ポート5000が使用中かチェック
if lsof -i:5000 > /dev/null 2>&1; then
    echo "Port 5000 is in use. Attempting to clean up..."
    force_cleanup
    sleep 2
fi

# 仮想環境が存在する場合はアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# MySQLが起動していることを確認
if ! pgrep mysqld > /dev/null; then
    echo "Starting MySQL..."
    mysql.server start
    sleep 2  # MySQLの起動を待つ
fi

# アプリケーションを起動（ターミナル出力を非表示）
python app.py > /dev/null 2>&1 &

# プロセスIDを保存
echo $! > .app.pid

# 少し待ってからブラウザを開く
sleep 2
open http://127.0.0.1:5000

# プロセスが終了するまで待機
wait
