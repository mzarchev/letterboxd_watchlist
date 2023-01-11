from bs4 import BeautifulSoup
from pandas import DataFrame
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

def download_lb_watchlist(url):
    # Initialize
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)
    # Load page and close cookies
    browser.get(url)
    cookies = WebDriverWait(browser, 4).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="html"]/body/div[6]/div[2]/div[1]/div[2]/div[2]/button[1]'))).click()
    # Get source
    page = browser.page_source

    # Check for second page (this should be a loop that breaks, however pages that do not exist do not return a 404 unfortunately)
    url_2 = url + "page/2/"
    browser.get(url_2)
    # Get source and close
    page2 = browser.page_source
    all_pages = page + page2

    browser.close()

    soup = BeautifulSoup(all_pages, "html.parser")
    films_elements = soup.find_all("a", class_="frame")
    film_title_years = [film["data-original-title"] for film in films_elements]

    film_titles = [re.sub(r"[(]\d+[)]", "", film).strip() for film in film_title_years] 
    film_years = [re.findall(r"(?<=[(])\d+(?=[)])", film)[0] for film in film_title_years]

    return(DataFrame({"Title":film_titles, "Year":film_years}))

