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
                    if item["level"] >= 8:
                        self.log(f"Item {item['iconName']} telah mencapai level maksimum: {item['level']}", Fore.CYAN)
                        self.burn(id=item.get("id"),name=item.get("iconName"))
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
                        else:
                            self.log(f"Upgrade gagal untuk: {item['iconName']}, Status: {upgrade_response.status_code}, pesan: {upgrade_response.json().get("errorCode", None)}", Fore.RED)
                    else:
                        self.log(f"Saldo tidak cukup untuk upgrade {item['iconName']} ke level {item['level'] + 1} ({self.coin} < {upgrade_cost})", Fore.RED)
                    time.sleep(3)

            except requests.exceptions.RequestException as e:
                self.log(f"Request failed: {e}", Fore.RED)
                break

            except ValueError as e:
                self.log(f"Data error: {e}", Fore.RED)
                break

            except Exception as e:
                self.log(f"Unexpected error: {e}", Fore.RED)
                break
            
            time.sleep(5)

            if not success:
                self.log("Tidak ada item yang berhasil di-upgrade dalam iterasi ini.", Fore.RED)
                break
    
    def burn(self, id: str, name: str) -> None:
        req_url = f"{self.BASE_URL}backpack/burn"
        burn_info_url = f"{self.BASE_URL}backpack/burn-info"

        headers = {**self.HEADERS, "telegram-data": self.token}
        payload = {"itemId": id}

        try:
            response = requests.get(burn_info_url, headers=headers)
            response.raise_for_status()

            burn_data = response.json().get("result")
            if not burn_data:
                self.log("Data 'result' tidak ditemukan dalam respons burn-info.", Fore.RED)
                return

            if burn_data.get("count") != 3:
                response = requests.post(req_url, headers=headers, json=payload)
                response.raise_for_status()

                result = response.json().get("ok")
                if result:
                    self.log(f"Berhasil mengupgrade hunter dengan item {name}", Fore.GREEN)
                    self.info()
                else:
                    self.log(f"Gagal mengupgrade hunter dengan item {name}", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Unexpected error: {e}", Fore.RED)

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
                self.log(f"Unexpected error: {e}", Fore.RED)
            
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
            self.log(f"Unexpected error: {e}", Fore.RED)

    def farm(self) -> None:
        req_url = f"{self.BASE_URL}farm/claim"

        headers = {**self.HEADERS, "telegram-data": self.token}
        
        try:
            response = requests.post(req_url, headers=headers)
            response.raise_for_status()  
            self.log(f"Berhasil mengclaim farming, Kamu mendapatkan item")
            self.map()

        except requests.exceptions.RequestException as e:
            self.log(f"Farm sudah terclaim", Fore.RED)
            self.map()
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Unexpected error: {e}", Fore.RED)

    def map(self):
        """Mengambil nama-nama map, memvalidasi hunters, dan mengirim region ke API."""

        req_url = f"{self.BASE_URL}map"
        headers = {**self.HEADERS, "telegram-data": self.token}

        try:
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data.get("ok") or "result" not in data:
                self.log("Data tidak valid atau kosong.", Fore.RED)
                return

            map_names = [item["name"] for item in data["result"]]
            self.log(f"Maps ditemukan: {map_names}", Fore.YELLOW)

            valid_maps = []
            for map_name in map_names:
                try:
                    map_detail_url = f"{req_url}/{map_name}"
                    map_response = requests.get(map_detail_url, headers=headers)
                    map_response.raise_for_status()
                    map_data = map_response.json()


                    if not map_data.get("ok"):
                        self.log(f"Status 'ok' tidak ditemukan atau False untuk map {map_name}.", Fore.RED)
                        continue
                    if "result" not in map_data:
                        self.log(f"'result' tidak ditemukan dalam data map {map_name}.", Fore.RED)
                        continue

                    hunters = map_data["result"].get("hunters", 0)

                    if hunters < self.power:
                        valid_maps.append(map_name)

                except requests.exceptions.RequestException as req_err:
                    self.log(f"Request error untuk map {map_name}: {req_err}", Fore.RED)
                except KeyError as key_err:
                    self.log(f"Key error untuk map {map_name}: {key_err}", Fore.RED)
                except ValueError as val_err:
                    self.log(f"Value error untuk map {map_name}: {val_err}", Fore.RED)
                except Exception as e:
                    self.log(f"Unexpected error untuk map {map_name}: {e}", Fore.RED)

            if valid_maps:
                attempts = 0
                total_maps = len(valid_maps)
                
                while attempts < total_maps:
                    selected_map = random.choice(valid_maps)
                    farm_url = f"{self.BASE_URL}farm/start"
                    payload = {"region": selected_map}

                    try:
                        farm_response = requests.post(farm_url, json=payload, headers=headers)
                        if farm_response.status_code == 200:
                            self.log(f"Berhasil mengirim ke region: {selected_map}", Fore.GREEN)
                            break
                        else:
                            self.log(f"Pengiriman gagal untuk region {selected_map}, status: {farm_response.status_code}, pesan: {farm_response.json().get("errorCode", None)}", Fore.RED)
                    except Exception as e:
                        self.log(f"Unexpected error while sending region {selected_map}: {e}", Fore.RED)
                    
                    attempts += 1
                
                if attempts == total_maps:
                    self.log("Farm sudah dimulai, telah mencoba semua map.", Fore.YELLOW)

            else:
                self.log("Tidak ada map yang memenuhi kriteria.", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"Unexpected error: {e}", Fore.RED)

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
            self.log(f"Unexpected error: {e}", Fore.RED)

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
            self.log(f"Unexpected error: {e}", Fore.RED)

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
            self.log(f"Unexpected error: {e}", Fore.RED)
            
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
            self.log(f"Unexpected error: {e}", Fore.RED)

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
        
        if index == max_index - 1:
            chunter.log(f"Berhenti untuk loop selanjutnya{Fore.CYAN},")
            chunter.log(f"Tidur selama {config.get("delay_loop")} detik{Fore.CYAN},")
            time.sleep(config.get("delay_loop"))
            index = 0
        else:
            chunter.log(f"Tidur selama {config.get("delay_pergantian_akun")} detik ,sebelum melanjutkan ke akun berikutnya")
            time.sleep(config.get("delay_pergantian_akun"))
            index += 1