from news_sender import NewsSender

class Subscriptions:
    '''The list of subscriptions to process at each cycle.
    Each item in the list is a subscription: subscriber name, email, and list
    of news topics of interest.
    '''

    IDX_FIRSTNAME = 0
    IDX_LASTNAME = 1
    IDx_EMAIL = 2
    IDX_TOPIC_LIST = 3

    def __init__(self, excel_filename: str):
        self.excel_filename: str = excel_filename
        # array of subscription arrays
        self.subscriptions_list: [[]] = self.load_subscriptions()
        self.news_sender = NewsSender("files/subscriptions.xls")

    def load_subscriptions(self) -> [[]]:
        pass

    def process_subscription(self) -> (int , int, int):
        '''process the subscriptions in the list'''
        pass
