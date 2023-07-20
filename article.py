

class Article:
    '''Article object consisting of topic it belongs to, the URL where it can be
    found, and a snippet from the aricle (e.g., title, firt few lines, etc)
    '''

    def __init__(self, topic:str, url: str, snippet: str):
        self.topic = topic
        self.url = url
        self.snippet = snippet
