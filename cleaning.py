import params #Importing project-specific parameters
import pandas as pd #Data frames
import time #Recording execution time
import re #Regular expressions
import datetime #For converting dates
import numpy as np #Data manipulation


def clean_kickstarters(ksdf):

    '''Removes superflous columns and convert promised time-til-delivery to days.
    
    Args:
        ksdf (pandas dataframe): Kickstarter dataframe, with project-level information.

    Raises:
        None

    Returns:
        None
    '''
    
    #Let's clean up the basic info, while the data frame is relatively small
    ksdf.drop(['slug','disable_communication','currency_trailing_code','currency_symbol','state_changed_at','profile','source_url','friends','created_at','is_starred','is_backing','permissions'],axis=1,inplace = True)
    
    ksdf['duration'] = (ksdf.deadline-ksdf.launched_at)/60.0/60/24 #Duration in days
    
    ksdf.category = ksdf.category.str.partition('"slug":"')[2].str.partition('/')[0]

def clean_comments(cmdf):

    '''Deletes projects with reward dates beyond our cutoff, cleans xml tags from comments, deletes projects with less than a minimum number of comments, and converts to Unix time.
    
    
    Args:
        cmdf (pandas dataframe): Comment dataframe, with comment-level information.

    Raises:
        None

    Returns:
        None
    '''

    #Rename columns to provide more information 
    cmdf.rename(columns={'id':'project_id','comment_dates':'comment_date'}, inplace = True)

    #Remove projects whose reward dates are after our cutoff
    cmdf.drop(cmdf[cmdf.reward_date > params.end_date].index, inplace = True)

    #Clean our comments by removing xml tags, newlines, and stripping brackets
    carrot_match = re.compile('<[^>]*>')    
    cmdf.comments = cmdf.comments.map(lambda x:[carrot_match.sub('',y.lstrip('[').rstrip(']').replace('\n', '')) for y in x])

    #Remove projects with an insufficient number of comments. 
    cmdf['project_comment_count'] = cmdf.comments.map(lambda x: len(x))
    cmdf.drop(cmdf[cmdf.project_comment_count < params.comment_cutoff].index, inplace=True) 
    
    #Converting the time format to Unix Time.
    cmdf['comment_date'] = [[time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()) for date in dates] for dates in cmdf.comment_date]
     
if __name__ == '__main__':
    start_time = time.time()    
    print("Starting program...")

    #Import dirty dataframes    
    ksdf = pd.read_pickle(params.raw_kickstarter_pickle)
    cmdf = pd.read_pickle(params.raw_comments_pickle)      

    #Squeaky clean
    clean_kickstarters(ksdf)
    clean_comments(cmdf)
    
    #Expand out the individual comments, as they are initially scraped on a per-project basis.
    cmdf = pd.DataFrame({
      col:np.repeat(cmdf[col].values, cmdf['comments'].str.len())
      for col in cmdf.columns.drop('comments').drop('comment_date')}
    ).assign(comments=np.concatenate(cmdf['comments'].values)).assign(comment_date=np.concatenate(cmdf['comment_date'].values))
    
    #Rearrange the dataframe to put the comments (long data) at the end.
    cmdf = cmdf[['project_id','project_comment_count','reward_date','comment_date','comments']]
    
    #mdf = pd.merge(cmdf,ksdf, on='id',how = 'inner' )
    
    #Save cleaned data frames
    ksdf.to_pickle(params.cleaned_kickstarter_pickle)
    cmdf.to_pickle(params.cleaned_comments_pickle)
    
    print("Finished! In", (time.time()-start_time)/60," minutes")