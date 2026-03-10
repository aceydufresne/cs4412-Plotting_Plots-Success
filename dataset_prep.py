import kagglehub
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from playwright.sync_api import sync_playwright
import os
import csv
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
model = SentenceTransformer('all-MiniLM-l6-v2')
import nltk
from nltk import PorterStemmer
from nltk.corpus import stopwords
import time
from sklearn.metrics.pairwise import cosine_similarity
from numpy import dot
from numpy.linalg import norm
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from sklearn.cluster import KMeans


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

def scrapeExample(title):
    xpath_prefix = 'xpath='
    
    strPath1 = "https://www.imdb.com/find/?q="
    strPath2 = "&s=tt&ttype=ft"
    #title = titles[27] #this is working
    title = title.strip() #this is working
    t = title.replace(" ", "+") #this is working
    #print(t)
    url = strPath1 + t + strPath2 #this is working
    #print(url)
    
    headers = { #this is working
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    page = requests.get(url, headers=headers, timeout = 20) #this is working
    soup = BeautifulSoup(page.text, 'html.parser') #this is working
    #print(soup)
    #with open('imbdHTML.txt', 'w') as file:
    #    file.write(str(soup))
    
    
    #https://www.youtube.com/watch?v=cO997sPYZ9U
    playwright = sync_playwright().start() #this is working
    browser = playwright.firefox.launch(headless = False) #this is working
    
    page = browser.new_page(java_script_enabled = True, viewport= {'width': 1920, 'height': 1080}) #this is working
    page.goto(url, wait_until = "domcontentloaded", timeout = 6000) #this is working
    
    ##xpath_input = '//input[@placeholder="search imbd"]'
    ##page.wait_for_selector(xpath_prefix + xpath_input, timeout = 5000)
    ##input_element = page.query_selector(xpath_prefix + xpath_input)
    
    ##if input_element:
    page.wait_for_selector('a[href^="/title/tt"]', timeout = 6000) #this is working
    link = page.locator('li.ipc-metadata-list-summary-item a[href^="/title/tt"]').first #this is working
    href = link.get_attribute("href") #this is working
    
    if href:
        full_url = "https://www.imdb.com" + href
        page.goto(full_url) #this is working, for this case test

    
    photoLink = page.get_by_role("heading", name="Photos") 
    photoLink.click()
    
    st=True
    
    folderName = t
    seen = set()
    #try:
        #os.makedirs(folderName, exist_ok=True)
    #except OSError as e:
        #print(f"BAD folder")
    countBar = page.locator('span[data-testid="action-bar__gallery-count"]').inner_text()
    current, total = countBar.split(" of ")
    current = int(current.strip())
    total = int(total.strip())
    img = page.locator('img[data-testid="media-viewer-image"]').first
    nextButton = page.locator('div[role="button"][aria-label="Next"]').first
    i = 0
    gridBtn = page.locator('[data-testid="mv-gallery-button"]')
    gridBtn.click()
    print(total)
    
    imgs = page.locator('a[data-testid^="mosaic-img"]')
    urls = []
    
    #for testing purposes, we'll set this to a higher
    #value when we need to start plotting data
    for i in range(10):
        href = imgs.nth(i).get_attribute("href")
        print(href)
        full = "https://www.imdb.com" + href
        urls.append(full)
    saveImg(urls, title)
    print(len(urls))
    
    #page.wait_for_timeout(30000)
    page.close()
    browser.close()
    playwright.stop()
    
    return 0
#def takeImg(page,url, filepath):
    #byte[] arr = page.screenshot
    #page.scrrenshot(new Page.ScreenshotOptions().setPath(filepath))
    

def saveImg(urls,title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    folder = os.path.join(os.getcwd(), title)
    os.makedirs(folder, exist_ok=True)
    index = 1
    for i in urls:
        path = os.path.join(folder, f"{index}.jpg")
        r = requests.get(i, timeout=30)
        
        with open(path,"wb") as f:
            f.write(r.content)
            print(f"saved {index}")
        index+=1
    return 0




#########################PLOT_VECTORS_SIMILIARITY###################################################





def embedPlot(path):
    movieData = []
    columns = []
    #replaced the csv reader for more efficient sorting
    df = pd.read_csv(path)
    #print(df["title"])
    plots = df["synopsis"]
    titles = df["title"]
    
    testName = titles[0]
    testPlot = plots[0]
    
    #We need punctution for right now
    #/match = re.findall(r"[A-Za-z0-9]+", testPlot)
    #print(match)
    #print( "\nremoving punctuation")
    
    #lowercased
    words = testPlot.lower()
    
    words = words.split()
    #print(words)
    ##print(len(words))
    #start configuring vectprs
    windows = []
    i = 1
    sentence = []
    for word in words:
        if i <= 10:
            #window/kernel size is 10
            sentence.append(word)
            i+=1
        elif i>10:
            i = 1
            windows.append(sentence)
            #sentence = sentence.clear()
            sentence = []
    #https://www.youtube.com/watch?v=OlhNZg4gOvA
    #print(windows[0])
    for sentences in windows:
        embeddings = model.encode(sentences)
    print(embeddings)
    return embeddings

def vectorizeData(data):
    #data is the set of movies in a specific critic review range
    setPlots = []    #removed the window to test performance
    
    for title,score,plot in data:
        embedding = model.encode(str(plot))
        setPlots.append((title,embedding))
    return setPlots

def vectorizeData1(data):
    titles = [x[0] for x in data]
    scores = [x[1] for x in data]
    plots = [x[2] for x in data]

    embeddings = model.encode(plots)

    return list(zip(titles, scores, embeddings))
        
        #https://www.youtube.com/watch?v=pgzXzVU4nJQ
def findSimiliarity(set):
    returnSet = []
    #i = 0
    #y = 1

    for i in range(len(set)):
        title1, emb1 = set[i]
        for y in range(i+1,len(set)):
            title2, emb2 = set[y]
            #cos_sim = dot(set[i], set[y]) / (norm(set[i]*norm(set[y])))
            temp = cosine_similarity([emb1], [emb2])[0][0]
            returnSet.append(((title1,title2),temp))
        #print(returnSet)
    return returnSet
            

def graphPlot(groupingName,genreData):
    
    titles = [t[0] for t in genreData]
    scores = [x[1] for x in genreData]
    genre = [y[2] for y in genreData]
    
    plt.figure(figsize=(10,7))
    plt.boxplot(scores)

    plt.xlabel("Genre")
    plt.ylabel("Critic Score")
    plt.boxplot(scores)
    plt.title(f"Box Plot for {groupingName}")
    plt.xticks([1], [groupingName])

    plt.show()
    
def graphVectors(cosSet):
    #we need to lookup the critic review for each film, much easier than modifying
    #the previous functions to implement the ranking
    path = "rotten_tomatoes_top_movies.csv"
    df = pd.read_csv(path)
    
    titles = [t[0] for t in cosSet]
    cos = [x[1] for x in cosSet]
    #bracket = [z[3] for z in cosSet]
    score = dict(zip(df['title'], df['critic_score']))
    xSet = []
    ySet1 = []
    ySet2 = []
    
    score = dict(zip(df['title'], df['critic_score']))
    
    
    for val, cosVal in cosSet:
        #two movie titles
        t1,t2 = val
        #search by title to get the score
        s1 = score.get(t1)
        s2 = score.get(t2)
        
        if s1 == "critic_score":
            print("caught")
        elif s1 <= 20:
            bracket = 10
        elif s1 <= 30:
            bracket = 20
        elif s1 <= 40:
            bracket = 30
        elif s1 <= 50:
            bracket = 40
        elif s1 <= 60:
            bracket = 50
        elif s1 <= 70:
            bracket = 60
        elif s1 <= 80:
            bracket = 70
        elif s1 <= 90:
            bracket = 80
        else:
            bracket = 90
        
        ySet1.append(s1)
        ySet2.append(s2)
        xSet.append(cosVal)
    
    plt.scatter(xSet, ySet1, color='blue', label='Movie 1')
    plt.scatter(xSet, ySet2, color='red', label='Movie 2')
    
    plt.xlabel('Cosine Similirity (kg)')
    plt.ylabel('Critic Score')
    plt.title(f'Comparison of similirity and critic reviews for {bracket}')
    plt.legend()
    plt.grid(True)
    plt.show()
        

def graphVectors1(vectors):
    titles = [x[0] for x in vectors]
    scores = [x[1] for x in vectors]
    embeddings = [x[2] for x in vectors]

    pca = PCA(n_components=2)
    coords = pca.fit_transform(embeddings)

    x = coords[:,0]
    y = coords[:,1]

    plt.figure(figsize=(10,7))
    scatter = plt.scatter(x, y, c=scores, cmap="viridis")

    plt.colorbar(scatter, label="Critic Score")

    plt.xlabel("Vector Dimension 1")
    plt.ylabel("Vector Dimension 2")
    plt.title(f"Vector Map for {groupingName}")

    plt.show()
    
def normalization(vectors):
    normalized = []
    #scaler = StandardScaler()
    #X_scaled = scaler.fit_transform(vectors)
    for title, embedding in vectors:
        vector = np.array(embedding, dtype=float)
        norm = np.linalg.norm(vector)
        if norm == 0:
            #return vector
            normalized.append(vector)
        else:
            normalized.append(vector / norm)
    return normalized

def pcaProc(nv):
    x = np.array(nv)
    print(x.shape)
    pca = PCA(n_components=20)
    pca.fit(x)
    data_pca = pca.transform(x)
    data_pca = pd.DataFrame(data_pca,columns=['PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8','PC9','PC10','PC11','PC12','PC13','PC14','PC15','PC16','PC17','PC18', 'PC19', 'PC20'])
    
    sns.heatmap(data_pca.corr())
    plt.show()
    
    print(data_pca.head())
    print(pca.explained_variance_ratio_)
    #https://www.geeksforgeeks.org/machine-learning/k-means-clustering-introduction/
    clusters = {}
    k = 10
    X = data_pca
    
    kmeans = KMeans(n_clusters=10, random_state=42)
    data_pca["cluster"] = kmeans.fit_predict(data_pca)

    sns.scatterplot(
        x=data_pca["PC1"],
        y=data_pca["PC2"],
        hue=data_pca["cluster"]
    )
    plt.show()
    
    data_pca["cluster"].value_counts().sort_index().plot(kind="bar")

    plt.xlabel("Cluster")
    plt.ylabel("Number of Movies")
    plt.title("Movies per Cluster")
    plt.show()

    return data_pca, kmeans
    
    
    
    
if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    
    #index = 1
    #titles = printSet(path)
    #for title in titles:
        #scrapeExample(title)
        #print(index)
        #index+=1
    ##path = kagglehub.dataset_download("thedevastator/rotten-tomatoes-top-movies-ratings-and-technical")
    #embeddings = embedPlot(path)
    
    
    
    df = pd.read_csv(path)
    synopsis = df["synopsis"]
    title = df["title"]
    review = df["critic_score"]
    genres = df["genre"]
    
    genreSet = {}
    for t1, score1, style in zip(title, review, genres):
        #style is a string
        genre = str(style).lower().strip()
        #genre is split into groups with divisor ','
        groups = genre.split(",")
        
        for group in groups:
            group = group.strip()
            
            if group not in genreSet:
                genreSet[group] = []
                genreSet[group].append((t1,score1,group))
            elif group in genreSet:
                genreSet[group].append((t1,score1,group))
        
    for groupingName,genreData in genreSet.items():
        #graphPlot(groupingName,genreData)
        #print(groupingName, len(vectors))
        vectors = vectorizeData1(genreData)
        #graphVectors(groupingName,vectors)
    
    set10 = []
    set20 = []
    set30 = []
    set40 = []
    set50 = []
    set60 = []
    set70 = []
    set80 = []
    set90 = []
    
    count = 1
    
    #sort into similiar scores
    for t, score,syn in zip(title, review,synopsis):
        if score == "critic_score":
            print("caught")
        elif score <= 20:
            set10.append((t, score,syn))
        elif score <= 30:
            set20.append((t, score,syn))
        elif score <= 40:
            set30.append((t, score,syn))
        elif score <= 50:
            set40.append((t, score,syn))
        elif score <= 60:
            set50.append((t, score,syn))
        elif score <= 70:
            set60.append((t, score,syn))
        elif score <= 80:
            set70.append((t, score,syn))
        elif score <= 90:
            set80.append((t, score,syn))
        else:
            set90.append((t, score,syn))
    allScores = []
    allScores.append(set10)
    allScores.append(set20)
    allScores.append(set30)
    allScores.append(set40)
    allScores.append(set50)
    allScores.append(set60)
    allScores.append(set70)
    allScores.append(set80)
    allScores.append(set90)
    
    allNormVec = []
    for set in allScores:
        test1 = vectorizeData(set)
        normVec = normalization(test1)
        #test2 = findSimiliarity(test1)
        #cosVec = findSimiliarity(normVec)
        #print(test1)
        #graphVectors(cosVec)
        #print(len(test2))
        allNormVec.extend(normVec)
    pcaProc(allNormVec)
