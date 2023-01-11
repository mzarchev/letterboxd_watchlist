from tmdb import MovieTMDB
from download_lb_watchlist import download_lb_watchlist
import pandas as pd

# Import exisiting data
df_movies_old = pd.read_parquet("data/df_movie_info.parquet")
df_movies_old = df_movies_old.drop("Year", axis=1)
# Get current watchlist data
df_lb_watchlist = download_lb_watchlist("https://letterboxd.com/mzarchev/watchlist/")
# Create a dataframe which have a variable for overlap in movies between watchlist and old dataframe 
outer_join = df_movies_old.merge(df_lb_watchlist,
                                 left_on="Title",
                                 right_on = "Title",
                                 how ="outer",
                                 indicator=True)

# Movies only in watchlist should be downloaded (new movies)
movies_to_download = outer_join[(outer_join._merge == "right_only")].drop("_merge", axis=1)
# Movies only in old dataframe but not watchlist should be removed (watched movies) 
movies_to_remove = outer_join[outer_join._merge == "left_only"].Title.values

df_movies = outer_join[outer_join._merge == "both"].drop("_merge", axis=1)

# Loop to extract info of movies to download
for lb_movie, lb_year in zip(movies_to_download.Title, movies_to_download.Year):
    
    movie = MovieTMDB()
    
    movie.find_movie(query=lb_movie, year=str(lb_year))
    
    try: # Catch if on first loop
        df_movies = pd.concat([movie.return_df(), df_movies],
                                ignore_index=True)
        print("\n Processed", movie.movie_info["title"], "by", movie.director, "\n")
    except: continue

# Export
df_lb_watchlist.to_csv("data/watchlist.csv")

df_movies = df_movies.astype({"Year":"int"})
df_movies.to_parquet("data/df_movie_info.parquet")
