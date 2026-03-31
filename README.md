# Oson uy-joy — backend (Django REST Framework)

## Talablar

- Python 3.11+

## O‘rnatish

```bash
cd osonuy-backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # ixtiyoriy: maxfiy kalitni o‘zgartiring
python manage.py migrate
python manage.py seed_demo  # namuna e'lonlar va reels
python manage.py createsuperuser   # admin panel uchun
python manage.py runserver
```

- API: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`
- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **ReDoc:** `http://127.0.0.1:8000/api/redoc/`
- OpenAPI schema (JSON): `http://127.0.0.1:8000/api/schema/`

## API

| Endpoint | Tavsif |
|----------|--------|
| `GET /api/listings/` | Barcha e'lonlar. Query: `category`, `vip`, `q` |
| `GET /api/listings/<id>/` | Bitta e'lon |
| `GET /api/reels/` | Reels ro‘yxati. Query: `category` (`uy`, `kvartira`, `ijara`) |
| `GET /api/reels/<id>/` | Bitta reel |

Javoblar JSON; e'lonlar maydonlari frontend `PropertyListing` bilan mos (camelCase).

## E’lon rasmlari (admin)

- Har bir **E’lon** kartochkasida pastda **«Rasmlar»** bo‘limi bor: har qatorda **bitta rasm**; **«Yana … qo‘shish»** tugmasi bilan qator qo‘shib **istagancha** rasm yuklash mumkin (cheksiz).
- Bir nechta rasm uchun bir nechta qator qo‘shasiz (standart Django admin shunday ishlaydi).
- Saqlanish: `media/listings/YYYY/MM/` (`media/` gitga kiritilmaydi).
- **DEBUG**da: `http://127.0.0.1:8000/media/...` orqali ochiladi.
- **Production**da fayllarni nginx/CDN orqali bering.

API dagi `images` maydoni — barcha rasmlarning **to‘liq URL**lari ro‘yxati (tartib raqami bo‘yicha).

**Admin panel** maydon nomlari va guruhlar **o‘zbekcha** ko‘rinadi (sarlavha, narx, manzil, rasmlar va hokazo).

## Loyiha tuzilmasi

- `config/` — Django sozlamalari, `urls`
- `listings/` — mulk e'lonlari (`Property`)
- `listings.PropertyImage` — e’longa bog‘langan rasmlar (cheksiz)
- `reels/` — video reels (`Reel`)

## CORS

Standart: Vite dev server (`http://localhost:5173`). `.env` da `CORS_ORIGINS` ni o‘zgartiring.

## Ishlab chiqish

```bash
python manage.py makemigrations
python manage.py migrate
```
