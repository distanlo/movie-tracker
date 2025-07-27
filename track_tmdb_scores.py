import requests
import pandas as pd
import os
from datetime import datetime

# Load API key from environment
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY is not set in environment variables.")

# File paths
MOVIES_FILE = "movies.txt"
CSV_FILE = "tmdb_scores.csv"
HTML_FILE = "index.html"

# Ensure the CSV exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write("title,timestamp,rating,vote_count,release_date\n")

# Load existing CSV
df = pd.read_csv(CSV_FILE)

# Load movie titles
with open(MOVIES_FILE, "r") as f:
    movie_names = [line.strip() for line in f if line.strip()]

new_rows = []

for movie in movie_names:
    print(f"[INFO] Fetching data for '{movie}'...")
    search_url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie}
    res = requests.get(search_url, params=params)

    if res.status_code != 200:
        print(f"❌ Error searching '{movie}': HTTP {res.status_code}")
        continue

    results = res.json().get("results")
    if not results:
        print(f"❌ No results found for '{movie}'")
        continue

    top = results[0]
    movie_id = top.get("id")
    title = top.get("title")
    release_date = top.get("release_date", "")

    # Get full movie details
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    detail_params = {"api_key": TMDB_API_KEY}
    details = requests.get(details_url, params=detail_params).json()

    rating = details.get("vote_average")
    vote_count = details.get("vote_count")

    if rating is not None and vote_count is not None:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ {title}: {rating} ({vote_count} votes)")
        new_rows.append({
            "title": title,
            "timestamp": timestamp,
            "rating": rating,
            "vote_count": vote_count,
            "release_date": release_date
        })
    else:
        print(f"❌ Failed to get score for {movie}")

# Append new data
if new_rows:
    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
else:
    print("⚠️ No new data added.")

# Generate index.html
grouped = df.groupby("title")
data_dict = {}

for title, group in grouped:
    group_sorted = group.sort_values("timestamp")
    entries = []
    for _, row in group_sorted.iterrows():
        entries.append({
            "timestamp": row["timestamp"],
            "rating": row["rating"],
            "vote_count": row["vote_count"],
            "release_date": row["release_date"]
        })
    data_dict[title] = entries

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>TMDb Score Tracker</title>
  <link rel="icon" href="favicon.ico" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body {{
      background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
      color: #f8f9fa;
      font-family: 'Segoe UI', sans-serif;
      padding: 1rem;
    }}
    .container {{
      max-width: 800px;
      margin: auto;
    }}
    h1 {{
      font-size: 2rem;
      text-align: center;
      margin-bottom: 1rem;
    }}
    select {{
      margin-bottom: 1rem;
    }}
    table {{
      font-size: 0.9rem;
    }}
    th {{
      background-color: #343a40;
    }}
    td, th {{
      text-align: center;
      vertical-align: middle;
      padding: 0.6rem;
    }}
    .table-dark tbody tr:nth-child(odd) {{
      background-color: #2d2d2d;
    }}
    footer {{
      text-align: center;
      font-size: 0.85rem;
      margin-top: 2rem;
      color: #ccc;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🎬 TMDb Score Tracker</h1>
    <label for="sel" class="form-label">🎞 Select a movie:</label>
    <select id="sel" class="form-select" onchange="update()"></select>

    <div class="table-responsive">
      <table class="table table-dark table-striped table-bordered mt-3">
        <thead>
          <tr>
            <th>Time</th>
            <th>Rating</th>
            <th>Votes</th>
            <th>Release</th>
          </tr>
        </thead>
        <tbody id="table"></tbody>
      </table>
    </div>

    <footer>⚡ Updated hourly via GitHub Actions · Built by Big Dawg 🍿</footer>
  </div>

  <script>
    const data = {data_dict};
    const sel = document.getElementById("sel");
    const tb = document.getElementById("table");

    window.onload = function () {{
      const movieNames = Object.keys(data);
      movieNames.forEach(name => {{
        const opt = document.createElement("option");
        opt.value = name;
        opt.innerText = name;
        sel.appendChild(opt);
      }});
      if (movieNames.length > 0) {{
        sel.value = movieNames[0];
        update();
      }}
    }};

    function update() {{
      const movie = sel.value;
      if (!movie || !data[movie]) return;
      tb.innerHTML = "";
      data[movie].forEach(row => {{
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.timestamp}</td><td>${row.rating}</td><td>${row.vote_count}</td><td>${row.release_date}</td>`;
        tb.appendChild(tr);
      }});
    }}
  </script>
</body>
</html>
"""

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTML page and CSV updated successfully.")
