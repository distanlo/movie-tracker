import os
import csv
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load .env locally if testing (safe to skip if you're using GitHub Secrets)
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY is not set")

CSV_FILE = "tmdb_scores.csv"
MOVIES_FILE = "movies.txt"

def fetch_movie_score(title):
    clean_title = title.strip()
    print(f"[DEBUG] Querying TMDb for: '{clean_title}'")
    
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": clean_title
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
        print(f"❌ HTTP Error: {res.status_code} for {clean_title}")
        return None

    data = res.json()
    if not data["results"]:
        print(f"❌ Movie not found: {clean_title}")
        return None

    movie = data["results"][0]
    rating = movie.get("vote_average", 0)
    vote_count = movie.get("vote_count", 0)
    release_date = movie.get("release_date", "N/A")
    return {
        "title": movie["title"],
        "rating": rating,
        "vote_count": vote_count,
        "release_date": release_date
    }

def main():
    if not os.path.exists(MOVIES_FILE):
        print(f"❌ {MOVIES_FILE} not found.")
        return

    with open(MOVIES_FILE, "r") as f:
        movie_titles = [line.strip() for line in f if line.strip()]

    timestamp = datetime.utcnow().isoformat()
    new_rows = []

    for title in movie_titles:
        result = fetch_movie_score(title)
        if result:
            new_rows.append([
                timestamp,
                result["title"],
                result["rating"],
                result["vote_count"],
                result["release_date"]
            ])
        else:
            print(f"❌ Failed {title}")

    if new_rows:
        header = ["Timestamp", "Title", "Rating", "Vote Count", "Release Date"]
        write_header = not os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(header)
            writer.writerows(new_rows)
        print(f"✅ Appended {len(new_rows)} rows to {CSV_FILE}")
    else:
        print("⚠️ No valid data to write to CSV.")

if __name__ == "__main__":
    main()
