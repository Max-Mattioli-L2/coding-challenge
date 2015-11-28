import analysis_functions as a
from datetime import date as dt


start_date = dt(2015,11,23)
end_date = dt(2015,11,28)

cereal_data = a.read_csv('cereal', False)
cold_cereal_data = a.read_csv('cold cereal', False)
cereal_pdata = a.read_csv('cereal', True)
cold_cereal_pdata = a.read_csv('cold cereal', True)


#example analysis for different types of recorded data
print '\nExample analysis for cereal data including percent recommended data'
print a.corr_attr_rank(cereal_pdata, 'rating', min_attr=0, rank_cutoff=100)
print a.avg_brand_attr(cereal_pdata, start_date, end_date, percent_rec=True)
print a.top_n_result_pct(cereal_pdata, start_date, end_date, rank_cutoff=3)

#print '\nExample analysis for cold cereal data including percent recommended data'
#print a.corr_attr_rank(cold_cereal_pdata, 'num reviews', rank_cutoff=50)
#print a.avg_brand_attr(cold_cereal_pdata, dt(2015,11,25), end_date, rank_cutoff=50, percent_rec=True)
#print a.top_n_result_pct(cold_cereal_pdata, dt(2015,11,25), end_date, rank_cutoff=50)
#
#print '\nExample analysis for cereal data not including percent recommended data'
#print a.corr_attr_rank(cereal_data, 'rating', min_attr=1, rank_cutoff=500)
#print a.avg_brand_attr(cereal_data, dt(2015,11,27), end_date, percent_rec=False, rank_cutoff=500)
#print a.top_n_result_pct(cereal_data, dt(2015,11,27), end_date, rank_cutoff=500)
#
#print '\nExample analysis for cold cereal data not including percent recommended data'
#print a.corr_attr_rank(cold_cereal_data, 'rating', min_attr=1)
#print a.avg_brand_attr(cold_cereal_data, dt(2015,11,27), end_date, percent_rec=False, drop_other=True)
#print a.top_n_result_pct(cold_cereal_data, dt(2015,11,27), end_date, drop_other=True)
