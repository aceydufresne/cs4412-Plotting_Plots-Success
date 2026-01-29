import kagglehub
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from playwright.sync_api import sync_playwright

def printSet(path):
    movieData = []
    columns = []
    #replaced the csv reader for more efficient sorting
    df = pd.read_csv(path)
    #print(df["title"])
    title = df["title"]
    return title

def createSet(titles):
    strPath1 = "https://www.imdb.com/find/?q="
    strPath2 = "&s=tt&ttype=ft"
    
    for title in titles:
        title =title.strip()
        t = title.replace(" ", "+")
        url = strPath1 + title + strPath2
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        print(soup)
        time.sleep(1)

def scrapeExample(titles):
    strPath1 = "https://www.imdb.com/find/?q="
    strPath2 = "&s=tt&ttype=ft"
    title = titles[27]
    title = title.strip()
    t = title.replace(" ", "+")
    #print(t)
    url = strPath1 + t + strPath2
    #print(url)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    page = requests.get(url, headers=headers, timeout = 20)
    soup = BeautifulSoup(page.text, 'html.parser')
    #print(soup.title.string)
    
    #https://www.youtube.com/watch?v=cO997sPYZ9U
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless = False)
    
    page = browser.new_page(java_script_enabled = True, viewport = {'width': 200, 'height': 100})
    page.goto(url, wait_until = 'load')
    
    time.sleep(10)
    page.close()
    browser.close()
    playwright.stop()

if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    titles = printSet(path)
    #createSet(titles)
    scrapeExample(titles)
