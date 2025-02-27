import fitz
from sort_by_reading_order import sort_by_reading_order

areas = [
    fitz.IRect(100,  20, 500,  60),   # 見出し1
    fitz.IRect( 50,  80, 150, 130),   # 本文1（3段組み）
    fitz.IRect(200,  80, 300, 130),   # 本文3
    fitz.IRect(350,  80, 450, 130),   # 本文4
    fitz.IRect(360, 140, 450, 150),   # 本文5
    fitz.IRect( 50, 140, 150, 150),   # 本文2
    
    fitz.IRect(100, 160, 500, 200),   # 見出し2
    fitz.IRect( 50, 220, 200, 270),   # 本文6（2段組み）
    fitz.IRect(250, 220, 400, 340),   # 本文8
    fitz.IRect( 45, 280, 160, 350),   # 本文7
]

sorted_areas = sort_by_reading_order(areas,550)
for i, rect in enumerate(sorted_areas, 1):
    print(f"{i}: {rect}")
