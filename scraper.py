from bs4 import BeautifulSoup as bs
from datetime import date as dt
import requests as req
import math
import time
import csv
import os.path
import schedule


def scrape_data(data_dic, page_data, page_num, robust_review_check):
    '''
    given an individual search pages data, scrape_data finds the relevant data
    of brand, rating, and number of reviews with relation to item rank.
    deepest function in the web scraping solution.
    '''
    brand_list = ['Cheerios', 'Kashi', 'Kellogg', 'Post']
    rank = (page_num - 1) * 25 + 1  # for 25 results a page the nth page will start with the (25(n-1) + 1)th ranked result
    for link in page_data.find_all('item'):
        data_dic[rank] = {}
        brand_text = link.find('name').contents[0]
        item_id = link.find('itemid').contents[0]
        raw_rating = link.find('customerrating')  # some results haven't been rated
        raw_num_reviews = link.find('numreviews')  # if a result has 1 rating there is no numreviews
        if raw_rating is not None and raw_num_reviews is not None:
            rating = float(raw_rating.contents[0])
            num_reviews = int(link.find('numreviews').contents[0])
        elif raw_num_reviews is None and raw_rating is not None:  # if a rating but no number for reviews, 1 review (walmarts specification)
            num_reviews = 1
            rating = float(raw_rating.contents[0])
        elif raw_num_reviews is None and raw_rating is None:  # if neither a rating or number for reviews
            if robust_review_check:  # if you want to be really sure, check the review api
                time.sleep(.07)
                site = req.get('http://api.walmartlabs.com/v1/reviews/' + item_id + '?apiKey=hqgqkj7ww6b4h8ja2468r3rg&format=xml')
                review_page_data = bs(site.content, from_encoding='xml')
                try:
                    rating = float(review_page_data.find('averageoverallrating').contents[0])
                    num_reviews = int(review_page_data.find('totalreviewcount').contents[0])
                except AttributeError:
                    rating = 0
                    num_reviews = 0
                time.sleep(.06)
            else:  # otherwise, just set both to 0
                rating = 0
                num_reviews = 0
        for brand in brand_list:
            if brand in brand_text:  # if our target brands are in the brand text
                data_dic[rank]['brand'] = brand  # record brand name
                break
            elif brand not in brand_text:
                data_dic[rank]['brand'] = 'other'  # if not, the brand doesn't matter
        data_dic[rank]['rating'] = rating
        data_dic[rank]['num reviews'] = num_reviews
        data_dic[rank]['id'] = item_id
        rank += 1


def get_term_data(search_term, robust_review_check):
    '''
    moderates the overall data collection for a given search term,
    calling scrape_page_data for each page in the total results
    '''
    data_dic = {}
    site = req.get('http://api.walmartlabs.com/v1/search?apiKey=hqgqkj7ww6b4h8ja2468r3rg&format=xml&numItems=25&start=' + '1' + '&query=' + search_term)
    page_data = bs(site.content, from_encoding='xml')
    num_results = int(page_data.find('totalresults').contents[0])  # number of matches for search in walmart database
    num_queries = int(math.ceil(num_results/25.0))  # maximum search results per request is 25 items
    if num_queries > 40:  # maximum total search results displayed is 1000 even if num_results > 1000
        num_queries = 40
    print 'starting quick api data scraping for ' + search_term
    scrape_data(data_dic, page_data, 1, robust_review_check)  # scrape first page for relevant data
    print str(1.0/num_queries*100)[0:4] + '% complete with scraping for ' + search_term
    for page_num in range(2, num_queries + 1):
        site = req.get('http://api.walmartlabs.com/v1/search?apiKey=hqgqkj7ww6b4h8ja2468r3rg&format=xml&numItems=25&start=' + str((page_num - 1) * 25 + 1) + '&query=' + search_term)
        page_data = bs(site.content, from_encoding='xml')
        scrape_data(data_dic, page_data, page_num, robust_review_check)
        print str(float(page_num)/float(num_queries)*100)[0:4] + '% complete with scraping for ' + search_term
        time.sleep(.1)  # walmart allows for no more than 5 api requests per second, this ensures that will never happen
    return data_dic


