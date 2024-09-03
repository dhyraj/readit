class InvalidRedditURLException(Exception):
    def __init__(self, message, errors):
        super(message)
        self.errors = errors