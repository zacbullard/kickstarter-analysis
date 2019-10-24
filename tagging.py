import params #Importing project-specific 
import pandas as pd #Data frames
import time #Recording execution time
import re #Regular expressions

def mark_delivered_regex(cmdf):
    '''Uses regular expressions as a first pass to identify comments confirming delivery.
    Adds a boolean "delivered_regex" column
    
    Args:
        cmdf (pandas dataframe): comment datafram, with comment-level information.

    Raises:
        None

    Returns:
        None
    '''
    
    #This regex expression essentially looks for words that confirm delivery, without being preceeded by a negative.
    delivered_regex = re.compile("(?<!not\s)(?<!hasen't\s)(?<!hasn't\s)(?<!haven't\sI\s)(?<!haven't\s)(?<!ever\s)(?<!never\s)(?<!yet\s)(recieved|received|arrived)", re.IGNORECASE)

    all_delivered_comments = []
    all_delivered_dates = []
    for i in range(len(cmdf.comments)):
        delivered_comments = []
        delivered_dates = []
        if delivered_regex.findall(cmdf.comments.iloc[i]):

    cmdf['delivered_comments'] = all_delivered_comments
    cmdf['delivered_comment_count'] = cmdf.delivered_comments.apply(lambda x: len(x))
    cmdf['delivered_dates'] = all_delivered_dates
    

    
if __name__ = '__main__':
    start_time = time.time()    
    print("Starting program...")
    
    ksdf = pd.read_pickle(params.cleaned_kickstarter_pickle)
    cmdf = pd.read_pickle(params.cleaned_comments_pickle)    
    
    
    print("Finished! In", (time.time()-start_time)/60," minutes")