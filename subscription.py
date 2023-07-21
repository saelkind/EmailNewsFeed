from typing import List


class Subscription:
    '''Subscript for one person.  Has his/her name, email address. and a list of
    topics of interest
    '''

    # def __init__(self, subscription_rec: []):
    def __init__(self):
        self.firstname: str = None
        self.lastname: str = None
        self.email_address: str = None
        self.subscription_list: list = None
