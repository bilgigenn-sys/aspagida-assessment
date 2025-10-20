# WordPress Entegrasyonu

Bu sistem bağımsız çalışır (FastAPI + SQLite). WordPress'e 3 farklı şekilde entegre edebilirsiniz:

## 1) iFrame (Önerilen, Hızlı)

1. Sunucunuzda uygulamayı 8000 portunda çalıştırın (veya bir reverse proxy ile alan adınıza bağlayın).
2. WordPress içinde bir Sayfa yazısına aşağıdaki kodu ekleyin:

```html
<iframe src="https://YOUR-DOMAIN/embed/form" width="100%" height="1400" frameborder="0"></iframe>
```

> Not: Yükseklik (height) alanını sayfadaki içeriğe göre artırabilirsiniz.

## 2) Direkt Link

WordPress’te bir butona veya menüye dış bağlantı olarak `https://YOUR-DOMAIN/` adresini ekleyin.

## 3) Popup (Modal) İçinde iFrame

Bir HTML blok eklentisi veya tema destekli modal/popup bileşeni ile iFrame’i bir butona bağlayabilirsiniz.

Örn. (temel bir fikir):

```html
<button onclick="document.getElementById('modal').style.display='block'">Assessment Aç</button>
<div id="modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,.5)">
  <div style="max-width:1000px; margin:40px auto; background:#fff; padding:10px; border-radius:12px;">
    <iframe src="https://YOUR-DOMAIN/embed/form" width="100%" height="900" frameborder="0"></iframe>
  </div>
</div>
```

## SMTP (Gmail) Ayarları

- Dashboard > SMTP Ayarları ekranından Gmail için Uygulama Şifresi ile giriş yapın.
- `smtp.gmail.com` / `587` / TLS = true
- Kullanıcı adı: Gmail adresiniz, Şifre: Uygulama Şifresi

## PDF Gönderimi

Her yeni assessment sonrası PDF otomatik oluşturulur ve `.env` / Dashboard ayarlarında belirttiğiniz adrese gönderilir (varsayılan `webmaster@bilgigen.com.tr`).

## Güvenlik Notları

- Admin girişi JWT tabanlıdır. İlk giriş bilgisi `.env.example` içinde verilir. Canlıya alırken **mutlaka** değiştirin.
- Reverse proxy (Nginx) / HTTPS (Let’s Encrypt) önerilir.
