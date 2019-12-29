'''
Deletes unnneeded information/bloat, renames columns to be more human-friendly,
and expands out comments to their own individual rows.
~Zac Bullard
'''

import params #Importing project-specific parameters
import pandas as pd #Data frames
import time #Recording execution time
import re #Regular expressions
import datetime #For converting dates
import numpy as np #Data manipulation
import os #For creating directories

def clean_kickstarters(ksdf):

    '''Removes superflous columns and convert promised time-til-delivery to days.

    Args:
        ksdf (pandas dataframe): Kickstarter dataframe, with project-level information.

    Raises:
        None

    Returns:
        Cleaned pandas dataframe.
    '''

    #Let's clean up the basic info, while the data frame is relatively small
    ksdf.drop(['slug','disable_communication','currency_trailing_code','currency_symbol','state_changed_at','profile','source_url','friends','created_at','is_starred','is_backing','permissions'],axis=1,inplace = True)

    ksdf['duration'] = (ksdf.deadline-ksdf.launched_at)/60.0/60/24 #Duration in days

    ksdf.category = ksdf.category.str.partition('"slug":"')[2].str.partition('/')[0]

    return ksdf

def clean_comments(cmdf):

    '''Deletes projects with reward dates beyond our cutoff, cleans xml tags from comments, deletes projects with less than a minimum number of comments, converts to Unix time, and expands comments.


    Args:
        cmdf (pandas dataframe): Comment dataframe, with comment-level information.

    Raises:
        None

    Returns:
        Cleaned pandas dataframe.
    '''

    #Rename columns to provide more information
    cmdf.rename(columns={'id':'project_id','comment_dates':'comment_date'}, inplace = True)

    #Remove projects whose reward dates are after our cutoff
    cmdf.drop(cmdf[cmdf.reward_date > params.end_date].index, inplace = True)

    #Clean our comments by removing xml tags, newlines, and stripping brackets
    carrot_match = re.compile('<[^>]*>')
    cmdf.comments = cmdf.comments.map(lambda x:[carrot_match.sub('',y.lstrip('[').rstrip(']').replace('\n', '')) for y in x])

    #Remove projects with an insufficient number of comments.
    cmdf['comment_count'] = cmdf.comments.map(lambda x: len(x))
    cmdf.drop(cmdf[cmdf.comment_count < params.comment_cutoff].index, inplace=True)

    #Converting the time format to Unix Time.
    cmdf['comment_date'] = [[time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()) for date in dates] for dates in cmdf.comment_date]

    #Expand out the individual comments, as they are initially scraped on a per-project basis.
    cmdf = pd.DataFrame({
      col:np.repeat(cmdf[col].values, cmdf['comments'].str.len())
      for col in cmdf.columns.drop('comments').drop('comment_date')}
    ).assign(comments=np.concatenate(cmdf['comments'].values)).assign(comment_date=np.concatenate(cmdf['comment_date'].values))

    #Rearrange the dataframe to put the comments (long data) at the end.
    cmdf = cmdf[['project_id','comment_count','reward_date','comment_date','comments']]

    return cmdf

def basic_stats(ksdf):
    '''Creates a dataframe with some basic summary information.

    Args:
        ksdf (pandas dataframe): Kickstarter dataframe, with project-level information.

    Raises:
        None

    Returns:
        Summary dataframe.
    '''

    return pd.DataFrame({'project_total':len(ksdf.index),
                         'funded_project_total':len(ksdf[ksdf.state == 'successful'].index),
                               'comment_total':ksdf.comment_count.sum(),
                               'comment_stats':ksdf.comment_count.describe().to_string(),
                               'successful_funding_ratio':len(ksdf[ksdf.state == 'successful'].index)/len(ksdf.index),
                               'funds_raised_total_millions':ksdf[ksdf.state == 'successful'].usd_pledged.sum()/1000000.0
                               }, index=[0])


if __name__ == '__main__':
    start_time = time.time()
    print("Starting program...")

    #Import dirty dataframes
    ksdf = pd.read_pickle(params.raw_kickstarter_pickle)
    cmdf = pd.read_pickle(params.raw_comments_pickle)

    #Squeaky clean
    ksdf = clean_kickstarters(ksdf)
    cmdf = clean_comments(cmdf)

    #Join some information from the comments back to the project dataframe.
    ksdf = ksdf.merge(cmdf.groupby("project_id", as_index = False).first()[["project_id","comment_count","reward_date"]],how='right',left_on='id',right_on='project_id').drop("id",axis=1)
    cmdf.drop(["comment_count"],axis=1,inplace=True)

    #Create basic summary stats, create output directory, and save.
    basic_stats_df = basic_stats(ksdf)
    if not os.path.exists(params.output_dir):
        os.makedirs(params.output_dir)
    basic_stats_df.to_csv(params.basic_stats_csv, index=False)

    #Only successfully funded projects can possibly deliver, so filter out the failures
    ksdf = ksdf[ksdf.state == 'successful']
    cmdf = cmdf.loc[cmdf['project_id'].isin(ksdf.project_id)]

    #Save cleaned data frames
    if not os.path.exists(params.processed_dir):
        os.makedirs(params.processed_dir)

    ksdf.to_pickle(params.cleaned_kickstarter_pickle)
    cmdf.to_pickle(params.cleaned_comments_pickle)

    print("Finished! In", (time.time()-start_time)/60," minutes")