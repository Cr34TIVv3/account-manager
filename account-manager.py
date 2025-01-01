import sys
import json
import requests
from prettytable import PrettyTable
from tqdm import tqdm

# Constants
DB_FILE = ".accounts.json"
API_BASE_URL = "https://{region}.api.riotgames.com"
HEADERS = {
    "X-Riot-Token": "RGAPI-d85aa07e-22d4-4c4e-8ff2-2ddc7ea8f268"
}
SHIFT_VALUE = 3  # Dummy encryption shift value

# Functions
def load_database():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_database(data):
    with open(DB_FILE, "w") as file:
        json.dump(data, file, indent=4)

def dummy_encrypt(data):
    return ''.join(chr((ord(char) + SHIFT_VALUE) % 256) for char in data)

def dummy_decrypt(data):
    return ''.join(chr((ord(char) - SHIFT_VALUE) % 256) for char in data)

def fetch_account(region, name, tag):
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching account data: {response.status_code}")
        sys.exit(1)

def fetch_summoner_by_puuid(region, puuid):
    url = f"{API_BASE_URL}/lol/summoner/v4/summoners/by-puuid/{puuid}".format(region=region)
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching summoner data: {response.status_code}")
        sys.exit(1)

def fetch_rank(region, summoner_id):
    url = f"{API_BASE_URL}/lol/league/v4/entries/by-summoner/{summoner_id}".format(region=region)
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        ranks = response.json()
        soloq = next((entry for entry in ranks if entry["queueType"] == "RANKED_SOLO_5x5"), None)
        flex = next((entry for entry in ranks if entry["queueType"] == "RANKED_FLEX_SR"), None)
        return {
            "soloq": {
                "tier": soloq["tier"] if soloq else "Unranked",
                "rank": soloq["rank"] if soloq else "-",
                "league_points": soloq["leaguePoints"] if soloq else 0,
                "wins": soloq["wins"] if soloq else 0,
                "losses": soloq["losses"] if soloq else 0
            },
            "flex": {
                "tier": flex["tier"] if flex else "Unranked",
                "rank": flex["rank"] if flex else "-",
                "league_points": flex["leaguePoints"] if flex else 0,
                "wins": flex["wins"] if flex else 0,
                "losses": flex["losses"] if flex else 0
            }
        }
    else:
        print(f"Error fetching rank data: {response.status_code}")
        sys.exit(1)

def add_account(region, name_tag, username, password):
    name, tag = name_tag.split("#")
    db = load_database()

    # Fetch account data
    account = fetch_account(region, name, tag)
    summoner = fetch_summoner_by_puuid(region, account["puuid"])
    rank = fetch_rank(region, summoner["id"])

    # Add to database
    db[name_tag] = {
        "region": region,
        "username": dummy_encrypt(username),
        "password": dummy_encrypt(password),
        "level": summoner["summonerLevel"],
        "rank": rank["soloq"]["tier"] if rank else "Unranked",
        "tier": rank["soloq"]["rank"] if rank else "-",
        "league_points": rank["soloq"]["league_points"] if rank else 0,
        "wins": rank["soloq"]["wins"] if rank else 0,
        "losses": rank["soloq"]["losses"] if rank else 0,
        "flex_rank": rank["flex"]["tier"] if rank else "Unranked",
        "flex_tier": rank["flex"]["rank"] if rank else "-",
        "flex_league_points": rank["flex"]["league_points"] if rank else 0,
        "flex_wins": rank["flex"]["wins"] if rank else 0,
        "flex_losses": rank["flex"]["losses"] if rank else 0
    }

    save_database(db)
    print(f"Account {name_tag} added successfully!")

def rank_tier_key(details):
    rank_order = ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
    tier_order = ["I", "II", "III", "IV"]
    rank = details["rank"]
    tier = details["tier"]
    # Sort by level if rank is "Unranked"
    if rank == "Unranked":
        return (len(rank_order), -details["level"])
    return (rank_order.index(rank) if rank in rank_order else len(rank_order),
            tier_order.index(tier) if tier in tier_order else len(tier_order))

def resync_accounts():
    db = load_database()

    # Resync all accounts with a progress bar
    with tqdm(total=len(db), desc="Resyncing accounts", unit="account") as pbar:
        for name_tag, details in db.items():
            region = details["region"]
            try:
                account = fetch_account(region, *name_tag.split("#"))
                summoner = fetch_summoner_by_puuid(region, account["puuid"])
                rank = fetch_rank(region, summoner["id"])

                # Update account details in the database
                details["level"] = summoner["summonerLevel"]
                details["rank"] = rank["soloq"]["tier"] if rank else "Unranked"
                details["tier"] = rank["soloq"]["rank"] if rank else "-"
                details["league_points"] = rank["soloq"]["league_points"] if rank else 0
                details["wins"] = rank["soloq"]["wins"] if rank else 0
                details["losses"] = rank["soloq"]["losses"] if rank else 0
                details["flex_rank"] = rank["flex"]["tier"] if rank else "Unranked"
                details["flex_tier"] = rank["flex"]["rank"] if rank else "-"
                details["flex_league_points"] = rank["flex"]["league_points"] if rank else 0
                details["flex_wins"] = rank["flex"]["wins"] if rank else 0
                details["flex_losses"] = rank["flex"]["losses"] if rank else 0
            except Exception as e:
                print(f"Failed to update account {name_tag}: {e}")
            pbar.update(1)

    save_database(db)
    print("All accounts have been resynced.")

def show_accounts(region, output_file=None, unsafe=False):
    db = load_database()
    table = PrettyTable()
    table.field_names = ["Name#Tag", "Region", "Level", "SOLOQ Rank", "LP", "Wins", "Losses", "FLEX Rank", "Flex LP", "Flex Wins", "Flex Losses", "Username", "Password"]

    sorted_accounts = sorted(db.items(), key=lambda item: rank_tier_key(item[1]))

    for name_tag, details in sorted_accounts:
        if region == "all" or details["region"] == region:
            username = dummy_decrypt(details["username"]) if unsafe else "[HIDDEN]"
            password = dummy_decrypt(details["password"]) if unsafe else "[HIDDEN]"
            soloq_rank = f"{details['rank']} {details['tier']}".strip() if details['tier'] != "-" else details['rank']
            flex_rank = f"{details['flex_rank']} {details['flex_tier']}".strip() if details['flex_tier'] != "-" else details['flex_rank']
            table.add_row([
                name_tag,
                details["region"],
                details["level"],
                soloq_rank,
                details["league_points"],
                details["wins"],
                details["losses"],
                flex_rank,
                details["flex_league_points"],
                details["flex_wins"],
                details["flex_losses"],
                username,
                password
            ])

    if output_file:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(table.get_string())
        print(f"Accounts exported to {output_file}")
    else:
        print(table)

# Command Line Interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python account-manager.py <command> [args]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "add":
        if len(sys.argv) != 6:
            print("Usage: python account-manager.py add <region> <name#tag> <username> <password>")
            sys.exit(1)
        add_account(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    elif command == "resync":
        resync_accounts()

    elif command == "show":
        if len(sys.argv) not in [3, 4, 5, 6]:
            print("Usage: python account-manager.py show <region> [-o <output_file>] [--unsafe]")
            sys.exit(1)

        region = sys.argv[2]
        output_file = None
        unsafe = "--unsafe" in sys.argv
        if "-o" in sys.argv:
            output_file = sys.argv[sys.argv.index("-o") + 1]

        show_accounts(region, output_file, unsafe)

    else:
        print(f"Unknown command: {command}")
