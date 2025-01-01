
# Account Manager Script Documentation

## Setting Up the Environment

To use the `account-manager.py` script, you must first set up your environment:

```bash
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
deactivate
```

### Riot API Token
You need a valid Riot Games API token to interact with the Riot API. Set your token in the script as follows:

Example:
```
X-Riot-Token
RGAPI-d85aa07e-22d4-4c4e-8ff2-2ddc7ea8f268
```

## Supported Riot API Endpoints

### Platform Status
Check the status of the platform:
```bash
https://eun1.api.riotgames.com/lol/status/v4/platform-data
```
Example Response:
```
ok
```

### Fetch Account by Riot ID
Retrieve account details using Riot ID:
```bash
https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/<name>/<tag>
```
Example:
```bash
https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/stilouu/EUNE
```
Response:
```json
{
    "puuid": "BupC5nJLoxqEGQyUgPPySQcyeNXbk9P-A4CLprFDxMa-7ik4dXfX3XHqx97UvtEz8CFiNrExp2tA6Q",
    "gameName": "stilouu",
    "tagLine": "EUNE"
}
```

### Fetch Account by PUUID
Retrieve account details using PUUID:
```bash
https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/<puuid>
```
Example:
```bash
https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/BupC5nJLoxqEGQyUgPPySQcyeNXbk9P-A4CLprFDxMa-7ik4dXfX3XHqx97UvtEz8CFiNrExp2tA6Q
```

### Fetch Summoner Details by PUUID
Retrieve summoner details using PUUID:
```bash
https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/<puuid>
```
Example Response:
```json
{
    "id": "z4RXskmCFAtSVl-95daonylzldduMjqrJOdKMCGje0xMjI0",
    "accountId": "PAGCliBrbB8ziG41KRANATcFZm3HulbcD0SWIbn6FL4YvA",
    "puuid": "30jfZqHOrOHTRfn0k3iw0RN522UlTJSWOyNDB4PzpVYCZAEdPuFWQxT0_agR9jLI55h3MdACD76aiA",
    "profileIconId": 3184,
    "revisionDate": 1724359760000,
    "summonerLevel": 262
}
```

### Fetch Ranked Information by Summoner ID
Retrieve ranked information for both Solo Queue and Flex Queue:
```bash
https://eun1.api.riotgames.com/lol/league/v4/entries/by-summoner/<summoner_id>
```
Example Response:
```json
[
    {
        "queueType": "RANKED_SOLO_5x5",
        "tier": "EMERALD",
        "rank": "II",
        "leaguePoints": 50,
        "wins": 16,
        "losses": 15
    }
]
```

## Script Commands

### Add an Account
Add an account to the local database:
```bash
python account-manager.py add <region> <name#tag> <username> <password>
```
Example:
```bash
python account-manager.py add eun1 loljomterry#TVTW tragLaMuIEgION plm
```

### Show Accounts
Show the details of stored accounts:
```bash
python account-manager.py show <region> [-o <output_file>] [--unsafe]
```
- `region`: Filter accounts by region (use `all` for all regions).
- `-o <output_file>`: Export the account details to a file.
- `--unsafe`: Show decrypted username and password in the output.

Example:
```bash
python account-manager.py show eun1 --unsafe -o file.txt
```

### Resync Accounts
Update the stored account details (rank, level, etc.) from the Riot API:
```bash
python account-manager.py resync
```

## Notes
- **Data Persistence**: Account details are stored in `accounts.json`. This file may not always reflect the current state, as rank and level can change over time.
- **Security**: Passwords are stored using a simple obfuscation mechanism. Use the `--unsafe` flag with caution.

## Requirements
- Python 3
- Required Python packages (specified in `requirements.txt`):
  ```
  prettytable
  requests
  ```
