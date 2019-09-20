# Webscraper

The intializing data script takes in several CSVs that have some initial information on homes that were sold in the last 3 years in Boston, MA. 

These initial CSVs were gotten from Redfin.com by searching Boston, MA and then switching to homes that were sold in the last 3 years. 
(https://www.redfin.com/city/1826/MA/Boston/filter/include=sold-3yr). Underneath the first ~20 listings that are shown in the side panel is a link to "download all" the listings that fit that criteria. 
However, this will only download the 350 listings by default. 
To get the initial information on more than those houses, zoom in on different areas of the map, and reduce the number of homes that fit the criteria (i.e., showing ~20 of ~18000 homes) to a number less than 350. 
Scroll around the map and download the different csvs will result in coverage for various areas.
This process is slow and could be result in a lot of overlap, but if a person wants to see where the homes are that are being downloaded the map on the left will provide that information.

The other option for downloading more than 350 homes is to alter the link that the "download all" button goes to (https://www.redfin.com/stingray/api/gis-csv?al=1&market=boston&min_stories=1&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id=1826&region_type=6&sold_within_days=1095&status=9&uipt=1,2,3,4,5,6&v=8). 
Change the "350" after "num_homes" to a larger number.
There may be a standard cap since it is changing the API request so some scrolling might be required but it should not be nearly as much.
Note: this could also be used to change how many years back to go with the data as it goes back 3 years from the current date. 
To go back further change "1095" to a larger number after "sold_within_days"

Then the initializing data script will take these CSVs in a subfolder and combine them all into a single dataframe and remove any duplicate entries (the URL of the entry is used as a unique identifier), and write a new csv with these home listings.

After these CSVs are combined, the webscraper will use the file generated to get key pieces of information needed. 
The initial data frame does not have the date a home was last listed or when there was some form of agreement to sell the home. 
Rather it only has the close date which is not as good to use for predictions because closing dates are often much later than the agreed sale date by months because banks can slow down the process. 
Furthermore, if you are a home buyer once there is an agreement you cannot put in a new offer even if the house hasn't closed.
Therefore, the difference between the list date and the agreed sale date is the one that should be used when determining how long a home is on the market.

The webscraper will go to various home listings and gather these key pieces of information. 
Selenium is used rather than other packages, because there is dynamic content on the page that needs to be loaded before the data can be captured.
A table must be clicked on to expand it so that the full history of a home listing can be grabbed.
This is necessary because some of the home listings do not have the date a home was last listed initially shown because of pricing changes.
After it grabs the pieces of information it will write/overwrite the file that it initally reads in so that the data are not lost.
The webscraper has builtin in fail safes, but there are some failures that it cannot handle such as loss of internet connection. 
Occasionally it will simply fail and it is unclear the reason why, i.e., it just stops and the error is not because content is missing or anything like that.

This webscraper was built to run on a single desktop computer for quite a while. 
It can simultaneously be run on another computer running from the end of the list at the same time by simply commenting out/commenting in the block of code that determines the urls that need to be loaded.
It might be possible to run multiple scrapers at once on a single machine but the script would need to be altered such that it does not start in the same spot/do the same listings (maybe set them up to do odds/evens) and does not write over the same file; however, this has not been tested.
Doing so could greatly speed up the process.
