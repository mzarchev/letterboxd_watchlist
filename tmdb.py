# import tmdbsimple as tmdb
from snake_case import snake_case, dash_case
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

## External data
# Genres come coded with ID
DF_GENRES = pd.read_csv("data/genre_ids.csv").drop_duplicates()
# Which streaming services I am subscribed to
SUBSCRIPTIONS = ["Amazon Prime Video", "HBO Max", "Netflix"]
# Append this to poster_path to get full link
POSTER_URL = "https://image.tmdb.org/t/p/w185"
# API access
with open("api") as f: API_KEY = f.readline()

class MovieTMDB:
    def __init__(self):
        
        self.movie_info = {}
        self.year = ""
        self.providers = []
        self.rt_score = ""
        self.lb_score = ""
        self.genres = []
        self.director = ""
        self.cast = []
        self.poster = ""
        
    def find_movie(self, query: str, year: str=""):
        self.year = int(year)
        self.movie_info = self.get_movie_info(query=query, year=year)
        self.providers = self.get_providers(self.movie_info["id"])
        self.rt_score = self.get_rt_score(self.movie_info["title"])
        self.lb_score = self.get_lb_score(self.movie_info["title"])
        self.genres = self.return_genres_list(self.movie_info["genre_ids"])
        self.director, self.cast = self.get_crew_cast(self.movie_info["id"]).values()
        self.poster = POSTER_URL + self.movie_info["poster_path"]

    def get_movie_info(self, query: str, year: str="", api: str=API_KEY) -> dict:
        """ Takes a search query (ideally with year)
            Returns a dictionary with the first result match from TMDB"""
            
        request = f"https://api.themoviedb.org/3/search/movie?api_key={api}&language=en-US&query={query}&page=1&include_adult=false&year={year}"
        response = requests.get(request)
        json_res = response.json()
        first_result = json_res["results"][0]
        return(first_result)

    def get_providers(self, movie_id: str, api: str=API_KEY) -> list:
        """ Takes a movie ID from TMDB database and checks if it is available
            on any of the platforms I am subscribed to.
            Returns a string with which providers it can be streamed on"""
        
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api}"
        json_res = requests.get(url).json()
        try:
            nl_all_streams = json_res["results"].get("NL").get("flatrate")    
        except AttributeError:
            return(["No streaming available"])
        if nl_all_streams is None: return(["No streaming available"])
        else:
            # Check if any of the available providers are ones I have subcribed to
            available_providers = [stream["provider_name"]
                                for stream in nl_all_streams
                                if stream["provider_name"] in SUBSCRIPTIONS]
            if len(available_providers) > 0: return(available_providers)
            # If not just say there is no streaming
            else: return(["No streaming available"])
            
    def match_genre_to_id(self, genre_id: str) -> str:
        genre_matched = DF_GENRES[DF_GENRES["id"] == genre_id]
        genre_label = genre_matched["genre"].item()
        return(genre_label)

    def return_genres_list(self, genre_ids: str) -> list:
        genre_labels = [self.match_genre_to_id(id) for id in genre_ids]
        return(genre_labels)
    
    def get_crew_cast(self, movie_id: str) -> dict:
        """ Takes TMDB movie id
            Returns dictionary with director and top 3 actors """ 
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US"
        request = requests.get(url)
        json_res = request.json()
        crew_members = json_res.get("crew")
        cast_members = json_res.get("cast")

        director = [member for member in crew_members if member["job"] == "Director"][0]["name"]
        cast = [member["name"] for member in cast_members[0:3]]

        results = {"director": director,
                    "cast": cast}
        return(results)
    
    def get_rt_score(self, movie_title: str) -> str:
        snake_title = snake_case(movie_title)
        url = f"https://www.rottentomatoes.com/m/{snake_title}_{self.year}"
        page = requests.get(url)

        # Try URL without the year if 404 and if that doesn't work give up
        if page.status_code == 404:
            url = f"https://www.rottentomatoes.com/m/{snake_title}"
            page = requests.get(url)
            if page.status_code == 404: return("-")

        soup = BeautifulSoup(page.content, "html.parser")

        rt_score = soup.find("score-board", class_="scoreboard")["tomatometerscore"] 
        rt_info = soup.find("p", class_="scoreboard__info").text
        rt_year = int(re.findall(r"\d+", rt_info)[0])

        if rt_year in [self.year, self.year + 1, self.year - 1]: return(rt_score)
        else: return("-")
    
    def get_lb_score(self, movie_title: str) -> str:
        dash_title = dash_case(movie_title)

        url = f"https://letterboxd.com/csi/film/{dash_title}-{self.year}/rating-histogram/"
        page = requests.get(url)

        # Try URL without the year if 404 and if that doesn't work give up
        if page.status_code == 404:
            url = f"https://letterboxd.com/csi/film/{dash_title}/rating-histogram/"
            page = requests.get(url)
            if page.status_code == 404: return("-")

        soup = BeautifulSoup(page.content, "html.parser")

        try: 
            lb_score = soup.find("a", class_="tooltip display-rating").text
        except AttributeError:
            try:
                lb_score = soup.find("a", class_="tooltip display-rating -highlight").text
            except AttributeError:
                return("-")
            
        return(lb_score)
    
    def return_df(self) -> pd.DataFrame:
        
        df = pd.DataFrame({"Title":self.movie_info["title"],
                           "Year": self.year,
                           "Stream on": [self.providers],
                           "RT score": self.rt_score,
                           "Letterboxd score": self.lb_score,
                           "Director": self.director,
                           "Cast": [self.cast],
                           "Genres": [self.genres],
                           "Language": self.movie_info["original_language"],
                           "Poster": self.poster},
                           index = [0])
        return(df)
    