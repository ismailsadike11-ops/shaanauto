> **Archived (2026-10-26):** the brand is back to **WARESOUQ / وير سوق**. Do not use this kit for new work. See `CLAUDE.md` at the repo root.

# WAREGRO · هوية بصرية

ملف الهوية البصرية الكامل لـ **WAREGRO / ويرغرو**، بنفس نظام هوية Waresouq (نفس الألوان، نفس الخطوط، نفس شكل الصندوق)،
مع تغيير **الاسم واللوغو** فقط، وإضافات تقوّي الهوية.

## الشعار
الصندوق نفسه وحرف **W** نفسه، لكن غطاء الصندوق مفتوح ويخرج منه **سهم نمو**:
`WARE` (السلعة / الصندوق) + `GRO` (النمو).

## محتوى الملف

| المجلد / الملف | المحتوى |
|---|---|
| `WAREGRO - Visual Identity.pdf` | دليل الهوية (24 صفحة): القصة، القيم، معنى الشعار، بناء الشعار، الألوان، الخطوط، الاستعمالات الخاطئة، المساحة الآمنة، نبرة الكلام، التطبيقات (سوشيال ميديا، بطاقات، تغليف، موقع، تطبيق) |
| `logo/svg` | ملفات فيكتور (للمصمم، الموقع، والطباعة) |
| `logo/pdf` | ملفات فيكتور للمطبعة |
| `logo/png` | خلفية شفافة، 3000px |
| `logo/jpeg` | خلفية ملونة، للمشاركة السريعة |
| `logo/favicon` | أيقونات المتصفح والتطبيق من 16 إلى 512px |
| `fonts` | خط Readex Pro (عربي) و Urbanist (بديل مجاني لـ Gelion) |
| `brand-tokens.css` / `.json` | الألوان والخطوط جاهزة للمبرمج |
| `brand-book/index.html` | مصدر دليل الهوية (قابل للتعديل) |
| `tools/` | سكربتات توليد كل الملفات |

### أشكال الشعار
`horizontal` (أفقي، الأساسي) · `stacked` (عمودي) · `mark` (الرمز فقط) · `wordmark-latin` · `wordmark-arabic` · `app-icon`

### نسخ الألوان
`primary` (على الأبيض) · `on-linen` · `on-orange` · `on-brown` · `white` · `black` · `orange`

## الألوان
| الاسم | HEX | RGB | CMYK |
|---|---|---|---|
| Mystic Red | `#FF5300` | 255 83 0 | 0 67 100 0 |
| Deep Ember | `#952801` | 149 40 1 | 0 73 99 42 |
| Linen | `#FFECE5` | 255 236 229 | 0 7 10 0 |
| Ink | `#1A1A1A` | 26 26 26 | 0 0 0 90 |

## إعادة توليد الملفات
لتغيير الكتابة العربية للاسم أو أي لون، عدّل الثوابت في أعلى `tools/build_logos.py` ثم:

```bash
pip install fonttools uharfbuzz
python3 waregro/tools/build_logos.py     # SVG
node waregro/tools/export_assets.js      # PNG / JPEG / PDF / favicon / دليل الهوية
```
