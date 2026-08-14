#!/usr/bin/env python3
"""Generate the נדל״ן נכון brand guide as one self-contained HTML page.

Logo SVGs are inlined and the brand typeface is embedded as a data URI, so the
page renders identically with no network access. Run after build_logo.py:

    python3 tools/build_brand_guide.py
"""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(ROOT, "brand", "logo", "svg")
FONT_DIR = os.path.join(ROOT, "brand", "fonts")
OUT = os.path.join(ROOT, "brand", "brand-guide.html")

SLATE, DEEP, TERRA, BONE = "#39414E", "#2E3540", "#D2703C", "#EAE7E1"


def svg(name, **attrs):
    """Inline an exported SVG, stripping its fixed width/height so CSS can size it."""
    with open(os.path.join(SVG_DIR, f"{name}.svg"), encoding="utf-8") as fh:
        markup = fh.read()
    markup = re.sub(r'\s(width|height)="[\d.]+"', "", markup, count=2)
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return markup.replace("<svg ", f"<svg {extra} ", 1)


def font_face(weight, family="Assistant"):
    with open(os.path.join(FONT_DIR, f"Assistant-{weight}.ttf"), "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")
    return (f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
            f"font-display:block;src:url(data:font/ttf;base64,{b64}) format('truetype');}}")


PALETTE = [
    ("צפחה", "Slate", SLATE, "צבע המותג הראשי. טקסט, קווים, ורקע כהה."),
    ("צפחה עמוקה", "Deep Slate", DEEP, "רקעים כהים גדולים, כשצריך שהלוגו יבלוט מעליהם."),
    ("טרקוטה", "Terracotta", TERRA, "אקסנט בלבד — הנקודה שבסוף השם. לא לטקסט רץ."),
    ("עצם", "Bone", BONE, "הלבן החם. טקסט ולוגו על רקע כהה."),
    ("אפור ביניים", "Muted", "#6B7583", "טקסט משני, תיאורים, הערות."),
]

FILES = [
    ("logo-horizontal-ondark.svg", "לוגו רוחבי, שקוף, לרקע כהה", "ראשי"),
    ("logo-horizontal-onlight.svg", "לוגו רוחבי, שקוף, לרקע בהיר", "ראשי"),
    ("logo-horizontal-dark.svg", "לוגו רוחבי על רקע צפחה מלא", "רשתות חברתיות"),
    ("logo-horizontal-light.svg", "לוגו רוחבי על רקע לבן מלא", "מסמכים"),
    ("logo-stacked-dark.svg / -light.svg", "גרסה מוערמת, שתי שורות", "פרופיל, חותמת"),
    ("logo-tagline-dark.svg / -light.svg", "עם שורת התיאור", "כרטיס ביקור, חתימת מייל"),
    ("logo-compact-onlight.svg / -ondark.svg", "גרסה מעובה לשימוש קטן", "מתחת ל‑200px"),
    ("logo-mono-black.svg / -white.svg", "צבע אחד, שחור או לבן", "דפוס, חריטה, פקס"),
    ("logo-mono-slate.svg / -bone.svg", "צבע אחד בגווני המותג", "רקע צבעוני"),
    ("icon-square-dark.svg", "אווטאר מרובע", "וואטסאפ, פייסבוק"),
    ("icon-circle-dark.svg", "אווטאר עגול", "אינסטגרם, גוגל"),
    ("icon-square-terra.svg / -light.svg", "אווטאר בגרסאות צבע נוספות", "ורייאציות"),
    ("favicon-512/180/48/32/16.svg", "אייקון אתר בכל הגדלים", "אתר"),
    ("logo-horizontal-editable.svg", "טקסט חי — נפתח בפלוני אם מותקן", "עריכה"),
]


