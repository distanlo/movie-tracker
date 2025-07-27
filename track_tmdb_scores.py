import pandas as pd
import json

csv_file = "tmdb_scores.csv"
df = pd.read_csv(csv_file)

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

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>TMDb Score Tracker</title>
  <link rel="icon" href="favicon.ico" type="image/x-icon" />
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
    const data = {json.dumps(data_dict, indent=2)};
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
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
