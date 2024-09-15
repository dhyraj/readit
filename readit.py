import requests
from bs4 import BeautifulSoup
from enum import Enum
from validations import ValidationService
from validations import ValidationUtils
from constants import Constants
import time

class RedditTimeFilterType(Enum):
    ALL = 'ALL'
    YEAR = 'YEAR'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    HOUR = 'HOUR'

    _filterMapPerValue = {
        'ALL': ALL,
        'YEAR': YEAR,
        'WEEK': WEEK,
        'MONTH': MONTH,
        'HOUR': HOUR       
    }

    def getFilterByString(filter:str):
        if filter in RedditTimeFilterType._filterMapPerValue:
            return RedditTimeFilterType._filterMapPerValue[filter]
        else:
            RedditTimeFilterType.ALL

class RedditSortType(Enum):
    HOT = 'hot'
    NEW = 'new'
    TYPE = 'type'
    RISING = 'rising'

    _filterMapPerValue = {
        'hot': HOT,
        'new': NEW,
        'type': TYPE,
        'rising': RISING  
    }

    def getFilterByString(sortType:str):

        if sortType in RedditTimeFilterType._filterMapPerValue:
            return RedditSortType._filterMapPerValue[sortType]
        else:
            return RedditSortType.NEW

class Readit:
    def __init__(self, subreddit:str = None, url:str = None) -> None:
        self._path = None
        self.pathForMore = "/svc/shreddit/community-more-posts"
        self._url = None
        self.subreddit = None
        self.sort = RedditSortType.NEW
        self.timeFilter = RedditTimeFilterType.ALL

        self.setRedditUrl(url)
        self.setSubreddit(subreddit, url)
    
    def setRedditUrl(self, url: str = None):
        ValidationService.isUrlValid(url)
        self._url = url
        self.setPathFromURL(url)
    
    def setSubreddit(self, subreddit: str = None, url: str = None):

            if ValidationUtils.isNotEmptyString(subreddit):
                self.subreddit = f'r/{subreddit}' if subreddit[:2]!= 'r/' else subreddit
            elif ValidationUtils.isNotEmptyString(url):
                ValidationService.isUrlValid(url)
                # add r/ at first then remove reddit.com/r/ and the rest will have NAME/SORT/?after=
                # split by / then at 0 we will get name of the subreddit which is added to r/ at start
                self.subreddit = 'r/' + url.split(f'{Constants.domain[-10:]}/r/')[1].split("/")[0]
    
    def setPathFromURL(self, url: str)-> None:
        self._path = "".join(url.split("reddit.com")[1:])
                
    
    def getRedditUrlForPostsAfter(self, after: str = None, feedlength: int= 100):
        if ValidationUtils.isNotEmptyString(after): 
            self._url = f'{Constants.domain}/{self.pathForMore}/{self.sort.value}/?after={after}%3D%3D&name={self.subreddit[2:]}&feedLength={feedlength}'
        else:
            self._url = f'{Constants.domain}/{self.subreddit}/{self.sort.value}'
        return self._url

    def getAllSubmissions(self, sort: str = None, timeFilter: str = None, limit: int = 1000):

        if ValidationUtils.isNotEmptyString(sort): 
            self.sort = RedditSortType.getFilterByString(sort)

        if ValidationUtils.isNotEmptyString(timeFilter): 
            self.timeFilter = RedditTimeFilterType.getFilterByString(timeFilter)

        redditUrl = self.getRedditUrlForPostsAfter()
        return self.getSubmissions(redditUrl=redditUrl, limit=limit)
    
    def getSubmissions(self, redditUrl: str = None, size: int = 3, limit: int = 1000):
        
        if limit <= 0:
            return None
        
        timeOfRequest = time.time_ns()
        print(f"url ({timeOfRequest}): {redditUrl}")
        response = requests.get(redditUrl, verify= True)

        with open(f"lastResponsePages{timeOfRequest}.html", "w+") as page:
            page.write(response.text)

        if response.status_code == 200:
            redditSoup = BeautifulSoup(response.text, "html.parser")
            posts = redditSoup.find_all("shreddit-post")
            if posts is not None:
                nextToken, jsonPosts = self.processPosts(posts)
                print(f'loaded: {len(jsonPosts)}')
                loadMoreUrl = None
                if ValidationUtils.isNotEmptyString(nextToken):
                    loadMoreUrl = self.getRedditUrlForPostsAfter(nextToken, feedlength=size+25)
                else:
                    nextPageMetaData= redditSoup.find('faceplate-partial', {'slot': 'load-after'})
                    if nextPageMetaData is not None and nextPageMetaData.attrs is not None and ValidationUtils.isNotEmptyString(nextPageMetaData.attrs['src']):
                        loadMoreUrl = f'{Constants.domain}{nextPageMetaData.attrs["src"]}'

                if ValidationUtils.isNotEmptyString(loadMoreUrl):
                    nextJsonPosts = self.getSubmissions(redditUrl=loadMoreUrl, limit=limit - len(jsonPosts), size=size+25)
                    if nextJsonPosts is not None: 
                        jsonPosts.union(nextJsonPosts)

                return jsonPosts
        else:
            return None
    
    def processPosts(self, postsContainer):
        posts = set()
        nextToken = None
        for post in postsContainer:
            if post != None and post.name != None:
                # convert to json
                posts.add(post)
                if post.attrs is not None and 'more-posts-cursor' in post.attrs:
                    # continue
                    nextToken = post.attrs['more-posts-cursor']
        return nextToken, posts

    def getFullPostLinks(posts, fullUrl=False):
        urlToPostMap = {}
        for post in posts:
            fullPostTag= post.find("a", {"slot": 'full-post-link'})
            if not fullUrl:
                if fullPostTag is not None and fullPostTag.attrs is not None:
                    if fullPostTag.attrs['href'] is not None:
                        urlToPostMap[fullPostTag.attrs['href']] = post
                    elif post is not None and post.attrs is not None and post.attrs["permalink"]:
                        urlToPostMap[post.attrs["permalink"]] = post
                    else:
                        print("No post url found at all :(")
            else:
                urlToPostMap[post.attrs["content-href"]] = post
        return urlToPostMap

class RedditCommentGrabber:
    def __init__(self, postUrl:str = None) -> None:
        self.postUrl = postUrl
    
    



