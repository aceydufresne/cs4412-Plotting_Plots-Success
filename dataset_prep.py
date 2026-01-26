#import kagglehub
import csv

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
            

if __name__ == "__main__":
    path = "rotten_tomatoes_top_movies.csv"
    printSet(path)

