'''
This file contains all the parameters required for the Kickstarter delivery analysis.
An end user should only manipulate this file.
~Zac Bullard
'''

import os #for directory management

'''
CONSTANTS
'''

#end-of-year dates in Unix time.
end_2013 = 1388534400
end_2014 = 1420070400
end_2015 = 1451606400
end_2016 = 1483228800

'''
CONTROL VARIABLES
'''

#The following switch determines whether the analysis should run on the full dataset, or a smaller test dataset.
testing = True

#If true, will take in a processed dataframe, and mark delivery confirmations determined via regular expression
mark_regex = True

#If true, will take in a processed dataframe, and mark delivery confirmations determined via Mechanical Turk
mark_mturk = False

#We will not consider projects with rewards promised beyond this date.
end_date = end_2015

#Minimum number of comments required for a kickstarter to be considered.
comment_cutoff = 50

#Minimum number of comments to test if the distribution is Gaussian or not.
#Scipy requires at least 20, but 50 is generally the minimum for normal_test.
delivery_comment_cutoff = 20

#Logistic sampling methodology. Options are:
#"none" for no sampling.  
#"equal" for undersampling the more prevalent class.
sampling_method = "equal"

'''
CONTROL VARIABLE COROLLARIES
'''

version = "full"
if testing:
	version = "test"

#Note that the following outcome_variables are hardcoded in tagging.py. 
#The latter outcome variables take over presidence from the previous ones, in case we use multiple methods.
outcome_var = "undefined"
if mark_regex:
	outcome_var = "delivered_regex"
if mark_mturk:
	outcome_var = "delivered_mturk"
'''
DIRECTORY SETUP
'''

execution_dir = os.getcwd()
input_dir = execution_dir + "/input"
processed_dir = execution_dir + "/processed_dataframes"
output_dir = execution_dir + "/output"
raw_dir = input_dir + "/raw_data"
auxiliary_dir = execution_dir + "/auxiliary"

mturk_cred_csv = auxiliary_dir + "/credentials.csv"

#Paths to the scraped kickstarter and comment pickles
raw_kickstarter_pickle = raw_dir+"/all_kickstarters_"+version
raw_comments_pickle = raw_dir+"/all_comments_"+version

#Paths to save the cleaned kickstarter and comment files
cleaned_kickstarter_pickle = processed_dir+"/kickstarters_"+version+"_cleaned"
cleaned_comments_pickle = processed_dir+"/comments_"+version+"_cleaned"
cleaned_comments_csv = processed_dir+"/comments_"+version+"_cleaned.csv"

regex_tagged_comments_pickle = processed_dir+"/comments_"+version+"_regex_tagged"
regex_tagged_comments_csv = processed_dir+"/comments_"+version+"_regex_tagged.csv"
regex_tagged_comments_pickle_sampled = processed_dir+"/comments_"+version+"_regex_tagged_sampled"
regex_tagged_comments_csv_sampled = processed_dir+"/comments_"+version+"_regex_tagged_sampled.csv"

mturk_tagged_comments_pickle = processed_dir+"/comments_"+version+"_mturk_tagged"
mturk_tagged_comments_csv = processed_dir+"/comments_"+version+"_mturk_tagged.csv"
mturk_tagged_comments_pickle_sampled = processed_dir+"/comments_"+version+"_mturk_tagged_sampled"
mturk_tagged_comments_csv_sampled = processed_dir+"/comments_"+version+"_mturk_tagged_sampled.csv"

if mark_regex:
    tagged_comments_pickle = regex_tagged_comments_pickle
    tagged_comments_pickle_sampled = regex_tagged_comments_pickle_sampled
    tagged_comments_csv = regex_tagged_comments_csv
    tagged_comments_csv_sampled = regex_tagged_comments_csv_sampled
elif mark_mturk:
    tagged_comments_pickle = mturk_tagged_comments_pickle
    tagged_comments_pickle_sampled = mturk_tagged_comments_pickle_sampled
    tagged_comments_csv = mturk_tagged_comments_csv
    tagged_comments_csv_sampled = mturk_tagged_comments_csv_sampled

#Paths to the summary analysis 
basic_stats_csv = output_dir + "/basic_stats.csv"
delivered_ksdf_csv = output_dir + "/delivered_ksdf.csv"
delivered_stats_text = output_dir + "/delivered_stats.txt"