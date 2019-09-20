#packages to import
import os
import pandas as pd

#create empty dataframe to hold all data
df = pd.DataFrame()

#iterate through files, and join them together
cwd = os.getcwd()
for files in os.listdir(cwd + '/CSVs to Combine'):
        file_dir = cwd + '/CSVs to Combine/' + files
        new_df = pd.read_csv(file_dir)
        df = pd.concat([df, new_df])

#rename URL column
df.rename(columns ={'URL (SEE http://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)':'URL'}
          , inplace = True)

#remove any listings that have duplicate URLS
df.drop_duplicates(subset = 'URL', inplace = True)

#drop any listings without a sold date
df.dropna(subset = ['SOLD DATE'], inplace = True)

#write file of houses that should be scraped
df.to_csv('past3yearshomes.csv')
