import requests
from bs4 import BeautifulSoup
from os import path as osPath
import time
import html_to_json as htmlToJson
import json
from inputimeout import inputimeout
import random

domain = "https://www.reddit.com"
path = "/r/AskReddit"
name="AskReddit"
redditTime = ['ALL', 'YEAR', 'WEEK', 'MONTH', 'HOUR']
timeCounter = 0

postTitles = set()
titleAndContentDict = {}

def getRedditTime():
    return redditTime[timeCounter]

def incTimeCounter():
    global timeCounter
    timeCounter += 1

def loadJsonFile() -> list:
    if osPath.isfile("./redditHotResponse.json") is False:
        return []
    
    with open("redditHotResponse.json", "r") as rr:
        return json.load(rr)

def writeToJsonFile(jsonList: list) -> None:
    with open("redditHotResponse.json", "w") as wr:
        wr.write(str(jsonList))

jsonfile = loadJsonFile()


def getUrl() -> str: return domain + path
# print(getUrl())

def populatePath(html):
    global path
    body = html.find("body")
    facePlatePartial = body.find("faceplate-partial", {'slot': 'load-after'})
    if facePlatePartial:
        nextPathSrc = facePlatePartial.attrs["src"] 
        if nextPathSrc != None:
            path = nextPathSrc.split("&")[0] + "&t=ALL&name=" + name
        else:
            print("No path")
            path = None 
    else:
        if len(postTitles) > 0:
            fname = f'redditLastresponse {time.ctime()}.html'
            print("file: ", fname)
            with open(fname,'wb') as f:
                f.write(html.encode('utf-8'))
        print("No Path")
        path = None



def crawlPerpetually():
    global jsonfile
    # try:
    # print("DOING A GET")
    response = requests.get(getUrl(), verify= True)
    if response.status_code == 200:
        html = BeautifulSoup(response.text, "html.parser")
        print(type(html.children))
        body = html.find("body")
        shApp = body.find("shreddit-app")
        facePlateBatch = shApp.find("faceplate-batch")

        populatePath(html)

        if facePlateBatch:
            processArticles(facePlateBatch)
            response = True
        else:
            # print("no facePlatebatch :(")
            response = False
    
    return response

    # except Exception as e:
    #     print("error occurred: ", e)
    #     # writeToJsonFile(jsonfile)

notPrinted = True
def processArticles(facePlateBatch):
    global path
    # print("processing article")
    if facePlateBatch != None:
        articles = facePlateBatch.find_all("article")
        # print("processing articles")
        for i,article in enumerate(articles):
            post = article.find("shreddit-post")
            jsonValue = htmlToJson.convert(post.text)
            # if notPrinted:
            #     print(jsonValue)
            jsonfile.append(jsonValue)
            textBodyPost = post.find("a", {"slot": "text-body"})
            title = post.find("a", {"slot": "full-post-link"}).text
            if textBodyPost == None:
                strippedTitle = str(title).strip()
                if title not in postTitles:
                    postTitles.add(title)
                    # print(f'articles processed: {len(jsonfile)} articles loaded: {len(postTitles)} duplicate articles: {len(jsonfile) - len(postTitles)}')
                else:
                    pass
                    # print(f'[Duplicate] {len(jsonfile)}. {strippedTitle if len(strippedTitle)<120 else strippedTitle[:110]+"..."}')
                print(f'articles processed: {len(jsonfile)} articles loaded: {len(postTitles)} duplicate articles: {len(jsonfile) - len(postTitles)}', end="\r")
                # print("no post body: ", titleOnlyPost.text)
                # print("givingContext for #attrs: ", post.find("a", {"slot": "full-post-link"}))
            else:
                if title not in titleAndContentDict:
                    titleAndContentDict[title] = textBodyPost.find_all('p')
            print(f'articles processed: {len(jsonfile)} articles loaded: {len(postTitles)} duplicate articles: {len(jsonfile) - len(postTitles)}', end="\r")
                
            if i == len(articles)-1 and path == None:
                if 'more-posts-cursor' in post.attrs and post.attrs['more-posts-cursor'] != "":
                    # print("resetting the next path using article")
                    path = f'/svc/shreddit/community-more-posts/hot/?after={post.attrs["more-posts-cursor"]}%3D%3D&t={random.choice(redditTime)}&name={name}'
                    print("NEW PATH: ", path)
                    incTimeCounter()
                    time.sleep(10)
                # print("Next Token: ", post.attrs["more-posts-cursor"])
                # print("Changed Path: ", path)
                # try:
                #     to = random.choice([15, 20, 25, 30])
                #     choice = inputimeout(prompt=f'Change( TimeOut: {to} ): ', timeout=to)
                # except:
                #     choice = ''
                # if choice == 'y':
                #     path = input("new URL: ")

    else: 
        # print("facePlateBatch is empty", facePlateBatch)
        pass

    
def crawl():
    response = crawlPerpetually()
    # print("titles: ", len(postTitles)," titleAndContentDict: ", len(titleAndContentDict))

    if response:
        if(len(titleAndContentDict) == 0):
            crawl()
        userInput = input(" do you want to continue: ")
        if  userInput in ['', None, "Y", "y"]:
                crawl()
        elif userInput == "show":
            print("\n\nTitles: ", postTitles)
            print("\n\nContent: ", **titleAndContentDict, sep="\n")
    elif not response:
        if path in [None, '']:
            exit()
        else:
            if len(postTitles) == 0:

                crawl()
            elif input("none response do you want to continue: ") in ['', None, "Y", "y"]:
                crawl()
            else: 
                exit()
    else:
        # print("Error Occurred on GET: ", response)
        exit()

crawl()
