import os
import csv
import requests
from datetime import datetime

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY is not set in environment variables.")

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_DETAILS_URL = "https://api.themoviedb.org/3/movie/{movie_id}/release_dates"

CSV_FILE = "tmdb_scores.csv"
MOVIES_FILE = "movies.txt"

HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "Content-Type": "application/json;charset=utf-8"
}

def fetch_movie_id(title):
    response = requests.get(TMDB_SEARCH_URL, params={"query": title}, headers=HEADERS)
    data = response.json()
    if data.get("results"):
        return data["results"][0]["id"], data["results"][0]["title"]
    return None, title

def fetch_score(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        vote_avg = data.get("vote_average", 0)
        vote_count = data.get("vote_count", 0)
        return round(vote_avg, 1), vote_count
    return None, None

def main():
    if not os.path.exists(MOVIES_FILE):
        raise FileNotFoundError(f"{MOVIES_FILE} not found.")

    results = []

    with open(MOVIES_FILE, "r") as f:
        movies = [line.strip() for line in f if line.strip()]

    for movie_title in movies:
        movie_id, resolved_title = fetch_movie_id(movie_title)
        if movie_id:
            score, count = fetch_score(movie_id)
            if score is not None:
                print(f"✅ {resolved_title}: {score} ({count} reviews)")
                results.append([resolved_title, score, count])
            else:
                print(f"❌ Failed to fetch score for {resolved_title}")
        else:
            print(f"❌ Movie not found: {movie_title}")

    if results:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Movie", "Score", "Review Count"])
            writer.writerows(results)
    else:
        print("⚠️ No valid data to write to CSV.")

if __name__ == "__main__":
    main()
