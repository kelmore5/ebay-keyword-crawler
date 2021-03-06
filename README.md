# Ebay Keyword Crawler

This is a tool that was used for a research project involving analysis of the community pages
on ebay.com

It uses peewee and SQLite for data management; Selenium, Chrome, and pyvirtualdisplay for headless browsing
(since ebay doesn't have its own API); and xlrd and xlwt for outputting the data to CSV and Excel.

Utilizing Selenium, the script has four steps: 

- Navigate to set community forums on ebay and download all the links for each board
- Once obtained, download all the messages for each forum post
- Parse out pre-defined keywords within each message and upload results to an SQLite database
- Output the results to CSV and/or Excel

Every page parsed using Selenium is downloaded and saved to a database via SQLite for safe-keeping,
and the script should restart the browser automatically to forgo ebay's crawling protection

This project utilizes two other projects of mine: [python-utilities](https://github.com/kelmore5/python-utilities) and [SeleniumBrowser](https://github.com/kelmore5/SeleniumBrowser), both of which
should already be uploaded within this git repository.

*Note: SQLite was chosen over MySQL or Postgres to improve portability of the script, but any database could be 
adopted if need be.

This has been checked and was working on **May 1, 2018**, but I have no plans to maintain the project.

## Install

### Dependencies

- python 3.6
- pyvirtualdisplay
- xlrd
- xlwt
- [selenium](http://selenium-python.readthedocs.io/installation.html)
- [Xvfb](https://www.x.org/archive/X11R7.6/doc/man/man1/Xvfb.1.xhtml) (May not be necessary - check install of pyvirtualdisplay)
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/)
- [peewee](https://github.com/coleifer/peewee)

*pyvirtualdisplay and Xvfb are used to create the headless display, selenium and chromedriver are used for the actual browsing

### Run

First, download the repo

    git clone --recurse-submodules -j8 https://github.com/kelmore5/ebay-keyword-crawler
    
Once downloaded and dependencies are installed, you can run it via

    python3 lib/EbayParser.py
    


You can change the boards being parsed and the keywords to search for by modifying EbayParser.py (top of file, line 40)

```python
# Set keywords to search for here
keywords = [
    ["good deal", "great deal", "fair deal", "best deal", "good price", "great price", "fair price", "best price",
    "good customer", "great customer", "repeat customer", "fair", "honest", "reasonable"],
    ["scam", "scams", "scammed", "scamming", "scammer", "scammers", "fraud", "frauds", "defrauded", "fraudster",
    "fraudsters", "con", "cons", "conned", "conning", "con artist", "con artists", "trick", "tricks", "tricked",
    "tricking", "trickster", "tricksters", "swindle", "swindles", "swindled", "swindler", "swindlers"]
]
    
# Set board names and links to be downloaded here
board_names = ['Bidding and Buying', 'Selling']
    
board_urls = ["http://community.ebay.com/t5/Bidding-Buying/bd-p/bidding-buying-db",
                "http://community.ebay.com/t5/Selling/bd-p/selling-db"]
```

## Extra Links

- [Selenium](https://www.seleniumhq.org/)
- [Selenium Python Docs](http://selenium-python.readthedocs.io/)
- [Peewee Documentation](http://docs.peewee-orm.com/en/latest/)

## Proof of Concept

You can see a demo from a slideshow I've created [here](https://docs.google.com/presentation/d/1VlSL0dZrbhQeY3bIFUGEmSkFARycCc31zmQlNqx_7BY/edit?usp=sharing)
or you can look at the sample output from [this](https://github.com/kelmore5/ebay-keyword-crawler/raw/master/demo/output_demo.xlsx) Excel sheet, screenshotted below.

Either way here are some pictures to give a proof of concept, with even more residing in 
the [demo](https://github.com/kelmore5/ebay-keyword-crawler/tree/master/demo) folder above

Here's a pic of the forum from ebay before download

![Ebay Bidding and Buying Forum](/demo/pictures/ebay_bidding_and_buying.png "Ebay Bidding and Buying Forum")

and the resulting database in SQL

![Posts SQL Database](/demo/pictures/posts_database.png "Posts SQL Database")

Some examples of the messages being parsed from ebay 

![Ebay Messages Example 1](/demo/pictures/ebay_messages_1.png "Ebay Messages Example")

![Ebay Messages Example 2](/demo/pictures/ebay_messages_2.png "Ebay Messages Example 2")

Both messages now in database, ready to be searched through for keywords

![Messages SQL Database](/demo/pictures/messages_database.png "Messages SQL Database")

The keywords database

![Keywords SQL Database](/demo/pictures/keywords_database.png "Keyboards SQL Database")

And finally the resulting output in Excel

![Excel Output - Main](/demo/pictures/excel_output_main.png "Excel Output - Main")

![Excel Output - Simple Stats](/demo/pictures/excel_output_keywords.png "Excel Output - Simple Stats")
