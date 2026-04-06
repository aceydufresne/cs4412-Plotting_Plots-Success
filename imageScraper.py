import os
import re
import requests
import pandas as pd
from playwright.sync_api import sync_playwright

from pathlib import Path
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from concurrent.futures import ProcessPoolExecutor
from sklearn.cluster import KMeans
import math

def saveImg(page, urls, title):
    BASE_PATH = r"E:\imageDataset"  # your external SSD path

    # Clean folder + filename
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    full_path = os.path.join(BASE_PATH, safe_title)

    # Create movie folder
    os.makedirs(full_path, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for i, media_url in enumerate(urls, start=1):
        try:
            page.goto(media_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)

            img_locator = page.locator('img[src*="media-amazon.com"]').first

            if img_locator.count() == 0:
                print(f"No image found for {media_url}")
                continue

            src = img_locator.get_attribute("src")

            if not src:
                print(f"No src found for {media_url}")
                continue

            # Optional: get higher quality IMDb image
            if "._" in src:
                src = src.split("._")[0] + ".jpg"

            file_path = os.path.join(full_path, f"{safe_title}_{i}.jpg")

            # Skip if already downloaded (optional but useful)
            if os.path.exists(file_path):
                print(f"Skipping (already exists): {file_path}")
                continue

            response = requests.get(src, headers=headers, timeout=20)

            if response.status_code != 200:
                print(f"Failed download {src} | Status {response.status_code}")
                continue

            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"Saved: {file_path}")

        except Exception as e:
            print(f"Error saving image {i} for {title}: {e}")


def scrapeExample(titles):
    strPath1 = "https://www.imdb.com/find/?q="
    strPath2 = "&s=tt&ttype=ft"

    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)
    page = browser.new_page(
        java_script_enabled=True,
        viewport={"width": 1920, "height": 1080}
    )

    try:
        for title in titles:
            try:
                clean_title = title.strip()
                search_title = clean_title.replace(" ", "+")
                search_url = strPath1 + search_title + strPath2

                page.goto(search_url, wait_until="domcontentloaded", timeout=10000)

                page.wait_for_selector(
                    'li.ipc-metadata-list-summary-item a[href^="/title/tt"]',
                    timeout=8000
                )

                link = page.locator(
                    'li.ipc-metadata-list-summary-item a[href^="/title/tt"]'
                ).first

                href = link.get_attribute("href")
                if not href:
                    print(f"No result found for {clean_title}")
                    continue

                movie_url = "https://www.imdb.com" + href
                page.goto(movie_url, wait_until="domcontentloaded", timeout=10000)

                photo_link = page.get_by_role("heading", name="Photos")
                photo_link.click()

                page.wait_for_selector('span[data-testid="action-bar__gallery-count"]', timeout=8000)
                count_bar = page.locator('span[data-testid="action-bar__gallery-count"]').inner_text()
                current, total = count_bar.split(" of ")
                total = int(total.strip())

                grid_btn = page.locator('[data-testid="mv-gallery-button"]')
                grid_btn.click()

                page.wait_for_selector('a[data-testid^="mosaic-img"]', timeout=8000)
                imgs = page.locator('a[data-testid^="mosaic-img"]')

                urls = []
                max_imgs = min(10, imgs.count())

                for i in range(max_imgs):
                    img_href = imgs.nth(i).get_attribute("href")
                    if img_href:
                        full_media_url = "https://www.imdb.com" + img_href
                        urls.append(full_media_url)

                print(f"{clean_title}: found {len(urls)} media page URLs out of {total} images")
                saveImg(page, urls, clean_title)

            except Exception as e:
                print(f"Error with {title}: {e}")
                continue

    finally:
        page.close()
        browser.close()
        playwright.stop()

