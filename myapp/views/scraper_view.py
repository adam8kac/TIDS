from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
import json
import time
import os

PIPE_PATH = "/tmp/scraper_pipe"

# Ustvari named pipe, če še ne obstaja
if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)


def write_to_pipe(data):
    """Piše v pipe"""
    try:
        with open(PIPE_PATH, "w") as pipe:
            pipe.write(json.dumps(data))
        print("Podatki uspešno zapisani v named pipe.")
    except Exception as e:
        print(f"Napaka pri pisanju v pipe: {e}")


def scrape_and_save_data():
    """Scrape data in shrani v JSON format"""
    base_url = "https://www.ceneje.si/L3/971/racunalnistvo/prenosniki/prenosniki?page="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    data = {}
    for page in range(1, 6):  # Scrapanje do 5 strani
        url = f"{base_url}{page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Napaka pri dostopu do strani {url}: {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        product_links = []
        product_names = []

        for product in soup.select("h3.productTitle a"):
            product_links.append(product["href"])
            product_names.append(product.text.strip())

        for link, name in zip(product_links, product_names):
            product_response = requests.get(link, headers=headers)
            if product_response.status_code != 200:
                print(f"Napaka pri dostopu do izdelka {link}: {product_response.status_code}")
                continue

            product_soup = BeautifulSoup(product_response.content, "html.parser")

            try:
                product_name = product_soup.select_one("h1.top-offer__name").text.strip()
            except AttributeError:
                product_name = name

            product_id = product_name.replace(" ", "_").lower()
            offers = product_soup.select("div.sortExstraData")
            product_offers = {}
            for offer in offers:
                try:
                    store_name = offer["data-sellername"]
                    price = offer["data-price"] + " €"
                    product_offers[store_name] = {"cena": price}
                except KeyError:
                    continue

            data[product_id] = product_offers
            time.sleep(1)  # Počakamo, da ne obremenimo strežnika

    # Shranimo podatke v JSON datoteko
    json_file_path = "myapp/scraped_data/ceneje_si_scraped_data.json"
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    return json_file_path
# TODO Naredi da se json za racu alnike shranjuje v JSON_rac, dodaj opcijo da uporabnik izbere kaj hoče scrapat(rac, tv, telefon, ...)
# TODO dodaj nepremicnice, OPSI index rasti nepremicnin


def scrape_data_view(request):
    """Kliče write and save in kliče write to pipe ki naredi pipe"""
    try:
        file_path = scrape_and_save_data()
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        write_to_pipe(data=data)
        return JsonResponse({"message": "Podatki so uspešno scrapani.", "file_path": file_path})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
