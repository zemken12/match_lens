import requests

MATCH_ID = 3890561  # sample StatsBomb open-data match

url = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{MATCH_ID}.json"

response = requests.get(url)
response.raise_for_status()

events = response.json()

shots = [event for event in events if event["type"]["name"] == "Shot"]

print(f"Found {len(shots)} shots\n")

for shot in shots:
    player = shot["player"]["name"]
    minute = shot["minute"]
    location = shot["location"]
    xg = shot["shot"]["statsbomb_xg"]
    outcome = shot["shot"]["outcome"]["name"]

    print(
        f"{minute}' | {player} | xG: {xg:.3f} | Location: {location} | Outcome: {outcome}"
    )