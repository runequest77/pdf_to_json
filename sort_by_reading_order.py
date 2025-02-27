import fitz
import math
import numpy as np

def detect_wide_zones(zones, page_width, wide_ratio=0.6):
    """
    広幅ゾーンを識別する。
    定義：
      - ページ内のゾーンの最大の横幅に対して大きな幅を持つ（デフォルト 60% 以上）
      - 他の本文より y0 の位置が独立している（周囲の本文と y の間隔が大きい）
    """
    wide_zones = []
    ## page_width 省略時はゾーンの最大幅を取得
    if page_width is None:
        page_width = max(b.x1 for b in zones)  # ページの最大幅

    for bbox in zones:
        bbox_width = bbox.x1 - bbox.x0
        if bbox_width / page_width > wide_ratio:  # ページの60%以上の幅を持つ
            wide_zones.append(bbox)

    return sorted(wide_zones, key=lambda b: b.y0)  # 広幅ゾーンを y0 順にソート

def detect_column_count(blocks, threshold=30):
    """
    ブロックの x0 座標から、ページ内の段組み数を推測する。
    - threshold: 同じカラムとみなす x0 の距離のしきい値
    """
    x_positions = sorted(set(b.x0 for b in blocks))  # x0 のリスト
    if len(x_positions) < 2:
        return 1  # 1段組み

    # クラスタリング（差分を計算）
    gaps = np.diff(x_positions)  # 隣接する x0 の差分
    column_count = 1 + sum(gap > threshold for gap in gaps)  # しきい値を超えるごとに段を増やす
    return column_count

def sort_by_reading_order(zones, page_width=None):
    """
    見出しを考慮し、各見出しごとに段組みの変化を反映しながらソートする。
    """
    if not zones:
        return []

    wide_zones = detect_wide_zones(zones, page_width)
    grouped_blocks = []
    remaining_blocks = sorted(zones, key=lambda b: (b.y0, b.x0))

    for zone in wide_zones:
        group = {"zone": zone, "blocks": []}
        for block in remaining_blocks[:]:  # コピーを作成してループ
            if block.y0 > zone.y0:  # 広幅ゾーンより下のものをグループ化
                group["blocks"].append(block)
                remaining_blocks.remove(block)

        # 段組み数を推測
        column_count = detect_column_count(group["blocks"])
        print(f"Detected {column_count} columns under wide zone {zone}")

        # 段組みに応じて並び替え
        sorted_blocks = []
        blocks = sorted(group["blocks"], key=lambda b: b.y0)  # 上から順に並べる
        columns = [[] for _ in range(column_count)]

        for block in blocks:
            # 最も近いカラムに分類
            column_index = np.argmin([abs(block.x0 - (columns[i][-1].x0 if columns[i] else 0)) for i in range(column_count)])
            columns[column_index].append(block)

        # 各カラムを行単位で再構築
        for row in zip(*[c for c in columns if c]):
            sorted_blocks.extend(row)

        group["blocks"] = sorted_blocks
        grouped_blocks.append(group)

    # フラットなリストとして返す
    sorted_blocks = []
    for group in grouped_blocks:
        sorted_blocks.append(group["zone"])  # 見出しを先に追加
        sorted_blocks.extend(group["blocks"])  # 本文を追加

    return sorted_blocks

