# موقع تحويل PDF إلى Word

```
pdf2word-site/
├── index.html          ← الواجهة (ترفعها على GitHub Pages)
└── backend/
    ├── main.py         ← السيرفر (FastAPI + pdf2docx)
    ├── requirements.txt
    └── Dockerfile
```

## 1) تشغيل محلي

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # على ويندوز: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

بعدين افتح `index.html` في المتصفح (الرابط جاهز على `http://localhost:8000`).

## 2) رفع السيرفر (Render مثلاً)

1. ارفع المشروع كله على GitHub.
2. في Render: New → Web Service → اختار الريبو.
3. Root Directory: `backend` — Runtime: Docker.
4. Environment Variables:
   - `ALLOWED_ORIGINS` = `https://USERNAME.github.io`
   - `MAX_MB` = `20`
5. انسخ الرابط (مثلاً `https://pdf2word-api.onrender.com`).

> الخطة المجانية في Render بتنام بعد فترة خمول، فأول طلب ممكن ياخد 30-60 ثانية.

## 3) رفع الواجهة (GitHub Pages)

1. في `index.html` غيّر السطر:
   ```js
   const API_URL = "https://pdf2word-api.onrender.com";
   ```
2. Repo → Settings → Pages → Branch: `main` / Folder: `/ (root)`.
3. موقعك هيكون على `https://USERNAME.github.io/REPO/`.

## ملاحظات

- ملفات PDF الممسوحة ضوئياً (صور) محتاجة OCR، وpdf2docx مش بيعملها.
- الملفات بتتحذف من السيرفر بعد التحويل مباشرة.
- Supabase مش لازم للنسخة دي. هتحتاجه لاحقاً لو أضفت تسجيل دخول أو اشتراكات أو سجل تحويلات.
