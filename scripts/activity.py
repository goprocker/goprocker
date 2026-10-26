"""Render assets/readme/activity.svg from the GitHub GraphQL API.

Usage: GITHUB_TOKEN=... python scripts/activity.py [username]
"""
import json
import os
import sys
import urllib.request
from datetime import date

USER = sys.argv[1] if len(sys.argv) > 1 else "goprocker"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "readme", "activity.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

SANS = "'Segoe UI',Inter,-apple-system,Helvetica,Arial,sans-serif"
MONO = "Consolas,'SF Mono',Menlo,monospace"
LEVELS = ["#151d38", "#1e3a8a", "#3b6cf6", "#70a5fd", "#c4b5fd"]


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": USER},
    )
    with urllib.request.urlopen(req) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]


def streaks(days):
    today = date.today().isoformat()
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["contributionCount"]:
            current += 1
        elif d["date"] != today:  # today without contributions doesn't break the streak yet
            break
    return current, longest


def level(count, peak):
    if count == 0:
        return 0
    return min(4, 1 + int(3 * count / max(peak, 1)))


def render(u):
    cc = u["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, longest = streaks(days)
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    peak = sorted(d["contributionCount"] for d in days)[int(len(days) * 0.95)] or 1

    tiles = [
        ("Contributions", f'{cc["contributionCalendar"]["totalContributions"]:,}', "past year", "#70a5fd"),
        ("Current streak", current, "days", "#34d399"),
        ("Longest streak", longest, "days", "#a78bfa"),
        ("Commits", f'{cc["totalCommitContributions"] + cc["restrictedContributionsCount"]:,}', "incl. private", "#fb923c"),
        ("Pull requests", cc["totalPullRequestContributions"], "past year", "#22d3ee"),
        ("Repos · Stars", f'{u["repositories"]["totalCount"]} · {stars}', "public", "#f472b6"),
    ]

    W, H = 1200, 420
    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub activity for {USER}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1430"/><stop offset="1" stop-color="#080c1a"/></linearGradient>
    <radialGradient id="o" cx="0" cy="0" r="1"><stop offset="0" stop-color="#3b6cf6" stop-opacity=".22"/><stop offset=".55" stop-color="#3b6cf6" stop-opacity="0"/></radialGradient>
  </defs>
  <rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="url(#g)" stroke="#ffffff" stroke-opacity=".09"/>
  <rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="url(#o)"/>''']

    gap, x0 = 12, 28
    tw = (W - 2 * x0 - gap * (len(tiles) - 1)) / len(tiles)
    for i, (label, value, sub, acc) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        out.append(f'''  <g transform="translate({x} 28)">
    <rect width="{tw}" height="108" rx="12" fill="#ffffff" fill-opacity=".035" stroke="#ffffff" stroke-opacity=".08"/>
    <rect x="16" y="0" width="32" height="3" rx="1.5" fill="{acc}"/>
    <text x="16" y="32" font-family="{SANS}" font-size="12.5" font-weight="600" fill="#8b98b8" letter-spacing=".6">{label.upper()}</text>
    <text x="16" y="72" font-family="{SANS}" font-size="32" font-weight="800" fill="#e6edf3">{value}</text>
    <text x="16" y="94" font-family="{SANS}" font-size="12.5" fill="{acc}">{sub}</text>
  </g>''')

    cell, step, top = 16, 21, 196
    left = (W - len(weeks) * step + (step - cell)) / 2
    out.append(f'  <text x="{left}" y="176" font-family="{SANS}" font-size="14" font-weight="600" fill="#c3cde6">Contribution calendar</text>')
    last_month, last_x = None, -99
    for wi, w in enumerate(weeks):
        x = left + wi * step
        m = w["contributionDays"][0]["date"][5:7]
        if m != last_month and wi < len(weeks) - 2 and x - last_x > 2 * step:
            name = date(2000, int(m), 1).strftime("%b")
            out.append(f'  <text x="{x}" y="{top + 7*step + 16}" font-family="{MONO}" font-size="11" fill="#5b6785">{name}</text>')
            last_month, last_x = m, x
        for d in w["contributionDays"]:
            y = top + date.fromisoformat(d["date"]).isoweekday() % 7 * step
            c = LEVELS[level(d["contributionCount"], peak)]
            out.append(f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{c}"><title>{d["date"]}: {d["contributionCount"]}</title></rect>')

    lx = W - 28 - 5 * 18 - 70
    out.append(f'  <text x="{lx - 8}" y="176" text-anchor="end" font-family="{SANS}" font-size="12" fill="#5b6785">Less</text>')
    for i, c in enumerate(LEVELS):
        out.append(f'  <rect x="{lx + i*18}" y="165" width="13" height="13" rx="3" fill="{c}"/>')
    out.append(f'  <text x="{lx + 5*18 + 4}" y="176" font-family="{SANS}" font-size="12" fill="#5b6785">More</text>')
    out.append(f'  <text x="{W-28}" y="{H-18}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#3d4766">updated {date.today().isoformat()}</text>')
    out.append("</svg>\n")
    return "\n".join(out)


if __name__ == "__main__":
    svg = render(fetch())
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {os.path.normpath(OUT)}")
