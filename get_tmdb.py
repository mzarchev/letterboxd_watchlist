import tmdbsimple as tmdb
import pandas as pd
import requests

## External data
# Import letterboxd (lb) watchlist data
df_lb_watchlist = pd.read_csv("data/watchlist.csv")
# Genres come coded with IDs
df_genres = pd.read_csv("data/genre_ids.csv")

## API access
with open("api") as f:
    api_key = f.readline()
    tmdb.API_KEY = api_key

## Methods for accessing TMDB
def get_movie_info(query, year="", api=api_key):
    """ Takes a search query (ideally with year)
        Returns a JSON object with the results from TMDB"""
        
    request = f"https://api.themoviedb.org/3/search/movie?api_key={api}&language=en-US&query={query}&page=1&include_adult=false&year={year}"
    response = requests.get(request)
    json_res = response.json()
    return(json_res["results"])

def get_providers(movie_id, api=api_key):
    """ Takes a movie ID from TMDB database
        Returns a JSON object with which providers it can be streamed on"""
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api}"
    return(requests.get(url).json()["results"])

for lb_movie, lb_year in zip(df_lb_watchlist.Name, df_lb_watchlist.Year):
    print("\n", lb_movie, lb_year, "\n")
    
    # Search for movie
    search = tmdb.Search()
    response = search.movie(query=lb_movie, year=lb_year)
    
    # Extract genre IDs and remove column
    tmdb_genres = search.results[0]["genre_ids"]
    search.results[0].pop("genre_ids", None)

    tmdb_res = pd.DataFrame(search.results[0], index=[0])
    
    
    genres = search.results[0]["genre_ids"]
    
    print(search.results)

search.results

[row[1][1] for row in df_genres.iterrows()]

# Poster URL to append poster path to
poster_url = "https://image.tmdb.org/t/p/w185"


# What attributes does it return?
movie = get_movie_info(query="Murder on the orient express", year="1975")
movie_id = movie[0]["id"]

get_providers(movie["id"])

url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}"
response = requests.get(url)

res = response.json().get("results")
nl_streams = res.get("NL").get("flatrate")

subscriptions = ["Amazon Prime Video", "HBO Max"]

if nl_streams is None: print("No providers")
else:
    for providers in nl_streams:
        if providers["provider_name"] in subscriptions:
            streamer = providers["provider_name"]
        elif providers["provider_name"] == "Netflix":
            streamer = "Netflix"
        else:
            streamer = "Not availble stream"