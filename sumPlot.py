import nltk
from nltk.corpus import names
import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util
import string
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans
from collections import defaultdict
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def setPrep(path):
    nltk
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('names')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('averaged_perceptron_tagger_eng')
    df = pd.read_csv(path)
    nameSet = names.words()
    synopsis = df["synopsis"]
    title = df["title"]
    genre = df["genre"]

    combined = []

    for s, t, g in zip(synopsis, title, genre):
        combined.append({
        "title": t,
        "synopsis": s,
        "genre": g
    })
    
    
    protang = [
        "hero",
        "heroine",
        "antihero",
        "tragic hero",
        "main protagonist",
        "ordinary person",
        
    "detective solving a mystery",
    "young hero discovering powers",
    "ordinary person in danger",
    "antihero seeking revenge",
    "student protagonist",
    "soldier in war",
    "bounty hunter antihero seeking revenge",
    "lawman or ranger enforcing justice",
    "criminal antihero in violent world",
    "lone gunslinger in western setting",
    "reluctant hero forced into action",
    "hero on a quest",
    "survivor in hostile environment",
    "explorer in unknown land",
    "superhero"
    ]
    
    environment = [
    "small town",
    "big city",
    "wild west",
    "desert environment",
    "forest environment",
    "war zone",
    "battlefield",
    "space setting",
    "future world",
    "post apocalyptic world",
    "school setting",
    "urban environment",
    "rural environment",
    "prison environment",
    "island setting",
    "ocean setting"
    ]
    
    mood = [
    "dark tone",
    "lighthearted tone",
    "tense atmosphere",
    "hopeful tone",
    "violent tone",
    "emotional tone",
    "tragic tone",
    "mysterious tone",
    "suspenseful tone",
    "romantic tone",
    "comedic tone"
    ]
    
    protangVec = []
    envVec = []
    moodVec = []
    for x in protang:
        embedding = model.encode(x,convert_to_tensor=True)
        protangVec.append((x, embedding))
        
    for y in environment:
        embedding = model.encode(y,convert_to_tensor=True)
        envVec.append((y,embedding))
    for z in mood:
        embedding = model.encode(z,convert_to_tensor=True)
        moodVec.append((z, embedding))
    
    pattern = r"(JJ.*\s+)*(NN.*)"
    highestMatches = []
    nameSet = set(name.lower() for name in names.words())
    for item in combined:
        syn = item["synopsis"]
        if pd.isna(syn):
            continue
        
        
        
        syn = str(syn)
        tempSyn = syn.split()
        tempSum = syn.lower()
        tempSum = tempSum.split()
        filtered = []

        filtered = []
        prev_was_person = False

        for term in tempSyn:
            clean = term.strip(string.punctuation).lower()

            if not clean:
                continue

            if clean in nameSet:

                if not prev_was_person:
                    filtered.append("person")
                    prev_was_person = True
            else:
                filtered.append(clean)
                prev_was_person = False

        tagged = nltk.pos_tag(filtered)
        
        
        matched = []
        i = 0
        while i<len(tagged):
            words = []
            while i < len(tagged) and tagged[i][1].startswith("JJ"):
                words.append(tagged[i][0])
                i+=1
            if i < len(tagged) and tagged[i][1].startswith("NN"):
                while i < len(tagged) and tagged[i][1].startswith("NN"):
                    words.append(tagged[i][0])
                    i+=1
                matched.append(" ".join(words))
            else:
                i+=1
        highestMatches.append({
            "title": item["title"],
            "genre": item["genre"],
            "synopsis": item["synopsis"],
            "matches": matched
        })
    #print(highestMatches)
    
    protangMatch = []
    moodMatch = []
    envMatch = []
    finalMatches = []
    
    
    for movie in highestMatches:
        bestScore = -1
        bestPhrase = None
        bestProtang = None
        
        for sequence in movie["matches"]:
            protangEmbed = model.encode(sequence, convert_to_tensor=True)
            
            for protangeName, protangeEmbedding in protangVec:
                score = util.cos_sim(protangEmbed, protangeEmbedding).item()
                
                if score > bestScore:
                    bestScore = score
                    bestPhrase = sequence
                    bestProtang = protangeName

        synopsisText = str(movie["synopsis"])
        synopsisEmbed = model.encode(synopsisText, convert_to_tensor=True)
        genVec = model.encode(synopsisText)
        bestEnv = None
        bestEnvScore = -1
        
        bestPro = None
        bestProScore = -1
        
        for proName, proEmbedding in protangVec:
            score = util.cos_sim(synopsisEmbed, proEmbedding).item()
            if score > bestProScore:
                bestProScore = score
                bestPro = proName
        
        for envName, envEmbedding in envVec:
            score = util.cos_sim(synopsisEmbed, envEmbedding).item()
            if score > bestEnvScore:
                bestEnvScore = score
                bestEnv = envName

        
        bestMood = None
        bestMoodScore = -1
        
        for moodName, moodEmbedding in moodVec:
            score = util.cos_sim(synopsisEmbed, moodEmbedding).item()
            if score > bestMoodScore:
                bestMoodScore = score
                bestMood = moodName
        
        finalMatches.append({
            
            "title": movie["title"],
            "mood": bestMood,
            "moodScore": bestMoodScore,
            "environment": bestEnv,
            "enviroment score": bestEnvScore,
            "protanginist": bestProtang,
            "protanganist score": bestScore,
            "altPro": bestPro,
            "altproScore": bestProScore,
            "genMatch": genVec
        })
        
    
    #print(finalMatches)
    return finalMatches

