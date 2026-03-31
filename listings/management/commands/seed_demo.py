"""
Demo e'lonlar va reels — faqat ishlab chiqish uchun.
"""
from io import BytesIO
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from listings.models import Property, PropertyImage
from reels.models import Reel

AGENT = {
    "name": "Javohir Karimov",
    "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=200&q=80&auto=format&fit=crop",
    "phone": "+998 90 123 45 67",
}

# Kategoriyaga mos professional stok-rasmlar (seed paytida yuklanadi; tarmoq yo‘q bo‘lsa demo PNG)
IMAGE_URLS: dict[str, list[str]] = {
    "kvartira": [
        "https://images.unsplash.com/photo-1560448204-6039e916e7c8?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&q=85&auto=format&fit=crop",
    ],
    "dacha": [
        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1575519143873-387cb5a6dd17?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&q=85&auto=format&fit=crop",
    ],
    "mehmonxona": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1590490360182-c33de577a351?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1631049307264-da0cb9d7038f?w=1200&q=85&auto=format&fit=crop",
    ],
    "quruq-yer": [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1628624747186-bd2f3903d36f?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1500076656116-558089c3dfdd?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1448630360428-65456885c650?w=1200&q=85&auto=format&fit=crop",
    ],
    "hovli": [
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=1200&q=85&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=1200&q=85&auto=format&fit=crop",
    ],
}


def _demo_png(seed: int) -> ContentFile:
    """Namuna rasm (tarmoq bo‘lmasa)."""
    buf = BytesIO()
    r, g, b = (180 + seed * 15) % 256, (200 + seed * 7) % 256, (220 - seed * 10) % 256
    img = Image.new("RGB", (640, 400), color=(r, g, b))
    img.save(buf, format="PNG")
    buf.seek(0)
    return ContentFile(buf.read(), name=f"demo_{seed}.png")


def _image_for_listing(cat_key: str, index_in_cat: int, global_seed: int) -> ContentFile:
    urls = IMAGE_URLS.get(cat_key, [])
    u = urls[index_in_cat % len(urls)] if urls else None
    if u:
        try:
            req = Request(u, headers={"User-Agent": "OsonUyJoySeed/1.0"})
            with urlopen(req, timeout=20) as resp:
                data = resp.read()
                ct = resp.headers.get("Content-Type", "")
            if len(data) > 2000:
                ext = "jpg"
                if "png" in ct:
                    ext = "png"
                return ContentFile(data, name=f"seed_{global_seed}.{ext}")
        except (URLError, OSError, TimeoutError, ValueError):
            pass
    return _demo_png(global_seed)


