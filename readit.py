import requests
from bs4 import BeautifulSoup
from enum import Enum
from validations import ValidationService
from validations import ValidationUtils
from constants import Constants

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
                
    
    def getRedditUrlForPostsAfter(self, after: str = None, feedlength: int= 31):
        if ValidationUtils.isNotEmptyString(after): 
            self._url = f'{Constants.domain}/{self.subreddit}/{self.sort.value}/?after={after}%3D%3D&name={self.subreddit[2:]}&feedLength={feedlength}'
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
    
    def getSubmissions(self, redditUrl: str = None, limit: int = 1000):
        print("url: ", redditUrl)
        response = requests.get(redditUrl, verify= True)
        if response.status_code == 200:
            redditSoup = BeautifulSoup(response.text, "html.parser")
            posts = redditSoup.find_all("shreddit-post")
            if posts is not None:
                nextToken, jsonPosts = self.processPosts(posts)

                loadMoreUrl = None
                if ValidationUtils.isNotEmptyString(nextToken):
                    loadMoreUrl = self.getRedditUrlForPostsAfter(nextToken)
                else:
                    nextPageMetaData= redditSoup.find('faceplate-partial', {'slot': 'load-after'})
                    if nextPageMetaData is not None and nextPageMetaData.attrs is not None and ValidationUtils.isNotEmptyString(nextPageMetaData.attrs['src']):
                        loadMoreUrl = f'{Constants.domain}{nextPageMetaData.attrs["src"]}'

                if ValidationUtils.isNotEmptyString(loadMoreUrl):
                    nextJsonPosts = self.getSubmissions(loadMoreUrl, limit - len(jsonPosts))
                    if nextJsonPosts is not None: 
                        jsonPosts.extend(nextJsonPosts)

                return jsonPosts
        else:
            return None
    
    def processPosts(self, postsContainer):
        posts = list()
        nextToken = None
        for post in postsContainer:
            if post != None and post.name != None:
                # convert to json
                posts.append(post)
                if post.atts is not None and 'more-posts-cursor' in post.atts:
                    print("cursor set up")
                    nextToken = post.attrs['more-posts-cursor']
        return nextToken, posts



