import kagglehub
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from playwright.sync_api import sync_playwright
import os

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
        url = strPath1 + t + strPath2
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        print(soup)
        time.sleep(1)

def scrapeExample(titles):
    xpath_prefix = 'xpath='
    
    strPath1 = "https://www.imdb.com/find/?q="
    strPath2 = "&s=tt&ttype=ft"
    title = titles[27]
    title = title.strip()
    t = title.replace(" ", "+")
    #print(t)
    url = strPath1 + t + strPath2
    print(url)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    page = requests.get(url, headers=headers, timeout = 20)
    soup = BeautifulSoup(page.text, 'html.parser')
    #print(soup)
    #with open('imbdHTML.txt', 'w') as file:
    #    file.write(str(soup))
    
    
    #https://www.youtube.com/watch?v=cO997sPYZ9U
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless = False)
    
    page = browser.new_page(java_script_enabled = True, viewport= {'width': 1920, 'height': 1080})
    page.goto(url, wait_until = "domcontentloaded", timeout = 6000)
    
    ##xpath_input = '//input[@placeholder="search imbd"]'
    ##page.wait_for_selector(xpath_prefix + xpath_input, timeout = 5000)
    ##input_element = page.query_selector(xpath_prefix + xpath_input)
    
    ##if input_element:
    page.wait_for_selector('a[href^="/title/tt"]', timeout = 6000)
    link = page.locator('a[href^="/title/tt"]').first
    href = link.get_attribute("href")
    
    if href:
        full_url = "https://www.imdb.com" + href
        page.goto(full_url)

    photoLink = page.locator('a[data-testid="hero__photo-link"]').click()
    
    
    
    
    
    st=True
    i = 0
    folderName = t
    seen = set()
    try:
        os.makedirs(folderName, exist_ok=True)
    except OSError as e:
        print(f"BAD folder")
    countBar = page.locator('span[data-testid="action-bar__gallery-count"]').inner_text()
    current, total = countBar.split(" of ")
    current = int(current.strip())
    total = int(total.strip())
    
    while st:
        
        nextButton = page.locator('div[role="button"][aria-label="Next"]')
        #imgURL = saveImg(url, page, headers)
        img = page.locator('img[data-testid="media-viewer-image"]').first
        
        #if nextButton.count() == 0 or imgURL in seen:
        if i >= total:
            st = False
            break
        
        else:
            #response = requests.get(imgURL, headers=headers,timeout=30)
            
            #if response.status_code == 200:
            filename = t + str(i) + ".png"
            filename2 = os.path.join(folderName, filename)
            print(filename2)
                
            img.screenshot(path=filename2)
                #with open(filename2, 'wb') as file:
                    #file.write(response.content)
                    
            #else:
                #print("BAD")
            
            #takeImg(page, url,  filename2)   
            i+=1
            #page.wait_for_selector('img[data-testid="media-viewer-image"]', timeout=20000)
            if i < total:
                nextButton.click()
            else:
                break
        #seen.add(imgURL)
        
    page.wait_for_timeout(30000)
    page.close()
    browser.close()
    playwright.stop()
    
#def takeImg(page,url, filepath):
    #byte[] arr = page.screenshot
    #page.scrrenshot(new Page.ScreenshotOptions().setPath(filepath))
    

def saveImg(url,page, headers):
    page.wait_for_selector('img[data-testid="media-viewer-image"]', timeout= 60000)
    imgScrape = page.locator('img[data-testid="media-viewer-image"]')
    srcset = imgScrape.get_attribute("srcset")
    
    return imgScrape.get_attribute("src")

if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    titles = printSet(path)
    #createSet(titles)
    scrapeExample(titles)
