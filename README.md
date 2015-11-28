There are two components to this project: the web scraper and the data analysis. All functions have detailed comments describing their purpose in greater detail.

For the automatic web scraper, call the start_collection function in scraper.py with the option to scraper percent recommended data (which takes a while longer as this information is not in any API) and with the option for robust review checking, as I noticed the walmart API would report inconsistent null review data for every 3-4/1000 items (default false as this is somewhat insignificant).
To exit out of the scraper, keyboard quit using ctrl+c

For the analysis functions, please see the images below for example outputs on all types of data produced by the scraper function. 

Finally, note that .csv files with 'pdata' include percent recommended data while those with 'data' do not (and analysis function calls should be adjusted accordingly.

cheers

![](https://cloud.githubusercontent.com/assets/15976155/11453930/2f738880-95eb-11e5-9d32-4488484d4989.png)
![](https://cloud.githubusercontent.com/assets/15976155/11453931/2f74c2f4-95eb-11e5-92b3-2c2c157801ae.png)
![](https://cloud.githubusercontent.com/assets/15976155/11453932/2f765e34-95eb-11e5-8945-ea597ea4a88f.png)
![](https://cloud.githubusercontent.com/assets/15976155/11453933/2f7b3788-95eb-11e5-99c3-6bf72016e1dd.png)
