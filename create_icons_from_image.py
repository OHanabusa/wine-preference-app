from PIL import Image
import os

def create_mac_icons(source_image_path):
    # アイコンセットのディレクトリを作成
    iconset_path = 'static/icon.iconset'
    if not os.path.exists(iconset_path):
        os.makedirs(iconset_path)
    
    # 元の画像を開く
    with Image.open(source_image_path) as img:
        # PNGに変換
        if img.format != 'PNG':
            img = img.convert('RGBA')
        
        # 必要なサイズのアイコンを生成
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            # 通常サイズ
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(f'{iconset_path}/icon_{size}x{size}.png')
            
            # Retinaディスプレイ用（2倍サイズ）
            if size <= 512:
                size_2x = size * 2
                resized_2x = img.resize((size_2x, size_2x), Image.Resampling.LANCZOS)
                resized_2x.save(f'{iconset_path}/icon_{size}x{size}@2x.png')

if __name__ == '__main__':
    source_image = 'static/icon.iconset/Wine App Icon Large.png'
    create_mac_icons(source_image)
