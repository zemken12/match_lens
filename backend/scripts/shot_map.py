import requests
import matplotlib.pyplot as plt
from mplsoccer import Pitch

MATCH_ID = 3890561

url = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{MATCH_ID}.json"

response = requests.get(url)
response.raise_for_status()

events = response.json()

shots = [event for event in events if event["type"]["name"] == "Shot"]

x_coords = []
y_coords = []
sizes = []
labels = []

for shot in shots:
    location = shot["location"]
    xg = shot["shot"]["statsbomb_xg"]
    player = shot["player"]["name"]
    outcome = shot["shot"]["outcome"]["name"]

    x_coords.append(location[0])
    y_coords.append(location[1])
    sizes.append(float(xg) * 1500)
    labels.append(f"{player} | xG {xg:.2f} | {outcome}")

pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
fig, ax = pitch.draw(figsize=(12, 8))

pitch.scatter(
    x_coords,
    y_coords,
    s=sizes,
    alpha=0.6,
    edgecolors="black",
    ax=ax,
)

ax.set_title("Match Lens - StatsBomb Shot Map", fontsize=18)

plt.savefig("shot_map.png", dpi=150, bbox_inches="tight")
plt.show()