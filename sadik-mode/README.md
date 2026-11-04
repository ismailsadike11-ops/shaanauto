# SADIK MODE · الصادق مود: هوية بصرية

ملف الهوية البصرية لمحل **SADIK MODE**: بيع بالجملة ديال الملابس الداخلية، وحوايج الدار، واللانجري، والبيجامات.

## الشعار
حرف **S** ذهبي (صادق) داخل لوزة مغربية بجوج ديال الحدود ونجوم فالزوايا، والإبرة والخيط دايزين فيه.
الكتابة: **SADIK MODE** بخط Cinzel، وتحتها **UNDERWEAR · HOMEWEAR · LINGERIE · PYJAMAS**.

## المحتوى
| المجلد / الملف | المحتوى |
|---|---|
| `SADIK MODE - Visual Identity.pdf` | دليل الهوية (24 صفحة) |
| `logo/svg`، `logo/pdf` | ملفات فيكتور (للمطبعة والمصمم) |
| `logo/png` | خلفية شفافة، 3000px |
| `logo/jpeg` | للواتساب |
| `logo/favicon` | أيقونات من 16 حتى 512px |
| `templates/` | بوست Instagram، ستوري، ليستة الأثمنة (HTML قابل للتعديل + أمثلة) |
| `mockups/` | عرض اللوغو على الجلد |
| `fonts/` | Cinzel، Montserrat، Amiri، Cairo |
| `tools/` | سكربتات توليد كل الملفات |

### أشكال اللوغو
`horizontal` · `horizontal-arabic` (مع الصادق مود) · `stacked` · `stacked-arabic` · `emblem` · `emblem-simple` (للحجم الصغير) · `wordmark` · `profile-*` · `app-icon`

### النسخ
`primary` · `on-cream` · `on-slate` (فحمي) · `on-bordeaux` · `metal` · `metal-dark` (للشاشة فقط) · `gold` · `white` · `black`

## الألوان
| الاسم | HEX | CMYK |
|---|---|---|
| البوردو | `#7A1530` | 0 83 61 52 |
| الذهبي الشامباني | `#D9A441` | 0 24 70 15 |
| الفحمي | `#1C1C1F` | 10 10 0 88 |
| الكريمي | `#F6EFE6` | 0 3 7 4 |

## إعادة توليد الملفات
```bash
pip install fonttools uharfbuzz
python3 sadik-mode/tools/build_logos.py
node sadik-mode/tools/export_assets.js
```
