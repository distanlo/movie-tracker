import os
import requests
import csv
from datetime import datetime

API_KEY = os.getenv("TMDB_API_KEY")
MOVIE_FILE = "movies.txt"
CSV_FILE = "tmdb_scores.csv"
HTML_FILE = "index.html"

def get_movie_score(title):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": API_KEY, "query": title}
    res = requests.get(url, params=params)
    data = res.json()
    if not data.get("results"):
        return None
    movie = data["results"][0]
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "rating": movie.get("vote_average", "N/A"),
        "vote_count": movie.get("vote_count", "N/A"),
        "release_date": movie.get("release_date", "N/A")
    }

def write_to_csv(row):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def generate_html():
    if not os.path.exists(CSV_FILE):
        return
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    movies = sorted(set(r["title"] for r in rows))
    grouped = {m: [r for r in rows if r["title"] == m] for m in movies}

    with open(HTML_FILE, "w") as f:
        f.write("<html><head><title>Movie Score Tracker</title></head><body>")
        f.write("<h1>TMDb Score Tracker</h1><select id='sel' onchange='update()'>")
        for movie in movies:
            f.write(f"<option value='{movie}'>{movie}</option>")
        f.write("</select><table border='1'><thead><tr><th>Time</th><th>Rating</th><th>Votes</th><th>Release</th></tr></thead><tbody id='table'></tbody></table>")
        f.write("<script>const data = {};")
        for movie, records in grouped.items():
            f.write(f"data['{movie}'] = {records};")
        f.write("""
function update(){
  const m = document.getElementById('sel').value;
  const tb = document.getElementById('table');
  tb.innerHTML = '';
  data[m].forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.timestamp}</td><td>${row.rating}</td><td>${row.vote_count}</td><td>${row.release_date}</td>`;
    tb.appendChild(tr);
  });
}
update();
</script></body></html>""")

def main():
    with open(MOVIE_FILE) as f:
        titles = [line.strip() for line in f if line.strip()]
    for title in titles:
        print(f"🔍 Fetching: {title}")
        row = get_movie_score(title)
        if row:
            write_to_csv(row)
            print(f"✅ {title}: {row['rating']} ({row['vote_count']} votes)")
        else:
            print(f"❌ Failed to get score for {title}")
    generate_html()

if __name__ == "__main__":
    main()