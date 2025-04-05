"""
Wine Preference Appのデスクトップアプリケーション化スクリプト
"""
import sys
from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = [
        'app.py',                      # メインスクリプト
        '--onefile',                   # 単一の実行ファイルにする
        '--windowed',                  # GUIアプリケーションとして実行
        '--add-data=templates:templates',  # テンプレートフォルダを含める
        '--add-data=static:static',    # 静的ファイルを含める
        '--icon=static/icon.icns',     # アプリケーションアイコン
        '--name=WinePreference',       # アプリケーション名
    ]
    
    run(opts)
