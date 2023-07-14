

class NewsSender:
    '''For any given subscription, the NewsSender located news items of intereest
    to the subscriber, then emails the list in a nicely-formatted (hah!) email
    to the subscriber
    The NewsSender also maintains a connection to the News Feed's email account for
    sending the emails
    '''

    MAX_ARTICLES_PER_TOPIC: int = 5
    EMAIL_ACCT_FILENAME = "files/email.json"

    def __init__(self):
        self.email_account_filename = email_account_filename
        self.sender_account_name = None
        self.sender_account_connection = None

    def open_email_account_connection(self) -> (bool, str):
        '''Open the connection to the email account.  If the connection fails,
        return False and the relevant error message to the caller.  Do  not store
        the password in anything but a local var'''
        pass
