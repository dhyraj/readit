from exceptions import InvalidRedditURLException
from constants import Constants

class ValidationService:

    def __init__(self) -> None:
        pass

    @staticmethod
    def isUrlValid(url: str = None):
        if ValidationUtils.isEmptyString(url) or url[:len(Constants.domain)] != Constants.domain:
                raise InvalidRedditURLException("reddit url must start with https://www.reddit.com")
        
        
    @staticmethod
    def isStringValid(anyString: str = None):
        if anyString is None or len(anyString)==0:
            raise InvalidRedditURLException("reddit url must start with https://www.reddit.com")
        
class ValidationUtils:
        
    @staticmethod
    def isEmptyString(anyString: str = None) -> bool:
        if anyString is None or len(anyString)==0:
            return True
        return False
    
    @staticmethod
    def isNotEmptyString(anyString: str = None) -> bool:
        return ValidationUtils.isEmptyString(anyString) == False
        