#https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
#https://pyimagesearch.com/2021/01/25/detecting-low-contrast-images-with-opencv-scikit-image-and-python/
def findContrast(path):
    setData = []
    for folder in path.iterdir():
        print("testing")
        tempBright= []
        tempContrast = []
                    #iterating through whole dataset
        for images in folder.iterdir():
            img = cv.imread(str(images), cv.IMREAD_GRAYSCALE)
            if img is None:
                print(f"image: {folder}")
                continue
            
            contrast = np.std(img)
            brightness = np.mean(img)
            tempBright.append(brightness)
            tempContrast.append(contrast)
            
            #histogram is for visuals, dont need it for the computation,
            #or the cdf
            #hist,bins = np.histogram(img.flatten(), 256,[0,256])
            #cdf = hist.cumsum()
            #cdfNormalized = cdf* float(hist.max()) / cdf.max()
            
            #plt.plot(cdfNormalized, color = 'b')
            #plt.hist(img.flatten(), 256, [0,256], color = 'r')
            #plt.xlim([0,256])
            #plt.legend(('cdf', 'histogram'), loc = 'upper left')
            #plt.show()
            
            
            
        #at the end we update the new averages for each film
        #print("testing")
        upBright = np.average(tempBright)
        upCont = np.average(tempContrast)
        setData.append({
                "title":folder.name,
                "avgBrightness": float(upBright),
                "avgContrast":float(upCont)
            })
    return setData

def orderContrast(setData):
    df = pd.DataFrame(setData)
    meanBrightness = df["avgBrightness"].mean()
    meanContrast = df["avgContrast"].mean()
    df1 = pd.read_csv("rotten_tomatoes_top_movies.csv")
    title = df1["title"]
    review = df1["critic_score"]
    setSize = len(setData)
    merged = pd.merge(
        df,
        df1,
        on="title",
        how="inner"
)
    
    #q1 = merged["critic_score"].quantile(0.25)
    #q2 = merged["critic_score"].quantile(0.50)
    #q3 = merged["critic_score"].quantile(0.75)
    
    setQ1 = []
    setQ2 = []
    setQ3 = []
    setQ4 = []
    q1Count = 0
    q2Count = 0
    q3Count = 0
    q4Count = 0
    
    q1Ratio = 0.0
    q2Ratio = 0.0
    q3Ratio = 0.0
    q4Ratio = 0.0
        
    #each movie is put into it's corresponding quarter
    merged["critic_score"] = pd.to_numeric(merged["critic_score"], errors="coerce")
    merged["avgContrast"] = pd.to_numeric(merged["avgContrast"], errors="coerce")
    merged["avgBrightness"] = pd.to_numeric(merged["avgBrightness"], errors="coerce")

    merged = merged.dropna(subset=["critic_score", "avgContrast", "avgBrightness"])

    q1 = merged["critic_score"].quantile(0.25)
    q2 = merged["critic_score"].quantile(0.50)
    q3 = merged["critic_score"].quantile(0.75)

    corr_contrast = merged["avgContrast"].corr(merged["critic_score"])
    corr_brightness = merged["avgBrightness"].corr(merged["critic_score"])

    print("Contrast vs Score:", corr_contrast)
    print("Brightness vs Score:", corr_brightness)
    
    #compare the contrast/brightness to the critic score, or outcome
    plt.scatter(merged["avgContrast"], merged["critic_score"])
    plt.xlabel("Contrast")
    plt.ylabel("Critic Score")
    plt.title("Contrast vs Critic Score")
    plt.show()
    
    plt.scatter(merged["avgBrightness"], merged["critic_score"])
    plt.xlabel("Brightness")
    plt.ylabel("Critic Score")
    plt.title("Brightness vs Critic Score")
    plt.show()



