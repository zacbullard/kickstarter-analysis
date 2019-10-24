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

    cmdf['delivered_regex'] = cmdf.comments.map(lambda x: len(delivered_regex.findall(x))>0)
    
        #Rearrange the dataframe to put the comments (long data) at the end.
    cmdf = cmdf[['project_id','project_comment_count','reward_date','comment_date','delivered_regex','comments']]
    
 
if __name__ == '__main__':
    start_time = time.time()    
    print("Starting program...")
    
    cmdf = pd.read_pickle(params.cleaned_comments_pickle)    
    
    mark_delivered_regex(cmdf)
    
    cmdf.to_pickle(params.cleaned_comments_pickle)
    
    print("Finished! In", (time.time()-start_time)/60," minutes")