# נדל״ן נכון — מותג

זהות חזותית לאיש נדל״ן: קו גג דק מעל וורדמארק בכתיב פתוח, ונקודת טרקוטה שסוגרת את השם.

📄 **[ספר המותג](brand/brand-guide.html)** — גרסאות, צבעים, כללי שימוש ורשימת הקבצים.

## מה יש כאן

```
brand/
  brand-guide.html          ספר המותג — עמוד אחד, עצמאי, נפתח בכל דפדפן
  logo/svg/                 קבצי מקור. האותיות מומרות לוקטורים — לא צריך גופן מותקן
  logo/png/                 ייצוא שקוף: לוגו ×3, אווטאר 1024, אייקונים בגודל מדויק
  fonts/                    Assistant (OFL) — הגופן שממנו נבנה הלוגו
tools/
  hebrew_text_to_svg.py     המרת טקסט עברי (RTL) לנתיבי SVG
  build_logo.py             בונה את כל קבצי הלוגו
  build_brand_guide.py      בונה את ספר המותג
  render_png.js             ממיר SVG ל‑PNG דרך Chromium
```

## הקבצים שכנראה תצטרך

| מתי | קובץ |
| --- | --- |
| ברירת מחדל, רקע בהיר | `logo-horizontal-onlight.svg` |
| ברירת מחדל, רקע כהה | `logo-horizontal-ondark.svg` |
| מתחת ל‑200px רוחב | `logo-compact-onlight.svg` / `-ondark.svg` |
| תמונת פרופיל | `icon-square-dark.svg` / `icon-circle-dark.svg` |
| אתר | `favicon-512.svg` ומטה |
| כרטיס ביקור, חתימת מייל | `logo-tagline-light.svg` |

## צבעים

| | HEX | תפקיד |
| --- | --- | --- |
| צפחה | `#39414E` | צבע ראשי — טקסט, קווים, רקע כהה |
| צפחה עמוקה | `#2E3540` | רקעים כהים גדולים |
| טרקוטה | `#D2703C` | אקסנט בלבד — הנקודה |
| עצם | `#EAE7E1` | לבן חם, על רקע כהה |
| אפור ביניים | `#6B7583` | טקסט משני |

## הגופן

הלוגו בנוי ב‑**Assistant** במשקל 300, עם ריווח אותיות של ‎+0.06em. הגופן חופשי (OFL),
אפשר להתקין ולהטמיע באתר בלי רישיון, והוא מצורף כאן ב‑`brand/fonts`.

אם יש לך רישיון ל**פלוני (Ploni)** — `logo-horizontal-editable.svg` שומר טקסט חי עם
`font-family` שמעדיף פלוני, כך שהקובץ נפתח בפלוני בקנבה, בפיגמה או באילוסטרייטור.
המידות של פלוני שונות מעט מ‑Assistant, אז אחרי ההחלפה צריך לכוונן מחדש את רוחב קו הגג
ואת מיקום הנקודה. שאר הקבצים כבר מומרים לוקטורים ולכן קפואים ובטוחים.

## בנייה מחדש

```bash
python3 tools/build_logo.py                              # קבצי SVG
python3 tools/build_brand_guide.py                       # ספר המותג
node tools/render_png.js brand/logo/png 3 transparent brand/logo/svg/logo-*.svg
```

`build_logo.py` דורש `fonttools` (‎`pip install fonttools`‎), ו‑`render_png.js` דורש Playwright
עם Chromium. כל פרופורציות הלוגו מוגדרות כקבועים בראש `build_logo.py` — שינוי של
`TRACKING`, `ROOF_PEAK` או `ROOF_WEIGHT` ובנייה מחדש מעדכנים את כל הסט בבת אחת.
