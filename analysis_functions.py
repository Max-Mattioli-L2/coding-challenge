from datetime import date as dt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from scipy.stats import pearsonr
import csv


def read_csv(search_term, scrape_perc_rec):
    '''
    reads csv data created by write_data into a dictionary of the same format
    as data_dic for analysis
    '''
    data_dic = {}
    dates_covered = []  # list of all of the dates for which data_dic has a subdictionary
    if scrape_perc_rec:
        reader = csv.reader(open(search_term + ' pdata.csv', mode='rt'))
        next(reader)  # skip header
        for date_str, rank_str, id_str, brand_str, rating_str, num_reviews_str, percent_rec_str in reader:
            date_list = date_str.split('-')
            year = int(date_list[0])
            month = int(date_list[1])
            day = int(date_list[2])
            date = dt(year, month, day)
            if date not in dates_covered:  # if no sub-dic exists for a date
                data_dic[date] = {}
                dates_covered.append(date)
            rank = int(rank_str)
            rating = float(rating_str)
            num_reviews = int(num_reviews_str)
            data_dic[date][rank] = {}
            if percent_rec_str == '':
                percent_rec = ''
            else:
                percent_rec = int(percent_rec_str)
            data_dic[date][rank]['percent rec'] = percent_rec
            data_dic[date][rank]['brand'] = brand_str
            data_dic[date][rank]['rating'] = rating
            data_dic[date][rank]['num reviews'] = num_reviews
    else:
        reader = csv.reader(open(search_term + ' data.csv', mode='rt'))
        next(reader)  # skip header
        for date_str, rank_str, id_str, brand_str, rating_str, num_reviews_str in reader:
            date_list = date_str.split('-')
            year = int(date_list[0])
            month = int(date_list[1])
            day = int(date_list[2])
            date = dt(year, month, day)
            if date not in dates_covered:  # if no sub-dic exists for a date
                data_dic[date] = {}
                dates_covered.append(date)
            rank = int(rank_str)
            rating = float(rating_str)
            num_reviews = int(num_reviews_str)
            data_dic[date][rank] = {}
            data_dic[date][rank]['brand'] = brand_str
            data_dic[date][rank]['rating'] = rating
            data_dic[date][rank]['num reviews'] = num_reviews
    return pd.Panel.from_dict(data_dic, orient='minor').swapaxes(axis1='items', axis2='minor')


def top_n_result_pct(data_panel, start_date, end_date, rank_cutoff=None, drop_other=False):
    '''
    calculates the percentages of the top n search results owned by either
    Cheerios, Kashi, Kelloggs, Post, or Other
    '''
    br_list = ['Cheerios', 'Kashi', 'Kellogg', 'Post', 'other']
    if drop_other:
        br_list = ['Cheerios', 'Kashi', 'Kellogg', 'Post']
    total = 0.0
    percent_dic = {}
    for brand in br_list:
        percent_dic[brand] = 0
    for day_data in date_range_data(data_panel, start_date, end_date):
        gb = day_data.transpose()[:rank_cutoff].groupby('brand')
        for brand in br_list:
            try:
                percent_dic[brand] += len(gb.get_group(brand).index)
                total += len(gb.get_group(brand).index)
            except KeyError:
                continue
    for brand in br_list:
        percent_dic[brand] = percent_dic[brand]/total*100
    if rank_cutoff:
        print '\nThe percentages of the top ' + str(rank_cutoff) + ' search results'\
                    + ' belonging to each brand are as follows:'
    else:
        print '\nThe percentages of the total search results belonging to each brand are as follows:'
    if drop_other:
        print '(Note: The reported percentages are relative, considering only search results '\
                + 'which contain our important brands.)'
    return percent_dic


