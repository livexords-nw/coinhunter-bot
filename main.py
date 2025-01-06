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

    ARROW_MAP = {"r": "➡️", "t": "⬆️", "b": "⬇️", "l": "⬅️"}

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.coin = 0
        self.ticket = 0
        self.power = 0
        self.config = self.load_config()
        self.result = None
        self.location = None
        self.name_craft = None
        self.type_craft = None

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

        headers = {**self.HEADERS, "telegram-data": self.token}
        success = True

        while success:
            success = False

            try:
                response = requests.get(req_url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if not data or "result" not in data:
                    raise ValueError("Data 'result' not found in the response.")

                items = [
                    {
                        "id": item.get("id"),
                        "iconName": item.get("iconName"),
                        "level": item.get("level"),
                        "type": item.get("type"),
                    }
                    for item in data.get("result", [])
                ]

                if not items:
                    self.log("⚠️ No items found in the backpack.", Fore.RED)
                    break

                upgrade_prices = self.get_upgrade_prices()
                required_items = self.craft(info=False)
                required_counts = {item["iconName"]: 0 for item in required_items}

                for item in items:
                    if item["iconName"] in required_counts:
                        required_counts[item["iconName"]] += 1

                for item in items:
                    if item["iconName"] in required_counts:
                        needed_count = sum(
                            1
                            for req_item in required_items
                            if req_item["iconName"] == item["iconName"]
                        )

                        if required_counts[item["iconName"]] <= needed_count:
                            self.log(
                                f"✅ Item '{item['iconName']}' is needed for crafting. Skipping burn or upgrade.",
                                Fore.GREEN,
                            )
                            continue

                        excess_count = required_counts[item["iconName"]] - needed_count

                        if excess_count > 0:
                            if item["level"] < 8:
                                self.log(
                                    f"🔧 Item '{item['iconName']}' will be upgraded to level 8 due to excess count.",
                                    Fore.CYAN,
                                )
                                self.upgrade_to_level_8(
                                    item, headers, upgrade_url, upgrade_prices
                                )

                            self.log(
                                f"❌ Item '{item['iconName']}' will be burned due to excess count.",
                                Fore.YELLOW,
                            )
                            self.burn(id=item["id"], name=item["iconName"])
                            required_counts[item["iconName"]] -= 1

                    else:
                        self.log(
                            f"⚠️ Item '{item['iconName']}' is not needed for crafting.",
                            Fore.MAGENTA,
                        )

                        if item["level"] < 8:
                            self.log(
                                f"🔧 Item '{item['iconName']}' is not needed. Upgrading to level 8.",
                                Fore.CYAN,
                            )
                            self.upgrade_to_level_8(
                                item, headers, upgrade_url, upgrade_prices
                            )

                        self.log(
                            f"❌ Item '{item['iconName']}' is not needed. Burning the item.",
                            Fore.YELLOW,
                        )
                        self.burn(id=item["id"], name=item["iconName"])

                all_items_available = all(
                    required_counts.get(req_item["iconName"], 0)
                    >= sum(
                        1
                        for item in required_items
                        if item["iconName"] == req_item["iconName"]
                    )
                    for req_item in required_items
                )

                if all_items_available:
                    self.log(
                        "🎉 All required items for crafting are available. Upgrading items to level 8...",
                        Fore.BLUE,
                    )

                    for upgrade_item in items:
                        if (
                            upgrade_item["iconName"] in required_counts
                            and upgrade_item["level"] < 8
                        ):
                            self.upgrade_to_level_8(
                                upgrade_item, headers, upgrade_url, upgrade_prices
                            )

                    while True:
                        post_response = requests.post(
                            f"{self.BASE_URL}craft/{self.type_craft}/{self.name_craft}",
                            headers=headers,
                        )
                        if post_response.status_code == 200:
                            self.log(
                                f"🎉 Successfully crafted {self.name_craft}.",
                                Fore.GREEN,
                            )
                            break
                        elif post_response.status_code == 400:
                            error_code = post_response.json().get(
                                "errorCode", "Unknown Error"
                            )
                            self.log(
                                f"❌ Crafting {self.name_craft} failed with message: {error_code}. Retrying...",
                                Fore.RED,
                            )
                            time.sleep(3)
                        else:
                            post_response.raise_for_status()
                    return

                response = requests.get(req_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                items = [
                    {
                        "id": item.get("id"),
                        "iconName": item.get("iconName"),
                        "level": item.get("level"),
                        "type": item.get("type"),
                    }
                    for item in data.get("result", [])
                ]

            except requests.exceptions.RequestException as e:
                self.log(f"❌ Request failed: {e}", Fore.RED)
                break

            except ValueError as e:
                self.log(f"⚠️ Data error: {e}", Fore.RED)
                break

            except Exception as e:
                self.log(f"❌ Upgrade | Unexpected error: {e}", Fore.RED)
                break

            time.sleep(5)

        self.log("🎉 Upgrade process completed.", Fore.GREEN)

    def upgrade_to_level_8(self, item, headers, upgrade_url, upgrade_prices):
        while item["level"] < 8:
            level_prices = upgrade_prices.get(str(item["level"] + 1))
            if not level_prices:
                self.log(
                    f"⚠️ No upgrade price data available for {item['iconName']} to level {item['level'] + 1}.",
                    Fore.YELLOW,
                )
                break

            type_data = level_prices.get(item["type"].lower())
            if not type_data:
                self.log(
                    f"⚠️ No price information for item type {item['type']} for level {item['level'] + 1}.",
                    Fore.YELLOW,
                )
                break

            upgrade_cost = type_data["price"]
            if self.coin < upgrade_cost:
                self.log(
                    f"❌ Insufficient balance to upgrade {item['iconName']} to level {item['level'] + 1}.",
                    Fore.RED,
                )
                break

            payload = {"itemId": item["id"], "useUpgradeScroll": False}
            upgrade_response = requests.post(upgrade_url, json=payload, headers=headers)

            if upgrade_response.status_code == 200:
                upgrade_data = upgrade_response.json()
                if upgrade_data.get("ok"):
                    item["level"] = upgrade_data["result"]["item"]["level"]
                    self.log(
                        f"🎉 Successfully upgraded {item['iconName']} to level {item['level']}.",
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
        """
        graph, items = self.build_graph(self.MAP)

        craft_data = self.craft(info=True)
        if not craft_data:
            self.log(
                "❌ Crafting data is invalid or empty. Please check the input.",
                Fore.RED,
            )
            return

        item_counts = {}
        for item in craft_data:
            name = item["iconName"]
            item_counts[name] = item_counts.get(name, 0) + 1

        required_items = [
            {"name": name, "quantity": quantity}
            for name, quantity in item_counts.items()
        ]
        self.log(f"📝 Items required: {required_items}", Fore.YELLOW)

        missing_items = []
        for required_item in required_items:
            item_name = required_item["name"]
            required_quantity = required_item["quantity"]

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

        for missing_item in missing_items:
            item_name = missing_item["name"]
            required_quantity = missing_item["quantity"]

            best_location, best_path, best_chance = (
                self.find_best_map_for_item_with_graph(
                    graph, items, self.location, item_name, required_quantity
                )
            )

            if best_location:
                self.log(
                    f"📍 Best location found: '{best_location}' with {best_chance:.2f}% chance for item '{item_name}'. Path: {best_path}",
                    Fore.GREEN,
                )
                next_location = best_path[1] if len(best_path) > 1 else best_location
                self.start_farming(next_location)
            else:
                self.log(
                    f"🚫 No suitable location found for item '{item_name}'. Please check the map or item availability.",
                    Fore.RED,
                )

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

    def craft(self, info=True):
        """
        Manage crafting flow based on slot capacity and prioritize backpack.
        """
        weapons_url = f"{self.BASE_URL}craft/WEAPONS"
        craft_url = f"{self.BASE_URL}craft/CRAFT_ITEMS"
        legendary_url = f"{self.BASE_URL}craft/LEGENDARY_ITEMS"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            weapons_data = requests.get(weapons_url, headers=headers).json()
            craft_data = requests.get(craft_url, headers=headers).json()
            legendary_data = requests.get(legendary_url, headers=headers).json()

            if (
                not weapons_data.get("ok")
                or not craft_data.get("ok")
                or not legendary_data.get("ok")
            ):
                raise ValueError("❌ Failed to fetch data from APIs.")

            weapons = weapons_data["result"]
            crafts = craft_data["result"]
            legendary_map = {item["name"]: item for item in legendary_data["result"]}

            # Initialize slot capacity
            slot_capacity = 3
            for item in crafts:
                if item["name"] == "backpack" and item["isUserOwn"]:
                    slot_capacity += item.get("reduce", 0)

            # Check if backpack is owned
            for item in crafts:
                if item["name"] == "backpack" and not item["isUserOwn"]:
                    if info:
                        self.log(
                            f"⚠️ Crafting 'backpack' to increase slot capacity.",
                            Fore.YELLOW,
                        )
                    crafting_items = item["items"]
                    return self.craft_items(crafting_items, legendary_map)

            # Prioritize crafting items within slot capacity
            for item in crafts:
                if item["level"] < 8 and len(item["items"]) <= slot_capacity:
                    if info:
                        self.log(
                            f"⚠️ Crafting '{item['name']}' to level up (current level: {item['level']}).",
                            Fore.CYAN,
                        )
                    crafting_items = item["items"]
                    return self.craft_items(crafting_items, legendary_map)

            # Check fishing_rod crafting
            for weapon in weapons:
                if weapon["name"] == "fishing_rod" and not weapon["isUserOwn"]:
                    if len(weapon["items"]) <= slot_capacity:
                        if info:
                            self.log(
                                f"⚠️ Crafting 'fishing_rod' (slots required: {len(weapon['items'])}).",
                                Fore.CYAN,
                            )
                        crafting_items = weapon["items"]
                        return self.craft_items(crafting_items, legendary_map)

            # Check vaporizer crafting
            for weapon in weapons:
                if weapon["name"] == "vaporizer" and not weapon["isUserOwn"]:
                    if len(weapon["items"]) <= slot_capacity:
                        if info:
                            self.log(
                                f"⚠️ Crafting 'vaporizer' (slots required: {len(weapon['items'])}).",
                                Fore.CYAN,
                            )
                        crafting_items = weapon["items"]
                        return self.craft_items(crafting_items, legendary_map)

            if info:
                self.log(
                    "🎉 All items are crafted or slots are insufficient.", Fore.GREEN
                )

        except requests.RequestException as e:
            self.log(f"❌ API request failed: {e}", Fore.RED)
            raise
        except ValueError as e:
            self.log(f"❌ Data validation error: {e}", Fore.RED)
            raise
        except Exception as e:
            self.log(f"❌ Unexpected error during crafting: {e}", Fore.RED)

    def craft_items(self, items, legendary_map):
        """
        Handle crafting of items, checking for legendary item requirements.
        """
        for material in items:
            icon_name = material["iconName"]
            if icon_name in legendary_map:
                legendary_recipe = legendary_map[icon_name]
                self.log(
                    f"🔧 Crafting material '{icon_name}' from LEGENDARY_ITEMS: '{legendary_recipe['name']}'.",
                    Fore.CYAN,
                )
                return legendary_recipe["items"]
        return items

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
                                craft_items = self.craft(info=False)

                                prizes = info_data["result"]["info"]["prizes"]

                                if craft_items:
                                    # Consolidate required items by name
                                    item_counts = {}
                                    for item in craft_items:
                                        name = item["iconName"]
                                        item_counts[name] = item_counts.get(name, 0) + 1

                                    for prize in prizes:
                                        icon_name = prize["iconName"]
                                        chance = prize["chance"]

                                        required_quantity = item_counts.get(
                                            icon_name, 0
                                        )

                                        if required_quantity > 0:
                                            if self.check_backpack(
                                                icon_name, required_quantity
                                            ):
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
                                                    claim_url = (
                                                        f"{self.BASE_URL}chest/open"
                                                    )
                                                    claim_res = requests.post(
                                                        claim_url, headers=headers
                                                    )
                                                    if claim_res.status_code == 200:
                                                        try:
                                                            check_data = (
                                                                claim_res.json()
                                                            )
                                                            if (
                                                                check_data.get("ok")
                                                                and "result"
                                                                in check_data
                                                            ):
                                                                item_name = check_data[
                                                                    "result"
                                                                ].get(
                                                                    "item",
                                                                    "Unknown item",
                                                                )
                                                                self.log(
                                                                    f"🎁 Chest opened successfully! Item obtained: {item_name}",
                                                                    Fore.GREEN,
                                                                )
                                                            else:
                                                                self.log(
                                                                    f"⚠️ Invalid data or chest not found. Please check server response.",
                                                                    Fore.RED,
                                                                )
                                                        except ValueError:
                                                            self.log(
                                                                f"❌ Failed to process JSON response from server.",
                                                                Fore.RED,
                                                            )
                                                    else:
                                                        try:
                                                            error_message = (
                                                                claim_res.json().get(
                                                                    "errorCode",
                                                                    "Unknown error",
                                                                )
                                                            )
                                                        except ValueError:
                                                            error_message = "Server response could not be processed."

                                                        self.log(
                                                            f"❌ Failed to claim chest. HTTP Status: {claim_res.status_code}, Message: {error_message}",
                                                            Fore.RED,
                                                        )
                                                    break
                                        else:
                                            self.log(
                                                f"⚠️ Item '{icon_name}' not required for crafting.",
                                                Fore.YELLOW,
                                            )
                                else:
                                    self.log(
                                        "❌ Failed to fetch crafting data or data is empty.",
                                        Fore.RED,
                                    )
                        except ValueError:
                            self.log(
                                f"❌ Failed to process JSON response from server.",
                                Fore.RED,
                            )
                    else:
                        self.log(
                            "❌ Failed to fetch crafting data or data is empty.",
                            Fore.RED,
                        )
                else:
                    self.log(f"❌ Incorrect combination: {code_icons}", Fore.RED)

                    for i, res in enumerate(result):
                        if not res:
                            current_code[i] = random.choice(possible_directions)

            except requests.exceptions.RequestException as e:
                self.log(
                    f"⚠️ Chest already unlocked, attempting to open chest.", Fore.RED
                )
                info_url = f"{self.BASE_URL}chest"
                info_res = requests.get(info_url, headers=headers)
                if info_res.status_code == 200:
                    try:
                        info_data = info_res.json()
                        if info_data.get("ok") and "result" in info_data:
                            craft_items = self.craft(info=False)

                            prizes = info_data["result"]["info"]["prizes"]

                            if craft_items:
                                # Consolidate required items by name
                                item_counts = {}
                                for item in craft_items:
                                    name = item["iconName"]
                                    item_counts[name] = item_counts.get(name, 0) + 1

                                for prize in prizes:
                                    icon_name = prize["iconName"]
                                    chance = prize["chance"]

                                    required_quantity = item_counts.get(icon_name, 0)

                                    if required_quantity > 0:
                                        if self.check_backpack(
                                            icon_name, required_quantity
                                        ):
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
                                                claim_res = requests.post(
                                                    claim_url, headers=headers
                                                )
                                                if claim_res.status_code == 200:
                                                    try:
                                                        check_data = claim_res.json()
                                                        if (
                                                            check_data.get("ok")
                                                            and "result" in check_data
                                                        ):
                                                            item_name = check_data[
                                                                "result"
                                                            ].get(
                                                                "item", "Unknown item"
                                                            )
                                                            self.log(
                                                                f"🎁 Chest opened successfully! Item obtained: {item_name}",
                                                                Fore.GREEN,
                                                            )
                                                        else:
                                                            self.log(
                                                                f"⚠️ Invalid data or chest not found. Please check server response.",
                                                                Fore.RED,
                                                            )
                                                    except ValueError:
                                                        self.log(
                                                            f"❌ Failed to process JSON response from server.",
                                                            Fore.RED,
                                                        )
                                                else:
                                                    try:
                                                        error_message = (
                                                            claim_res.json().get(
                                                                "errorCode",
                                                                "Unknown error",
                                                            )
                                                        )
                                                    except ValueError:
                                                        error_message = "Server response could not be processed."

                                                    self.log(
                                                        f"❌ Failed to claim chest. HTTP Status: {claim_res.status_code}, Message: {error_message}",
                                                        Fore.RED,
                                                    )
                                                break
                                    else:
                                        self.log(
                                            f"⚠️ Item '{icon_name}' not required for crafting.",
                                            Fore.YELLOW,
                                        )
                            else:
                                self.log(
                                    "❌ Failed to fetch crafting data or data is empty.",
                                    Fore.RED,
                                )
                    except ValueError:
                        self.log(
                            f"❌ Failed to process JSON response from server.", Fore.RED
                        )
                else:
                    self.log(
                        "❌ Failed to fetch crafting data or data is empty.", Fore.RED
                    )
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