def comVec(finalMatches):
    comFinVec = []
    proWeight = 1.5
    moodWeight = 1.5
    envWeight = 1.0
    genWeight = .25
    for entry in finalMatches:
        
        itemTitle = entry["title"]
        itemMood = model.encode(entry["mood"])
        itemEnv = model.encode(entry["environment"])
        itemPro = model.encode(entry["altPro"])
        itemGen = entry["genMatch"]
        
        weightedPro = itemPro * proWeight
        weightedMood = itemMood *moodWeight
        weightedEnv = itemEnv * envWeight
        weightedGen = itemGen * genWeight
        
        combined = np.concatenate([
            weightedPro, weightedMood, weightedEnv, weightedGen
        ])
        normalizedCombined = normalize(combined.reshape(1, -1))[0]
        comFinVec.append({
            "title": itemTitle,
            "combined": normalizedCombined
        }
        )
        
    return comFinVec

def group(finalVecs):
    k = 8
    X = np.array([entry["combined"] for entry in finalVecs])
    kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(X)
    clustered = []
    
    for entry, label in zip(finalVecs, labels):
        clustered.append({
            "title": entry["title"],
            "cluster": int(label),
            "combined": entry["combined"]
        })
    clusterGroups = defaultdict(list)
        
    for entry in clustered:
        clusterGroups[entry["cluster"]].append(entry["title"])
    return clustered, clusterGroups, kmeans

def graph(clustered):
    X = np.array([entry["combined"] for entry in clustered])
    labels = [entry["cluster"] for entry in clustered]
    titles = [entry["title"] for entry in clustered]
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X)
    
    plt.figure(figsize=(10, 7))
    scatter = plt.scatter(coords[:, 0], coords[:, 1], c=labels)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("Updated Implementation")
    plt.colorbar(scatter, label="Cluster")
    
    plt.show()
    
def kRating(clustered, path):
    df = pd.read_csv(path)
    df["critic_score"] = pd.to_numeric(df["critic_score"], errors="coerce")

    scoreMap = dict(zip(df["title"], df["critic_score"]))
    clusterScores = defaultdict(list)

    for entry in clustered:
        title = entry["title"]
        cluster = entry["cluster"]
        score = scoreMap.get(title)

        if pd.notna(score):
            clusterScores[cluster].append(float(score))

    results = {}

    for cluster, scores in clusterScores.items():
        if len(scores) > 0:
            scores_arr = np.array(scores)

            avg = scores_arr.mean()
            std = scores_arr.std()

            results[cluster] = {
                "average": avg,
                "std": std,
                "count": len(scores),
                "min": scores_arr.min(),
                "max": scores_arr.max()
            }

            print(
                f"Cluster {cluster}: "
                f"Avg = {avg:.2f}, "
                f"Std = {std:.2f}, "
                f"Min = {scores_arr.min()}, "
                f"Max = {scores_arr.max()}"
            )

    return results


def graphClusterReviews(clustered, path, targetCluster):
    df = pd.read_csv(path)
    scoreMap = dict(zip(df["title"], df["critic_score"]))

    titles = []
    scores = []

    for entry in clustered:
        if entry["cluster"] == targetCluster:
            title = entry["title"]
            score = scoreMap.get(title)

            if score is not None:
                titles.append(title)
                scores.append(score)

    plt.figure(figsize=(12, 6))
    plt.bar(titles, scores)

    plt.xlabel("Movie")
    plt.ylabel("Critic Score")
    plt.title(f"Critic Scores for Cluster {targetCluster}")

    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
    
def describeClusters(clustered, matches):
    matchMap = {m["title"]: m for m in matches}
    clusters = defaultdict(list)

    for entry in clustered:
        clusters[entry["cluster"]].append(entry["title"])

    for c, titles in clusters.items():
        prot = []
        mood = []
        env = []

        for t in titles:
            m = matchMap[t]
            prot.append(m["altPro"])
            mood.append(m["mood"])
            env.append(m["environment"])

        topProt = Counter(prot).most_common(2)
        topMood = Counter(mood).most_common(2)
        topEnv = Counter(env).most_common(2)

        print(f"\nCluster {c}")
        print("Top Prot:", topProt)
        print("Top Mood:", topMood)
        print("Top Env:", topEnv)
        
def runAssociationRules(transactions):
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)

    df = pd.DataFrame(te_array, columns=te.columns_)
    frequent = apriori(df, min_support=0.05, use_colnames=True)

    rules = association_rules(frequent, metric="lift", min_threshold=1.2)
    print(rules[["antecedents", "consequents", "support", "confidence", "lift"]])

    return rules

def buildTransactions(matches):
    transactions = []

    for m in matches:
        transaction = [
            m["altPro"],
            m["mood"],
            m["environment"]
        ]
        transactions.append(transaction)

    return transactions


if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    
    matches = setPrep(path)
    normalizedFinal = comVec(matches)
    clustered, clusterGroups, kmeans = group(normalizedFinal)
    graph(clustered)
    results = kRating(clustered, path)
    print(results)
    
    for cluster in results.keys():
        graphClusterReviews(clustered, path, cluster)
    
    describeClusters(clustered, matches)
    transactions = buildTransactions(matches)
    rules = runAssociationRules(transactions)