class Command(BaseCommand):
    help = "Ma'lumotlar bazasiga namuna e'lonlar va reels qo'shadi"

    def handle(self, *args, **options):
        PropertyImage.objects.all().delete()
        Property.objects.all().delete()
        Reel.objects.all().delete()

        # (id, title, type_label, category_id, vip, rating_avg, rating_count, district, lat, lng,
        #  price, price_label, beds, baths, area_m2, description, more_gallery_count)
        rows: list[dict] = [
            # Kvartiralar
            dict(
                id="k1",
                title="Skyline Residence — 4 xonali panorama",
                type_label="Kvartira",
                category_id="kvartira",
                vip=True,
                rating_avg="4.85",
                rating_count=412,
                district="Yunusobod",
                latitude=41.364,
                longitude=69.289,
                price="$2 100",
                price_label="/ oyiga",
                beds=4,
                baths=2,
                area_m2=128,
                more_gallery_count=10,
                description=(
                    "Yangi turar-joy majmuasi, panoramali oynalar, inverter konditsioner, "
                    "joylashgan avtoparkoz va bolalar maydonchasi. Metro va savdo markazlari 10 daqiqa."
                ),
            ),
            dict(
                id="k2",
                title="Chilonzor — 3 xonali remontlangan",
                type_label="Kvartira",
                category_id="kvartira",
                vip=False,
                rating_avg="4.52",
                rating_count=198,
                district="Chilonzor",
                latitude=41.285,
                longitude=69.203,
                price="$1 480",
                price_label="/ oyiga",
                beds=3,
                baths=1,
                area_m2=78,
                more_gallery_count=6,
                description=(
                    "Yevro remont, mebel bilan, issiq pol, zamonaviy oshxona. Maktab va bog‘cha yon-atrofda."
                ),
            ),
            dict(
                id="k3",
                title="Studiya — yakka turuvchilar uchun",
                type_label="Kvartira",
                category_id="kvartira",
                vip=False,
                rating_avg="4.38",
                rating_count=156,
                district="Mirobod",
                latitude=41.298,
                longitude=69.265,
                price="$720",
                price_label="/ oyiga",
                beds=1,
                baths=1,
                area_m2=36,
                more_gallery_count=4,
                description=(
                    "Zamonaviy studiya, toza kirish yo‘li, xavfsizlik. Markaz va ish joylariga yaqin."
                ),
            ),
            dict(
                id="k4",
                title="Yangi bosqich — 2 xonali kvartira",
                type_label="Kvartira",
                category_id="kvartira",
                vip=True,
                rating_avg="4.71",
                rating_count=89,
                district="Yashnobod",
                latitude=41.318,
                longitude=69.335,
                price="$1 890",
                price_label="/ oyiga",
                beds=2,
                baths=1,
                area_m2=62,
                more_gallery_count=8,
                description=(
                    "Birinchi egadan, dokumentlar tayyor. Balkon, podvaldagi saqlash xonasi. "
                    "Ipoteka va muddatli to‘lov imkoniyati."
                ),
            ),
            dict(
                id="k5",
                title="Shayxontohur — ikki qavatli loft uslubi",
                type_label="Kvartira",
                category_id="kvartira",
                vip=False,
                rating_avg="4.60",
                rating_count=64,
                district="Shayxontohur",
                latitude=41.311,
                longitude=69.279,
                price="$1 650",
                price_label="/ oyiga",
                beds=3,
                baths=2,
                area_m2=95,
                more_gallery_count=7,
                description=(
                    "Yuqori shift, ochiq reja, dizayner yoritish. Tarixiy markaz va kafelar piyoda masofada."
                ),
            ),
            # Dachalar
            dict(
                id="d1",
                title="Zangiota — hovli va bog‘ bilan dacha",
                type_label="Dacha",
                category_id="dacha",
                vip=True,
                rating_avg="4.78",
                rating_count=45,
                district="Zangiota tumani",
                latitude=41.189,
                longitude=69.104,
                price="$950",
                price_label="/ oyiga",
                beds=3,
                baths=2,
                area_m2=110,
                more_gallery_count=12,
                description=(
                    "Mevali daraxtlar, barbekyu maydoni, avtoturargoh. Dam olish va oilaviy dam uchun ideal."
                ),
            ),
            dict(
                id="d2",
                title="Bektemir — qishloq uslubidagi hovli",
                type_label="Dacha",
                category_id="dacha",
                vip=False,
                rating_avg="4.55",
                rating_count=31,
                district="Bektemir",
                latitude=41.222,
                longitude=69.334,
                price="$820",
                price_label="/ oyiga",
                beds=2,
                baths=1,
                area_m2=72,
                more_gallery_count=5,
                description=(
                    "Tinch muhit, toza havo, dala va issiqxona. Toshkent markaziga 25–30 daqiqa."
                ),
            ),
            dict(
                id="d3",
                title="«Bog‘» — ikki qavatli yozgi uy",
                type_label="Dacha",
                category_id="dacha",
                vip=False,
                rating_avg="4.62",
                rating_count=28,
                district="Yangihayot",
                latitude=41.341,
                longitude=69.293,
                price="$1 100",
                price_label="/ oyiga",
                beds=4,
                baths=2,
                area_m2=140,
                more_gallery_count=9,
                description=(
                    "Katta veranda, basseyn uchun tayyorlangan maydon, bolalar uchun swing. "
                    "Kunlik va haftalik ijaraga beriladi."
                ),
            ),
            dict(
                id="d4",
                title="Chorva uchun qulay dacha uchastkasi",
                type_label="Dacha",
                category_id="dacha",
                vip=False,
                rating_avg="4.40",
                rating_count=12,
                district="Qibray tumani",
                latitude=41.384,
                longitude=69.465,
                price="$680",
                price_label="/ oyiga",
                beds=2,
                baths=1,
                area_m2=55,
                more_gallery_count=3,
                description=(
                    "Fermer xo‘jaligi va dam olish uchun kombinatsiya. Quduq va elektr ta’minoti bor."
                ),
            ),
            # Mehmonxonalar
            dict(
                id="m1",
                title="Grand Hotel — standart xona",
                type_label="Mehmonxona",
                category_id="mehmonxona",
                vip=True,
                rating_avg="4.72",
                rating_count=520,
                district="Yakkasaroy",
                latitude=41.299,
                longitude=69.240,
                price="$95",
                price_label="/ kecha",
                beds=1,
                baths=1,
                area_m2=28,
                more_gallery_count=15,
                description=(
                    "Nonushta, Wi‑Fi, fitnes va spa kirish. Aeroport transferi va 24 soat resepshn."
                ),
            ),
            dict(
                id="m2",
                title="Boutique — dizayner interyer",
                type_label="Mehmonxona",
                category_id="mehmonxona",
                vip=False,
                rating_avg="4.65",
                rating_count=188,
                district="Mirobod",
                latitude=41.308,
                longitude=69.271,
                price="$120",
                price_label="/ kecha",
                beds=1,
                baths=1,
                area_m2=32,
                more_gallery_count=8,
                description=(
                    "Shahar markazida, restoran va lounge. Biznes mehmonlar uchun maxsus chegirmalar."
                ),
            ),
            dict(
                id="m3",
                title="Oilaviy apart — ikki xonali suite",
                type_label="Mehmonxona",
                category_id="mehmonxona",
                vip=False,
                rating_avg="4.58",
                rating_count=96,
                district="Chilonzor",
                latitude=41.276,
                longitude=69.211,
                price="$140",
                price_label="/ kecha",
                beds=2,
                baths=1,
                area_m2=45,
                more_gallery_count=6,
                description=(
                    "Oshxona zonasi, kir yuvish mashinasi, bolalar uchun qo‘shimcha karavot. Uzoq muddatli bron."
                ),
            ),
            dict(
                id="m4",
                title="Ekonom klass — qulay va toza",
                type_label="Mehmonxona",
                category_id="mehmonxona",
                vip=False,
                rating_avg="4.35",
                rating_count=240,
                district="Sergeli",
                latitude=41.228,
                longitude=69.216,
                price="$48",
                price_label="/ kecha",
                beds=1,
                baths=1,
                area_m2=22,
                more_gallery_count=4,
                description=(
                    "Temir yo‘l va avtobus bekatlari yonida. Qisqa muddatli sayohatchilar uchun."
                ),
            ),
            # Quruq yerlar
            dict(
                id="q1",
                title="Sergeli — 12 sotix investitsiya uchun",
                type_label="Quruq yer",
                category_id="quruq-yer",
                vip=True,
                rating_avg="4.68",
                rating_count=34,
                district="Sergeli",
                latitude=41.231,
                longitude=69.219,
                price="$58 000",
                price_label="/ sotuv",
                beds=0,
                baths=0,
                area_m2=480,
                more_gallery_count=6,
                description=(
                    "Barqaror yer, barcha kommunikatsiyalar yo‘li oldida. Savdo va turar-joy qurilishiga mos."
                ),
            ),
            dict(
                id="q2",
                title="Yangihayot — 8 sotix hovli uchun",
                type_label="Quruq yer",
                category_id="quruq-yer",
                vip=False,
                rating_avg="4.50",
                rating_count=19,
                district="Yangihayot",
                latitude=41.338,
                longitude=69.287,
                price="$42 000",
                price_label="/ sotuv",
                beds=0,
                baths=0,
                area_m2=320,
                more_gallery_count=5,
                description=(
                    "Tog‘ va shahar manzarasi. Asfalt yo‘l, elektr va gaz tarmog‘iga ulanish imkoniyati."
                ),
            ),
            dict(
                id="q3",
                title="Qishloq yer maydoni — fermerlik",
                type_label="Quruq yer",
                category_id="quruq-yer",
                vip=False,
                rating_avg="4.42",
                rating_count=8,
                district="Zangiota tumani",
                latitude=41.175,
                longitude=69.088,
                price="$28 000",
                price_label="/ sotuv",
                beds=0,
                baths=0,
                area_m2=2500,
                more_gallery_count=4,
                description=(
                    "Sug‘orish uchun kanal yaqin. Ekin va bog‘dorchilik uchun qulay tuproq."
                ),
            ),
            dict(
                id="q4",
                title="Toshkent halqa yo‘li yonida uchastka",
                type_label="Quruq yer",
                category_id="quruq-yer",
                vip=False,
                rating_avg="4.55",
                rating_count=15,
                district="Yashnobod",
                latitude=41.325,
                longitude=69.348,
                price="$72 000",
                price_label="/ sotuv",
                beds=0,
                baths=0,
                area_m2=600,
                more_gallery_count=7,
                description=(
                    "Logistika va omborxona uchun strategik joy. Hujjatlar rasmiylashtirilgan."
                ),
            ),
            # Ijara
            dict(
                id="i1",
                title="Mirobod — 2 xonali ijara kvartira",
                type_label="Ijara",
                category_id="ijara",
                vip=True,
                rating_avg="4.76",
                rating_count=128,
                district="Mirobod",
                latitude=41.304,
                longitude=69.276,
                price="$890",
                price_label="/ oyiga",
                beds=2,
                baths=1,
                area_m2=64,
                more_gallery_count=9,
                description=(
                    "To‘liq jihozlangan, yangi remont, metroga yaqin. Oilali juftliklar uchun qulay."
                ),
            ),
            dict(
                id="i2",
                title="Chilonzor — ekonom ijara",
                type_label="Ijara",
                category_id="ijara",
                vip=False,
                rating_avg="4.41",
                rating_count=73,
                district="Chilonzor",
                latitude=41.283,
                longitude=69.205,
                price="$520",
                price_label="/ oyiga",
                beds=1,
                baths=1,
                area_m2=42,
                more_gallery_count=4,
                description=(
                    "Talabalar va yosh oilalar uchun arzon variant. Transport va bozorga yaqin."
                ),
            ),
            dict(
                id="i3",
                title="Yunusobod — premium ijara",
                type_label="Ijara",
                category_id="ijara",
                vip=False,
                rating_avg="4.83",
                rating_count=52,
                district="Yunusobod",
                latitude=41.366,
                longitude=69.291,
                price="$1 250",
                price_label="/ oyiga",
                beds=3,
                baths=2,
                area_m2=102,
                more_gallery_count=8,
                description=(
                    "Katta oilalar uchun premium variant: qo‘riqlanadigan hovli, parking va bolalar maydoni."
                ),
            ),
            # Hovli
            dict(
                id="h1",
                title="Yunusobod — ikki qavatli hovli uy",
                type_label="Hovli",
                category_id="hovli",
                vip=True,
                rating_avg="4.82",
                rating_count=120,
                district="Yunusobod",
                latitude=41.358,
                longitude=69.295,
                price="$2 200",
                price_label="/ oyiga",
                beds=5,
                baths=3,
                area_m2=220,
                more_gallery_count=14,
                description=(
                    "Katta hovli, mehmonxonalar, garaj. Oilaviy yashash uchun barqaror va xavfsiz mahalla."
                ),
            ),
            dict(
                id="h2",
                title="Sergeli — yangi qurilgan hovli",
                type_label="Hovli",
                category_id="hovli",
                vip=False,
                rating_avg="4.70",
                rating_count=67,
                district="Sergeli",
                latitude=41.236,
                longitude=69.225,
                price="$1 950",
                price_label="/ oyiga",
                beds=4,
                baths=2,
                area_m2=180,
                more_gallery_count=8,
                description=(
                    "Zamonaviy fasad, avtomatik darvoza, bolalar xonasi. Hujjatlar tayyor, ko‘chmas mulk."
                ),
            ),
            dict(
                id="h3",
                title="Mirobod — klassik hovli",
                type_label="Hovli",
                category_id="hovli",
                vip=False,
                rating_avg="4.58",
                rating_count=44,
                district="Mirobod",
                latitude=41.302,
                longitude=69.268,
                price="$1 750",
                price_label="/ oyiga",
                beds=3,
                baths=2,
                area_m2=165,
                more_gallery_count=6,
                description=(
                    "An‘anaviy reja, keng zal va oshxona. Metro va bozor 15 daqiqada."
                ),
            ),
        ]

        cat_index: dict[str, int] = {}
        for i, row in enumerate(rows):
            cat = row["category_id"]
            ci = cat_index.get(cat, 0)
            cat_index[cat] = ci + 1

            p = Property.objects.create(
                id=row["id"],
                title=row["title"],
                type_label=row["type_label"],
                category_id=row["category_id"],
                vip=row["vip"],
                rating_avg=row["rating_avg"],
                rating_count=row["rating_count"],
                views_count=0,
                district=row["district"],
                region="Toshkent shahri",
                address_line=f"{row['district']}, Toshkent",
                latitude=row["latitude"],
                longitude=row["longitude"],
                price=row["price"],
                price_label=row["price_label"],
                more_gallery_count=row["more_gallery_count"],
                beds=row["beds"],
                baths=row["baths"],
                area_m2=row["area_m2"],
                description=row["description"],
                agent_name=AGENT["name"],
                agent_avatar=AGENT["avatar"],
                agent_phone=AGENT["phone"],
            )
            # Har e‘longa 2–3 ta rasm
            n_photos = 3 if row["vip"] else 2
            for j in range(n_photos):
                img = _image_for_listing(cat, ci + j, i * 10 + j)
                PropertyImage.objects.create(
                    property=p,
                    image=img,
                    sort_order=j,
                )

        reels = [
            Reel(
                id="r1",
                video_url="https://www.youtube.com/watch?v=LXb3EKWsInQ",
                title="Zamonaviy uy — ekskursiya",
                location="Toshkent",
                category=Reel.Category.UY,
                views=18420,
                sort_order=1,
            ),
            Reel(
                id="r2",
                video_url="https://www.youtube.com/watch?v=M7lc1UVf-VE",
                title="Kvartira ijarasi",
                location="Samarqand",
                category=Reel.Category.KVARTIRA,
                views=9320,
                sort_order=2,
            ),
            Reel(
                id="r3",
                video_url="https://www.youtube.com/watch?v=jNQXAC9IVRw",
                title="Hovli uyi",
                location="Andijon",
                category=Reel.Category.UY,
                views=45600,
                sort_order=3,
            ),
        ]
        Reel.objects.bulk_create(reels)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo qo'shildi: {len(rows)} e'lon (kvartira, dacha, mehmonxona, quruq yer, ijara, hovli), "
                f"har biri 2–3 rasm, 3 reel."
            )
        )
