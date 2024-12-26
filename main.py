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
            "neighbors": ["checkpoint-charlie", "water-plant"],
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
            "neighbors": ["robbed-truck"],
            "items": ["food-can", "bolt", "zombie-blood"],
        },
        {
            "name": "abandoned-checkpoint",
            "neighbors": ["swampy-ground", "wrecked-house"],
            "items": ["food-can", "copper-wire", "zombie-tooth"],
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

    def banner(self):
        """
        Display the bot's banner with information about the creator and the channel.
        """
        print("🎉 Welcome to Coinhunters Free Bot 🎉")
        print("🚀 Created by LIVEXORDS\n")
        print("📢 Join our channel: t.me/livexordsscript\n")

    def log(self, message, color=Fore.RESET):
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d:%H:%M:%S] |")
            + " "
            + color
            + message
            + Fore.RESET
        )

    def load_config(self):
        """
        Reads configuration from the 'config.json' file.
        Returns the configuration data if successful, or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config_data = json.load(config_file)
                print("✅ Config loaded successfully!")
                return config_data
        except FileNotFoundError:
            print("❌ 'config.json' file not found! Please make sure the file exists.")
            return {}
        except json.JSONDecodeError:
            print("⚠️ Error occurred while reading 'config.json'. Invalid JSON format!")
            return {}

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

    def load_query(self, path_file="query.txt"):
        """
        Loads queries from a text file. If the file is empty or not found, it handles errors gracefully.
        Displays relevant messages to the user.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                print("⚠️ Warning: The file is empty, no queries to load.")
                return []

            print(f"✅ Data Loaded: {len(queries)} queries successfully loaded!")
            return queries

        except FileNotFoundError:
            print(f"❌ Error: The file '{path_file}' was not found!")
            return []
        except Exception as e:
            print(f"⚠️ Error while loading queries: {e}")
            return []

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
                            1 for req_item in required_items if req_item["iconName"] == item["iconName"]
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
                                self.upgrade_to_level_8(item, headers, upgrade_url, upgrade_prices)

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
                            self.upgrade_to_level_8(item, headers, upgrade_url, upgrade_prices)

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
                            self.upgrade_to_level_8(upgrade_item, headers, upgrade_url, upgrade_prices)

                    while True:
                        post_response = requests.post(
                            f"{self.BASE_URL}craft/{self.type_craft}/{self.name_craft}",
                            headers=headers,
                        )
                        if post_response.status_code == 200:
                            self.log(f"🎉 Successfully crafted {self.name_craft}.", Fore.GREEN)
                            break
                        elif post_response.status_code == 400:
                            error_code = post_response.json().get("errorCode", "Unknown Error")
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
                self.log(f"🎉 Successfully upgraded hunter using item: {name}", Fore.GREEN)
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

                reward_type = data.get('userReward', {}).get('type', "Unknown")
                reward_amount = data.get('userReward', {}).get('amount', 0)
                reward_rarity = data.get('userReward', {}).get('rarity', "Unknown")

                self.log(
                    f"🎉 Reward Received! Type: {reward_type}, Amount: {reward_amount}, Rarity: {reward_rarity}",
                    Fore.GREEN
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

            self.log("🎉 Successfully claimed farming rewards! You received items.", Fore.GREEN)
            self.map()

        except requests.exceptions.RequestException as e:
            error_code = response.json().get("errorCode", "Unknown Error Code")
            self.log(f"⚠️ Farming already claimed. Message: {error_code}", Fore.RED)
            self.map()
        except ValueError as e:
            self.log(f"⚠️ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Farm | Unexpected error: {e}", Fore.RED)

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
        """
        Manage the flow to search for materials, validate locations, and start farming.
        """

        # Retrieve crafting data
        craft_data = self.craft(info=True)
        if not craft_data:
            self.log("❌ Crafting data is invalid or empty. Please check the input.", Fore.RED)
            return

        # Consolidate required items by name
        item_counts = {}
        for item in craft_data:
            name = item["iconName"]
            item_counts[name] = item_counts.get(name, 0) + 1

        required_items = [{"name": name, "quantity": quantity} for name, quantity in item_counts.items()]
        self.log(f"📝 Items required: {required_items}", Fore.YELLOW)

        # Check items in the backpack
        missing_items = []
        for required_item in required_items:
            item_name = required_item["name"]
            required_quantity = required_item["quantity"]

            # Use check_backpack to validate quantities
            if not self.check_backpack(item_name, required_quantity):
                self.log(
                    f"⚠️ Item '{item_name}' is insufficient ({required_quantity} required).",
                    Fore.RED,
                )
                missing_items.append(required_item)
            else:
                self.log(f"✅ Item '{item_name}' is available in sufficient quantity.", Fore.GREEN)

        # Stop process if all items are already sufficient
        if not missing_items:
            self.log("🎉 All required items are already available in the backpack.", Fore.GREEN)
            return

        # Build navigation graph
        graph, items = self.build_graph(self.MAP)

        # Find the closest missing item
        closest_item = None
        shortest_distance = float("inf")

        for target_item in missing_items:
            location, path = self.find_closest_item(
                graph, items, self.location, target_item["name"]
            )
            if location:
                distance = len(path)
                if distance < shortest_distance:
                    closest_item = target_item
                    shortest_distance = distance

        # Start farming or move to a new location
        if closest_item:
            self.log(
                f"🔍 Searching for item '{closest_item['name']}' that is still insufficient...",
                Fore.YELLOW,
            )
            location, path = self.find_closest_item(
                graph, items, self.location, closest_item["name"]
            )

            if location:
                self.log(
                    f"📍 Item '{closest_item['name']}' found at location '{location}' with path: {path}",
                    Fore.GREEN,
                )

                if location == self.location:
                    self.start_farming(location)
                else:
                    next_location = path[1] if len(path) > 1 else location
                    self.log(
                        f"➡️ Moving to location '{next_location}' to search for item '{closest_item['name']}'.",
                        Fore.YELLOW,
                    )
                    self.start_farming(next_location)
        else:
            self.log("🚫 No items found on the map. Please check the configuration.", Fore.RED)

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
                item_count = sum(1 for item in items_in_backpack if item.get("iconName") == item_name)

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
        Manage crafting flow, including checking item levels and crafting requirements.
        """
        craft_url = f"{self.BASE_URL}craft/CRAFT_ITEMS"
        legendary_url = f"{self.BASE_URL}craft/LEGENDARY_ITEMS"
        potions_url = f"{self.BASE_URL}craft/POTIONS"
        weapons_url = f"{self.BASE_URL}craft/WEAPONS"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            # Fetch data from APIs
            craft_data = requests.get(craft_url, headers=headers).json()
            legendary_data = requests.get(legendary_url, headers=headers).json()
            potions_data = requests.get(potions_url, headers=headers).json()
            weapons_data = requests.get(weapons_url, headers=headers).json()

            if not craft_data.get("ok"):
                raise ValueError("❌ Failed to fetch data from CRAFT_ITEMS API.")
            if not legendary_data.get("ok"):
                raise ValueError("❌ Failed to fetch data from LEGENDARY_ITEMS API.")
            if not potions_data.get("ok"):
                raise ValueError("❌ Failed to fetch data from POTIONS API.")
            if not weapons_data.get("ok"):
                raise ValueError("❌ Failed to fetch data from WEAPONS API.")

            craft_result = craft_data.get("result", [])
            legendary_map = {item["name"]: item for item in legendary_data.get("result", [])}

            # Process CRAFT_ITEMS
            for item in craft_result:
                if item["level"] < 8:
                    if info:
                        self.log(
                            f"⚠️ Item '{item['name']}' is level {item['level']}. Upgrade to level 8 required.",
                            Fore.YELLOW,
                        )
                        self.name_craft = item["name"]

                    crafting_items = item.get("items", [])
                    for crafting_material in crafting_items:
                        icon_name = crafting_material["iconName"]

                        if icon_name in legendary_map:
                            legendary_recipe = legendary_map[icon_name]
                            if info:
                                self.log(
                                    f"🔧 Material '{icon_name}' required for '{item['name']}'. Crafting via LEGENDARY_ITEMS: '{legendary_recipe['name']}'.",
                                    Fore.CYAN,
                                )
                                self.type_craft = "LEGENDARY_ITEMS"
                            return legendary_recipe["items"]

                        self.type_craft = "CRAFT_ITEMS"
                    return crafting_items
                else:
                    if info:
                        self.log(
                            f"✅ Item '{item['name']}' meets the requirements (Level {item['level']}).",
                            Fore.GREEN,
                        )
                    return item

            if info:
                self.log("🎉 All CRAFT_ITEMS are at level 8. Proceeding to WEAPONS.", Fore.CYAN)

            # Process WEAPONS
            for weapon in weapons_data.get("result", []):
                if weapon["name"] == "vaporizer" and weapon["level"] < 8:
                    if info:
                        self.log(
                            f"⚠️ Weapon '{weapon['name']}' is level {weapon['level']}. Upgrade to level 8 required.",
                            Fore.YELLOW,
                        )
                        self.name_craft = weapon["name"]

                    crafting_items = weapon.get("items", [])
                    for crafting_material in crafting_items:
                        icon_name = crafting_material["iconName"]

                        if icon_name in legendary_map:
                            legendary_recipe = legendary_map[icon_name]
                            if info:
                                self.log(
                                    f"🔧 Material '{icon_name}' required for '{weapon['name']}'. Crafting via LEGENDARY_ITEMS: '{legendary_recipe['name']}'.",
                                    Fore.CYAN,
                                )
                                self.type_craft = "LEGENDARY_ITEMS"
                            return legendary_recipe["items"]

                        self.type_craft = "WEAPONS"
                    return crafting_items

            if info:
                self.log("🎉 All WEAPONS are complete. Proceeding to POTIONS.", Fore.CYAN)

            # Process POTIONS
            for potion in potions_data.get("result", []):
                if info:
                    self.log(f"🧪 Crafting '{potion['name']}' from POTIONS.", Fore.CYAN)
                    self.type_craft = "POTIONS"
                return potion["items"]

        except requests.RequestException as e:
            self.log(f"❌ API request failed: {e}", Fore.RED)
            raise
        except ValueError as e:
            self.log(f"❌ Data validation error: {e}", Fore.RED)
            raise
        except Exception as e:
            self.log(f"❌ Unexpected error during crafting: {e}", Fore.RED)

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
                    self.log(f"🎉 Success! All combinations correct: {code_icons}", Fore.GREEN)
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
                                                            error_message = claim_res.json().get(
                                                                "errorCode", "Unknown error"
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
                                        "❌ Failed to fetch crafting data or data is empty.", Fore.RED
                                    )
                        except ValueError:
                            self.log(
                                f"❌ Failed to process JSON response from server.", Fore.RED
                            )
                    else:
                        self.log("❌ Failed to fetch crafting data or data is empty.", Fore.RED)
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
                                                        error_message = claim_res.json().get(
                                                            "errorCode", "Unknown error"
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
                                    "❌ Failed to fetch crafting data or data is empty.", Fore.RED
                                )
                    except ValueError:
                        self.log(f"❌ Failed to process JSON response from server.", Fore.RED)
                else:
                    self.log("❌ Failed to fetch crafting data or data is empty.", Fore.RED)
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

    while True:
        # Display current progress
        chunter.log(
            f"{Fore.GREEN}[LIVEXORDS]===== {index + 1}/{max_index} =====[LIVEXORDS]{Fore.RESET}"
        )
        chunter.login(index)

        # Daily Task
        if config.get("daily", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] daily: ✅ Enabled{Fore.RESET}")
            chunter.daily()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] daily: ❌ Disabled{Fore.RESET}")

        # Upgrade Task
        if config.get("upgrade", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] upgrade: ✅ Enabled{Fore.RESET}")
            chunter.upgrade()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] upgrade: ❌ Disabled{Fore.RESET}")

        # Wheel Task
        if config.get("wheel", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] wheel: ✅ Enabled{Fore.RESET}")
            chunter.wheel()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] wheel: ❌ Disabled{Fore.RESET}")

        # Farming Task
        if config.get("farm", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] farm: ✅ Enabled{Fore.RESET}")
            chunter.farm()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] farm: ❌ Disabled{Fore.RESET}")

        # Mission Task
        if config.get("mission", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] mission: ✅ Enabled{Fore.RESET}")
            chunter.mission()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] mission: ❌ Disabled{Fore.RESET}")

        # Tasks Task
        if config.get("tasks", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] tasks: ✅ Enabled{Fore.RESET}")
            chunter.tasks()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] tasks: ❌ Disabled{Fore.RESET}")

        # Chest Task
        if config.get("chest", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] chest: ✅ Enabled{Fore.RESET}")
            chunter.chest()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] chest: ❌ Disabled{Fore.RESET}")

        # Referral Task
        if config.get("reff", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] reff: ✅ Enabled{Fore.RESET}")
            chunter.reff()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] reff: ❌ Disabled{Fore.RESET}")

        # Upgrade Task (Again)
        if config.get("upgrade", False):
            chunter.log(f"{Fore.YELLOW}[CONFIG] upgrade: ✅ Enabled{Fore.RESET}")
            chunter.upgrade()
        else:
            chunter.log(f"{Fore.RED}[CONFIG] upgrade: ❌ Disabled{Fore.RESET}")

        # Loop Control
        if index == max_index - 1:
            chunter.log(f"⏳ Pausing for the next loop...", Fore.CYAN)
            chunter.log(f"💤 Sleeping for {config.get('delay_loop')} seconds...", Fore.CYAN)
            time.sleep(config.get("delay_loop"))
            index = 0
        else:
            chunter.log(
                f"💤 Sleeping for {config.get('delay_account_switch')} seconds before moving to the next account...",
                Fore.CYAN
            )
            time.sleep(config.get("delay_account_switch"))
            index += 1
