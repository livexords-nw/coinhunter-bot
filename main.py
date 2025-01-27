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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    }

    MAP = [
        {
            "name": "training-camp",
            "neighbors": ["survivor-camp", "haystack-field"],
            "items": ["pizza-slice", "meat", "zoombie-blood"],
        },
        {
            "name": "survivor-camp",
            "neighbors": ["supply-barn"],
            "items": ["pizza-slice", "leather", "zombie-blood"],
        },
        {
            "name": "haystack-field",
            "neighbors": ["supply-barn"],
            "items": ["lucky-clever", "rope", "zombie-tooth", "plastic-bottle"],
        },
        {
            "name": "supply-barn",
            "neighbors": ["survivor-camp", "fuel-depot", "haystack-field"],
            "items": ["meat", "hammer", "zombie-blood"],
        },
        {
            "name": "fuel-depot",
            "neighbors": [
                "supply-barn",
                "checkpoint-charlie",
                "bulldozer-yard",
                "muddy-patch",
            ],
            "items": ["food-can", "gasoline", "plastic-bottle"],
        },
        {
            "name": "checkpoint-charlie",
            "neighbors": [
                "fuel-depot",
                "robbed-truck",
                "muddy-patch",
                "fishing-spot-1",
            ],
            "items": ["food-can", "lucky-clever", "microchip", "zombie-tooth"],
        },
        {
            "name": "bulldozer-yard",
            "neighbors": ["fuel-depot", "muddy-patch", "ruined-house"],
            "items": ["lucky-clever", "wrench", "screw", "zombie-tooth"],
        },
        {
            "name": "muddy-patch",
            "neighbors": [
                "swampy-ground",
                "fuel-depot",
                "bulldozer-yard",
                "checkpoint-charlie",
            ],
            "items": ["lucky-clever", "wood"],
        },
        {
            "name": "robbed-truck",
            "neighbors": [
                "checkpoint-charlie",
                "water-plant",
                "fishing-spot-2",
                "fishing-spot-1",
            ],
            "items": ["food-can", "lucky-clever", "dirty-textile", "zombie-tooth"],
        },
        {
            "name": "ruined-house",
            "neighbors": ["sos-shelter", "bulldozer-yard"],
            "items": ["food-can", "pizza-slice", "rubber", "plastic-bottle"],
        },
        {
            "name": "sos-shelter",
            "neighbors": ["ruined-house", "wrecked-house"],
            "items": ["food-can", "pizza-slice", "lucky-clever", "glass"],
        },
        {
            "name": "wrecked-house",
            "neighbors": ["swampy-ground", "sos-shelter", "abandoned-checkpoint"],
            "items": ["food-can", "plastic-bottle", "super-glue", "dirty-textile"],
        },
        {
            "name": "swampy-ground",
            "neighbors": ["abandoned-checkpoint", "wrecked-house", "muddy-patch"],
            "items": ["swamp-oyster", "chemicals", "zombie-blood"],
        },
        {
            "name": "water-plant",
            "neighbors": ["robbed-truck", "las-vegas"],
            "items": ["food-can", "bolt", "zombie-blood"],
        },
        {
            "name": "abandoned-checkpoint",
            "neighbors": ["swampy-ground", "wrecked-house", "soon-airdrop", "helipad"],
            "items": ["food-can", "copper-wire", "zombie-tooth"],
        },
        {
            "name": "soon-airdrop",
            "neighbors": [
                "abandoned-checkpoint",
                "helipad",
                "helipad",
                "las-vegas",
                "cemetery",
            ],
            "items": ["pizza-slice", "leather", "bamboo_v2"],
        },
        {
            "name": "helipad",
            "neighbors": ["abandoned-checkpoint", "soon-airdrop", "radiostation"],
            "items": ["food-can", "screw", "zombie-blood"],
        },
        {
            "name": "radiostation",
            "neighbors": ["helipad"],
            "items": ["food-can", "copper-wire", "glass", "battery"],
        },
        {
            "name": "las-vegas",
            "neighbors": ["cemetery", "soon-airdrop", "water-plant", "bay"],
            "items": [
                "lucky-clever",
                "fish-hook",
                "tickets",
                "coupon-hunt-5",
                "reset-egg",
            ],
        },
        {
            "name": "cemetery",
            "neighbors": ["las-vegas", "soon-airdrop", "bay", "fishing-spot-3"],
            "items": ["food-can", "zombie-blood", "zombie-tooth", "silver-bar"],
        },
        {
            "name": "fishing-spot-3",
            "neighbors": ["cemetery", "metro-1"],
            "items": ["swamp-oyster", "bolt", "tickets", "coupon-hunt-5"],
        },
        {
            "name": "metro-1",
            "neighbors": ["fishing-spot-3"],
            "items": ["food-can", "zombie-blood", "copper-wire", "wrench"],
        },
        {
            "name": "bay",
            "neighbors": ["cemetery", "las-vegas", "pirates"],
            "items": ["salted-fish", "fish-hook", "microchip"],
        },
        {
            "name": "pirates",
            "neighbors": ["bay", "mines", "west-lighthouse"],
            "items": ["bomb", "pirates-gold", "pirate-rum"],
        },
        {
            "name": "mines",
            "neighbors": ["pirates", "containers"],
            "items": ["food-can", "iron-bar"],
        },
        {
            "name": "containers",
            "neighbors": ["mines"],
            "items": ["salted-fish", "rubber", "fish-hook", "bolt"],
        },
        {
            "name": "west-lighthouse",
            "neighbors": ["pirates"],
            "items": ["food-can", "battery", "fishing-line"],
        },
        {
            "name": "fishing-spot-2",
            "neighbors": ["robbed-truck"],
            "items": ["food-can", "lucky-clever", "dirty-textile", "zombie-tooth"],
        },
        {
            "name": "fishing-spot-1",
            "neighbors": ["robbed-truck", "checkpoint-charlie"],
            "items": ["food-can", "lucky-clever", "microchip", "zombie-tooth"],
        },
    ]

    LEGENDARY_ITEMS_LIST = [
        {
            "alias": "metal-box-legendary",
            "name": "metal-box",
            "price": 20000000,
            "items": [
                {"iconName": "iron-bar", "type": "uncommon", "name": "Iron Bar", "level": 8},
                {"iconName": "iron-bar", "type": "uncommon", "name": "Iron Bar", "level": 8},
                {"iconName": "screw", "type": "rare", "name": "Screw", "level": 8},
                {"iconName": "bolt", "type": "rare", "name": "Bolt", "level": 8},
            ],
        },
        {
            "alias": "silver-box-legendary",
            "name": "silver-box",
            "price": 20000000,
            "items": [
                {"iconName": "silver-bar", "type": "rare", "name": "Silver Bar", "level": 8},
                {"iconName": "silver-bar", "type": "rare", "name": "Silver Bar", "level": 8},
                {"iconName": "screw", "type": "rare", "name": "Screw", "level": 8},
                {"iconName": "bolt", "type": "rare", "name": "Bolt", "level": 8},
            ],
        },
        {
            "alias": "gold-box-legendary",
            "name": "gold-box",
            "price": 20000000,
            "items": [
                {"iconName": "pirates-gold", "type": "epic", "name": "Pirates Gold", "level": 8},
                {"iconName": "pirates-gold", "type": "epic", "name": "Pirates Gold", "level": 8},
                {"iconName": "screw", "type": "rare", "name": "Screw", "level": 8},
                {"iconName": "bolt", "type": "rare", "name": "Bolt", "level": 8},
            ],
        },
        {
            "alias": "chemicals-legendary",
            "name": "chemicals-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "chemicals", "type": "uncommon", "name": "Chemicals", "level": 8},
            ],
        },
        {
            "alias": "zombie-blood-legendary",
            "name": "zombie-blood-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "zombie-blood", "type": "uncommon", "name": "Zombie Blood", "level": 8},
            ],
        },
        {
            "alias": "gasoline-legendary",
            "name": "gasoline-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "gasoline", "type": "uncommon", "name": "Gasoline", "level": 8},
            ],
        },
        {
            "alias": "rubber-legendary",
            "name": "rubber-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "rubber", "type": "uncommon", "name": "Rubber", "level": 8},
            ],
        },
        {
            "alias": "hammer-legendary",
            "name": "hammer-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "silver-box", "type": "legendary", "name": "Silver Box", "level": 8},
                {"iconName": "hammer", "type": "rare", "name": "Hammer", "level": 8},
            ],
        },
        {
            "alias": "screw-legendary",
            "name": "screw-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "silver-box", "type": "legendary", "name": "Silver Box", "level": 8},
                {"iconName": "screw", "type": "rare", "name": "Screw", "level": 8},
            ],
        },
        {
            "alias": "glass-legendary",
            "name": "glass-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "silver-box", "type": "legendary", "name": "Silver Box", "level": 8},
                {"iconName": "glass", "type": "rare", "name": "Glass", "level": 8},
            ],
        },
        {
            "alias": "rope-legendary",
            "name": "rope-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "rope", "type": "uncommon", "name": "Rope", "level": 8},
            ],
        },
        {
            "alias": "dirty-textile-legendary",
            "name": "dirty-textile-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "dirty-textile", "type": "common", "name": "Dirty Textile", "level": 8},
            ],
        },
        {
            "alias": "copper-wire-legendary",
            "name": "copper-wire-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "copper-wire", "type": "uncommon", "name": "Copper Wire", "level": 8},
            ],
        },
        {
            "alias": "microchip-legendary",
            "name": "microchip-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "gold-box", "type": "legendary", "name": "Gold Box", "level": 8},
                {"iconName": "microchip", "type": "epic", "name": "Microchip", "level": 8},
            ],
        },
        {
            "alias": "plastic-bottle-legendary",
            "name": "plastic-bottle-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "silver-box", "type": "legendary", "name": "Silver Box", "level": 8},
                {"iconName": "plastic-bottle", "type": "uncommon", "name": "Plastic Bottle", "level": 8},
            ],
        },
        {
            "alias": "leather-legendary",
            "name": "leather-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "leather", "type": "uncommon", "name": "Leather", "level": 8},
            ],
        },
        {
            "alias": "wood-legendary",
            "name": "wood-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "wood", "type": "uncommon", "name": "Wood", "level": 8},
            ],
        },
        {
            "alias": "wrench-legendary",
            "name": "wrench-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "gold-box", "type": "legendary", "name": "Gold Box", "level": 8},
                {"iconName": "wrench", "type": "epic", "name": "Wrench", "level": 8},
            ],
        },
        {
            "alias": "super-glue-legendary",
            "name": "super-glue-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "metal-box", "type": "legendary", "name": "Metal Box", "level": 8},
                {"iconName": "super-glue", "type": "uncommon", "name": "Super Glue", "level": 8},
            ],
        },
        {
            "alias": "battery-legendary",
            "name": "battery-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "gold-box", "type": "legendary", "name": "Gold Box", "level": 8},
                {"iconName": "battery", "type": "epic", "name": "Battery", "level": 8},
            ],
        },
        {
            "alias": "bolt-legendary",
            "name": "bolt-legendary",
            "price": 20000000,
            "items": [
                {"iconName": "silver-box", "type": "legendary", "name": "Silver Box", "level": 8},
                {"iconName": "bolt", "type": "rare", "name": "Bolt", "level": 8},
            ],
        },
    ]

    ARROW_MAP = {"r": "➡️", "t": "⬆️", "b": "⬇️", "l": "⬅️"}

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.coin = 0
        self.ticket = 0
        self.power = 0
        self.result = None
        self.location = None
        self.name_craft = None
        self.type_craft = None
        self.level_item_craft = 0
        self.protected_items = []

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 CoinHunters Free Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |")
            + " "
            + color
            + message
            + Fore.RESET
        )

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log("❌ Failed to parse config.json. Please check the file format.", Fore.RED)
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        """Login to the API using the query list."""
        try:
            queries = self.query_list

            if index < 0 or index >= len(queries):
                raise IndexError(
                    f"⚠️ Index {index} is invalid. Query list contains only {len(queries)} items."
                )

            req_url = f"{self.BASE_URL}user"
            headers = {**self.HEADERS, "telegram-data": queries[index]}

            response = requests.get(req_url, headers=headers)
            response.raise_for_status()

            data = response.json().get("result")
            if not data:
                raise ValueError("❌ 'result' data not found in the response.")

            self.log("✅ Login successful!", Fore.GREEN)
            self.log(f"👤 Username: {data.get('name', 'Unknown')}", Fore.YELLOW)
            self.log(f"💰 Coins: {data.get('coins', 0)}")
            self.log(f"🎟️ Tickets: {data.get('tickets', 0)}")
            self.log(f"🔋 Power: {data.get('power', 0)}")
            self.log(f"🏆 Level: {data.get('level', 'Unknown')}")

            self.token = queries[index]
            self.coin = data.get("coins", 0)
            self.ticket = data.get("tickets", 0)
            self.power = data.get("power", 0)
            self.location = data.get("currentRegion", "Unknown")

        except IndexError as e:
            self.log(f"❌ Error: {e}", Fore.RED)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)

    def get_upgrade_prices(self) -> dict:
        """Fetch upgrade price data from the API."""
        upgrade_url = f"{self.BASE_URL}backpack/items-upgrades"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.get(upgrade_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            if not data.get("ok"):
                raise ValueError("❌ Failed to fetch upgrade price data.")

            self.log("✅ Successfully fetched upgrade price data.", Fore.GREEN)
            return data.get("result", {})
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)

        return {}

    def upgrade(self) -> None:
        """Manages backpack items by checking crafting, upgrading, and burning."""
        req_url = f"{self.BASE_URL}backpack"
        upgrade_url = f"{self.BASE_URL}backpack/upgrade"
        upgrade_prices = self.get_upgrade_prices()

        headers = {**self.HEADERS, "telegram-data": self.token}

        def search_missing_items(item_name, crafting_data, depth=1):
            """
            Traverse items down to their base materials, prioritizing legendary items.
            If all materials are non-legendary and unavailable in the backpack, return the parent item name if all materials are available; otherwise, return None.
            """
            indent = "  " * depth
            self.log(f"{indent}🔍 Checking item '{item_name}' (Depth: {depth})", Fore.MAGENTA)

            # Check if the item is in the backpack
            if self.check_backpack(item_name):
                self.log(f"{indent}✅ Item '{item_name}' is already in the backpack.", Fore.CYAN)
                return None

            # If the item is legendary, process its materials
            if item_name.endswith("-legendary"):
                legendary_item = next((item for item in crafting_data if item.get("name") == item_name), None)
                if not legendary_item:
                    # Search in LEGENDARY_ITEMS_LIST
                    legendary_item = next((item for item in self.LEGENDARY_ITEMS_LIST if item.get("alias") == item_name), None)

                if legendary_item:
                    self.log(f"{indent}📜 Found legendary item '{item_name}'. Checking its materials.", Fore.GREEN)
                    materials_key = "materials" if legendary_item.get("materials") else "items"
                    all_available = True
                    for material in legendary_item.get(materials_key, []):
                        if not self.check_backpack(material.get("name")):
                            missing = search_missing_items(material.get("name"), crafting_data, depth + 1)
                            if missing:
                                all_available = False
                    return item_name if all_available else None
                else:
                    self.log(f"{indent}🚫 No recipe found for legendary item '{item_name}'.", Fore.RED)
                    return None

            # Check non-legendary items directly in the backpack
            if self.check_backpack(item_name):
                self.log(f"{indent}✅ Non-legendary item '{item_name}' found in the backpack.", Fore.CYAN)
                return None

            # If item is not found in the backpack and has a recipe, process it
            recipe = next((r for r in crafting_data if r.get("name") == item_name), None)
            if recipe and recipe.get("materials"):
                self.log(f"{indent}📜 Found recipe for '{item_name}'. Checking its materials.", Fore.GREEN)
                all_available = True
                for material in recipe.get("materials", []):
                    if not self.check_backpack(material.get("name")):
                        if material.get("name", "").endswith("-legendary"):
                            self.log(f"{indent}📜 Material '{material.get('name')}' is legendary. Diving deeper.", Fore.BLUE)
                            missing = search_missing_items(material.get("name"), crafting_data, depth + 1)
                            if missing:
                                all_available = False
                        else:
                            self.log(f"{indent}🚫 Missing non-legendary material '{material.get('name')}' in backpack.", Fore.RED)
                            all_available = False
                return item_name if all_available else None

            self.log(f"{indent}🚫 No recipe or entry found for '{item_name}'.", Fore.RED)
            return None

        def craft_or_upgrade_item(item_name):
            """Attempts to craft or upgrade an item, including legendary items."""
            while True:
                if item_name == None:
                    break

                if item_name.endswith("-legendary"):
                    post_response = requests.post(
                        f"{self.BASE_URL}craft/LEGENDARY_ITEMS/{item_name}",
                        headers=headers,
                    )
                else:
                    if self.level_item_craft > 0:
                        post_response = requests.post(
                            f"{self.BASE_URL}craft/{self.type_craft}/{self.name_craft}/upgrade",
                            headers=headers,
                        )
                    else:
                        post_response = requests.post(
                            f"{self.BASE_URL}craft/{self.type_craft}/{self.name_craft}",
                            headers=headers,
                        )

                if post_response.status_code == 200:
                    self.log(f"🎉 Successfully processed '{item_name}'.", Fore.GREEN)
                    break
                elif post_response.status_code == 400:
                    error_code = post_response.json().get("errorCode", "Unknown Error")
                    self.log(f"❌ Processing failed for '{item_name}' with message: {error_code}. Retrying...", Fore.RED)
                    time.sleep(3)
                else:
                    post_response.raise_for_status()

        # Fungsi untuk mendapatkan bahan yang diperlukan untuk item
        def get_required_materials(item_name, crafting_data, backpack_items, legendary_items_list, depth=1, visited=None):
            visited = visited or set()
            if item_name in visited:
                return set()  # Hindari infinite loop jika ada siklus crafting.

            visited.add(item_name)
            materials = set()

            # Cek apakah item_name adalah bahan crafting (dengan resep)
            recipe = next((r for r in crafting_data if r.get("name") == item_name), None)
            if recipe:
                # Jika item legendary ada di backpack dan juga ada dalam resep, lindungi item tersebut
                if recipe["type"] == "legendary" and item_name in backpack_items:
                    materials.add(item_name)
                else:
                    for material in recipe.get("materials", []):
                        material_name = material.get("name")
                        materials.add(material_name)  # Tambahkan bahan ke daftar
                        
                        # Jika material memiliki sufiks '-legendary', bongkar item legendary
                        if material_name.endswith("-legendary"):
                            # Cari data dalam LEGENDARY_ITEMS_LIST berdasarkan alias
                            legendary_item = next((item for item in legendary_items_list if item["alias"] == material_name), None)
                            if legendary_item:
                                # Tambahkan semua bahan dari legendary item ke dalam materials
                                for item in legendary_item["items"]:
                                    materials.add(item["iconName"])  # Tambahkan bahan dari legendary item ke daftar bahan
                            else:
                                # Rekursi jika bahan belum ada di backpack
                                if material_name not in backpack_items:
                                    materials.update(get_required_materials(material_name, crafting_data, backpack_items, legendary_items_list, depth + 1, visited))
                        else:
                            # Jika bahan non-legendary ada di backpack dan diperlukan dalam resep, lindungi bahan tersebut
                            if material_name in backpack_items:
                                materials.add(material_name)

            return materials


        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data or "result" not in data:
                raise ValueError("Data 'result' not found in the response.")

            items = data.get("result", [])
            crafting_data = self.craft(info=False)  # Get crafting recipes

            # Ambil daftar item di backpack
            backpack_items = {item.get("iconName") for item in items if item.get("iconName")}

            # Hitung semua bahan yang diperlukan secara rekursif
            all_required_items = set()
            for recipe in crafting_data:
                all_required_items.add(recipe["name"])  # Nama item utama juga perlu dimasukkan
                all_required_items.update(get_required_materials(recipe["name"], crafting_data, backpack_items, self.LEGENDARY_ITEMS_LIST))

            # Hitung jumlah item yang dimiliki berdasarkan nama (iconName)
            item_counts = {item.get("iconName"): item.get("quantity", 0) for item in items if item.get("iconName")}

            for item in items:
                item_name = item.get("iconName")
                if not item_name:
                    continue

                item_level = item.get("level", 1)  # Default level to 1 if not specified.

                # Hitung jumlah yang dibutuhkan untuk crafting (termasuk bahan rekursif)
                required_quantity = sum(
                    1
                    for recipe in crafting_data
                    if recipe.get("materials")
                    for material in recipe.get("materials", [])
                    if material.get("name") == item_name
                )
                owned_quantity = item_counts.get(item_name, 0)

                self.log(f"Owned: {owned_quantity}")
                self.log(f"All required items: {all_required_items}")

                # Jika item legendary ada di backpack dan ada di resep, tidak perlu diupgrade atau dibakar
                if item_name in all_required_items and item_name.endswith("-legendary") and item_name in backpack_items:
                    self.log(f"✔️ Legendary item '{item_name}' is protected from burning/upgrading.")
                    continue  # Skip burning or upgrading for protected items

                # Jangan upgrade item yang dibutuhkan untuk crafting (termasuk bahan-bahan non-legendary yang ada di backpack)
                if item_name not in all_required_items and item_level < 8:
                    self.upgrade_to_level_8(item, headers, upgrade_url, upgrade_prices)

                # Bakar item jika tidak termasuk dalam resep (meskipun sudah ada di backpack)
                if item_name not in all_required_items:
                    self.log(
                        f"🔥 Burning unnecessary item '{item_name}' (Owned: {owned_quantity}, Not in crafting recipes).",
                        Fore.YELLOW,
                    )
                    for _ in range(owned_quantity):
                        self.burn(id=item.get("id"), name=item_name)
                    continue

                # Bakar item jika jumlahnya melebihi kebutuhan crafting
                if owned_quantity > required_quantity:
                    excess_quantity = max(0, owned_quantity - required_quantity)
                    self.log(
                        f"🔥 Burning {excess_quantity} excess of '{item_name}' (Owned: {owned_quantity}, Required: {required_quantity}).",
                        Fore.YELLOW,
                    )
                    for _ in range(excess_quantity):
                        self.burn(id=item.get("id"), name=item_name)

            # Melanjutkan proses upgrade dan crafting
            for craft_item in crafting_data:
                missing_item = search_missing_items(craft_item.get("name"), crafting_data)
                if missing_item:
                    self.log(f"⚠️ Missing item: '{missing_item}'. Attempting to craft.", Fore.YELLOW)

                    # Ensure materials are upgraded to level 8 before crafting
                    self.upgrade_to_level_8(missing_item, headers, upgrade_url, upgrade_prices)

                    craft_or_upgrade_item(missing_item)

            # Proses legendary items jika diperlukan
            for item in crafting_data:
                if item.get("name", "").endswith("-legendary"):
                    self.log(f"⚒️ Processing legendary item: '{item.get('name')}'.", Fore.CYAN)
                    missing_item = search_missing_items(item.get("name"), crafting_data)
                    if missing_item:
                        self.log(f"⚠️ Missing material for legendary item: '{missing_item}'. Attempting to craft.", Fore.YELLOW)

                        # Ensure materials are upgraded to level 8 before crafting
                        self.upgrade_to_level_8(missing_item, headers, upgrade_url, upgrade_prices)

                        craft_or_upgrade_item(missing_item)

            # Proses selesai
            self.log("🎉 Upgrade process completed.", Fore.GREEN)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)

        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)

        except Exception as e:
            self.log(f"❌ Upgrade | Unexpected error: {e}", Fore.RED)

    def upgrade_to_level_8(self, item, headers, upgrade_url, upgrade_prices):
        """
        Upgrade a single item to level 8 if it is not already at level 8.
        """
        self.log(f"🔧 Upgrading item: {item}")
        while item["level"] < 8:
            next_level = item["level"] + 1

            # Cek data harga upgrade untuk level berikutnya
            level_prices = upgrade_prices.get(str(next_level))  # Pastikan level sebagai string
            if not level_prices:
                self.log(
                    f"⚠️ No upgrade price data available for {item['iconName']} to level {next_level}.",
                    Fore.YELLOW,
                )
                break

            # Cek harga berdasarkan tipe item (konversi ke huruf kecil)
            type_data = level_prices.get(item["type"].lower())
            if not type_data:
                self.log(
                    f"⚠️ No price information for item type '{item['type']}' for level {next_level}.",
                    Fore.YELLOW,
                )
                break

            upgrade_cost = type_data["price"]
            if self.coin < upgrade_cost:
                self.log(
                    f"❌ Insufficient balance to upgrade {item['iconName']} to level {next_level}. Cost: {upgrade_cost}, Coins: {self.coin}.",
                    Fore.RED,
                )
                break

            payload = {"itemId": item["id"], "useUpgradeScroll": False}
            upgrade_response = requests.post(upgrade_url, json=payload, headers=headers)

            if upgrade_response.status_code == 200:
                upgrade_data = upgrade_response.json()
                if upgrade_data.get("ok"):
                    item["level"] = upgrade_data["result"]["item"]["level"]
                    self.coin = upgrade_data["result"]["user"]["coins"]
                    self.log(
                        f"🎉 Successfully upgraded {item['iconName']} to level {item['level']}. Remaining coins: {self.coin}.",
                        Fore.GREEN,
                    )
                else:
                    self.log(
                        f"❌ Upgrade failed: {upgrade_data.get('message', 'Unknown error')}.",
                        Fore.RED,
                    )
                    break
            elif upgrade_response.status_code == 400:
                self.log(
                    f"⚠️ Upgrade failed for {item['iconName']} (Bad Request). Status: {upgrade_response.status_code}.",
                    Fore.RED,
                )
                self.log("🔧 Please wait before trying again...", Fore.YELLOW)
                time.sleep(5)
            else:
                self.log(
                    f"❌ Upgrade failed for {item['iconName']}. Status: {upgrade_response.status_code}.",
                    Fore.RED,
                )
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
                self.log(
                    f"🎉 Successfully upgraded hunter using item: {name}", Fore.GREEN
                )
                self.info()
            else:
                self.log(f"❌ Failed to upgrade hunter using item: {name}", Fore.RED)

        except requests.exceptions.RequestException as e:
            error_code = response.json().get("errorCode", "Unknown Error Code")
            self.log(f"❌ Request failed | Error Code: {error_code}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Burn | Unexpected error: {e}", Fore.RED)

    def wheel(self) -> None:
        req_url = f"{self.BASE_URL}wheel/roll"
        headers = {**self.HEADERS, "telegram-data": self.token}

        while self.ticket > 0:
            try:
                response = requests.post(req_url, headers=headers)
                response.raise_for_status()

                data = response.json().get("result")
                if not data:
                    raise ValueError("No 'result' data found in the response.")

                reward_type = data.get("userReward", {}).get("type", "Unknown")
                reward_amount = data.get("userReward", {}).get("amount", 0)
                reward_rarity = data.get("userReward", {}).get("rarity", "Unknown")

                self.log(
                    f"🎉 Reward Received! Type: {reward_type}, Amount: {reward_amount}, Rarity: {reward_rarity}",
                    Fore.GREEN,
                )

            except requests.exceptions.RequestException as e:
                self.log(f"❌ Request failed: {e}", Fore.RED)
            except ValueError as e:
                self.log(f"⚠️ Data error: {e}", Fore.RED)
            except Exception as e:
                self.log(f"❌ Wheel | Unexpected error: {e}", Fore.RED)

            # Update the coin data after each roll
            self.dataCoin()

    def daily(self) -> None:
        req_url = f"{self.BASE_URL}daily-bonus/claim"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.post(req_url, headers=headers)
            response.raise_for_status()

            data = response.json().get("ok")
            if not data:
                raise ValueError("No 'result' data found in the response.")

            if data is True:
                self.log("🎉 Successfully claimed daily bonus!", Fore.GREEN)

        except requests.exceptions.RequestException as e:
            error_code = response.json().get("errorCode", "Unknown Error Code")
            self.log(f"⚠️ Daily bonus already claimed. Message: {error_code}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Daily | Unexpected error: {e}", Fore.RED)

    def farm(self) -> None:
        req_url = f"{self.BASE_URL}farm/claim"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.post(req_url, headers=headers)
            response.raise_for_status()

            self.log(
                "🎉 Successfully claimed farming rewards! You received items.",
                Fore.GREEN,
            )
            self.map()

        except requests.exceptions.RequestException as e:
            error_code = response.json().get("errorCode", "Unknown Error Code")
            self.log(f"⚠️ Farming already claimed. Message: {error_code}", Fore.RED)
            self.map()
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Farm | Unexpected error: {e}", Fore.RED)
    
    def api_request(self, endpoint, params=None):
        """
        Generalized API request handler.
        """
        headers = {**self.HEADERS, "telegram-data": self.token}
        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}", headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"❌ API request to {endpoint} failed: {response.text}", Fore.RED)
                return None
        except Exception as e:
            self.log(f"❌ Exception during API request: {str(e)}", Fore.RED)
            return None

    def build_graph(self, data):
        """
        Build the graph and item dictionaries from the map data.
        """
        graph = {}
        items = {}
        for item in data:
            graph[item["name"]] = item["neighbors"]
            items[item["name"]] = item["items"]
        return graph, items

    def check_backpack(self, item_name, required_quantity):
        """
        Check if the backpack contains the required quantity of an item.
        """
        response = self.api_request("backpack")
        if not response or not response.get("ok"):
            self.log(f"❌ Failed to retrieve backpack data.", Fore.RED)
            return False

        backpack_items = response.get("result", [])
        item_count = sum(1 for item in backpack_items if item["iconName"] == item_name)
        return item_count >= required_quantity

    def check_weapon(self, weapon_name, required_level):
        """
        Check if the required weapon is available at the required level.
        """
        response = self.api_request("craft/WEAPONS")
        if not response or not response.get("ok"):
            self.log(f"❌ Failed to retrieve weapons data.", Fore.RED)
            return False

        weapons = response.get("result", [])
        for weapon in weapons:
            if (
                weapon["name"] == weapon_name
                and weapon["isUserOwn"]
                and weapon["level"] >= required_level
            ):
                return True
        return False

    def find_all_locations_with_item(self, graph, items, current_location, target_item):
        """
        Find all locations where the target item can be farmed and return the paths to those locations.
        """
        from collections import deque

        visited = set()
        queue = deque([(current_location, [])])
        locations_with_item = []

        while queue:
            location, path = queue.popleft()

            if location in visited:
                continue
            visited.add(location)

            current_path = path + [location]

            if target_item in items.get(location, {}):
                locations_with_item.append((location, current_path))

            for neighbor in graph.get(location, []):
                if neighbor not in visited:
                    queue.append((neighbor, current_path))

        return locations_with_item

    def find_best_map_for_item_with_graph(
        self, graph, items, current_location, target_item, required_quantity
    ):
        """
        Find the best map for farming the target item based on the highest drop chance and graph navigation.
        """
        best_location = None
        best_path = []
        best_chance = 0
        shortest_distance = float("inf")

        locations_with_item = self.find_all_locations_with_item(
            graph, items, current_location, target_item
        )

        for location, path in locations_with_item:
            response = self.api_request(f"map/{location}")
            if not response or not response.get("ok"):
                self.log(f"❌ Failed to retrieve map data for '{location}'.", Fore.RED)
                continue

            map_info = response["result"]
            drop_items = map_info.get("drop", [])
            requirements = map_info.get("require", [])

            available_chance = 0
            for drop_item in drop_items:
                if drop_item["iconName"] == target_item:
                    available_chance = drop_item["chance"]

            unmet_requirements = []
            for req in requirements:
                if req["type"] == "weapon":
                    if not self.check_weapon(req["name"], req["level"]):
                        unmet_requirements.append(req)
                elif req["type"] == "item":
                    if not self.check_backpack(req["itemName"], req["amount"]):
                        unmet_requirements.append(req)

            if unmet_requirements:
                self.log(
                    f"🚫 Location '{location}' skipped due to unmet requirements: {unmet_requirements}.",
                    Fore.RED,
                )
                continue

            if available_chance > best_chance or (
                available_chance == best_chance and len(path) < shortest_distance
            ):
                best_location = location
                best_path = path
                best_chance = available_chance
                shortest_distance = len(path)

        return best_location, best_path, best_chance

    def map(self):
        """
        Manage the flow to search for materials, validate locations, and start farming.
        Prioritize digging into sub-materials if legendary items are missing.
        """
        try:
            # Build graph and item list from MAP
            graph, items = self.build_graph(self.MAP)
            if not graph or not items:
                self.log("❌ Failed to build graph or item list from map data.", Fore.RED)
                return

            # Retrieve crafting data
            craft_data = self.craft(info=False)
            if not craft_data:
                self.log(
                    "❌ Crafting data is invalid or empty. Please check the input.",
                    Fore.RED,
                )
                return

            # Count the required items
            item_counts = {}
            for item in craft_data:
                if "name" in item and item["name"]:  # Validate key
                    name = item["name"]
                    item_counts[name] = item_counts.get(name, 0) + 1
                else:
                    self.log(f"⚠️ Missing or invalid 'name' in item: {item}", Fore.YELLOW)

            required_items = [
                {"iconName": name, "quantity": quantity}
                for name, quantity in item_counts.items()
            ]
            self.log(f"📝 Items required: {required_items}", Fore.YELLOW)

            # Check for missing items in the backpack
            missing_items = []
            for required_item in required_items:
                item_name = required_item["iconName"]
                required_quantity = required_item["quantity"]

                # Check item availability
                if not self.check_backpack(item_name, required_quantity):
                    self.log(
                        f"⚠️ Item '{item_name}' is insufficient ({required_quantity} required).",
                        Fore.RED,
                    )
                    missing_items.append(required_item)
                else:
                    self.log(
                        f"✅ Item '{item_name}' is available in sufficient quantity.",
                        Fore.GREEN,
                    )

            if not missing_items:
                self.log(
                    "🎉 All required items are already available in the backpack.",
                    Fore.GREEN,
                )
                return

            # Process missing materials recursively
            def search_missing_items(item_name):
                """
                Traverse items down to their base materials, prioritizing legendary items.
                If all materials are non-legendary and unavailable in the backpack, immediately return the first missing item.
                """
                def process_item(current_item, depth=1):
                    indent = "  " * depth
                    self.log(f"{indent}🔍 Checking item '{current_item}' (Depth: {depth})", Fore.MAGENTA)

                    # Base case: Check if the item is available in the backpack
                    if self.check_backpack(current_item):
                        self.log(f"{indent}✅ Item '{current_item}' is already in the backpack.", Fore.CYAN)
                        return None  # All materials are available, proceed to the next item

                    # If the item is legendary, process its materials
                    if current_item.endswith("-legendary"):
                        legendary_item = next((item for item in self.LEGENDARY_ITEMS_LIST if item["alias"] == current_item), None)
                        if legendary_item:
                            self.log(f"{indent}📜 Found legendary item '{current_item}' in LEGENDARY_ITEMS_LIST. Checking its materials.", Fore.GREEN)
                            for material in legendary_item["items"]:
                                material_name = material["iconName"]
                                material_type = material["type"]

                                self.log(f"{indent}  🔍 Checking legendary material '{material_name}' (type: {material_type})", Fore.YELLOW)
                                
                                # Process legendary materials first
                                missing = process_item(material_name if material_type != "legendary" else material_name + "-legendary", depth + 1)
                                if missing:
                                    return missing  # Return immediately if any non-legendary material is missing
                            return None  # All materials for this legendary item are processed
                        else:
                            self.log(f"{indent}🚫 No entry found for legendary item '{current_item}' in LEGENDARY_ITEMS_LIST.", Fore.RED)
                            return current_item  # Treat the item as missing if not found in the list

                    # Search for the recipe of non-legendary items
                    recipe = next((r for r in craft_data if r["name"] == current_item), None)
                    if recipe and "materials" in recipe:
                        self.log(f"{indent}📜 Found recipe for '{current_item}'. Checking its materials.", Fore.GREEN)
                        for material in recipe["materials"]:
                            material_name = material["name"]
                            material_type = material["type"]

                            self.log(f"{indent}  🔍 Checking material '{material_name}' (type: {material_type})", Fore.YELLOW)
                            missing = process_item(material_name if material_type != "legendary" else material_name + "-legendary", depth + 1)
                            if missing:
                                return missing  # Return immediately if any non-legendary material is missing
                        return None  # All materials for this non-legendary item are processed
                    else:
                        self.log(f"{indent}🚫 No recipe found for '{current_item}'.", Fore.RED)
                        return current_item  # Treat the item as missing if no recipe is found

                # Start from the main item
                missing_item = process_item(item_name)
                if missing_item:
                    self.log(f"⚠️ Missing item: '{missing_item}'. Returning to prevent unnecessary stacking.", Fore.RED)
                    return missing_item  # Return the first missing item
                self.log(f"✅ All materials for '{item_name}' checked successfully.", Fore.GREEN)
                return None  # All materials are found

            # Handle all missing items
            for missing_item in missing_items:
                item_name = missing_item["iconName"]

                # Search for the item recursively
                missing_material = search_missing_items(item_name)

                if missing_material:
                    # Find the best location for the missing item
                    best_location, best_path, best_chance = (
                        self.find_best_map_for_item_with_graph(
                            graph, items, self.location, missing_material, 1
                        )
                    )

                    if best_location and best_path:
                        self.log(
                            f"📍 Best location found: '{best_location}' with {best_chance:.2f}% chance for item '{missing_material}'. Path: {best_path}",
                            Fore.GREEN,
                        )
                        # Start farming at the next location
                        next_location = best_path[1] if len(best_path) > 1 else best_location
                        self.start_farming(next_location)
                    else:
                        self.log(
                            f"🚫 No suitable location found for item '{missing_material}'. Please check the map or item availability.",
                            Fore.RED,
                        )

        except Exception as e:
            self.log(f"❗ Error in map process: {str(e)}", Fore.RED)

    def start_farming(self, location):
        """
        Sends a request to start farming at a specific location.

        :param location: The location where farming should start.
        """
        farm_url = f"{self.BASE_URL}farm/start"
        headers = {**self.HEADERS, "telegram-data": self.token}
        payload = {"region": location}

        try:
            # Send POST request to start farming
            farm_response = requests.post(farm_url, json=payload, headers=headers)

            if farm_response.status_code == 200:
                self.log(
                    f"🌱 Farming successfully started at location '{location}'! Happy farming! 🌾",
                    Fore.GREEN,
                )
            else:
                error_message = farm_response.json().get("errorCode", "Unknown error")
                self.log(
                    f"❌ Farming failed at location '{location}'. Status: {farm_response.status_code}, Error: {error_message}",
                    Fore.RED,
                )
        except requests.exceptions.RequestException as e:
            self.log(
                f"❗ Request error while trying to start farming at '{location}': {e}",
                Fore.RED,
            )
        except Exception as e:
            self.log(
                f"⚠️ Unexpected error while starting farming at '{location}': {e}",
                Fore.RED,
            )

    def check_backpack(self, item_name, required_quantity=1):
        """
        Check if the required quantity of a specific item is available in the backpack.

        :param item_name: The name of the item to check.
        :param required_quantity: The required number of occurrences of the item (default: 1).
        :return: True if the required quantity is met, False otherwise.
        """
        backpack_url = f"{self.BASE_URL}backpack"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            # Fetch data from the backpack API
            backpack_response = requests.get(backpack_url, headers=headers)
            backpack_response.raise_for_status()
            backpack_data = backpack_response.json()

            if backpack_data.get("ok"):
                # Count occurrences of the item in the backpack
                items_in_backpack = backpack_data.get("result", [])
                item_count = sum(
                    1 for item in items_in_backpack if item.get("iconName") == item_name
                )

                # Check if the count meets the required quantity
                if item_count >= required_quantity:
                    self.log(
                        f"✅ Item '{item_name}' is available in sufficient quantity! ({item_count}/{required_quantity})",
                        Fore.GREEN,
                    )
                    return True
                else:
                    self.log(
                        f"⚠️ Item '{item_name}' found {item_count} times, but not enough ({item_count}/{required_quantity}).",
                        Fore.YELLOW,
                    )
                    return False
            else:
                self.log(
                    f"❌ Failed to retrieve backpack data: {backpack_data.get('error', 'Unknown error')}.",
                    Fore.RED,
                )
                return False
        except requests.RequestException as e:
            self.log(f"❗ Request error while checking the backpack: {e}", Fore.RED)
            return False

    def get_backpack(self):
        backpack_url = f"{self.BASE_URL}backpack"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            backpack_data = requests.get(backpack_url, headers=headers).json()
            if not backpack_data.get("ok"):
                raise ValueError("❌ Gagal mengambil data dari API Backpack.")
            return backpack_data
        except requests.RequestException as e:
            self.log(f"❌ Gagal request API: {e}", Fore.RED)
            raise
        except ValueError as e:
            self.log(f"❌ Error validasi data: {e}", Fore.RED)
            raise
        except Exception as e:
            self.log(f"❌ Error tak terduga saat mengambil data backpack: {e}", Fore.RED)

    def craft(self, info=True):
        """
        Initiates the crafting process by fetching recipes from the API
        and printing detailed recipes, including legendary items if required.
        """
        backpackinfo_url = f"{self.BASE_URL}user/config"
        def get_crafting_data():
            """
            Fetch crafting data from the API.
            """
            weapons_url = f"{self.BASE_URL}craft/WEAPONS"
            craft_url = f"{self.BASE_URL}craft/CRAFT_ITEMS"
            headers = {**self.HEADERS, "telegram-data": self.token}

            try:
                # Fetch data from the API
                weapons_data = requests.get(weapons_url, headers=headers).json()
                craft_data = requests.get(craft_url, headers=headers).json()

                if not weapons_data.get("ok") or not craft_data.get("ok"):
                    raise ValueError("❌ Failed to retrieve data from the API. Check API response.")

                return weapons_data["result"], craft_data["result"]

            except requests.RequestException as e:
                self.log(f"❌ API request failed: {e}", Fore.RED)
                raise
            except ValueError as e:
                self.log(f"❌ Data validation error: {e}", Fore.RED)
                raise
            except Exception as e:
                self.log(f"❌ Unexpected error while fetching crafting data: {e}", Fore.RED)
                raise

        def process_legendary_item(item_name, materials, parent_item=None):
            """
            Process legendary materials and add them to the material list while maintaining context.
            """
            base_name = item_name.replace("-legendary", "")
            
            # Retrieve legendary item based on context
            legendary_item = next(
                (item for item in self.LEGENDARY_ITEMS_LIST if item["alias"] == f"{item_name}-legendary"),
                None
            )
            if legendary_item:
                sub_materials = []
                for mat in legendary_item["items"]:
                    # If the material is legendary, process it further
                    if mat["type"] == "legendary":
                        process_legendary_item(mat["iconName"], sub_materials, item_name)
                    else:
                        # Add regular material to sub-materials
                        sub_materials.append({
                            "name": mat["iconName"],
                            "type": mat["type"],
                            "parent": item_name
                        })

                # Add the legendary item after all its sub-materials are processed
                materials.append({
                    "name": f"{base_name}-legendary",
                    "type": "legendary",
                    "materials": sub_materials,
                    "parent": parent_item
                })

        def get_full_recipe(item_name, crafting_list):
            """
            Retrieve the full recipe for a specific item, including legendary materials.
            """
            item = next((i for i in crafting_list if i["name"] == item_name), None)
            if not item:
                self.log(f"❌ Item '{item_name}' not found.", Fore.RED)
                return []

            materials = []
            for mat in item["items"]:
                if mat["type"] == "legendary":  # Process legendary items
                    process_legendary_item(mat["iconName"], materials, item_name)
                else:
                    # Ensure only unprocessed materials are added
                    if mat["iconName"] not in [m["name"] for m in materials]:
                        materials.append({"name": mat["iconName"], "type": mat["type"], "parent": item_name})

            return materials

        def log_and_return_recipe(item_name, crafting_list):
            """
            Retrieve and log the full recipe.
            """
            recipe = get_full_recipe(item_name, crafting_list)
            
            # Format JSON neatly and structurally
            recipe_json = json.dumps(recipe, indent=4)
            
            if info:
                self.log(f"📝 Full recipe for item '{item_name}':\n{recipe_json}", Fore.GREEN)

            return recipe

        # Fetch crafting data
        weapons, crafts = get_crafting_data()

        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.get(backpackinfo_url, headers=headers)
            response.raise_for_status()
            max_backpack_size = response.json().get("result", {}).get("maxBackpackSize", 0)
        except Exception as e:
            self.log(f"❌ Error fetching backpack info: {e}", Fore.RED)
            max_backpack_size = 0

        def can_craft(items):
            return len(items) <= max_backpack_size

        # Check weapon crafting first
        for weapon in weapons:
            if weapon["name"] in ["fishing_rod", "vaporizer"] and not weapon["isUserOwn"]:
                weapon_level = weapon["level"] if weapon["name"] != "fishing_rod" else min(weapon["level"], 3)
                if info:
                    self.log(f"⚠️ Crafting '{weapon['name']}' for weapon requirements.", Fore.CYAN)
                
                if can_craft(weapon["items"]):
                    self.type_craft = "WEAPONS"
                    self.level_item_craft = weapon_level - 1 if not weapon["isUserOwn"] else weapon_level
                    self.name_craft = weapon["name"]
                    return log_and_return_recipe(weapon["name"], weapons)
                else:
                    self.log(f"❌ Not enough backpack space for '{weapon['name']}'!", Fore.RED)

        # Prioritize crafting items
        for item in crafts:
            if item["level"] < 8:
                if info:
                    self.log(f"⚠️ Crafting '{item['name']}' to increase its level.", Fore.CYAN)
                if can_craft(item.get("items", [])):
                    self.type_craft = "CRAFT_ITEMS"
                    self.level_item_craft = item['level'] - 1 if not weapon["isUserOwn"] else item['level']
                    self.name_craft = item['name']
                    return log_and_return_recipe(item["name"], crafts)
                else:
                    self.log(f"❌ Not enough backpack space for '{item['name']}'!", Fore.RED)

            if item["name"] == "backpack" and not item["isUserOwn"]:
                if info:
                    self.log(f"⚠️ Crafting 'backpack' to increase slot capacity.", Fore.YELLOW)
                if can_craft(item.get("items", [])):
                    self.type_craft = "CRAFT_ITEMS"
                    self.level_item_craft = item['level'] - 1 if not weapon["isUserOwn"] else item['level']
                    self.name_craft = item['name']
                    return log_and_return_recipe(item["name"], crafts)
                else:
                    self.log(f"❌ Not enough backpack space for 'backpack'!", Fore.RED)

        if info:
            self.log("🎉 All items are already crafted or no new crafting is required.", Fore.GREEN)
        return []

    def info(self) -> None:
        req_url = f"{self.BASE_URL}user"

        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()

            data = response.json().get("result")
            if not data:
                raise ValueError("The 'result' field was not found in the response.")

            self.log(f"🔑 Username: {data.get('name', 'Unknown')}", Fore.YELLOW)
            self.log(f"💰 Coins: {data.get('coins', 0)}")
            self.log(f"🌐 Tokens: {data.get('tokens', 0)}")
            self.log(f"🎫 Tickets: {data.get('tickets', 0)}")
            self.log(f"⚛️ Power: {data.get('power', 0)}")
            self.log(f"👤 Level: {data.get('level', 'Unknown')}")

        except requests.exceptions.RequestException as e:
            self.log(f"⚠️ Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"🛠️ Info | Unexpected error: {e}", Fore.RED)

    def dataCoin(self) -> None:
        req_url = f"{self.BASE_URL}user"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()

            data = response.json().get("result")
            if not data:
                raise ValueError("Data 'result' tidak ditemukan dalam respons.")

            self.coin = data.get("coins", 0)
            self.ticket = data.get("tickets", 0)
            self.power = data.get("power", 0)

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
                self.log(f"📋 Mission Names: {mission_names}", Fore.YELLOW)
                for mission_name in mission_names:
                    mission_start_url = f"{req_url}/start"
                    payload = {"name": mission_name}

                    try:
                        farm_response = requests.post(
                            mission_start_url, json=payload, headers=headers
                        )
                        if farm_response.status_code == 200:
                            self.log(
                                f"✅ Successfully started mission '{mission_name}' with payload: {payload}",
                                Fore.GREEN,
                            )

                            mission_check_url = f"{req_url}/check"
                            payload = {"name": mission_name}
                            check_response = requests.post(
                                mission_check_url, headers=headers, json=payload
                            )

                            if check_response.status_code == 200:
                                check_data = check_response.json()
                                if check_data.get("ok") and "result" in check_data:
                                    self.log(
                                        f"🎯 Mission '{mission_name}' status checked: Completed - {check_data['result']['completed']}",
                                        Fore.GREEN,
                                    )
                                else:
                                    self.log(
                                        f"⚠️ Mission '{mission_name}' status not found or invalid data.",
                                        Fore.RED,
                                    )

                            else:
                                self.log(
                                    f"❌ Failed to check status for mission '{mission_name}', Status Code: {check_response.status_code}, Error: {check_response.json().get('errorCode', 'Unknown')}.",
                                    Fore.RED,
                                )
                        else:
                            self.log(
                                f"❌ Failed to start mission '{mission_name}', Status Code: {farm_response.status_code}.",
                                Fore.RED,
                            )
                    except Exception as e:
                        self.log(
                            f"🔧 Unexpected error while processing mission '{mission_name}': {e}",
                            Fore.RED,
                        )
            else:
                self.log("⚠️ Invalid or empty data.", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"🔧 Mission | Unexpected error: {e}", Fore.RED)

    def tasks(self) -> None:
        req_url = f"{self.BASE_URL}tasks"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if data.get("ok") and "result" in data:
                tasks = data["result"]

                customer_names = [task["customer"] for task in tasks]
                self.log(f"📋 Task Names: {customer_names}", Fore.YELLOW)
                for customer_name in customer_names:
                    claim_check_url = f"{req_url}/check"
                    payload = {"customer": customer_name}
                    check_response = requests.post(
                        claim_check_url, headers=headers, json=payload
                    )

                    if check_response.status_code == 200:
                        check_data = check_response.json()
                        if check_data.get("ok") and "result" in check_data:
                            self.log(
                                f"🎯 Task '{customer_name}' status checked: {check_data['result']['status']}",
                                Fore.GREEN,
                            )
                        else:
                            self.log(
                                f"⚠️ Task '{customer_name}' status not found or invalid data.",
                                Fore.RED,
                            )

                    else:
                        self.log(
                            f"❌ Failed to check status for task '{customer_name}', Status Code: {check_response.status_code}, Error: {check_response.json().get('errorCode', 'Unknown')}.",
                            Fore.RED,
                        )
            else:
                self.log("⚠️ Invalid or empty data.", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"🔧 Tasks | Unexpected error: {e}", Fore.RED)

    def chest(self):
        req_url = f"{self.BASE_URL}chest/validate"
        headers = {**self.HEADERS, "telegram-data": self.token}
        possible_directions = ["r", "t", "b", "l"]
        current_code = random.sample(possible_directions, len(possible_directions))
        attempt = 1

        while True:
            payload = {"code": current_code}
            code_icons = " ".join(self.ARROW_MAP[k] for k in current_code)

            self.log(f"🔄 Attempt {attempt}: Sending code {code_icons}", Fore.BLUE)

            try:
                response = requests.post(req_url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                result = data.get("result", {}).get("code", [])

                if all(result):
                    self.log(
                        f"🎉 Success! All combinations correct: {code_icons}",
                        Fore.GREEN,
                    )
                    info_url = f"{self.BASE_URL}chest"
                    info_res = requests.get(info_url, headers=headers)
                    if info_res.status_code == 200:
                        try:
                            info_data = info_res.json()
                            if info_data.get("ok") and "result" in info_data:
                                craft_items = self.craft(info=False)  # Get craft items

                                if craft_items:
                                    # Consolidate required items by name
                                    item_counts = {}
                                    for item in craft_items:
                                        name = item["iconName"]
                                        item_counts[name] = item_counts.get(name, 0) + 1

                                    prizes = info_data["result"]["info"]["prizes"]
                                    for prize in prizes:
                                        icon_name = prize["iconName"]
                                        chance = prize["chance"]
                                        required_quantity = item_counts.get(icon_name, 0)

                                        if required_quantity > 0:
                                            if self.check_backpack(icon_name, required_quantity):
                                                self.log(
                                                    f"✅ Item '{icon_name}' is sufficient in backpack ({required_quantity} required).",
                                                    Fore.GREEN,
                                                )
                                            else:
                                                if chance < 50:
                                                    self.log(
                                                        f"⚠️ Item '{icon_name}' has a low chance ({chance}%).",
                                                        Fore.RED,
                                                    )
                                                else:
                                                    self.log(
                                                        f"✅ Item '{icon_name}' has a high chance ({chance}%), claiming chest.",
                                                        Fore.GREEN,
                                                    )
                                                    claim_url = f"{self.BASE_URL}chest/open"
                                                    claim_res = requests.post(claim_url, headers=headers)
                                                    if claim_res.status_code == 200:
                                                        try:
                                                            check_data = claim_res.json()
                                                            if check_data.get("ok") and "result" in check_data:
                                                                item_name = check_data["result"].get("item", "Unknown item")
                                                                self.log(f"🎁 Chest opened successfully! Item obtained: {item_name}", Fore.GREEN)
                                                            else:
                                                                self.log("⚠️ Invalid data or chest not found. Please check server response.", Fore.RED)
                                                        except ValueError:
                                                            self.log("❌ Failed to process JSON response from server.", Fore.RED)
                                                    else:
                                                        try:
                                                            error_message = claim_res.json().get("errorCode", "Unknown error")
                                                        except ValueError:
                                                            error_message = "Server response could not be processed."
                                                        self.log(f"❌ Failed to claim chest. HTTP Status: {claim_res.status_code}, Message: {error_message}", Fore.RED)
                                                    break
                                        else:
                                            self.log(f"⚠️ Item '{icon_name}' not required for crafting.", Fore.YELLOW)
                                else:
                                    self.log("❌ Failed to fetch crafting data or data is empty.", Fore.RED)
                            else:
                                self.log("❌ Failed to fetch chest data or data is empty.", Fore.RED)
                        except ValueError:
                            self.log("❌ Failed to process JSON response from server.", Fore.RED)
                    else:
                        self.log("❌ Failed to fetch chest data.", Fore.RED)
                else:
                    self.log(f"❌ Incorrect combination: {code_icons}", Fore.RED)
                    for i, res in enumerate(result):
                        if not res:
                            current_code[i] = random.choice(possible_directions)

            except requests.exceptions.RequestException as e:
                self.log("⚠️ Chest already unlocked, attempting to open chest.", Fore.RED)
                info_url = f"{self.BASE_URL}chest"
                info_res = requests.get(info_url, headers=headers)
                if info_res.status_code == 200:
                    try:
                        info_data = info_res.json()
                        if info_data.get("ok") and "result" in info_data:
                            craft_items = self.craft(info=False)  # Get craft items

                            if craft_items:
                                # Consolidate required items by name
                                item_counts = {}
                                for item in craft_items:
                                    name = item["iconName"]
                                    item_counts[name] = item_counts.get(name, 0) + 1

                                prizes = info_data["result"]["info"]["prizes"]
                                for prize in prizes:
                                    icon_name = prize["iconName"]
                                    chance = prize["chance"]
                                    required_quantity = item_counts.get(icon_name, 0)

                                    if required_quantity > 0:
                                        if self.check_backpack(icon_name, required_quantity):
                                            self.log(
                                                f"✅ Item '{icon_name}' is sufficient in backpack ({required_quantity} required).",
                                                Fore.GREEN,
                                            )
                                        else:
                                            if chance < 50:
                                                self.log(
                                                    f"⚠️ Item '{icon_name}' has a low chance ({chance}%).",
                                                    Fore.RED,
                                                )
                                            else:
                                                self.log(
                                                    f"✅ Item '{icon_name}' has a high chance ({chance}%), claiming chest.",
                                                    Fore.GREEN,
                                                )
                                                claim_url = f"{self.BASE_URL}chest/open"
                                                claim_res = requests.post(claim_url, headers=headers)
                                                if claim_res.status_code == 200:
                                                    try:
                                                        check_data = claim_res.json()
                                                        if check_data.get("ok") and "result" in check_data:
                                                            item_name = check_data["result"].get("item", "Unknown item")
                                                            self.log(f"🎁 Chest opened successfully! Item obtained: {item_name}", Fore.GREEN)
                                                        else:
                                                            self.log("⚠️ Invalid data or chest not found. Please check server response.", Fore.RED)
                                                    except ValueError:
                                                        self.log("❌ Failed to process JSON response from server.", Fore.RED)
                                                else:
                                                    try:
                                                        error_message = claim_res.json().get("errorCode", "Unknown error")
                                                    except ValueError:
                                                        error_message = "Server response could not be processed."
                                                    self.log(f"❌ Failed to claim chest. HTTP Status: {claim_res.status_code}, Message: {error_message}", Fore.RED)
                                                break
                                    else:
                                        self.log(f"⚠️ Item '{icon_name}' not required for crafting.", Fore.YELLOW)
                            else:
                                self.log("❌ Failed to fetch crafting data or data is empty.", Fore.RED)
                    except ValueError:
                        self.log("❌ Failed to process JSON response from server.", Fore.RED)
                else:
                    self.log("❌ Failed to fetch chest data.", Fore.RED)
                break
            except ValueError as e:
                self.log(f"⚠️ Data error: {e}", Fore.RED)
                break
            except Exception as e:
                self.log(f"🔧 Unexpected error: {e}", Fore.RED)
                break

            attempt += 1

    def reff(self) -> None:
        req_url = f"{self.BASE_URL}referrals/claim"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.post(req_url, headers=headers)
            response.raise_for_status()

            data = response.json().get("result")
            if not data:
                raise ValueError("No 'result' data found in the response.")

            self.log("🎉 Successfully claimed referral points!", Fore.GREEN)
            self.info()

        except requests.exceptions.RequestException as e:
            error_code = response.json().get("errorCode", "Unknown Error Code")
            self.log(f"❌ Request failed | Error Code: {error_code}", Fore.RED)
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)

if __name__ == "__main__":
    chunter = coinhunter()
    index = 0
    max_index = len(chunter.query_list)
    config = chunter.load_config()

    chunter.log("🎉 [LIVEXORDS] === Welcome to CoinHunter Automation === [LIVEXORDS]", Fore.YELLOW)
    chunter.log(f"📂 Loaded {max_index} accounts from query list.", Fore.YELLOW)

    while True:
        # Display current account info
        current_account = chunter.query_list[index]
        display_account = (
            current_account[:10] + "..." if len(current_account) > 10 else current_account
        )
        chunter.log(f"👤 [ACCOUNT] Processing account {index + 1}/{max_index}: {display_account}", Fore.YELLOW)

        chunter.login(index)
        # chunter.log(str(chunter.craft()))

        # Task execution
        chunter.log("🛠️ Starting task execution...")
        tasks = {
            "daily": "🌞 Daily Task",
            "upgrade": "🔧 Upgrade Task",
            "wheel": "🎡 Spin the Wheel",
            "farm": "🌾 Farming Resources",
            "mission": "🚀 Mission Progress",
            "tasks": "📋 General Tasks",
            "chest": "💼 Chest Collection",
            "reff": "🤝 Referral Program",
        }

        for task_key, task_name in tasks.items():
            task_status = config.get(task_key, False)
            chunter.log(
                f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
                Fore.YELLOW if task_status else Fore.RED,
            )

            if task_status:
                chunter.log(f"🔄 Executing {task_name}...")
                getattr(chunter, task_key)()

        # Loop Control
        if index == max_index - 1:
            chunter.log("🔁 All accounts processed. Restarting loop.", Fore.CYAN)
            chunter.log(
                f"⏳ Sleeping for {config.get('delay_loop', 30)} seconds before restarting.",
                Fore.CYAN,
            )
            time.sleep(config.get("delay_loop", 30))
            index = 0
        else:
            chunter.log(
                f"➡️ Switching to the next account in {config.get('delay_account_switch', 10)} seconds.",
                Fore.CYAN,
            )
            time.sleep(config.get("delay_account_switch", 10))
            index += 1