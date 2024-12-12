from collections import deque
from datetime import datetime
import json
import random
import time
import requests
from colorama import Fore

class coinhunter:

    BASE_URL = "https://europe-central2-coinhuntersprod.cloudfunctions.net/api/"
    HEADERS = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "origin": "https://coinhuntersprod.vercel.app",
        "priority": "u=1, i",
        "referer": "https://coinhuntersprod.vercel.app/",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "telegram-bot": "GAME",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0" 
    }
    
    MAP = [
            {"name": "training-camp", "neighbors": ["survivor-camp","haystack-field"], "items": ["pizza-slice", "meat", "zoombie-blood"]},
            {"name": "survivor-camp", "neighbors": ["supply-barn"], "items": ["pizza-slice", "leather", "zombie-blood"]},
            {"name": "haystack-field", "neighbors": ["supply-barn"], "items": ["lucky-clever", "rope", "zombie-tooth", "plastic-bottle"]},
            {"name": "supply-barn", "neighbors": ["survivor-camp", "fuel-depot", "haystack-field"], "items": ["meat", "hammer", "zombie-blood"]},
            {"name": "fuel-depot", "neighbors": ["supply-barn", "checkpoint-charlie", "bulldozer-yard", "muddy-patch"], "items": ["food-can", "gasoline", "plastic-bottle"]},
            {"name": "checkpoint-charlie", "neighbors": ["fuel-depot", "robbed-truck", "muddy-patch", ], "items": ["food-can", "lucky-clever", "microchip", "zombie-tooth"]},
            {"name": "bulldozer-yard", "neighbors": ["fuel-depot", "muddy-patch", "ruined-house"], "items": ["lucky-clever", "wrench", "screw", "zombie-tooth"]},
            {"name": "muddy-patch", "neighbors": ["swampy-ground", "fuel-depot", "bulldozer-yard", "checkpoint-charlie"], "items": ["lucky-clever", "wood"]},
            {"name": "robbed-truck", "neighbors": ["checkpoint-charlie", "water-plant"], "items": ["food-can", "lucky-clever", "dirty-textile", "zombie-tooth"]},
            {"name": "ruined-house", "neighbors": ["sos-shelter", "bulldozer-yard"], "items": ["food-can", "pizza-slice", "rubber", "plastic-bottle"]},
            {"name": "sos-shelter", "neighbors": ["ruined-house", "wrecked-house"], "items": ["food-can", "pizza-slice", "lucky-clever", "glass"]},
            {"name": "wrecked-house", "neighbors": ["swampy-ground", "sos-shelter", "abandoned-checkpoint"], "items": ["food-can", "plastic-bottle", "super-glue", "dirty-textile"]},
            {"name": "swampy-ground", "neighbors": ["abandoned-checkpoint", "wrecked-house", "muddy-patch"], "items": ["swamp-oyster", "chemicals", "zombie-blood"]},
            {"name": "water-plant", "neighbors": ["robbed-truck"], "items": ["food-can", "bolt", "zombie-blood"]},
            {"name": "abandoned-checkpoint", "neighbors": ["swampy-ground", "wrecked-house"], "items": ["food-can", "copper-wire", "zombie-tooth"]},
        ]
    
    ARROW_MAP = {
        "r": "➡️",  
        "t": "⬆️",  
        "b": "⬇️",  
        "l": "⬅️"   
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.coin = 0
        self.ticket = 0
        self.power = 0
        self.config = self.load_config()
        self.result = None
        self.is_crafting_material = None
        self.location = None

    def banner(self):
            print("     Coinhunters Free Bot")
            print("     This Bot Created By LIVEXORDS\n")
            print("     Channel: t.me/livexordsscript")

    def log(self, message, color=Fore.RESET):
        print(Fore.LIGHTBLACK_EX + datetime.now().strftime("[%Y:%m:%d:%H:%M:%S] |") + " " + color + message + Fore.RESET)

    def load_config(self):
        """Membaca konfigurasi dari file config.json"""
        try:
            with open("config.json", "r") as config_file:
                config_data = json.load(config_file)
                return config_data
        except FileNotFoundError:
            print("File config.json tidak ditemukan!")
            return {}
        except json.JSONDecodeError:
            print("Terjadi kesalahan dalam membaca config.json!")
            return {}

    def login(self, index: int) -> None:
        """Melakukan login ke API menggunakan query list."""
        try:
            queries = self.query_list
            
            if index < 0 or index >= len(queries):
                raise IndexError(f"Index {index} tidak valid. Query list hanya memiliki {len(queries)} elemen.")
            
            req_url = f"{self.BASE_URL}user"
            headers = {**self.HEADERS, "telegram-data": queries[index]}

            response = requests.get(req_url, headers=headers)
            response.raise_for_status()  

            data = response.json().get("result")
            if not data:
                raise ValueError("Data 'result' tidak ditemukan dalam respons.")

            self.log("Success Login.....", Fore.GREEN)
            self.log(f"Username: {data.get('name', 'Unknown')}", Fore.YELLOW)
            self.log(f"Coins: {data.get('coins', 0)}")
            self.log(f"Tokens: {data.get('tokens', 0)}")
            self.log(f"Tickets: {data.get('tickets', 0)}")
            self.log(f"Power: {data.get('power', 0)}")
            self.log(f"Level: {data.get('level', 'Unknown')}")

            self.token = queries[index]
            self.coin = data.get('coins', 0)
            self.ticket = data.get('tickets', 0)
            self.power = data.get('power', 0)
            self.location = data.get('currentRegion', None)

        except IndexError as e:
            self.log(f"Error: {e}", Fore.RED)
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Unexpected error: {e}", Fore.RED)

    def load_query(self, path_file="query.txt"):
        self.banner()
        
        try:
            with open(path_file, 'r') as file:
                queries = [line.strip() for line in file if line.strip()]    
            
            if not queries:
                self.log(f"Warning: {path_file} is empty.", Fore.YELLOW)
            
            self.log(f"Data Load : {len(queries)} queries loaded.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"Error while loading queries from file: {e}", Fore.RED)
            return []

    def get_upgrade_prices(self) -> None:
        """Ambil data harga upgrade dari API."""
        upgrade_url = f"{self.BASE_URL}backpack/items-upgrades"
        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.get(upgrade_url, headers=headers)
            response.raise_for_status() 
            data = response.json()
            if not data.get("ok"):
                raise ValueError("Gagal mengambil data upgrade.")
            return data.get("result")
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)

    def upgrade(self) -> None:
        req_url = f"{self.BASE_URL}backpack"
        upgrade_url = f"{self.BASE_URL}backpack/upgrade"

        headers = {**self.HEADERS, "telegram-data": self.token}
        success = True 

        while success:
            success = False

            try:
                response = requests.get(req_url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if not data or "result" not in data:
                    raise ValueError("Data 'result' tidak ditemukan dalam respons.")

                items = [{"id": item.get("id"), "iconName": item.get("iconName"), "level": item.get("level"), "type": item.get("type")}
                        for item in data.get("result", [])]

                if not items:
                    self.log("Tidak ada data 'id' dan 'iconName' yang ditemukan.", Fore.RED)
                    break

                upgrade_prices = self.get_upgrade_prices()

                self.log("Item yang ditemukan:", Fore.YELLOW)
                for item in items:
                    self.log(f"- Name: {item['iconName']}, Level: {item['level']}, Type: {item['type']}", Fore.GREEN)

                for item in items:
                    req_item = self.craft(info=False)                    
                    if not req_item:
                        if item["level"] < 8:
                            self.log(f"Item {item['iconName']} tidak sesuai untuk crafting, upgrade ke level 8 sebelum burn.", Fore.CYAN)
                            self.upgrade_to_level_8(item, headers, upgrade_url, upgrade_prices)
                        self.burn(id=item.get("id"), name=item.get("iconName"))
                        continue

                    if item["level"] >= 8:
                        self.log(f"Item {item['iconName']} telah mencapai level maksimum: {item['level']}", Fore.CYAN)
                        continue

                    level_prices = upgrade_prices.get(str(item["level"] + 1))
                    if not level_prices:
                        self.log(f"Tidak ada data harga untuk level {item['level']} pada item {item['iconName']}", Fore.RED)
                        continue

                    type_data = level_prices.get(item["type"].lower())
                    if not type_data:
                        self.log(f"Tidak ada data harga untuk tipe {item['type']} pada item {item['iconName']}", Fore.RED)
                        continue

                    upgrade_cost = type_data["price"]
                    self.log(f"Harga upgrade untuk {item['iconName']} ke level {item['level'] + 1} adalah: {upgrade_cost}", Fore.YELLOW)
                    self.dataCoin()

                    if self.coin >= upgrade_cost:
                        payload = {"itemId": item["id"], "useUpgradeScroll": False}
                        upgrade_response = requests.post(upgrade_url, json=payload, headers=headers)

                        if upgrade_response.status_code == 200:
                            upgrade_data = upgrade_response.json()
                            if upgrade_data.get("ok"):
                                user_power = upgrade_data["result"]["user"]["power"]
                                user_level = upgrade_data["result"]["user"]["level"]
                                item_power = upgrade_data["result"]["item"]["power"]
                                item_level = upgrade_data["result"]["item"]["level"]
                                name = upgrade_data["result"]["item"]["iconName"]

                                self.log(f"Upgrade berhasil untuk: {name}", Fore.GREEN)
                                self.log(f" - User Power: {user_power}, User Level: {user_level}", Fore.LIGHTMAGENTA_EX)
                                self.log(f" - Item Power: {item_power}, Item Level: {item_level}", Fore.LIGHTMAGENTA_EX)

                                success = True 
                            else:
                                self.log(f"Upgrade gagal: {upgrade_data.get('message')}", Fore.RED)
                                success = False
                        else:
                            self.log(f"Upgrade gagal untuk: {item['iconName']}, Status: {upgrade_response.status_code}, pesan: {upgrade_response.json().get('errorCode', None)}", Fore.RED)
                            success = True
                    else:
                        self.log(f"Saldo tidak cukup untuk upgrade {item['iconName']} ke level {item['level'] + 1} ({self.coin} < {upgrade_cost})", Fore.RED)
                        success = False
                    time.sleep(3)

            except requests.exceptions.RequestException as e:
                self.log(f"Request failed: {e}", Fore.RED)
                break

            except ValueError as e:
                self.log(f"Data error: {e}", Fore.RED)
                break

            except Exception as e:
                self.log(f"Upgrade | Unexpected error: {e}", Fore.RED)
                break

            time.sleep(5)

            if not success:
                self.log("Tidak ada item yang berhasil di-upgrade dalam iterasi ini.", Fore.RED)
                break

    def upgrade_to_level_8(self, item, headers, upgrade_url, upgrade_prices):
        while item["level"] < 8:
            level_prices = upgrade_prices.get(str(item["level"] + 1))
            if not level_prices:
                break

            type_data = level_prices.get(item["type"].lower())
            if not type_data:
                break

            upgrade_cost = type_data["price"]
            if self.coin < upgrade_cost:
                self.log(f"Saldo tidak cukup untuk upgrade {item['iconName']} ke level {item['level'] + 1}", Fore.RED)
                break

            payload = {"itemId": item["id"], "useUpgradeScroll": False}
            upgrade_response = requests.post(upgrade_url, json=payload, headers=headers)

            if upgrade_response.status_code == 200:
                upgrade_data = upgrade_response.json()
                if upgrade_data.get("ok"):
                    item["level"] = upgrade_data["result"]["item"]["level"]
                    self.log(f"Upgrade berhasil untuk {item['iconName']} ke level {item['level']}", Fore.GREEN)
                else:
                    self.log(f"Upgrade gagal: {upgrade_data.get('message')}", Fore.RED)
                    break
            elif upgrade_response.status_code == 400:  # Handle error status 400 specifically
                self.log(f"Upgrade gagal untuk: {item['iconName']}, Status: {upgrade_response.status_code}", Fore.RED)
                self.log("Tunggu sebentar sebelum mencoba lagi...", Fore.YELLOW)
                time.sleep(5)  # Wait before retrying
            else:
                self.log(f"Upgrade gagal untuk: {item['iconName']}, Status: {upgrade_response.status_code}", Fore.RED)
                break

            time.sleep(3)

    def burn(self, id: str, name: str) -> None:
        req_url = f"{self.BASE_URL}backpack/burn"

        headers = {**self.HEADERS, "telegram-data": self.token}
        payload = {"itemId": id}

        try:
            response = requests.post(req_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json().get("ok")
            if result:
                self.log(f"Berhasil mengupgrade hunter dengan item {name}", Fore.GREEN)
                self.info()
            else:
                self.log(f"Gagal mengupgrade hunter dengan item {name}", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"Request failed | {response.json().get("errorCode", None)}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Burn | Unexpected error: {e}", Fore.RED)

    def wheel(self) -> None:
        req_url = f"{self.BASE_URL}wheel/roll"

        headers = {**self.HEADERS, "telegram-data": self.token}
        
        while self.ticket > 0:
            try:
                response = requests.post(req_url, headers=headers)
                response.raise_for_status()  
                
                data = response.json().get("result")
                if not data:
                    raise ValueError("Data 'result' tidak ditemukan dalam respons.")

                self.log(f"Reward: {data.get('userReward').get('type', None)}, Amount: {data.get('userReward').get('amount', 0)}, Rarity: {data.get('userReward').get('rarity', None)}")

            except requests.exceptions.RequestException as e:
                self.log(f"Request failed: {e}", Fore.RED)
            except ValueError as e:
                self.log(f"Data error: {e}", Fore.RED)
            except Exception as e:
                self.log(f"Wheel | Unexpected error: {e}", Fore.RED)
            
            self.dataCoin()

    def daily(self) -> None:
        req_url = f"{self.BASE_URL}daily-bonus/claim"
        
        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.post(req_url, headers=headers)
            response.raise_for_status() 
            
            data = response.json().get('ok')
            if not data:
                raise ValueError("Data 'result' tidak ditemukan dalam respons.")

            if data is True:
                self.log(f"Succes mengclaim daily : {data}", Fore.GREEN)

        except requests.exceptions.RequestException as e:
            self.log(f"Daily sudah terclaim, pesan: {response.json().get("errorCode", None)}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Daily | Unexpected error: {e}", Fore.RED)

    def farm(self) -> None:
        req_url = f"{self.BASE_URL}farm/claim"

        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.post(req_url, headers=headers)
            response.raise_for_status()  
            self.log(f"Berhasil mengclaim farming, Kamu mendapatkan item")
            self.map()

        except requests.exceptions.RequestException as e:
            self.log(f"Farm sudah terclaim , pesan: {response.json().get("errorCode", None)}", Fore.RED)
            self.map()
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Farm | Unexpected error: {e}", Fore.RED)

    def build_graph(self, data):
        graph = {}
        items = {}
        for item in data:
            graph[item["name"]] = item["neighbors"]
            items[item["name"]] = item["items"]
        return graph, items

    def find_closest_item(self, graph, items, start_name, target_item):
        queue = deque([(start_name, [start_name])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if target_item in items[current]:
                return current, path

            for neighbor in graph[current]:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return None, []

    def map(self):
        """Mengatur alur untuk mencari material, memvalidasi lokasi, dan memulai farming."""

        # Panggil fungsi craft untuk mendapatkan daftar item yang dibutuhkan
        craft_data = self.craft(info=True)
        if not craft_data:
            self.log("Data craft tidak valid atau kosong.", Fore.RED)
            return

        required_items = [item["iconName"] for item in craft_data]
        self.log(f"Item yang dibutuhkan: {required_items}", Fore.YELLOW)

        # Cek keberadaan item di backpack satu per satu
        backpack_items = []
        for required_item in required_items:
            backpack_item = self.check_backpack(required_item)  # Pastikan ini mengirim nama item untuk pengecekan
            if not backpack_item:
                self.log(f"Item '{required_item}' tidak ditemukan di backpack.", Fore.RED)
                backpack_items.append(required_item)  # Menyimpan item yang tidak ada di backpack
            else:
                self.log(f"Item '{required_item}' ditemukan di backpack.", Fore.GREEN)

        # Jika tidak ada item yang perlu dicari, hentikan proses
        if not backpack_items:
            self.log("Semua item sudah ada di backpack.", Fore.GREEN)
            return

        # Pertimbangkan jarak lokasi item-item yang belum ada di backpack
        graph, items = self.build_graph(self.MAP)

        # Mencari lokasi terdekat untuk item yang belum ada di backpack
        closest_item = None
        shortest_distance = float('inf')  # Set jarak terpendek dengan nilai tak terhingga

        for target_item in backpack_items:
            location, path = self.find_closest_item(graph, items, self.location, target_item)
            if location:
                distance = len(path)  # Misalkan panjang path adalah jarak, bisa disesuaikan dengan logika lainnya
                if distance < shortest_distance:
                    closest_item = target_item
                    shortest_distance = distance

        if closest_item:
            # Setelah mendapatkan item yang paling dekat, kirimkan permintaan untuk item tersebut
            self.log(f"Mencari item '{closest_item}' yang belum ada di backpack...", Fore.YELLOW)
            location, path = self.find_closest_item(graph, items, self.location, closest_item)

            if location:
                self.log(f"Item '{closest_item}' ditemukan di lokasi '{location}' dengan jalur: {path}", Fore.GREEN)

                # Jika lokasi saat ini memiliki item, langsung mulai farming
                if location == self.location:
                    self.start_farming(location)
                else:
                    # Pindah ke lokasi berikutnya dari path dan mulai farming
                    next_location = path[1] if len(path) > 1 else location
                    self.log(f"Berpindah ke lokasi '{next_location}' untuk mencari item '{closest_item}'.", Fore.YELLOW)
                    self.start_farming(next_location)

        else:
            self.log(f"Tidak ada item yang ditemukan di peta.", Fore.RED)


    def start_farming(self, location):
        """Mengirim permintaan untuk memulai farming di lokasi tertentu."""
        farm_url = f"{self.BASE_URL}farm/start"
        headers = {**self.HEADERS, "telegram-data": self.token}
        payload = {"region": location}

        try:
            farm_response = requests.post(farm_url, json=payload, headers=headers)
            if farm_response.status_code == 200:
                self.log(f"Farming berhasil dimulai di lokasi '{location}'.", Fore.GREEN)
            else:
                self.log(f"Farming gagal di lokasi '{location}', status: {farm_response.status_code}, pesan: {farm_response.json().get('errorCode', None)}", Fore.RED)
        except requests.exceptions.RequestException as e:
            self.log(f"Request error saat memulai farming: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Unexpected error saat memulai farming: {e}", Fore.RED)

    def check_backpack(self, item_name):
        """Memeriksa apakah item ada di dalam backpack."""
        backpack_url = f"{self.BASE_URL}backpack"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            backpack_response = requests.get(backpack_url, headers=headers)
            backpack_response.raise_for_status()
            backpack_data = backpack_response.json()

            if backpack_data.get("ok"):
                items_in_backpack = backpack_data.get("result", [])
                for item in items_in_backpack:
                    if item.get("name") == item_name:
                        return True
                return False  
            else:
                self.log(f"Failed to retrieve backpack items: {backpack_data.get('error', 'Unknown error')}", Fore.RED)
                return False

        except requests.exceptions.RequestException as e:
            self.log(f"Backpack request failed: {e}", Fore.RED)
            return False

    def craft(self, info=True):
        req_url = f"{self.BASE_URL}craft/CRAFT_ITEMS"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            if not data.get("ok"):
                raise ValueError("Response indicates failure: 'ok' field is False.")

            result = data.get("result")
            if not result:
                raise ValueError("Data 'result' tidak ditemukan dalam respons.")

            for item in result:
                if item['level'] < 8:
                    if info:
                        self.log(f"Hasil crafting '{item['name']}' memiliki level {item['level']}. Upgrade ke level 8 diperlukan.", Fore.YELLOW)
                    return item['items']
                else:
                    if info:
                        self.log(f"Hasil crafting '{item['name']}' sudah memenuhi syarat (Level {item['level']}).", Fore.GREEN)
                    return item

        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Craft | Unexpected error: {e}", Fore.RED)

    def info(self) -> None:
        req_url = f"{self.BASE_URL}user"

        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()  
            
            data = response.json().get("result")
            if not data:
                raise ValueError("Data 'result' tidak ditemukan dalam respons.")

            self.log(f"Username: {data.get('name', 'Unknown')}", Fore.YELLOW)
            self.log(f"Coins: {data.get('coins', 0)}")
            self.log(f"Tokens: {data.get('tokens', 0)}")
            self.log(f"Tickets: {data.get('tickets', 0)}")
            self.log(f"Power: {data.get('power', 0)}")
            self.log(f"Level: {data.get('level', 'Unknown')}")
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Info | Unexpected error: {e}", Fore.RED)

    def dataCoin(self) -> None:
        req_url = f"{self.BASE_URL}user"
        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()  
            
            data = response.json().get("result")
            if not data:
                raise ValueError("Data 'result' tidak ditemukan dalam respons.")
            
            self.coin = data.get('coins', 0)
            self.ticket = data.get('tickets', 0)
            self.power = data.get('power', 0)
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Data | Unexpected error: {e}", Fore.RED)

    def mission(self) -> None:
        req_url = f"{self.BASE_URL}missions"
        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()  
            
            data = response.json()

            if data.get("ok") and "result" in data:
                missions = data["result"]

                mission_names = [mission["name"] for mission in missions]
                self.log(f"Daftar mission names: {mission_names}", Fore.YELLOW)
                for mission_name in mission_names:
                    mission_start_url = f"{req_url}/start"
                    payload = {"name": mission_name}

                    try:
                        farm_response = requests.post(mission_start_url, json=payload, headers=headers)
                        if farm_response.status_code == 200:
                            self.log(f"Berhasil mengirim ke mission {mission_name} dengan payload {payload}", Fore.GREEN)
                            
                            mission_check_url = f"{req_url}/check"
                            payload = {"name": mission_name}
                            check_response = requests.post(mission_check_url, headers=headers, json=payload)
                            
                            if check_response.status_code == 200:
                                check_data = check_response.json()
                                if check_data.get("ok") and "result" in check_data:
                                    self.log(f"Status mission {mission_name} diperiksa: {check_data['result']['completed']}", Fore.GREEN)
                                else:
                                    self.log(f"Status mission {mission_name} tidak ditemukan atau data tidak valid.", Fore.RED)

                            else:
                                self.log(f"Gagal memeriksa status mission {mission_name}, status: {check_response.status_code}, pesan: {check_response.json().get("errorCode", None)}", Fore.RED)
                        else:
                            self.log(f"Pengiriman gagal untuk mission {mission_name}, status: {farm_response.status_code}", Fore.RED)
                    except Exception as e:
                        self.log(f"Unexpected error while sending mission {mission_name}: {e}", Fore.RED)
            else:
                self.log("Data tidak valid atau kosong.", Fore.RED)
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Mission | Unexpected error: {e}", Fore.RED)
            
    def tasks(self) -> None:
        req_url = f"{self.BASE_URL}tasks"
        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()  
            
            data = response.json()

            if data.get("ok") and "result" in data:
                missions = data["result"]

                customer_name = [mission["customer"] for mission in missions]
                self.log(f"Daftar tasks names: {customer_name}", Fore.YELLOW)
                for customer_name in customer_name:
                        claim_check_url = f"{req_url}/check"
                        payload = {"customer": customer_name}
                        check_response = requests.post(claim_check_url, headers=headers, json=payload)
                        
                        if check_response.status_code == 200:
                            check_data = check_response.json()
                            if check_data.get("ok") and "result" in check_data:
                                self.log(f"Status task {customer_name} | {check_data['result']['status']}", Fore.GREEN)
                            else:
                                self.log(f"Status task {customer_name} tidak ditemukan atau data tidak valid.", Fore.RED)

                        else:
                            self.log(f"Gagal memeriksa status task {customer_name}, status: {check_response.status_code}, pesan: {check_response.json().get("errorCode", None)}", Fore.RED)
            else:
                self.log("Data tidak valid atau kosong.", Fore.RED)
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Tasks | Unexpected error: {e}", Fore.RED)

    def chest(self):
        req_url = f"{self.BASE_URL}chest/validate"
        headers = {**self.HEADERS, "telegram-data": self.token}
        kemungkinan_arah = ["r", "t", "b", "l"]
        kode_saat_ini = random.sample(kemungkinan_arah, len(kemungkinan_arah))
        percobaan = 1

        while True:
            payload = {"code": kode_saat_ini}
            ikon_kode = " ".join(self.ARROW_MAP[k] for k in kode_saat_ini)

            self.log(f"Percobaan {percobaan}: Mengirim kode {ikon_kode}", Fore.BLUE)

            try:
                response = requests.post(req_url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                hasil = data.get("result", {}).get("code", [])

                if all(hasil):
                    self.log(f"Berhasil! Semua kombinasi benar: {ikon_kode}", Fore.GREEN)
                    claim_url = f"{self.BASE_URL}chest/open"
                    claim_res = requests.post(claim_url, headers=headers)
                    if claim_res.status_code == 200:
                        try:
                            check_data = claim_res.json()
                            if check_data.get("ok") and "result" in check_data:
                                item_name = check_data["result"].get("item", "Item tidak dikenal")
                                self.log(f"Berhasil membuka chest! Item yang diperoleh: {item_name}", Fore.GREEN)
                            else:
                                self.log(
                                    f"Data tidak valid atau chest tidak ditemukan. Periksa kembali respons server.",
                                    Fore.RED
                                )
                        except ValueError:
                            self.log(f"Gagal memproses respons JSON dari server.", Fore.RED)
                    else:
                        try:
                            error_message = claim_res.json().get("errorCode", "Kesalahan tidak diketahui")
                        except ValueError:
                            error_message = "Respons server tidak dapat diproses."

                        self.log(
                            f"Gagal memeriksa status chest. Status HTTP: {claim_res.status_code}, Pesan: {error_message}",
                            Fore.RED
                        )
                    break
                else:
                    self.log(f"Kombinasi salah: {ikon_kode}", Fore.RED)

                    for i, res in enumerate(hasil):
                        if not res:
                            kode_saat_ini[i] = random.choice(kemungkinan_arah)

            except requests.exceptions.RequestException as e:
                self.log(f"Kamu sudah mengbuka kunci chestnya", Fore.RED)
                claim_url = f"{self.BASE_URL}chest/open"
                claim_res = requests.post(claim_url, headers=headers)
                if claim_res.status_code == 200:
                    try:
                        check_data = claim_res.json()
                        if check_data.get("ok") and "result" in check_data:
                            item_name = check_data["result"].get("item", "Item tidak dikenal")
                            self.log(f"Berhasil membuka chest! Item yang diperoleh: {item_name}", Fore.GREEN)
                        else:
                            self.log(
                                f"Data tidak valid atau chest tidak ditemukan. Periksa kembali respons server.",
                                Fore.RED
                            )
                    except ValueError:
                        self.log(f"Gagal memproses respons JSON dari server.", Fore.RED)
                else:
                    try:
                        error_message = claim_res.json().get("errorCode", "Kesalahan tidak diketahui")
                    except ValueError:
                        error_message = "Respons server tidak dapat diproses."

                    self.log(
                        f"Gagal memeriksa status chest. Status HTTP: {claim_res.status_code}, Pesan: {error_message}",
                        Fore.RED
                    )
                break
            except ValueError as e:
                self.log(f"Kesalahan data: {e}", Fore.RED)
                break
            except Exception as e:
                self.log(f"Kesalahan tidak terduga: {e}", Fore.RED)
                break
            
            percobaan += 1
    
    def reff(self) -> None:
        req_url = f"{self.BASE_URL}referrals/claim"

        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.post(req_url, headers=headers)
            response.raise_for_status()  
            
            data = response.json().get("result")
            if not data:
                raise ValueError("Data 'result' tidak ditemukan dalam respons.")

            self.log(f"Berhasil mengclaim point reff..", Fore.GREEN)
            self.info()
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed | {response.json().get("errorCode", None)}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Reff | Unexpected error: {e}", Fore.RED)

if __name__ == "__main__":
    chunter = coinhunter()
    index = 0
    max_index = len(chunter.query_list)
    config = chunter.load_config()
    
    while True:
        chunter.log(f"{Fore.GREEN}[LIVEXORDS]===== {index + 1}/{len(chunter.query_list)} =====[LIVEXORDS]{Fore.RESET}")
        chunter.login(index)
        
        if config.get("daily", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] daily: True{Fore.RESET},")
            chunter.daily()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] daily: False{Fore.RESET},")
        
        if config.get("upgrade", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] upgrade: True{Fore.RESET},")
            chunter.upgrade()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] upgrade: False{Fore.RESET},")
        
        if config.get("wheel", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] wheel: True{Fore.RESET},")
            chunter.wheel()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] wheel: False{Fore.RESET},")
        
        if config.get("farm", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] farm: True{Fore.RESET},")
            chunter.farm()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] farm: False{Fore.RESET},")
        
        if config.get("mission", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] mission: True{Fore.RESET},")
            chunter.mission()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] mission: False{Fore.RESET},")
        
        if config.get("tasks", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] tasks: True{Fore.RESET},")
            chunter.tasks()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] tasks: False{Fore.RESET},")
        
        if config.get("chest", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] chest: True{Fore.RESET},")
            chunter.chest()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] chest: False{Fore.RESET},")
        
        if config.get("reff", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] reff: True{Fore.RESET},")
            chunter.reff()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] reff: False{Fore.RESET},")
        
        if index == max_index - 1:
            chunter.log(f"Berhenti untuk loop selanjutnya{Fore.CYAN},")
            chunter.log(f"Tidur selama {config.get("delay_loop")} detik{Fore.CYAN},")
            time.sleep(config.get("delay_loop"))
            index = 0
        else:
            chunter.log(f"Tidur selama {config.get("delay_pergantian_akun")} detik ,sebelum melanjutkan ke akun berikutnya")
            time.sleep(config.get("delay_pergantian_akun"))
            index += 1