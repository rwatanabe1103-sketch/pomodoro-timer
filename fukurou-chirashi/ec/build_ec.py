#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64, io, os
from PIL import Image
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "src")
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

def b64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

def b64_up(path, target_long=1200):
    """元画像を高品質に拡大(不足時のみ)＋軽くシャープ化して返す"""
    from PIL import ImageFilter
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    s = target_long / max(w, h)
    if s > 1:
        im = im.resize((round(w*s), round(h*s)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2.0, percent=80, threshold=2))
    buf = io.BytesIO(); im.save(buf, format="PNG"); buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

A = {
 "id":"A","type":"TYPE A","code":"774-01","name":"アイビーのリース仕立て",
 "price":"3,480","s1":"全体の高さ 約30cm","s2":"丸い鉢・直径 約13cm",
 "catch":"アーチを描く葉が涼やか。枝にとまる2羽のフクロウがアクセント。",
 "ftitle":"枝にとまる、2羽のフクロウ",
 "points":[("リース仕立て","アーチを描くアイビーの葉が涼やか。"),
           ("2羽のフクロウ","枝にちょこんと。物語のワンシーンのよう。"),
           ("明るい窓辺に","光を受けて葉がいきいきと映えます。")],
 "prod":b64_up(f"{SRC}/prodA.png",1300),"owl":b64_up(f"{SRC}/owlA.png",760),
}
B = {
 "id":"B","type":"TYPE B","code":"774-02","name":"ガジュマル ― 多幸の木",
 "price":"3,480","s1":"全体の高さ 約25cm","s2":"丸い鉢・直径 約10cm",
 "catch":"ぷっくりした幹が愛らしい“幸せを呼ぶ木”。丈夫で育てやすい。",
 "ftitle":"多幸の木に寄り添う、2羽のフクロウ",
 "points":[("多幸の木","“幸せを呼ぶ木”と親しまれるガジュマル。"),
           ("育てやすい","丈夫で、はじめての一鉢にもおすすめ。"),
           ("愛らしい幹","ぷっくりした幹に2羽が寄り添います。")],
 "prod":b64_up(f"{SRC}/prodB.png",1300),"owl":b64_up(f"{SRC}/owlB.png",760),
}
C = {
 "id":"C","type":"TYPE C","code":"774-03","name":"サボテンの寄せ植え",
 "price":"2,980","s1":"全体の高さ 約10cm前後","s2":"横長の鉢・幅20×奥行5cm",
 "catch":"サボテンを横長鉢に。水やりは少なめでOK。小さな砂漠の景色。",
 "ftitle":"小さな砂漠に、2羽のフクロウ",
 "points":[("横長鉢の寄せ植え","数種のサボテンを一鉢に。"),
           ("水やり少なめ","乾燥に強く、お手入れかんたん。"),
           ("小さな景色","フクロウと並ぶ砂漠のワンシーン。")],
 "prod":b64_up(f"{SRC}/prodC.png",1300),"owl":b64_up(f"{SRC}/owlC.png",760),
}
PRODUCTS=[A,B,C]

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--green:#2a4531;--green2:#35543f;--cream:#ece5d3;--creamlt:#f5f0e4;
--terra:#b06a3c;--gold:#b0a06a;--price:#b25e2c;--ink:#39382f}
.canvas{width:1200px;height:1200px;position:relative;overflow:hidden;
font-family:'Noto Sans CJK JP',sans-serif;color:var(--ink)}
.mincho{font-family:'Noto Serif CJK JP',serif}
/* ---------- MAIN (価格なし・商品大きめ) ---------- */
.main{background:radial-gradient(120% 100% at 50% 40%,#f7f2e7 0%,#efe8d8 55%,#e7dfcc 100%)}
.main .circle{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
width:960px;height:960px;border-radius:50%;
background:radial-gradient(circle,#e5ead9 0%,#e5ead9 56%,rgba(229,234,217,0) 72%)}
.main .brand{position:absolute;top:54px;left:0;right:0;text-align:center;
color:var(--gold);letter-spacing:.34em;font-size:27px;font-weight:600}
.main .brand span{display:inline-block;padding:0 24px;position:relative}
.main .brand span:before,.main .brand span:after{content:"";position:absolute;top:50%;
width:64px;height:1px;background:var(--gold);opacity:.7}
.main .brand span:before{right:100%}.main .brand span:after{left:100%}
.main .product{position:absolute;left:50%;top:47%;transform:translate(-50%,-50%);
width:1060px;height:940px;object-fit:contain;filter:drop-shadow(0 28px 28px rgba(60,50,30,.20))}
.main .foot{position:absolute;left:0;right:0;bottom:56px;text-align:center}
.main .badge{display:inline-block;background:var(--green);color:#f2ead8;
font-size:26px;letter-spacing:.2em;padding:9px 26px;border-radius:24px;margin-bottom:22px;font-weight:600}
.main .pname{font-size:72px;color:var(--green);font-weight:600;letter-spacing:.03em;line-height:1.1}
/* ---------- FEATURE (余白少なめ・大きめ) ---------- */
.feat{background:var(--creamlt)}
.feat .head{height:196px;background:var(--green);color:#f4ecd9;
display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative}
.feat .head .sub{color:var(--gold);letter-spacing:.3em;font-size:24px;font-weight:600;margin-bottom:12px}
.feat .head .ft{font-size:60px;font-weight:600;letter-spacing:.04em}
.feat .body{position:absolute;top:196px;left:0;right:0;bottom:64px;display:flex}
.feat .col-img{width:552px;position:relative;flex:none;display:flex;align-items:center;justify-content:center}
.feat .col-img .prod{width:540px;height:756px;object-fit:contain;
filter:drop-shadow(0 22px 24px rgba(60,50,30,.18))}
.feat .owl{position:absolute;right:2px;bottom:34px;width:266px;height:266px;border-radius:50%;
object-fit:cover;border:8px solid #fff;box-shadow:0 14px 26px rgba(60,50,30,.24)}
.feat .owl-cap{position:absolute;right:16px;bottom:6px;background:var(--terra);color:#fff;
font-size:22px;font-weight:700;padding:6px 18px;border-radius:16px;letter-spacing:.06em}
.feat .col-txt{flex:1;padding:26px 54px 22px 10px;display:flex;flex-direction:column;justify-content:space-evenly}
.feat .pt{display:flex;align-items:flex-start;margin-bottom:0}
.feat .pt .no{font-family:'Noto Serif CJK JP',serif;color:var(--terra);font-size:54px;
font-weight:700;line-height:1;margin-right:24px;min-width:64px}
.feat .pt .lab{font-size:42px;color:var(--green);font-weight:700;margin-bottom:10px;letter-spacing:.02em;line-height:1.15}
.feat .pt .txt{font-size:28px;color:#54514a;line-height:1.5}
.feat .spec{margin-top:8px;display:flex;gap:14px;flex-wrap:wrap}
.feat .spec .chip{background:#fff;border:2px solid #d8cdb2;border-radius:14px;
padding:12px 22px;font-size:26px;color:var(--green);font-weight:700}
.feat .note{position:absolute;left:0;right:0;bottom:0;height:64px;background:#e6ddc7;color:#6a6555;
font-size:20px;display:flex;align-items:center;justify-content:center;padding:0 30px;
text-align:center;letter-spacing:.01em}
"""

def main_html(p):
    return f"""<div class="canvas main">
  <div class="circle"></div>
  <div class="brand"><span>FUKURŌ &#10005; INTERIOR GREEN</span></div>
  <img class="product" src="{p['prod']}">
  <div class="foot">
    <div class="badge">{p['type']}</div>
    <div class="pname mincho">{p['name']}</div>
  </div>
</div>"""

def feat_html(p):
    pts=""
    for i,(lab,txt) in enumerate(p["points"],1):
        pts+=f'<div class="pt"><div class="no">0{i}</div><div><div class="lab">{lab}</div><div class="txt">{txt}</div></div></div>'
    return f"""<div class="canvas feat">
  <div class="head">
    <div class="sub">POINT</div>
    <div class="ft mincho">{p['ftitle']}</div>
  </div>
  <div class="body">
    <div class="col-img">
      <img class="prod" src="{p['prod']}">
      <img class="owl" src="{p['owl']}">
      <div class="owl-cap">2羽のフクロウ</div>
    </div>
    <div class="col-txt">
      {pts}
      <div class="spec"><span class="chip">{p['s1']}</span><span class="chip">{p['s2']}</span></div>
    </div>
  </div>
  <div class="note">※植物・フィギュアには個体差があり、形状やデザインが異なる場合があります。</div>
</div>"""

def page(inner):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{inner}</body></html>"

def run():
    jobs=[]
    for p in PRODUCTS:
        jobs.append((f"{p['id']}_1_main", main_html(p)))
        jobs.append((f"{p['id']}_2_feature", feat_html(p)))
    with sync_playwright() as pw:
        br=pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",args=["--force-color-profile=srgb","--no-sandbox"])
        pg=br.new_page(viewport={"width":1200,"height":1200},device_scale_factor=2)
        for name,inner in jobs:
            pg.set_content(page(inner), wait_until="networkidle")
            pg.wait_for_timeout(150)
            png=pg.screenshot(clip={"x":0,"y":0,"width":1200,"height":1200})
            im=Image.open(io.BytesIO(png))            # 2400x2400
            im=im.resize((1200,1200), Image.LANCZOS)  # supersample down
            out=os.path.join(OUT,f"TYPE{name}.png")
            im.save(out)
            print("saved",out,im.size)
        br.close()

if __name__=="__main__":
    run()
