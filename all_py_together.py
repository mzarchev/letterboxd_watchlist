import os
import subprocess

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = os.open(os.devnull, os.O_RDWR)

output = subprocess.check_output(cmd, stdin=DEVNULL, stderr=DEVNULL)

from bs4 import BeautifulSoup
from pandas import DataFrame
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

def download_lb_watchlist(user):
    
    url = f"https://letterboxd.com/{user}/watchlist"

    # Initialize
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)
    # Load page and close cookies
    browser.get(url)
    sleep(2)
    cookies = WebDriverWait(browser, 4).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="html"]/body/div[6]/div[2]/div[1]/div[2]/div[2]/button[1]'))).click()
    # Get source and close
    page = browser.page_source
    browser.close()

    soup = BeautifulSoup(page, "html.parser")
    films_elements = soup.find_all("a", class_="frame")
    film_title_years = [film["data-original-title"] for film in films_elements]

    film_titles = [re.sub(r"[(]\d+[)]", "", film) for film in film_title_years] 
    film_years = [re.findall(r"(?<=[(])\d+(?=[)])", film)[0] for film in film_title_years]

    return(DataFrame({"Name":film_titles, "Year":film_years}))

from re import sub

def snake_case(s):
  str1 = '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower().replace("&", "and")
  return sub("-[^a-zA-Z\d\s-]", "", str1)
  
def dash_case(s):
  str1 = '-'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()
  return sub("-[^a-zA-Z\d\s-]", "", str1)
# import tmdbsimple as tmdb
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

## External data
# Genres come coded with ID
DF_GENRES = pd.read_csv("data/genre_ids.csv").drop_duplicates()
# Which streaming services I am subscribed to
SUBSCRIPTIONS = ["Amazon Prime Video", "Netflix"]
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
        self.description = ""
        self.director = ""
        self.cast = []
        self.poster = ""
        
    def find_movie(self, query: str, year: str=""):
        self.year = int(year) if re.match("\d", year) else ""
        try:
            self.movie_info = self.get_movie_info(query=query, year=year)
        except:
            return("-")
        self.providers = self.get_providers(self.movie_info["id"])
        self.providers.append(self.get_hbo_bg_provider(self.movie_info["id"]))
        self.rt_score = self.get_rt_score(self.movie_info["title"])
        self.lb_score = self.get_lb_score(self.movie_info["title"])
        self.genres = self.return_genres_list(self.movie_info["genre_ids"])
        self.description = self.movie_info["overview"]
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
            if available_providers: return(available_providers)
            # If not just say there is no streaming
            else: return(["No streaming available"])
                        
    def get_hbo_bg_provider(self, movie_id: str) -> str:
        """ Takes TMDB id as input
            Returns "HBO max" if available in bulgaria or an empty string if not"""
        
        url = f"https://www.themoviedb.org/movie/{movie_id}/watch?translate=false&locale=BG"

        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        page = requests.get(url, headers=header)
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            providers = soup.find("ul", class_="providers").find_all("a")
        except AttributeError: 
            return("")
        contains_hbo = [provider["title"] for provider in providers if re.match(".+HBO Max", provider["title"])]
        hbo_bulgaria = "HBO Max" if contains_hbo else ""
        
        return(hbo_bulgaria)

            
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
                           "Description":  [self.description],
                           "Language": self.movie_info["original_language"],
                           "Poster": self.poster},
                           index = [0])
        return(df)
    
import pandas as pd

# Get watchlist data
df_lb_watchlist = download_lb_watchlist("mzarchev")

# Loop to extract info of all movies from watchlist
for lb_movie, lb_year in zip(df_lb_watchlist.Name, df_lb_watchlist.Year):
    
    movie = MovieTMDB()
    
    movie.find_movie(query=lb_movie, year=str(lb_year))
    
    try: # Catch if movie cannot be found
        try: # Catch if on first loop
            df_movies = pd.concat([df_movies, movie.return_df()],
                                ignore_index=True)
            print("\n Processed", movie.movie_info["title"], "by", movie.director, "\n")
        except NameError:
            df_movies = movie.return_df()
    except KeyError:
        pass
        

# Export

df_lb_watchlist.to_csv("data/watchlist.csv")
df_movies.to_parquet("data/df_movie_info.parquet")

import pandas as pd

# Import data
df_movies = pd.read_parquet("data/df_movie_info.parquet")
df_formatted = df_movies.copy()

## Create boolean variables for each genre type
all_genres = [genre for list_genres in df_movies.Genres for genre in list_genres] # Flatten list
unique_genres = list(set(all_genres)) # Get unique values
varnames_genres = ["is_" + genre for genre in unique_genres] # Append "is_" to beginning of each

def check_is_genre(genre):
    """ Take a genre, go through each list in the series
        Return True or False if genre is in it """
    return([genre in list_genres for list_genres in df_movies.Genres])


""" for varnames_genre, genre in zip(varnames_genres, unique_genres):
    
    df_formatted[varnames_genre] = check_is_genre(genre)
 """
df_formatted["Genres"] = [", ".join(genres_list) for genres_list in df_formatted.Genres]
    
## Add images to providers
df_providers = pd.read_csv("data/provider_img.csv")

def get_img_provider(list_providers):
    """ Take a list of providers, check if img is available for any
        Return html image tag if available """
    df_available = df_providers[df_providers.provider.isin(list_providers)]
    if df_available.empty:
        return("Unavailable")
    else:
        html_img = [f"<img src='{img}'height='50', style='border-radius: 10%;'></img>" for img in df_available.img]
        return(" ".join(html_img))

df_formatted["Stream on"] = df_formatted["Stream on"].apply(lambda s:get_img_provider(s))        

## Cast members
df_formatted["Cast"] = df_formatted.Cast.apply(lambda s: ", ".join(s)) 

# Export
df_formatted.to_csv("data/df_formatted.csv") 
pd.DataFrame({"genres":unique_genres}).to_csv("data/unique_genres.csv", index=False)      