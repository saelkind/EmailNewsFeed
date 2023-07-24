
# EmailNewsFeed Application

My App #7 solution for the _*Advanced Python Programming: Build 10 OOP Applications.*_

Command line program that sends emails to subscribers with  news items from topics they subscribe to.

The subscriptions are kept in an Excel spreadsheet which is read at startup.

All the articles are found through the _newsapi.org_ API. However, we depend on the free account limitations, so the news is actually from yesterday.

Sends using a gmail account specified in the config file, where that and other externally-configurable params are found.
