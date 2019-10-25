'''
This file contains all the parameters required for the Kickstarter delivery analysis.
'''
testing = True

#end-of-year dates in Unix time.
end_2013 = 1388534400
end_2014 = 1420070400
end_2015 = 1451606400
end_2016 = 1483228800

#We will not consider projects with rewards promised beyond this date.
end_date = end_2015

#Path to the scraped kickstarter and comment pickles
if testing:
	#Small test files
	raw_kickstarter_pickle = "input/processed_dataframes/all_kickstarters_test"
	raw_comments_pickle = "input/processed_dataframes/all_comments_test"
else:
	#Large full files
	raw_kickstarter_pickle = "input/processed_dataframes/all_kickstarters_full"
	raw_comments_pickle = "input/processed_dataframes/all_comments_full"

#Path to safe the cleaned kickstarter and comment pickles
if testing:
	#Small test files
	cleaned_kickstarter_pickle = "input/processed_dataframes/all_kickstarters_test_cleaned"
	cleaned_comments_pickle = "input/processed_dataframes/all_comments_test_cleaned"
else:
	#Large full files
	cleaned_kickstarter_pickle = "input/processed_dataframes/all_kickstarters_full_cleaned"
	cleaned_comments_pickle = "input/processed_dataframes/all_comments_full_cleaned"

#Path to safe the cleaned kickstarter and comment csvs
if testing:
	#Small test files
	cleaned_comments_csv = "input/processed_dataframes/all_comments_test_cleaned.csv"
else:
	#Large full files
	cleaned_comments_csv = "input/processed_dataframes/all_comments_full_cleaned.csv"


#Minimum number of comments required for a kickstarter to be considered.
comment_cutoff = 50