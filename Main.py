import requests
import random
from bs4 import BeautifulSoup
import json
import os
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1501681893228412938/aryvHLZKH6spq5Br0A4OrQFOybWUcj9drljHmNXWIzgWodfh74x8JWEwVukXhhcVspuw"
URLS = [
    "https://www.emag.ro/apa-de-parfum-lattafa-najdia-barbati-30-ml-6291108731161/pd/D6HX6CMBM/?ref=fav_pd-title",
    "https://www.emag.ro/rasasi-hawas-for-him-eau-de-parfum-pentru-barbati-100-ml-614514331026/pd/DJ27QM2BM/?ref=fav_pd-title",
    "https://www.emag.ro/apa-de-parfum-lattafa-khamrah-qahwa-100ml-6290360593661/pd/DMQ89TYBM/?ref=fav_pd-title",
    "https://www.emag.ro/parfum-barbatesc-afnan-9-pm-pour-homme-combinatie-unica-culoare-neagra-100-ml-qp-x7/pd/DS52MQ3BM/",
    "https://www.emag.ro/apa-de-parfum-lattafa-jasoor-unisex-100ml-6290360591513/pd/DRY63HYBM/"

]

DB_FILE = "last_prices.json"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]


def get_product_info(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            # Extrage numele produsului
            title_tag = soup.find('h1', {'class': 'page-title'})
            title = title_tag.get_text().strip() if title_tag else "Produs Necunoscut"

            # Extrage pretul
            price_tag = soup.find('p', {'class': 'product-new-price'})
            if price_tag:
                # Curata textul
                raw_price = price_tag.get_text().replace(".", "").replace(",", ".").split(" ")[0]
                return title, float(raw_price)
    except Exception as e:
        print(f"Eroare la accesarea URL-ului: {e}")
    return None, None


def check_prices():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = {}

    new_data = {}
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)

    found_any = False  # Indicator: am gasit macar un produs?

    print("Se verifică prețurile...")

    for url in URLS:
        name, current_price = get_product_info(url)

        if name and current_price:
            found_any = True
            old_price = old_data.get(name)

            color = "808080"
            description = f"Preț actual: **{current_price} RON**"

            if old_price:
                if current_price < old_price:
                    color = "00ff00"
                    description = f"📉 **REDUCERE!**\nDe la ~~{old_price} RON~~ la **{current_price} RON**"
                elif current_price > old_price:
                    color = "ff0000"
                    description = f"📈 **SCUMPIRE!**\nDe la {old_price} RON la **{current_price} RON**"
            else:
                description = f"Monitorizare începută.\nPreț: **{current_price} RON**"

            embed = DiscordEmbed(title=name, description=description, color=color)
            embed.set_timestamp()
            webhook.add_embed(embed)

            new_data[name] = current_price
            print(f"Succes: {name[:30]}...")
        else:
            print(f"❌ Atenție: Nu am putut extrage date de la: {url[:40]}...")

    wait_time = random.uniform(7, 15)
    print(f"Aștept {wait_time:.2f} secunde până la următorul produs...")
    time.sleep(wait_time)

    # Verificam dacă avem ce trimite
    if found_any:
        response = webhook.execute()
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=4)
        print("✅ Verificare finalizată și mesaje trimise pe Discord.")
    else:
        print(
            "⚠️ Eroare: Nu s-a trimis nimic pe Discord pentru că nu am găsit date pe site (URL-uri invalide sau blocaj).")

    # 5. Salveaza noile preturi in fisierul JSON
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4)
    print("Verificare finalizată și date salvate.")


# Rulam scriptul
if __name__ == "__main__":
    check_prices()
