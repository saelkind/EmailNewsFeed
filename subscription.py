from typing import List


class Subscription:
    '''Subscript for one person.  Has his/her name, email address. and a list of
    topics of interest
    '''

    def __init__(self, subscription_rec: []):
        self.firstname = None
        self.lastname = None
        self.email_address = None
        self.subscription_list: () = None