def scrape_percent_rec(data_dic, search_term):
    '''
    collects the percent recommended data for each product using their produc reviews page.
    as this is not in the API, full scraping for all search terms takes some time.
    '''
    total_results = float(len(data_dic.keys()))
    print 'starting percent recommended data scraping for ' + search_term
    for rank in data_dic.keys():
        item_id = data_dic[rank]['id']
        num_reviews = data_dic[rank]['num reviews']
        if num_reviews == 0:  # probably not a % rec if no reviews
            percent_rec = 0
        else:
            site = req.get('https://www.walmart.com/reviews/product/' + item_id)
            page_data = bs(site.content, 'html5lib')
            raw_recommend_str = page_data.find('b', {'class': 'meter-text'})
            if raw_recommend_str is None:
                percent_rec = ''  # different from 0 - 0 means no one recommends
            else:
                percent_rec = int(page_data.find('b', {'class': 'meter-text'}).find(text=True)[0: -1])
        data_dic[rank]['percent rec'] = percent_rec
        if rank % 25 == 0:
            print str(float(rank)/total_results*100)[0:4] + '% complete with scraping percent recommended data for ' + search_term
    return data_dic


def write_data(data_dic, search_term, scrape_perc_rec):
    '''
    writes the data given a populated data dictionary for a given search term
    if scrape_perc_rec, writes/appends to csv of name 'cereal pdata.csv'
    if not, writes/appends to csv of name 'cereal data.csv'
    '''
    today = dt.today()
    write_header = True
    if scrape_perc_rec:
        if os.path.isfile(search_term + ' pdata.csv'):  # if the file already exists
            write_header = False  # dont write a header
        with open(search_term + ' pdata.csv', 'a') as datafile:  # add on to existing csv
            df = csv.writer(datafile)
            if write_header:
                df.writerow(['date'] + ['search rank'] + ['id'] + ['brand'] + ['rating'] + ['num reviews'] + ['percent rec'])
            attrs = ['id', 'brand', 'rating', 'num reviews', 'percent rec']
            for rank in data_dic.keys():
                df.writerow([today] + [rank] + [data_dic[rank][attr] for attr in attrs])
    else:
        if os.path.isfile(search_term + ' data.csv'):  # if the file already exists
            write_header = False  # dont write a header
        with open(search_term + ' data.csv', 'a') as datafile:  # add on to existing csv
            df = csv.writer(datafile)
            if write_header:
                df.writerow(['date'] + ['search rank'] + ['id'] + ['brand'] + ['rating'] + ['num reviews'])
            attrs = ['id', 'brand', 'rating', 'num reviews']
            for rank in data_dic.keys():
                df.writerow([today] + [rank] + [data_dic[rank][attr] for attr in attrs])
    datafile.close()


def process_all_data(scrape_perc_rec, robust_review_check):
    '''
    calls get_term_data and write_data for all desired search terms
    '''
    search_terms = ['cereal', 'cold cereal']
    for search_term in search_terms:
        data_dic = get_term_data(search_term, robust_review_check)
        if scrape_perc_rec:
            data_dic = scrape_percent_rec(data_dic, search_term)
        write_data(data_dic, search_term, scrape_perc_rec)


def start_collection(scrape_perc_rec=True, robust_review_check=False):
    '''
    initiates a daily loop to collect and process all data.
    highest level function in scraping automation.

    if scrape_perc_rec, an additional scraping sequence is called after the bare-bones
    scraping where ther percent recommended data is collected for each item. This data
    is not in the walmart API so adds some time.

    if robust_review_check, the bare-bones scraping will double check wal-marts search API
    against the review API, as there are around ~4 discrepansies per 1000 products.
    Default is false as this adds some time for almost the same results
    '''
    schedule.every().day.at('12:00').do(process_all_data, scrape_perc_rec, robust_review_check)
    while True:
        schedule.run_pending()
        time.sleep(1)
