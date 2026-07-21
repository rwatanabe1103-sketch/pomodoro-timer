#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フクロウチラシ A5(表裏) を A4横に2面付けした両面入稿データを作成する。
方式: 各A5ページを CropBox で「内側(中央)の塗り足しを除いた版」に分割し、
      中央でぴったり突き合わせ(隙間・重なりなし)、外周は塗り足しを残す。
"""
import fitz

SRC = "/root/.claude/uploads/8cc6f76a-b99e-517d-9eaf-a5998afa9cc3/7ddc35a2-________A5_________.pdf"
OUT = "/tmp/claude-0/-home-user-pomodoro-timer/8cc6f76a-b99e-517d-9eaf-a5998afa9cc3/scratchpad/フクロウチラシ_A4面付_両面_入稿用.pdf"
MM = 72.0 / 25.4

def mm(v): return v * MM

# レイアウト(mm)
FIN_W, FIN_H = 297.0, 210.0
BLEED = 3.0
MARK = 8.0
MARGIN = BLEED + MARK           # 11

CANVAS_W = FIN_W + 2 * MARGIN    # 319
CANVAS_H = FIN_H + 2 * MARGIN    # 232
FL, FT = MARGIN, MARGIN
FR, FB = MARGIN + FIN_W, MARGIN + FIN_H
CX = FL + FIN_W / 2.0            # 159.5
BL, BT, BR, BB = FL - BLEED, FT - BLEED, FR + BLEED, FB + BLEED

src = fitz.open(SRC)
sp = src[0].rect
SRC_W = sp.width / MM
SRC_H = sp.height / MM
STL, STT = 3.0, 3.0                    # source trim inset
STR, STB = SRC_W - 3.0, SRC_H - 3.0

def cropped_doc(pno, side):
    """side 'L': 右(内側)塗り足しを落とす / 'R': 左(内側)塗り足しを落とす"""
    tmp = fitz.open()
    tmp.insert_pdf(src, from_page=pno, to_page=pno)
    pg = tmp[0]
    if side == 'L':
        cb = fitz.Rect(0, 0, mm(STR), mm(SRC_H))          # x:0..151.178
    else:
        cb = fitz.Rect(mm(STL), 0, mm(SRC_W), mm(SRC_H))  # x:3..154.178
    pg.set_cropbox(cb)
    return tmp

def place(page, pno, side):
    doc = cropped_doc(pno, side)
    # 水平マッピング: source trim(STL..STR) -> finished
    if side == 'L':
        fx0, fx1 = FL, CX
    else:
        fx0, fx1 = CX, FR
    sx = (fx1 - fx0) / (STR - STL)
    # cropbox の左右端(source座標)
    cxl = 0.0 if side == 'L' else STL
    cxr = STR if side == 'L' else SRC_W
    tx0 = fx0 + (cxl - STL) * sx
    tx1 = fx0 + (cxr - STL) * sx
    # 垂直: trim(STT..STB)->(FT..FB); cropbox は上下フル(0..SRC_H)
    sy = (FB - FT) / (STB - STT)
    ty0 = FT + (0.0 - STT) * sy
    ty1 = FT + (SRC_H - STT) * sy
    target = fitz.Rect(mm(tx0), mm(ty0), mm(tx1), mm(ty1))
    page.show_pdf_page(target, doc, 0, keep_proportion=False)

def draw_marks(page):
    black = (0, 0, 0); w = 0.3
    def line(x0, y0, x1, y1):
        page.draw_line(fitz.Point(mm(x0), mm(y0)), fitz.Point(mm(x1), mm(y1)),
                       color=black, width=w)
    corners = [(FL, FT, -1, -1), (FR, FT, +1, -1), (FL, FB, -1, +1), (FR, FB, +1, +1)]
    for x, y, sxg, syg in corners:
        line(x, y + syg * BLEED, x, y + syg * (BLEED + MARK))
        line(x + sxg * BLEED, y, x + sxg * (BLEED + MARK), y)
    # センター断裁ガイド(上下)
    line(CX, BT - MARK, CX, BT)
    line(CX, BB, CX, BB + MARK)

out = fitz.open()
for pno in range(2):
    page = out.new_page(width=mm(CANVAS_W), height=mm(CANVAS_H))
    place(page, pno, 'L')
    place(page, pno, 'R')
    draw_marks(page)

out.set_metadata({"title": "フクロウチラシ A4 2面付け 両面 入稿用"})
out.save(OUT, garbage=4, deflate=True)
print("saved:", OUT)
o = fitz.open(OUT)
for i in range(o.page_count):
    r = o[i].rect
    print(f"page{i+1}: {r.width/MM:.2f} x {r.height/MM:.2f} mm")
