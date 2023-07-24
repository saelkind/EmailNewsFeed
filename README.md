Command line program that sends emails to subscribers with  news items from topics they subscribe to.

The subscriptions are kept in an Excel spreadsheet which is read at startup.

All the articles are found through the newsapi.org API, although since we depend on the free account, the news is actually from yesterday.

Sends using a gmail account spec'd in the config file, where that and other externally-configurable params are found.
