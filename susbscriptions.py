

class Subscriptions:
    '''The list of subscriptions to process at each cycle.
    Each item in the list is a subscription: subscriber name, email, and list
    of news topics of interest.
    '''

    def __init__(self, excel_filename):
        self.excel_filename = excel_filename
        self.subscriptions_list = self.load_subscriptions()
        self.news_sender = NewsSender("files/subscriptions.xls")

    def load_subscriptions(self):
        pass

    def process_subscriptione(self) -> (int , int, int):
        '''process the subscriptions in the list'''
        pass
