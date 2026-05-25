import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

kpis = [
    {"area": "RISK",       "name": "Loan\nDefault Rate",   "val": 9.8,  "target": 5,  "dir": "lower"},
    {"area": "GROWTH",     "name": "Cross-Sell\nGap",      "val": 51.4, "target": 40, "dir": "lower"},
    {"area": "ENGAGEMENT", "name": "App\nAdoption",        "val": 66.3, "target": 65, "dir": "higher"},
    {"area": "COMPLIANCE", "name": "KYC\nVerified",        "val": 69.9, "target": 95, "dir": "higher"},
    {"area": "RETENTION",  "name": "Savings\nGrowing",     "val": 99.0, "target": 70, "dir": "higher"},
]

for k in kpis:
    k["met"]   = k["val"] <= k["target"] if k["dir"] == "lower" else k["val"] >= k["target"]
    k["color"] = "#2ECC71" if k["met"] else "#E74C3C"
    k["label"] = "ON TRACK" if k["met"] else "NEEDS ACTION"

BG, CARD = "#0D0D0D", "#141414"

fig = plt.figure(figsize=(16, 7), facecolor=BG)

# Title
fig.text(0.5, 0.95, "FinSight Lanka — KPI Dashboard",
         ha="center", fontsize=20, fontweight="bold", color="#F0F0F0")
fig.text(0.5, 0.89, "Monthly customer health metrics  ·  Dialog Finance PLC  ·  508 records",
         ha="center", fontsize=10, color="#555555")

n = len(kpis)
for i, k in enumerate(kpis):
    left = 0.04 + i * 0.193
    ax = fig.add_axes([left, 0.08, 0.175, 0.74])
    ax.set_facecolor(CARD)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Top accent bar
    ax.plot([-1.3, 1.3], [1.28, 1.28], color=k["color"], linewidth=5,
            solid_capstyle="butt", clip_on=False)

    # Area label
    ax.text(0, 1.1, k["area"], ha="center", va="center",
            fontsize=8, color=k["color"], fontweight="bold")

    # Donut ring — background
    theta = np.linspace(np.pi/2, np.pi/2 - 2*np.pi, 300)
    ax.plot(np.cos(theta)*0.75, np.sin(theta)*0.75,
            color="#1E1E1E", linewidth=14, solid_capstyle="round")

    # Target arc
    tgt_frac = min(k["target"] / 100, 1.0)
    theta_tgt = np.linspace(np.pi/2, np.pi/2 - 2*np.pi*tgt_frac, 200)
    ax.plot(np.cos(theta_tgt)*0.75, np.sin(theta_tgt)*0.75,
            color="#333333", linewidth=14, solid_capstyle="round")

    # Value arc
    val_frac = min(k["val"] / 100, 1.0)
    theta_val = np.linspace(np.pi/2, np.pi/2 - 2*np.pi*val_frac, 200)
    ax.plot(np.cos(theta_val)*0.75, np.sin(theta_val)*0.75,
            color=k["color"], linewidth=14, solid_capstyle="round", alpha=0.9)

    # Centre value
    ax.text(0, 0.08, f"{k['val']}%", ha="center", va="center",
            fontsize=20, fontweight="bold", color=k["color"])
    ax.text(0, -0.18, "current", ha="center", va="center",
            fontsize=8, color="#555555")

    # KPI name
    ax.text(0, -0.52, k["name"], ha="center", va="center",
            fontsize=11, color="#DDDDDD", fontweight="bold", linespacing=1.5)

    # Target label
    arrow = "<" if k["dir"] == "lower" else ">"
    ax.text(0, -0.85, f"Target  {arrow} {k['target']}%", ha="center", va="center",
            fontsize=9, color="#777777")

    # Status badge
    badge_bg = "#1A2E1A" if k["met"] else "#2E1A1A"
    badge_ec = "#27AE60" if k["met"] else "#C0392B"
    badge_tc = "#27AE60" if k["met"] else "#C0392B"
    rect = mpatches.FancyBboxPatch((-0.72, -1.18), 1.44, 0.28,
                                    boxstyle="round,pad=0.04",
                                    facecolor=badge_bg, edgecolor=badge_ec, linewidth=1)
    ax.add_patch(rect)
    ax.text(0, -1.04, k["label"], ha="center", va="center",
            fontsize=8, color=badge_tc, fontweight="bold")

# Footer
fig.text(0.5, 0.02,
         "2 of 5 KPIs on track  ·  Priority: reduce default rate & complete KYC verification  ·  Green = on track  ·  Red = needs action",
         ha="center", fontsize=8.5, color="#444444")

plt.savefig("kpi_dashboard.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.show()
print("Saved: kpi_dashboard.png")