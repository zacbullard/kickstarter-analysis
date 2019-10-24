import pandas as pd #Data processing
pd.options.mode.chained_assignment = None  # default='warn' #Supresses warning
import glob as glob
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np
import re
from bs4 import BeautifulSoup #HTML parsing
import requests #Accessing websites
import time #Recording execution time
import datetime #Manipulating dates
import plotly.plotly as py
from plotly.graph_objs import *
import plotly.graph_objs as go
import plotly.tools as tls
import cufflinks as cf
from operator import itemgetter

#end-of-year dates in Unix time.
end_2013 = 1388534400
end_2014 = 1420070400
end_2015 = 1451606400
end_2016 = 1483228800



if __name__ == '__main__':
    start_time = time.time()    
    print("Starting program...")

    #Import dirty dataframes    

    ksdf = pd.read_pickle(kickstarter_pickle)
    cmdf = pd.read_pickle(comments_pickle)      

    #cddf = pd.read_pickle("processed_dataframes/confirmed_deliveries_df")
    #fpdf = pd.read_pickle("processed_dataframes/50_plus_df")
    #cddf['confirm_ratio'] = cddf.delivered_comment_count/cddf.comment_count
    #print(cddf.confirm_ratio.describe())
    #print(cddf[cddf.delivered_comment_count == 50].comment_count.describe())
    print(list(ksdf))
    print(list(cmdf))
    #print(ksdf[ksdf.comment_count >= 250].describe())
    
    print("Finished! In" + (time.time()-start_time/60 + " minutes"))