# BilgiGEN Workcube Assessment (FastAPI)

Modern, responsive assessment formu + Admin dashboard + SMTP/PDF + WordPress entegrasyonu.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # düzenleyin
./run.sh               # Windows: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Uygulama: http://localhost:8000  
Admin Giriş: http://localhost:8000/login

## Özellikler

- Kullanıcı bilgileri + format validasyonları
- Sonsuz dallanma yapısı (JSON tabanlı `QUESTION_TREE`)
- Çoklu seçim, ilerleme çubuğu, geri dönüş için yeniden render
- JWT korumalı Admin
- İstatistikler, listeler, PDF indirme
- SMTP ayarları (Gmail App Password destekli)
- Otomatik PDF (ReportLab) ve e-posta gönderimi
- WordPress iFrame/direkt link/popup entegrasyonu

## Notlar

- İlk admin `.env` içindedir. Canlıya geçerken değiştirin.
- PDF’ler `storage/pdfs` klasörüne yazılır.
