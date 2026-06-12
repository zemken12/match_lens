import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 7))

# Simple pitch outline
ax.plot([0, 120, 120, 0, 0], [0, 0, 80, 80, 0])

# Fake shots: x, y, xG
shots = [
    (105, 40, 0.35),
    (98, 50, 0.12),
    (88, 32, 0.05),
]

for x, y, xg in shots:
    ax.scatter(x, y, s=xg * 1000, alpha=0.6)

ax.set_xlim(0, 120)
ax.set_ylim(0, 80)
ax.set_aspect("equal")
ax.set_title("Match Lens - First Shot Map")

plt.savefig("first_shot_map.png", dpi=150)
plt.show()