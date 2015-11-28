import scraper as s

s.start_collection(scrape_perc_rec=False, robust_review_check=False)
#s.start_collection(scrape_perc_rec=True, robust_review_check=False)  # scrapes percent recommended data but takes a while longer
#s.start_collection(scrape_perc_rec=False, robust_review_check=True)  # double checks null rating/numreviews with review api, takes a bit longer 

# (api errors only occur every 4/1000 items so often not worth robust review check)