def corr_attr_rank(data_panel, attribute, rank_cutoff=None, min_attr=0):
    '''
    Up to an optional maximum rank, DOES SOMETHING !! for a specific attribute
    'rating', 'num reviews', or 'percent rec' and an (optional) minimum value of the attribute,
    ex. min_attr=1 for 'rating' to exclude all without ratings
    '''
    all_attributes = np.array(data_panel.axes[1])
    attr_index = np.where(all_attributes == attribute)[0][0]
    trimmed_data = data_panel[:, attr_index, :rank_cutoff][(data_panel[:, attr_index, :rank_cutoff] >= min_attr).all(1)]
    trimmed_data = trimmed_data[trimmed_data != ''].dropna()
    ranks = np.array(trimmed_data.index)
    if not rank_cutoff:
        rank_cutoff = ranks[-1]
    attr_matrix = trimmed_data.values.transpose()
    attr_matrix = np.float64(attr_matrix)
    attr_vals = np.reshape(attr_matrix, len(attr_matrix)*len(ranks))
    ranks = np.float64(np.tile(ranks, len(attr_matrix)))
    corr = pearsonr(attr_vals, ranks)
    x_reg = np.copy(attr_vals)
    x_reg = sm.add_constant(x_reg)
    model = sm.RLM(ranks, x_reg)
    ft = model.fit()
    print ft.summary()
    plt.figure()    
    plt.plot(attr_vals, ft.predict(x_reg))
    plt.gca().invert_yaxis()
    plt.gca().set_xlim(min(attr_vals)-1, max(attr_vals)+1)
    plt.gca().set_ylim([rank_cutoff+1, 0])
    plt.xlabel(attribute)
    plt.ylabel('search rank')
    plt.title('search rank vs ' + attribute)
    plt.scatter(attr_vals, ranks)
    return '\nThere is a ' + str(corr[0])[:7] + ' correlation between search rank and '\
                    + attribute + ' with p-value ' + str(corr[1])[:7]


def date_range_data(data_panel, start_date, end_date):
    '''
    gets all of the data in a date range for a datapanel
    '''
    dates_with_data = np.array(data_panel.axes[0])
    for date in pd.date_range(start_date, end_date):
        date = dt(date.year, date.month, date.day)
        if date not in dates_with_data:
            print 'no data for ' + str(date) + ', skipping'
        else:
            yield data_panel[date]


def avg_brand_attr(data_panel, start_date, end_date, rank_cutoff=None, percent_rec=False, drop_zeros=True, drop_other=False):
    '''
    calculates the average attribute for each brand in the entire data panel up to a rank cutoff
    set percent_rec to True to include % recommended, drop_zeros to False
    to include zero values and drop_other to True to exclude brand-nonspecific data
    '''
    br_list = ['Cheerios', 'Kashi', 'Kellogg', 'Post', 'other']
    days_counted = 0
    br_without_data = []
    avg_attr_dic = {}
    if drop_other:
        br_list.remove('other')
    for day_data in date_range_data(data_panel, start_date, end_date):
        days_counted += 1
        gb = day_data.transpose()[:rank_cutoff].groupby('brand')
        for brand in br_list:
            try:
                brand_data = gb.get_group(brand).transpose().drop('brand')
                if percent_rec:
                    brand_data = brand_data.drop(brand_data.columns[np.where((brand_data.loc['percent rec'] == ''))[0]], axis=1)
                if drop_zeros:
                    brand_data = brand_data.drop(brand_data.columns[np.where((brand_data.loc['num reviews'] == 0))[0]], axis=1)
            except KeyError:
                print 'not enough data for ' + brand
                br_without_data.append(brand)
                continue
            try:
                avg_attr_dic[brand] += brand_data.transpose().mean()
            except KeyError:
                avg_attr_dic[brand] = brand_data.transpose().mean()
    avg_attr_df = pd.DataFrame.from_dict(avg_attr_dic)
    for brand in br_list:
        if days_counted == br_without_data.count(brand):
            continue
        else:
            avg_attr_df[brand] = avg_attr_df[brand] / (days_counted - br_without_data.count(brand))
    if rank_cutoff:
        print '\nThe average attributes of each brand over the given date range and up to search rank ' + str(rank_cutoff)\
                + ' are as follows:'
    else:
        print '\nThe average attributes of each brand over the given date range over all search results '\
                + ' are as follows:'
    return avg_attr_df
