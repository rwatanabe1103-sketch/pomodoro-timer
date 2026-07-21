#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アウトライン化済みA5データから「安全余白版」の元データを生成。
- 仕上がり内の内容を s=0.95 に縮小して安全余白を確保
- 端は edge-extend（端ピクセル複製）で塗り足しを自動生成（帯は端まで届く見た目を維持）
- 出力は各ページ画像化した source_safe.pdf（154.178x215.9mm = A5+3mm bleed）
"""
import fitz, numpy as np
from PIL import Image
import io

SRC = "/tmp/claude-0/-home-user-pomodoro-timer/8cc6f76a-b99e-517d-9eaf-a5998afa9cc3/scratchpad/source_outlined.pdf"
OUT = "/tmp/claude-0/-home-user-pomodoro-timer/8cc6f76a-b99e-517d-9eaf-a5998afa9cc3/scratchpad/source_safe.pdf"
MM = 72.0/25.4
DPI = 400
S = 0.95            # 内容の縮小率
BLEED = 3.0         # mm

src = fitz.open(SRC)
out = fitz.open()

for pno in range(src.page_count):
    pg = src[pno]
    W_pt, H_pt = pg.rect.width, pg.rect.height
    W_mm, H_mm = W_pt/MM, H_pt/MM
    px_per_mm = DPI/25.4
    # ページ全体をレンダリング（ロゴ等が仕上がり線より下にあっても切らない）
    pix = pg.get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
    art = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].copy()
    Ah, Aw = art.shape[0], art.shape[1]
    # 元データの塗り足し不良を、仕上がり線(3mm inset)の色で補修（左・右・上のみ。下はロゴを残す）
    tl = int(round(BLEED*px_per_mm)); tr = Aw - tl
    tt = int(round(BLEED*px_per_mm))
    art[:, tr:, :] = art[:, tr-1:tr, :]     # 右塗り足し：仕上がり線の色で延長
    art[:, :tl, :] = art[:, tl:tl+1, :]     # 左塗り足し
    art[:tt, :, :] = art[tt:tt+1, :, :]     # 上塗り足し
    fin = Image.fromarray(art, "RGB")
    CW = int(round(W_mm*px_per_mm)); CH = int(round(H_mm*px_per_mm))
    # ページ全体を S 縮小（ロゴも一律縮小され、仕上がり線から余白ができる）
    cw = max(1,int(round(fin.width*S))); ch = max(1,int(round(fin.height*S)))
    scaled = fin.resize((cw, ch), Image.LANCZOS)
    sc = np.asarray(scaled)
    # キャンバス中央に配置（縮小で空いた縁は端ピクセル延長で塗り足し生成）
    ox = int(round((CW - cw)/2.0))
    oy = int(round((CH - ch)/2.0))
    ys = np.clip(np.arange(CH)-oy, 0, ch-1)
    xs = np.clip(np.arange(CW)-ox, 0, cw-1)
    canvas = sc[ys][:, xs].copy()
    img = Image.fromarray(canvas, "RGB")
    # JPEGにしてPDFへ
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=92); buf.seek(0)
    np_page = out.new_page(width=W_pt, height=H_pt)
    np_page.insert_image(np_page.rect, stream=buf.getvalue())
    print(f"page{pno+1}: canvas {CW}x{CH}px  content {cw}x{ch}px offset({ox},{oy})")

out.save(OUT, deflate=True)
print("saved", OUT)