def build():
    fonts = "".join(font_face(w) for w in (300, 400, 600))
    swatches = "".join(
        f'<div class="swatch"><div class="chip" style="background:{hexv}"></div>'
        f'<div class="chip-meta"><b>{he}</b><span class="mono">{hexv}</span>'
        f'<span class="en mono">{en}</span><p>{use}</p></div></div>'
        for he, en, hexv, use in PALETTE)

    rows = "".join(
        f'<tr><td class="mono file">{name}</td><td>{desc}</td>'
        f'<td class="use">{use}</td></tr>' for name, desc, use in FILES)

    html = f"""<title>ספר המותג נדל״ן נכון</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{fonts}
:root {{
  --slate:{SLATE}; --deep:{DEEP}; --terra:{TERRA}; --bone:{BONE};
  --ground:#F1F2F4; --surface:#FFFFFF; --line:#DCDFE4;
  --text:{SLATE}; --muted:#6B7583; --preview:#FFFFFF;
  --shadow:0 1px 2px rgba(46,53,64,.06), 0 8px 24px rgba(46,53,64,.05);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#252B34; --surface:{DEEP}; --line:#414A57;
    --text:{BONE}; --muted:#98A3B0; --preview:#E7E5E0;
    --shadow:0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.22);
  }}
}}
:root[data-theme="dark"] {{
  --ground:#252B34; --surface:{DEEP}; --line:#414A57;
  --text:{BONE}; --muted:#98A3B0; --preview:#E7E5E0;
  --shadow:0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.22);
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--ground); color:var(--text);
  font-family:'Assistant', system-ui, sans-serif; font-weight:400;
  line-height:1.65; direction:rtl; text-align:right;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:1080px; margin:0 auto; padding:0 24px 96px; }}
h1,h2,h3 {{ font-weight:600; line-height:1.2; text-wrap:balance; margin:0; }}
h2 {{ font-size:clamp(22px,2.4vw,28px); letter-spacing:-.01em; }}
h3 {{ font-size:17px; font-weight:600; }}
p {{ margin:0; max-width:62ch; }}
.mono {{ font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace; font-size:12.5px;
        letter-spacing:0; direction:ltr; unicode-bidi:isolate; }}

/* ---- hero ---- */
.hero {{ background:var(--slate); color:var(--bone); margin-bottom:56px; }}
.hero-in {{ max-width:1080px; margin:0 auto; padding:clamp(48px,8vw,104px) 24px clamp(40px,6vw,72px);
           display:flex; flex-direction:column; gap:40px; }}
.hero svg {{ width:min(560px,88%); height:auto; display:block; }}
.eyebrow {{ font-size:12px; letter-spacing:.16em; color:#9FA9B6; margin:0; }}
.hero p.lead {{ color:#C3CAD3; font-size:17px; max-width:52ch; }}

/* ---- sections ---- */
section {{ display:grid; grid-template-columns:170px 1fr; gap:32px;
           padding:44px 0; border-top:1px solid var(--line); }}
section > .col-label {{ display:flex; flex-direction:column; gap:6px; }}
.col-label .n {{ font-size:12px; letter-spacing:.14em; color:var(--muted); }}
.col-body {{ display:flex; flex-direction:column; gap:24px; min-width:0; }}
@media (max-width:760px) {{
  section {{ grid-template-columns:1fr; gap:18px; }}
  .variants, .rules {{ grid-template-columns:1fr; }}
}}

/* ---- preview surface with a ground switcher ---- */
.stage {{ background:var(--preview); border:1px solid var(--line); border-radius:4px;
          padding:44px 32px; display:flex; align-items:center; justify-content:center;
          flex-wrap:wrap; gap:44px; transition:background .25s ease; }}
.stage svg {{ height:auto; display:block; }}
.grounds {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; }}
.grounds span {{ font-size:12.5px; color:var(--muted); margin-left:4px; }}
.gbtn {{ width:26px; height:26px; border-radius:50%; border:1px solid var(--line);
         cursor:pointer; padding:0; }}
.gbtn[aria-pressed="true"] {{ outline:2px solid var(--terra); outline-offset:2px; }}
.gbtn:focus-visible {{ outline:2px solid var(--terra); outline-offset:2px; }}

/* ---- pieces ---- */
.idea {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }}
.idea > div {{ background:var(--surface); border:1px solid var(--line); border-radius:4px;
               padding:20px; display:flex; flex-direction:column; gap:8px; }}
.idea b {{ font-weight:600; }}
.idea p {{ font-size:14.5px; color:var(--muted); }}
@media (max-width:700px) {{ .idea {{ grid-template-columns:1fr; }} }}

.variants {{ display:grid; grid-template-columns:repeat(2,1fr); gap:18px; }}
.card {{ background:var(--surface); border:1px solid var(--line); border-radius:4px;
         overflow:hidden; display:flex; flex-direction:column; }}
.card .art {{ padding:30px 22px; display:flex; align-items:center; justify-content:center;
              min-height:132px; flex:1; background:var(--preview); }}
.card .art.on-dark {{ background:var(--slate); }}
.card .cap {{ border-top:1px solid var(--line); padding:10px 14px; font-size:13px;
              color:var(--muted); display:flex; justify-content:space-between; gap:10px; }}
.card svg {{ width:100%; height:auto; max-width:230px; }}

.sizes {{ display:flex; align-items:flex-end; gap:26px; flex-wrap:wrap; }}
.sizes figure {{ margin:0; display:flex; flex-direction:column; gap:8px; align-items:center; }}
.sizes figcaption {{ font-size:11.5px; color:#6B7583; }}
.avatars {{ display:flex; align-items:center; gap:22px; flex-wrap:wrap; }}
.avatars svg {{ display:block; }}

.swatches {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:16px; }}
.swatch {{ display:flex; gap:14px; align-items:flex-start; }}
.chip {{ width:52px; height:52px; border-radius:3px; border:1px solid var(--line);
         flex:none; }}
.chip-meta {{ display:flex; flex-direction:column; gap:1px; min-width:0; }}
.chip-meta b {{ font-weight:600; font-size:15px; }}
.chip-meta .en {{ color:var(--muted); font-size:11.5px; }}
.chip-meta p {{ font-size:13.5px; color:var(--muted); line-height:1.5; margin-top:4px; }}

.typerow {{ display:flex; flex-direction:column; gap:2px; padding:16px 0;
            border-bottom:1px solid var(--line); }}
.typerow:last-child {{ border-bottom:0; }}
.typerow .spec {{ color:var(--muted); }}
.w300 {{ font-weight:300; }} .w400 {{ font-weight:400; }} .w600 {{ font-weight:600; }}
.sample {{ font-size:28px; line-height:1.3; }}

.rules {{ display:grid; grid-template-columns:repeat(2,1fr); gap:18px; }}
.rule {{ background:var(--surface); border:1px solid var(--line); border-radius:4px; padding:18px;
         display:flex; flex-direction:column; gap:12px; }}
.rule .demo {{ background:var(--preview); border-radius:3px; height:92px; display:flex;
               align-items:center; justify-content:center; overflow:hidden; padding:12px; }}
.rule .demo svg {{ max-width:150px; width:100%; height:auto; }}
.rule .tag {{ font-size:13px; font-weight:600; display:flex; align-items:center; gap:7px; }}
.rule .tag i {{ width:7px; height:7px; border-radius:50%; background:var(--terra);
                font-style:normal; flex:none; }}
.rule.ok .tag i {{ background:#4C8C6B; }}
.rule p {{ font-size:13.5px; color:var(--muted); }}
.squash svg {{ transform:scaleX(.62); }}
.tilt svg {{ transform:rotate(-7deg); }}
.tint svg path[fill]:not([fill="none"]) {{ fill:#7A5BA8 !important; }}
.tint svg path[stroke] {{ stroke:#7A5BA8 !important; }}
.tint svg rect {{ fill:#3FA9A0 !important; }}

.clearspace {{ position:relative; display:inline-block; padding:0; }}
.clearspace .box {{ border:1px dashed var(--terra); padding:clamp(14px,3vw,26px); border-radius:2px; }}
.clearspace svg {{ width:min(360px,72vw); height:auto; display:block; }}

table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th, td {{ text-align:right; padding:9px 10px; border-bottom:1px solid var(--line);
          vertical-align:top; }}
th {{ font-size:11.5px; letter-spacing:.1em; color:var(--muted); font-weight:400; }}
td.file {{ white-space:nowrap; }}
td.use {{ color:var(--muted); white-space:nowrap; }}
.scroll {{ overflow-x:auto; }}

footer {{ border-top:1px solid var(--line); margin-top:36px; padding-top:22px;
          color:var(--muted); font-size:13.5px; display:flex; justify-content:space-between;
          gap:16px; flex-wrap:wrap; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; }} }}
</style>

<header class="hero">
  <div class="hero-in">
    <p class="eyebrow">ספר מותג · גרסה 1.0</p>
    {svg("logo-horizontal-ondark")}
    <p class="lead">זהות חזותית לאיש נדל״ן: קו גג אחד, שם בכתיב פתוח, ונקודה שסוגרת את המשפט.
      הדף הזה מרכז את הגרסאות, הצבעים והכללים — וכל הקבצים שיוצאים איתו.</p>
  </div>
</header>

<div class="wrap">

<section>
  <div class="col-label"><span class="n">הרעיון</span></div>
  <div class="col-body">
    <h2>שלושה מהלכים, בלי איורים</h2>
    <div class="idea">
      <div><b>קו הגג</b><p>קו דק אחד עם שיפוע ארוך ונקודת שיא ימנית. לא ציור של בית —
        רמז לגג, שמניח את השם תחתיו.</p></div>
      <div><b>הכתיב הפתוח</b><p>משקל דק וריווח אותיות נדיב. השם נקרא רגוע ובטוח,
        בלי להרים את הקול.</p></div>
      <div><b>הנקודה</b><p>ריבוע טרקוטה קטן שסוגר את השם. זה כל הצבע החם שיש במותג,
        ולכן הוא עובד.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">לוגו ראשי</span><h3>נקי, על רקע אחיד</h3></div>
  <div class="col-body">
    <div class="grounds" role="group" aria-label="בחירת רקע לתצוגה">
      <span>רקע תצוגה:</span>
      <button class="gbtn" data-bg="#FFFFFF" data-ink="light" aria-pressed="true" aria-label="לבן"
              style="background:#FFFFFF"></button>
      <button class="gbtn" data-bg="{BONE}" data-ink="light" aria-pressed="false" aria-label="עצם"
              style="background:{BONE}"></button>
      <button class="gbtn" data-bg="{SLATE}" data-ink="dark" aria-pressed="false" aria-label="צפחה"
              style="background:{SLATE}"></button>
      <button class="gbtn" data-bg="{DEEP}" data-ink="dark" aria-pressed="false" aria-label="צפחה עמוקה"
              style="background:{DEEP}"></button>
      <button class="gbtn" data-bg="{TERRA}" data-ink="dark" aria-pressed="false" aria-label="טרקוטה"
              style="background:{TERRA}"></button>
    </div>
    <div class="stage" id="stage">
      <span id="stage-light">{svg("logo-horizontal-onlight", style="width:min(430px,80vw)")}</span>
      <span id="stage-dark" hidden>{svg("logo-horizontal-ondark", style="width:min(430px,80vw)")}</span>
    </div>
    <p>הלוגו הרוחבי הוא ברירת המחדל. יש לו שתי גרסאות צבע — כהה לרקע בהיר, ובהיר לרקע כהה.
      על רקע טרקוטה משתמשים בגרסה הבהירה.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">גרסאות</span><h3>מתי משתמשים במה</h3></div>
  <div class="col-body">
    <div class="variants">
      <div class="card"><div class="art on-dark">{svg("logo-horizontal-ondark")}</div>
        <div class="cap"><span>רוחבי</span><span>ברירת מחדל</span></div></div>
      <div class="card"><div class="art on-dark">{svg("logo-stacked-dark")}</div>
        <div class="cap"><span>מוערם</span><span>ריבוע, פרופיל</span></div></div>
      <div class="card"><div class="art on-dark">{svg("logo-tagline-dark")}</div>
        <div class="cap"><span>עם תיאור</span><span>כרטיס, חתימה</span></div></div>
      <div class="card"><div class="art on-dark">{svg("logo-compact-ondark")}</div>
        <div class="cap"><span>מעובה</span><span>מתחת ל‑200px</span></div></div>
    </div>
    <p>הגרסה המעובה זהה בפרופורציות, אבל עם משקל אות וקו גג עבים יותר — כדי שהלוגו
      לא ייעלם בגדלים קטנים או בדפוס.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">קנה מידה</span><h3>עד כמה קטן מותר</h3></div>
  <div class="col-body">
    <div class="stage" style="justify-content:flex-start">
      <div class="sizes">
        <figure>{svg("logo-horizontal-onlight", style="width:320px")}
          <figcaption class="mono">320px</figcaption></figure>
        <figure>{svg("logo-horizontal-onlight", style="width:200px")}
          <figcaption class="mono">200px · מינימום</figcaption></figure>
        <figure>{svg("logo-compact-onlight", style="width:140px")}
          <figcaption class="mono">140px · מעובה</figcaption></figure>
      </div>
    </div>
    <p>מתחת ל‑200 פיקסל רוחב עוברים לגרסה המעובה, ומתחת ל‑120 פיקסל מוותרים על הוורדמארק
      ומשתמשים בסמל בלבד.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">סמל</span><h3>אווטאר ואייקון אתר</h3></div>
  <div class="col-body">
    <div class="stage">
      <div class="avatars">
        {svg("icon-square-dark", style="width:104px;height:104px")}
        {svg("icon-circle-dark", style="width:104px;height:104px")}
        {svg("icon-square-terra", style="width:72px;height:72px")}
        {svg("icon-square-light", style="width:72px;height:72px")}
        {svg("favicon-48", style="width:48px;height:48px")}
        {svg("favicon-32", style="width:32px;height:32px")}
        {svg("favicon-16", style="width:16px;height:16px")}
      </div>
    </div>
    <p>הסמל הוא קו הגג מעל האות נ׳ — ראשי־תיבות של שני חלקי השם. מ‑48 פיקסל ומטה
      קו הגג נמחק ונשארת האות בלבד, כדי שהאייקון יישאר חד בלשונית הדפדפן.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">צבע</span><h3>חמישה ערכים</h3></div>
  <div class="col-body">
    <div class="swatches">{swatches}</div>
    <p>הטרקוטה היא אקסנט ולא צבע מותג שווה־ערך. בכל חומר שיווקי היא מופיעה במינון קטן —
      נקודה, קו הדגשה, כפתור — ולא כרקע לטקסט ארוך.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">טיפוגרפיה</span><h3>אסיסטנט, ובפלוני אם יש</h3></div>
  <div class="col-body">
    <div class="typerow"><span class="sample w300">נדל״ן נכון · דירות, קרקעות והשקעות</span>
      <span class="spec mono">Assistant Light 300 · logo, headlines · tracking +0.06em</span></div>
    <div class="typerow"><span class="sample w400">ליווי אישי לכל אורך העסקה</span>
      <span class="spec mono">Assistant Regular 400 · body copy</span></div>
    <div class="typerow"><span class="sample w600">קביעת פגישה</span>
      <span class="spec mono">Assistant SemiBold 600 · buttons, emphasis</span></div>
    <p>הלוגו בנוי ב‑Assistant, גופן חופשי (OFL) שאפשר להתקין בכל מקום ולהטמיע באתר בלי רישיון.
      אם יש לך רישיון ל<b>פלוני</b>, הקובץ <span class="mono">logo-horizontal-editable.svg</span>
      נפתח עם טקסט חי ומתחלף לפלוני אוטומטית — צריך רק לכוונן מחדש את רוחב קו הגג ואת מקום
      הנקודה, כי המידות של פלוני שונות מעט.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">שוליים</span><h3>אוויר מסביב</h3></div>
  <div class="col-body">
    <div class="stage"><div class="clearspace"><div class="box">
      {svg("logo-horizontal-onlight")}</div></div></div>
    <p>שומרים מרווח פנוי מסביב ללוגו בגובה האות נ׳ לפחות. שום טקסט, תמונה או מסגרת
      לא נכנסים לתוך המרווח הזה.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">כללים</span><h3>מה לא לעשות</h3></div>
  <div class="col-body">
    <div class="rules">
      <div class="rule ok"><div class="demo">{svg("logo-horizontal-onlight")}</div>
        <span class="tag"><i></i>נכון</span><p>פרופורציות מקוריות, אחד מצבעי המותג.</p></div>
      <div class="rule"><div class="demo squash">{svg("logo-horizontal-onlight")}</div>
        <span class="tag"><i></i>לא למתוח</span><p>תמיד לשנות גודל באופן יחסי בשני הצירים.</p></div>
      <div class="rule"><div class="demo tilt">{svg("logo-horizontal-onlight")}</div>
        <span class="tag"><i></i>לא להטות</span><p>הלוגו יושב ישר. קו הגג הוא האלכסון היחיד.</p></div>
      <div class="rule"><div class="demo tint">{svg("logo-horizontal-onlight")}</div>
        <span class="tag"><i></i>לא לצבוע מחדש</span><p>רק צפחה, עצם, שחור או לבן — והנקודה בטרקוטה.</p></div>
    </div>
    <p>עוד שניים שאין להם תמונה: לא להוסיף צל או זוהר, ולא להניח את הלוגו על תמונה עמוסה
      בלי שכבת כהות מתחתיו.</p>
  </div>
</section>

<section>
  <div class="col-label"><span class="n">קבצים</span><h3>מה יש בתיקייה</h3></div>
  <div class="col-body">
    <div class="scroll"><table>
      <thead><tr><th>קובץ</th><th>מה זה</th><th>לאן</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <p>כל קובץ קיים גם כ‑PNG שקוף ב‑<span class="mono">brand/logo/png</span> —
      הלוגואים ברזולוציה משולשת, האווטארים ב‑1024, והאייקונים בגודל המדויק שלהם.
      ה‑SVG הוא המקור: האותיות בו כבר מומרות לוקטורים, ולכן הוא נראה זהה בכל מחשב
      גם בלי הגופן.</p>
  </div>
</section>

<footer>
  <span>נדל״ן נכון · ספר מותג 1.0</span>
  <span class="mono">Assistant (OFL) · SVG + PNG</span>
</footer>
</div>

<script>
(function () {{
  var stage = document.getElementById('stage');
  var light = document.getElementById('stage-light');
  var dark = document.getElementById('stage-dark');
  document.querySelectorAll('.gbtn').forEach(function (btn) {{
    btn.addEventListener('click', function () {{
      document.querySelectorAll('.gbtn').forEach(function (b) {{
        b.setAttribute('aria-pressed', String(b === btn));
      }});
      stage.style.background = btn.dataset.bg;
      var useDark = btn.dataset.ink === 'dark';
      light.hidden = useDark;
      dark.hidden = !useDark;
    }});
  }});
}})();
</script>
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"{os.path.relpath(OUT)}  ({os.path.getsize(OUT)/1024:.0f} KB)")


if __name__ == "__main__":
    build()
