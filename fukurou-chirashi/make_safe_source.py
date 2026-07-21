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
    # 仕上がり(トリム=3mm inset)内の内容をレンダリング（左右/上は帯色が仕上がり線まで来ている）
    clip = fitz.Rect(BLEED*MM, BLEED*MM, (W_mm-BLEED)*MM, (H_mm-BLEED)*MM)
    pix = pg.get_pixmap(clip=clip, dpi=DPI, colorspace=fitz.csRGB)
    fin = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    px_per_mm = DPI/25.4
    CW = int(round(W_mm*px_per_mm)); CH = int(round(H_mm*px_per_mm))
    # 仕上がり内容を S 縮小
    cw = max(1,int(round(fin.width*S))); ch = max(1,int(round(fin.height*S)))
    scaled = fin.resize((cw, ch), Image.LANCZOS)
    sc = np.asarray(scaled)  # (ch,cw,3)
    # 仕上がり内で中央寄せ（bleed 分内側から配置）
    fin_x0 = BLEED*px_per_mm; fin_y0 = BLEED*px_per_mm
    ox = int(round(fin_x0 + (fin.width - cw)/2.0))
    oy = int(round(fin_y0 + (fin.height - ch)/2.0))
    # 上・左・右は端ピクセル延長（帯色が仕上がり線まであるので正しい色になる）
    ys = np.clip(np.arange(CH)-oy, 0, ch-1)
    xs = np.clip(np.arange(CW)-ox, 0, cw-1)
    canvas = sc[ys][:, xs].copy()  # (CH,CW,3)
    # 下端は中央にロゴ等があり端ピクセル延長だと尾引くため、
    # 下端の「背景色」（左右の角から採取。表=クリーム/裏=白）で塗り足す
    content_bottom = oy + ch
    strip = sc[max(0, ch-6):ch, :, :]
    ew = max(1, int(cw*0.06))
    bg_samples = np.vstack([strip[:, :ew, :].reshape(-1, 3),
                            strip[:, cw-ew:, :].reshape(-1, 3)])
    bg = np.median(bg_samples, axis=0).astype(np.uint8)
    canvas[content_bottom:, :, :] = bg
    img = Image.fromarray(canvas, "RGB")
    # JPEGにしてPDFへ
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=92); buf.seek(0)
    np_page = out.new_page(width=W_pt, height=H_pt)
    np_page.insert_image(np_page.rect, stream=buf.getvalue())
    print(f"page{pno+1}: canvas {CW}x{CH}px  content {cw}x{ch}px offset({ox},{oy})")

out.save(OUT, deflate=True)
print("saved", OUT)
