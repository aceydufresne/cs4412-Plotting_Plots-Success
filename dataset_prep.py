import kagglehub
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests

def printSet(path):
    movieData = []
    columns = []
    with open(path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            movieData.append(row)
    for topic in movieData[0]:
        columns.append(topic)
        columns[0] = '0'
    print(columns)
    with open(path, mode='r', newline='', encoding='utf-8') as file:
        reader2 = csv.reader(file, delimiter=',')
        for r2 in reader2:
            print("placeholder")

def createSet(titles):
    strPath1 = "https://www.imdb.com/find/?q="
    strPath2 = "&s=tt&ttype=ft"
    
    for title in titles:
        url = strPath1 + title + strPath2
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html')
        print(soup)

if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    #printSet(path)
