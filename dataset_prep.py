import kagglehub
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

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
        url = strPath1 + title + strPath2
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        print(soup)
        time.sleep(1)

if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    titles = printSet(path)
    createSet(titles)