def moodFind(path):
    kernel = 0
    tempThresh = 30
    results = []
    for folder in path.iterdir():
        print("working")
        movieColors = {   
        }
        filmCount = []
        for imageFile in folder.iterdir():
            mergedColors = []
            sceneCol = {
            }
            count = 0
            img = cv.imread(str(imageFile))
            if img is None:
                continue
            #refactor the size of the image
            #to increase efficiency, dont need details in the image
            img = cv.resize(img,(50,50))
            for y in range(img.shape[0]):
                for x in range(img.shape[1]):
                    pixel = img[y,x]
                    #rgb values
                    b,g,r = pixel
                    #convert array into tuple
                    color = tuple(int(v) for v in pixel)
                    if color in movieColors:
                        movieColors[color] += 1
                    else:   
                        movieColors[color] = 1
                    
                    #this is for specific scene coutners:
                    if color in sceneCol:
                        sceneCol[color] += 1
                    else:
                        sceneCol[color] = 1
            #keys = list(sceneCol.keys())
            #for i in range(len(keys)):
             #   for j in range(i + 1, len(keys)):
              #      c2 = keys[i]
               #     c1 = keys[j]
                #        #use count to find the weighted averages
                 #   w1 = sceneCol[c1]
                  #  w2 = sceneCol[c2]
                   #         #euclidean distance
                    #eDist = (math.sqrt((c2[0] - c1[0])**2+(c2[1]-c1[1])**2+(c2[2]-c1[2])**2))
                     #       #if the distance between the colors is close enough
                            #then we merge those colors
                    #if eDist <= tempThresh:
                     #   wAvg = ((((c2[0]*w2)+(c1[0]*w1))/(w1+w2)),(((c2[1]*w2)+(c1[1]*w1))/(w1+w2)),(((c2[2]*w2)+(c1[2]*w1))/(w1+w2)))
                      #  mergedColors.append((wAvg, w2+w1))
            #prevent duplicated colors
            used = set()
            keys = list(sceneCol.keys())

            for m in range(len(keys)):
                base = keys[m]

                if base in used:
                    continue

                group = [base]
                used.add(base)

                for n in range(m + 1, len(keys)):
                    other = keys[n]

                    if other in used:
                        continue

                    eDist = math.sqrt(
                        (base[0] - other[0])**2 +
                        (base[1] - other[1])**2 +
                        (base[2] - other[2])**2
        )

                    if eDist <= tempThresh:
                        group.append(other)
                        used.add(other)
                        
                totalWeight = 0
                sumB = 0
                sumG = 0
                sumR = 0
                
                for c in group:
                    weight = sceneCol[c]
                    totalWeight += weight
                    sumB += c[0] * weight
                    sumG += c[1] * weight
                    sumR += c[2] * weight
                mergedColor = (sumB/totalWeight, sumG/totalWeight, sumR/totalWeight)
                mergedColors.append((mergedColor, totalWeight))
            ratios = []
            for merg in mergedColors:
                #50x50
                ratio = merg[1] / 2500
                ratios.append((merg[0], ratio))
    
                            
    #order the ratios, to get the highest three:
            ratios.sort(key=lambda x: x[1], reverse=True)
    #2500 * .15
            if len(ratios) < 3:
                    continue
            r1 = ratios[0][1]
            r2 = ratios[1][1]
            r3 = ratios[2][1]
                #normalize
            total3 = r1+r2+r3
            if total3 == 0:
                continue
            r1 = r1/total3
            r2 = r2/total3
            r3 = r3/total3
            trange = .15
                
            check60 = abs(r1 - 0.60) <= trange
            check30 = abs(r2 - 0.30) <= trange
            check10 = abs(r3 - 0.10) <= trange
            checkScene = check60 and check30 and check10
            filmCount.append((str(imageFile.name), checkScene, (r1, r2, r3)))
        movieName = folder.name 
        goodScenes = sum(1 for scene in filmCount if scene[1])
        totalScenes = len(filmCount)
        if totalScenes > 0:
            filmScore = goodScenes / totalScenes
            results.append((movieName, filmScore))
        else:
            filmScore = 0
            results.append((movieName, filmScore))
    
    return results

def plotGoodScenesVsCritic(results, df1):
    results = sorted(results, key=lambda x: x[1])
    plotted = []

    for movieName, filmScore in results:
        match = df1.loc[df1["title"] == movieName, "critic_score"]
        if len(match) == 0:
            continue
        critic_score = match.iloc[0]
        plotted.append((movieName, filmScore, critic_score))
    plotted.sort(key=lambda x: x[1])

    x = list(range(len(plotted)))
    critic_scores = [r[2] for r in plotted]

    plt.figure(figsize=(12,6))
    plt.scatter(x, critic_scores)
    plt.xlabel("60-30-10 Rule (Good Scene Ratio)")
    plt.ylabel("Critic Score")
    plt.title("Films by 60-30-10")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

       
if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    
    df1 = pd.read_csv(path)
    synopsis = df1["synopsis"]
    title = df1["title"]
    review = df1["critic_score"]
    genres = df1["genre"]
    
    #scrapeExample(title)
    #
    path2 = Path("E:/imageDataset")
    #setData = findContrast(path2)
    
    #print(setData)
    #df = pd.DataFrame(setData)
    #df.to_csv("movieFeatures.csv", index=False)
    #orderContrast(setData)
    results = moodFind(path2)
    plotGoodScenesVsCritic(results,df1)