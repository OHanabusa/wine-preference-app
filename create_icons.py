from PIL import Image, ImageDraw
import os

def create_wine_icon(size):
    # 新しい画像を作成（背景を透明に）
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # ワイングラスの色
    glass_color = (114, 47, 55)    # ダークレッド
    wine_color = (168, 36, 62)     # ワインレッド
    
    # サイズに基づくパラメータ
    stem_width = size // 8
    bowl_width = size // 2
    bowl_height = size * 2 // 3
    stem_height = size // 4
    base_width = size // 2
    base_height = size // 12
    
    # グラスの上部（ボウル）
    bowl_top = size // 6
    bowl_left = (size - bowl_width) // 2
    draw.ellipse(
        [(bowl_left, bowl_top),
         (bowl_left + bowl_width, bowl_top + bowl_height)],
        fill=glass_color
    )
    
    # ワイン
    wine_top = bowl_top + bowl_height // 4
    draw.ellipse(
        [(bowl_left + 4, wine_top),
         (bowl_left + bowl_width - 4, bowl_top + bowl_height - 4)],
        fill=wine_color
    )
    
    # 脚
    stem_left = (size - stem_width) // 2
    stem_top = bowl_top + bowl_height - 4
    draw.rectangle(
        [(stem_left, stem_top),
         (stem_left + stem_width, stem_top + stem_height)],
        fill=glass_color
    )
    
    # 台座
    base_left = (size - base_width) // 2
    base_top = stem_top + stem_height - 2
    draw.ellipse(
        [(base_left, base_top),
         (base_left + base_width, base_top + base_height)],
        fill=glass_color
    )
    
    return image

def create_mac_icons():
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    iconset_path = 'static/icon.iconset'
    
    if not os.path.exists(iconset_path):
        os.makedirs(iconset_path)
    
    for size in sizes:
        icon = create_wine_icon(size)
        # 通常サイズ
        icon.save(f'{iconset_path}/icon_{size}x{size}.png')
        # Retinaディスプレイ用（サイズの2倍）
        if size <= 512:
            icon_2x = create_wine_icon(size * 2)
            icon_2x.save(f'{iconset_path}/icon_{size}x{size}@2x.png')

if __name__ == '__main__':
    create_mac_icons()
