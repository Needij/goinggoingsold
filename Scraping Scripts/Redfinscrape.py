#load packages that will be used
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import numpy as np

#read in dataframe that contains all the listings and create a list of all the urls
#NOTE when this process first begins this is a copy of the past3years.csv file that was created by the other script.
df_sold = pd.read_csv('housingtoscrape.csv', low_memory = False)
urls = df_sold['URL']


#load webdriver (this is dependent on where the webdriver exe is loaded on the computer 
driver = webdriver.Chrome('C:/ProgramData/Chrome Driver/chromedriver.exe')

#find where to begin the scraper
for i in df_sold.index:
    if(pd.isna(df_sold.iloc[i].DATE_LAST_LISTED) == True): #date last listed will be filled in throughout the process so checking if this is missing will make sure the process starts
       urlstodo = urls[i:len(urls)] #use just a subset of the urls
       break

#when using another computer to start at the end and work forward use following
#make sure to comment out above code to not waste time iterating through the front portion
#for i in df_sold.index[::-1]: #reverse order
#       if(pd.isna(df_sold.iloc[i].DATE_LAST_LISTED) == True: 
#          urlstodo = urls[0:i] #grab all the urls from beginning to the point where the urls aren't filled in
#          urlstodo = urlstodo[::-1] #reverse the order so that the process begins at the end
#          break

#for all the urls that need to be done iterate through and grab the pieces of information that are needed
for i in urlstodo:
    #create empty objects for the various pieces of information that need to be grabbed
    date_last_listed = ''
    contin_sale_date = ''
    agree_sale_date = ''
    description = ''
    listed_price = ''

    #load the webpage
    driver.get(i)
    #wait for page to load
    time.sleep(3)

    #try to see if the page loaded
    #if it does not find that element wait a minute and then try to load the page again
    #then wait another minute
    try:
        driver.find_element_by_id('content')
    except NoSuchElementException:
        time.sleep(60)
        driver.get(i)
        time.sleep(60)

    #try to find a description if there is no the description found, label it as 'Not found'    
    try:
        desc_cont = driver.find_element_by_id('marketing-remarks-scroll')
        description = desc_cont.text
    except NoSuchElementException:
        description = 'NOT_FOUND'

    #try to find the table that contains the dates listed and dates sold/under some contract
    #if that does exist. Click on it to expand it. If it does not do nothing
    try:
        driver.find_element_by_id('propertyHistory-expandable-segment').click()
        time.sleep(1)
    except NoSuchElementException:
        pass

    #find the element that contains the table that contains the dates
    #get the html of that table so it can be converted to a dataframe
    tableholder = driver.find_element_by_id('property-history-transition-node')
    table = pd.read_html(tableholder.get_attribute('innerHTML'))
    table = pd.DataFrame(table[0])

    #find the date listed and the price listed
    listeddates = list(table[table['Event & Source'].str.contains('Listed')]['Date'])
    listedprice = list(table[table['Event & Source'].str.contains('Listed')]['Price'])
    #find a contingent sale and agreed sale date
    pending_contin = list(table[table['Event & Source'].str.contains('Cont')]['Date'])
    pending_agree = list(table[table['Event & Source'].str.contains('Under')]['Date'])

    #if there is multiple contingent sales in the table, keep only the most recent one
    try:
        contin_sale_date = pending_contin[0]
    except IndexError:
        pass

    #if there are multiple agreed sales in the table, keep only the most recent one
    try:
        agree_sale_date = pending_agree[0]
    except IndexError:
        pass

    #if there are multiple listed dates in the table, keep only the most recent one, if there is no most recent sale date retry everything 
    try:
        date_last_listed = listeddates[0]
    except IndexError:
        try:
            time.sleep(2) #wait 2 seconds
            driver.find_element_by_id('propertyHistory-expandable-segment').click() #click on table to expand it
            time.sleep(1) #wait a second
            tableholder = driver.find_element_by_id('property-history-transition-node') #grab the table container
            table = pd.read_html(tableholder.get_attribute('innerHTML')) #convert to html
            table = pd.DataFrame(table[0]) #convert html to dataframe
            listeddates = list(table[table['Event & Source'].str.contains('Listed')]['Date']) #find list date
            listedprice = list(table[table['Event & Source'].str.contains('Listed')]['Price'])#find list price
            pending_contin = list(table[table['Event & Source'].str.contains('Cont')]['Date'])#find contingent sale date
            pending_agree = list(table[table['Event & Source'].str.contains('Under')]['Date'])#find agreed sale date
            date_last_listed = listeddates[0]#grab most recent last listed date
            try:
                contin_sale_date = pending_contin[0] #keep only most recent contingent sale date
            except IndexError:
                pass
        
            try:
                agree_sale_date = pending_agree[0] #keep only the most recent agreed sale date
            except IndexError:
                pass
            
        except NoSuchElementException: #if the element doesn't exist then pass
            pass

    #set listed price to most recent list price    
    listed_price = listedprice[0]
    #set the date listed, list price, description, contingent sale date, agreed sale date for only the selected house. Leave all other homes alone
    df_sold.DATE_LAST_LISTED = np.where(df_sold.URL == i, date_last_listed, df_sold.DATE_LAST_LISTED)
    df_sold.LIST_PRICE = np.where(df_sold.URL == i, listed_price, df_sold.LIST_PRICE)
    df_sold.DESCRP = np.where(df_sold.URL == i, description, df_sold.DESCRP)
    df_sold.CONT_SALE_DATE = np.where(df_sold.URL == i, contin_sale_date, df_sold.CONT_SALE_DATE)
    df_sold.AGREE_SALE_DATE = np.where(df_sold.URL == i, agree_sale_date, df_sold.AGREE_SALE_DATE)

    #write file (so that no data is lost throughout the process
    df_sold.to_csv('housingtorescrape.csv', index = False)
    time.sleep(1) #wait a second before continuing

driver.quit() #quit webdriver once all URLS have been iterated through
