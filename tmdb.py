import os
import re
import requests
import argparse
# from gooey import Gooey, GooeyParser  # Uncomment if you want GUI

# === YOUR TMDB CREDENTIALS ===
TMDB_API_KEY = "your_tmdb_api_key"  # ← Replace with your TMDb v3 API Key
TMDB_BEARER_TOKEN = "your_tmdb_bearer_token"  # ← Replace with your TMDb v4 Bearer Token

# === TMDb API ENDPOINTS ===
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_LISTS_URL = "https://api.themoviedb.org/4/list"

# === PARSE MOVIE FILENAME (e.g., the_dark_knight.2008.mp4) ===
def parse_filename(filename):
    match = re.match(r"(.+?)\.(\d{4})\.(mp4|mkv|avi|mov)$", filename, re.IGNORECASE)
    if match:
        name = match.group(1).replace("_", " ").title()
        year = match.group(2)
        return name, year
    return None, None

# === SEARCH TMDB FOR MOVIE ===
def search_movie(title, year):
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "year": year
    }
    response = requests.get(TMDB_SEARCH_URL, params=params)
    if response.status_code == 200 and response.json()["results"]:
        return response.json()["results"][0]
    return None

# === CREATE TMDB LIST ===
def create_tmdb_list(name, description="Auto-generated movie list"):
    headers = {
        "Authorization": f"Bearer {TMDB_BEARER_TOKEN}",
        "Content-Type": "application/json;charset=utf-8"
    }
    data = {
        "name": name,
        "iso_639_1": "en",
        "description": description,
        "public": False
    }
    response = requests.post(TMDB_LISTS_URL, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()["id"]
    else:
        print("❌ Failed to create list:", response.text)
        return None

# === ADD MOVIE TO TMDB LIST ===
def add_movie_to_list(list_id, movie_id):
    headers = {
        "Authorization": f"Bearer {TMDB_BEARER_TOKEN}",
        "Content-Type": "application/json;charset=utf-8"
    }
    data = {
        "items": [{"media_type": "movie", "media_id": movie_id}]
    }
    url = f"{TMDB_LISTS_URL}/{list_id}/items"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        return True
    else:
        print("❌ Failed to add movie:", response.text)
        return False

# === MAIN MOVIE SCANNING AND UPLOAD FUNCTION ===
def process_movies(folder_path, list_name):
    movies = []
    for file in os.listdir(folder_path):
        if file.lower().endswith((".mp4", ".mkv", ".avi", ".mov")):
            title, year = parse_filename(file)
            if title and year:
                print(f"🎬 Searching for: {title} ({year})")
                result = search_movie(title, year)
                if result:
                    print(f"✅ Found: {result['title']} ({result['release_date']})")
                    movies.append(result)
                else:
                    print(f"❌ Not found: {title} ({year})")

    if not movies:
        print("⚠️ No valid movies found or matched.")
        return

    list_id = create_tmdb_list(list_name)
    if not list_id:
        print("❌ Could not create list. Aborting.")
        return

    print(f"\n📂 Adding {len(movies)} movies to your TMDb list...")
    for movie in movies:
        added = add_movie_to_list(list_id, movie["id"])
        if added:
            print(f"➕ {movie['title']} added.")
        else:
            print(f"⚠️ Failed to add {movie['title']}.")

    print(f"\n✅ Done! View your list: https://www.themoviedb.org/list/{list_id}")

# === ARGPARSE / GOOEY ENTRY ===

# @Gooey(program_name="TMDb Movie List Uploader")  # Uncomment to use GUI
def main():
    parser = argparse.ArgumentParser(description="Upload local movie files to a TMDb list.")
    parser.add_argument(
        "-f", "--folder", 
        required=True, 
        help="Folder containing your local movie files (e.g., *.mp4)"
    )
    parser.add_argument(
        "-n", "--name", 
        required=True, 
        help="Name of the TMDb list to create"
    )
    args = parser.parse_args()

    process_movies(args.folder, args.name)

# === RUN ===
if __name__ == "__main__":
    main()
