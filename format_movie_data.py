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