
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
