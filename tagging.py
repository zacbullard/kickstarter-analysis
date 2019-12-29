'''
Tags individual comments as either confirming a delivery or not,
either using regular expressions or Amazon's Mechanical Turk.
Can additionally perform sampling, i.e. for unbalanced classes, as delivery confirmations are relatively rare.
~Zac Bullard
'''

import params #Importing project-specific parameters
import pandas as pd #Data frames
import time #Recording execution time
import re #Regular expressions
import boto3 #For Mechanical Turk
import xmltodict #For reading Mechanical Turk results
import os #For creating directories

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
    delivered_regex = re.compile("(?<!not\s)(?<!not\salready\s)(?<!ain't\s)(?<!aint\s)(?<!hasen't\s)(?<!hasent\s)(?<!hasn't\s)(?<!hasnt\s)(?<!haven't\sI\s)(?<!havent\s)(?<!ever\s)(?<!never\s)(?<!yet\s)(recieved|received|arrived)(?!\snothing)(?!\sanything\?)", re.IGNORECASE)

    cmdf['delivered_regex'] = cmdf.comments.map(lambda x: len(delivered_regex.findall(x))>0)

def mark_delivered_mturk_example(cmdf):
    '''UNDER CONSTRUCTION. Uses the Mechanical Turk to label data.

    Args:
        cmdf (pandas dataframe): comment dataframe, with comment-level information.

    Raises:
        None

    Returns:
        None
    '''

    #Read in mturk credentials
    mturk_creds = pd.read_csv(params.mturk_cred_csv)

    #Sandbox url
    MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

    #Create mturk connection
    mturk = boto3.client('mturk',
        aws_access_key_id = mturk_creds['Access key ID'][0],
        aws_secret_access_key = mturk_creds['Secret access key'][0],
        region_name='us-east-1',
        endpoint_url = MTURK_SANDBOX
    )

    #Load questions
    question = open(file=auxiliary_dir+'/questions.xml',mode='r').read()

    #Create HIT
    new_hit = mturk.create_hit(
        Title = 'Is this Tweet happy, angry, excited, scared, annoyed or upset?',
        Description = 'Read this tweet and type out one word to describe the emotion of the person posting it: happy, angry, scared, annoyed or upset',
        Keywords = 'text, quick, labeling',
        Reward = '0.01',
        MaxAssignments = 2, #Max number of workers on this task
        LifetimeInSeconds = 172800, #Duration of the assignment on the marketplace
        AssignmentDurationInSeconds = 600, #How long they have to complete the assignment
        AutoApprovalDelayInSeconds = 14400, #2 days before auto-approve kicks in
        Question = question,
    )

    hit_id = new_hit["HIT"]["HITId"]

    #Retrieve HIT Results
    worker_results = mturk.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])

    if worker_results['NumResults'] > 0:
       for assignment in worker_results['Assignments']:
          xml_doc = xmltodict.parse(assignment['Answer'])

          print("Worker's answer was:")
          if type(xml_doc['QuestionFormAnswers']['Answer']) is list:
             # Multiple fields in HIT layout
             for answer_field in xml_doc['QuestionFormAnswers']['Answer']:
                print("For input field: " + answer_field['QuestionIdentifier'])
                print("Submitted answer: " + answer_field['FreeText'])
          else:
             # One field found in HIT layout
             print("For input field: " + xml_doc['QuestionFormAnswers']['Answer']['QuestionIdentifier'])
             print("Submitted answer: " + xml_doc['QuestionFormAnswers']['Answer']['FreeText'])
    else:
       print("No results ready yet")

    #Extracting hits under construction
    cmdf['delivered_mturk'] = None

def sample(cmdf, sampling_method, outcome_var):
    '''Samples logistic data.

    Args:
        cmdf (pandas dataframe): comment dataframe, with comment-level information.
        sampling_method: either "none" or "equal" for undersampling the more prevalent class.
        outcome_var: boolean column with the values we are trying to predict.

    Raises:
        ValueError: sampling_method must be one of the methods present.

    Returns:
        None
    '''

    sampling_methods = ["none","equal"]

    if not sampling_method in sampling_methods:
        raise ValueError("Unrecognized sampling_method given is \"" + sampling_method + "\", it needs to be in " + ", ".join(sampling_methods))

    if sampling_method == "equal":

        true_count = cmdf[outcome_var].sum()
        false_count = (~cmdf[outcome_var]).sum()

        if(false_count > true_count):
            undersample_class = False
            undersample_amount = false_count - true_count
        else:
            undersample_class = True
            undersample_amount = true_count - false_count

        #Drop the excess class to match the lesser class in number
        cmdf.drop(cmdf[cmdf[outcome_var]==undersample_class].sample(undersample_amount).index, inplace = True)

if __name__ == '__main__':
    start_time = time.time()
    print("Starting program...")

    cmdf = pd.read_pickle(params.cleaned_comments_pickle)

    if params.mark_regex:
        mark_delivered_regex(cmdf)

    if params.mark_mturk:
        mark_delivered_mturk_example(cmdf)

    cmdf.to_pickle(params.tagged_comments_pickle)
    cmdf.to_csv(params.tagged_comments_csv, index=False)

    if params.sampling_method != "none":
        sampling_method = params.sampling_method
        sample(cmdf, params.sampling_method, params.outcome_var)
        cmdf.to_pickle(params.tagged_comments_pickle_sampled)
        cmdf.to_csv(params.tagged_comments_csv_sampled, index=False)

    print("Finished! In", (time.time()-start_time)/60," minutes")