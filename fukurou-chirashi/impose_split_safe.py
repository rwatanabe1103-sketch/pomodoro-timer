#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フクロウチラシ A5(表裏) を A4横2面付け。表/裏を別ファイルで出力。
トンボあり版(319x232) と トンボなし版(303x216) の両方を生成する。
"""
import fitz

SRC = "/tmp/claude-0/-home-user-pomodoro-timer/8cc6f76a-b99e-517d-9eaf-a5998afa9cc3/scratchpad/source_safe.pdf"
OUTDIR = "/tmp/claude-0/-home-user-pomodoro-timer/8cc6f76a-b99e-517d-9eaf-a5998afa9cc3/scratchpad/"
MM = 72.0 / 25.4
def mm(v): return v * MM

FIN_W, FIN_H = 297.0, 210.0
BLEED = 3.0
MARK = 8.0

src = fitz.open(SRC)
sp = src[0].rect
SRC_W = sp.width / MM
SRC_H = sp.height / MM
STL, STT = 3.0, 3.0
STR, STB = SRC_W - 3.0, SRC_H - 3.0

def cropped_doc(pno, side):
    tmp = fitz.open()
    tmp.insert_pdf(src, from_page=pno, to_page=pno)
    pg = tmp[0]
    if side == 'L':
        pg.set_cropbox(fitz.Rect(0, 0, mm(STR), mm(SRC_H)))
    else:
        pg.set_cropbox(fitz.Rect(mm(STL), 0, mm(SRC_W), mm(SRC_H)))
    return tmp

def build(pno, with_marks, out):
    MARGIN = (BLEED + MARK) if with_marks else BLEED
    CW = FIN_W + 2 * MARGIN
    CH = FIN_H + 2 * MARGIN
    FL, FT = MARGIN, MARGIN
    FR, FB = MARGIN + FIN_W, MARGIN + FIN_H
    CX = FL + FIN_W / 2.0
    BL, BT, BR, BB = FL - BLEED, FT - BLEED, FR + BLEED, FB + BLEED

    out_doc = fitz.open()
    page = out_doc.new_page(width=mm(CW), height=mm(CH))

    def place(side):
        doc = cropped_doc(pno, side)
        if side == 'L':
            fx0, fx1 = FL, CX
            cxl, cxr = 0.0, STR
        else:
            fx0, fx1 = CX, FR
            cxl, cxr = STL, SRC_W
        sx = (fx1 - fx0) / (STR - STL)
        tx0 = fx0 + (cxl - STL) * sx
        tx1 = fx0 + (cxr - STL) * sx
        sy = (FB - FT) / (STB - STT)
        ty0 = FT + (0.0 - STT) * sy
        ty1 = FT + (SRC_H - STT) * sy
        page.show_pdf_page(fitz.Rect(mm(tx0), mm(ty0), mm(tx1), mm(ty1)),
                           doc, 0, keep_proportion=False)

    place('L')
    place('R')

    if with_marks:
        black = (0, 0, 0); w = 0.3
        def line(x0, y0, x1, y1):
            page.draw_line(fitz.Point(mm(x0), mm(y0)), fitz.Point(mm(x1), mm(y1)),
                           color=black, width=w)
        for x, y, sxg, syg in [(FL, FT, -1, -1), (FR, FT, +1, -1),
                               (FL, FB, -1, +1), (FR, FB, +1, +1)]:
            line(x, y + syg * BLEED, x, y + syg * (BLEED + MARK))
            line(x + sxg * BLEED, y, x + sxg * (BLEED + MARK), y)
        line(CX, BT - MARK, CX, BT)
        line(CX, BB, CX, BB + MARK)

    out_doc.save(out, garbage=4, deflate=True)
    r = fitz.open(out)[0].rect
    print(f"{out.split('/')[-1]}: {r.width/MM:.1f}x{r.height/MM:.1f}mm")

sides = [(0, 'omote'), (1, 'ura')]
for pno, name in sides:
    build(pno, True,  OUTDIR + f"fukurou_A4menzuke_{name}_tombo_safe.pdf")
    build(pno, False, OUTDIR + f"fukurou_A4menzuke_{name}_notombo_safe.pdf")
