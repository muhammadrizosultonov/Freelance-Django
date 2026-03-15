# FreelanceUZ

FreelanceUZ — mijoz va freelancerlarni bog'laydigan platforma. Loyiha yaratish, ariza yuborish, shartnoma tuzish va chat orqali muloqot qilish imkonini beradi. Bu repo GitHub uchun demo/portfolio ko'rinishida, production deploy uchun tayyorlanmagan.

**Asosiy imkoniyatlar**
- Mijoz va freelancer rollari
- Loyiha yaratish va ariza yuborish
- Shartnoma tuzish va progress kuzatish
- Chat (xabar yozish, unread hisoblash)
- OTP login (email/telefon) + parol bilan yakuniy kirish
- Profil va sozlamalar

**Texnologiyalar**
- Django
- PostgreSQL
- HTML/CSS/JS

## Tez start

1) Virtual muhit va kutubxonalar
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) `.env` sozlash
```bash
cp .env.example .env
```

3) Migratsiyalar
```bash
python manage.py migrate
```

4) Admin yaratish
```bash
python manage.py createsuperuser
```

5) Serverni ishga tushirish
```bash
python manage.py runserver
```

## .env o'zgaruvchilar

Quyidagilarni `.env` fayliga kiriting:
- `DBNAME`, `USER`, `PASSWORD`, `HOST`, `PORT`
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`

## OTP login oqimi

1) Email yoki telefon raqam kiritiladi
2) Kod yuboriladi (email bo'lsa emailga, telefon bo'lsa terminalga chiqadi)
3) Kod tasdiqlangach parol kiritish bosqichi ochiladi
4) Parol to'g'ri bo'lsa login bo'ladi

## Admin panel

Admin panel: `/admin/`


## Eslatma

- Email yuborish ishlashi uchun SMTP sozlamalar to'g'ri bo'lishi kerak.
- Default `EMAIL_BACKEND` console bo'lsa, email terminalga chiqadi.
- Production uchun `DEBUG=False` va `ALLOWED_HOSTS` to'ldirish tavsiya etiladi.
