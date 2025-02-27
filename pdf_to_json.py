import sys
import json
import fitz
from multi_column import column_boxes  # 既存の column_boxes 関数をインポート
from sort_by_reading_order import sort_by_reading_order  # 既存の sort_by_reading_order 関数をインポート

def serialize_rect(rect):
    """fitz.IRect を JSON でシリアライズ可能な dict に変換する"""
    if rect is None:
        return None
    return {"x0": rect.x0, "y0": rect.y0, "x1": rect.x1, "y1": rect.y1}

def extract_pdf_structure(pdf_path, footer_margin=0, header_margin=0, no_image_text=False):
    """PDFの全ページを解析し、column_boxesを使用して構造を抽出しJSONに保存する
    構造: page → zone → block → line → span
    """
    doc = fitz.open(pdf_path)
    pdf_data = []

    for page_num, page in enumerate(doc):
        # カラム情報の取得
        zones = column_boxes(
            page,
            footer_margin=footer_margin,
            header_margin=header_margin,
            no_image_text=no_image_text,
        )
        # 見出しを考慮したソート
        reading_orderd_zones = sort_by_reading_order(zones, page.rect.width)
        # zones に固有番号を付与（1-based index）
        zones_with_id = [{"zone_number": i + 1, "rect": zone} for i, zone in enumerate(reading_orderd_zones)]
        print(f"Page {page_num + 1}: {len(zones_with_id)} zones")

        # zoneごとに初期構造を作成
        zone_map = {}
        for zone in zones_with_id:
            zone_map[zone["zone_number"]] = {
                "zone_number": zone["zone_number"],
                "rect": serialize_rect(zone["rect"]),
                "blocks": []
            }

        # ページごとのデータを格納
        page_data = {
            "page": page_num + 1,  # 1-based index
            "width": page.rect.width,
            "height": page.rect.height,
            "zones": list(zone_map.values())
        }

        # テキストブロックを取得
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            bbox = fitz.IRect(block["bbox"])  # ブロックの矩形座標

            # どのzoneに属するか確認
            matched_zone = None
            for zone in zones_with_id:
                if bbox in zone["rect"]:
                    matched_zone = zone["zone_number"]
                    break

            block_data = {
                "block_bbox": block["bbox"],
                "block_number": block.get("number", 0),
                "lines": []
            }

            span_total = 0
            for line in block.get("lines", []):
                line_spans = []
                for span in line.get("spans", []):
                    span_data = {
                        "span_bbox": span["bbox"],
                        "text": span["text"],
                        "font": span.get("font", ""),
                        "size": span.get("size", 0),
                        "color": span.get("color", [0, 0, 0]),
                        "alpha": span.get("alpha", 1),
                        "bold": bool(span.get("flags", 0) & fitz.TEXT_FONT_BOLD),
                        "italic": bool(span.get("flags", 0) & fitz.TEXT_FONT_ITALIC)
                    }
                    line_spans.append(span_data)
                if line_spans:
                    line_data = {
                        "line_bbox": line["bbox"],
                        "spans": line_spans
                    }
                    block_data["lines"].append(line_data)
                    span_total += len(line_spans)

            # spanが1つもないblockはスキップ
            if span_total == 0:
                continue

            # zoneに所属している場合はそのグループに追加
            if matched_zone is not None:
                zone_map[matched_zone]["blocks"].append(block_data)
            else:
                # zoneに属さないブロックは、例として zone "zone_number": 0 のグループにまとめる
                if 0 not in zone_map:
                    zone_map[0] = {"zone_number": 0, "rect": None, "blocks": []}
                    # ページ内の zones リストにも追加しておく
                    page_data["zones"].append(zone_map[0])
                zone_map[0]["blocks"].append(block_data)

        pdf_data.append(page_data)

    return pdf_data

if __name__ == "__main__":
    # コマンドライン引数からPDFファイル名を取得
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_structure.py input.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_json = pdf_path.replace(".pdf", "_structure.json")

    # PDF構造を抽出
    pdf_structure = extract_pdf_structure(pdf_path)

    # JSONに保存
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(pdf_structure, f, indent=2, ensure_ascii=False)

    print(f"Extracted structure saved to {output_json}")
