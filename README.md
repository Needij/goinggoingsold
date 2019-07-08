# GoingGoingSold
Predicting how long a home is on the market. 

This app predicts how long a home in Boston, MA will be on the market.

Users input the neighborhood, the list price, HOA fees (0 if N/A), the years since the home has been remodeled last, the age of the home in years, and if the kitchen and bathroom have been remodeled (i.e., are semi-modern, modern, or luxury in style). 

Upon hitting submit, the days predicted on the market will be updated and range will be provided. The range is built by using the RMSE to build the interval. 

It should be noted that some inputs only result in minor changes in predictions, and due to rounding do not reflect changes in the days predicted upon hitting submit.

Also, users who are curious about how their home compares to others in a particular neighborhood, they can switch modes to visualize the list price by days on the market for homes using a different set of features of the home. In this mode users can select neighborhood, number of bedrooms, number of bathrooms, and the minmum and maximum square footage they want to view (contrained to have a range of at least 500 between the min/max.). The graph below these inputs will automatically update with homes that meet those criteria (if no homes meet that criteria an error message is overlayed on the graph). Additionally users can hover over points to gather more information about a particular home, such as the exact square footage, the home type (condo, single-family, etc.), and some information about the remodeling that has been done.
