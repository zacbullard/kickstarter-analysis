import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn' #Supresses warning
import glob as glob
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np
import re
from bs4 import BeautifulSoup
import requests 
import time
import datetime
import plotly.plotly as py
from plotly.graph_objs import *
import plotly.graph_objs as go
import plotly.tools as tls
import cufflinks as cf
from operator import itemgetter

end_2013 = 1388534400
end_2014 = 1420070400
end_2015 = 1451606400
end_2016 = 1483228800

#Thanks for the download link
#work fine
#I actually got shipped
# I've had mine since I can't even remember when

if __name__ == '__main__':
    
    do_plotting = False
    #Preliminary clean-up of projects without a significant number of comments.
    delivered_comment_cutoff = 50

    print("Starting program...")

    #Import dirty dataframes    
    ksdf = pd.read_pickle("processed_dataframes/all_kickstarters_test")
    cmdf = pd.read_pickle("processed_dataframes/all_comments_test")

    #Let's clean up the basic info, while the data frame is relatively small
    ksdf = ksdf.drop(['slug','disable_communication','currency_trailing_code','currency_symbol','state_changed_at','profile','source_url','friends','created_at','is_starred','is_backing','permissions'],axis=1)
    ksdf['duration'] = (ksdf.deadline-ksdf.launched_at)/60.0/60/24 #Duration in days
    ksdf.category = ksdf.category.str.partition('"slug":"')[2].str.partition('/')[0]

    #Remove projects whose reward dates are after our cutoff
    cmdf = cmdf[cmdf.reward_date <= end_2015]

    #Clean our comments by removing xml tags, newlines, and stripping brackets
    carrot_match = re.compile('<[^>]*>')    
    cmdf.comments = cmdf.comments.map(lambda x:[carrot_match.sub('',y.lstrip('[').rstrip(']').replace('\n', '')) for y in x])

    #Remove projects with an insufficient number of comments. 
    cmdf['comment_count'] = cmdf.comments.map(lambda x: len(x))
    #cmdf = cmdf[cmdf.comment_count >= comment_cutoff] 
    
    #Converting the time format to Unix Time.
    cmdf['comment_dates'] = [[time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()) for date in dates] for dates in cmdf.comment_dates]

    mdf = pd.merge(cmdf,ksdf, on='id',how = 'right' )
    
    print_basic_stats(mdf)
    
    mdf = find_delivered(mdf)

    #Our merged df is going to be pared down in the operation to find the delayed deliveries, so make a copy now with the delived comment count.
    ddf = mdf.copy()

    mdf = find_delays(mdf)
    
    if do_plotting:
        plotly_funding_boxes(mdf[mdf.state == 'successful'])
        plotly_delay_boxes(mdf)
        plot_date_distribution(df.delivered_dates.iloc[0])


def print_basic_stats(df):
    print('TOTAL # OF PROJECTS',len(df.index))
    print('COMMENTS STATS:\nSUM:',df.comment_count.sum(),'\n',df.comment_count.describe())
    print('SUCCESSFUL FUNDING RATIO',len(df[df.state == 'successful'].index)/len(df.index))
    print('TOTAL FUNDS RAISED, MILLIONS', df[df.state == 'successful'].usd_pledged.sum()/1000000.0)
    

def find_delivered(df):
    delivered_regex = re.compile("(?<!not\s)(?<!hasen't\s)(?<!hasn't\s)(?<!haven't\sI\s)(?<!haven't\s)(?<!ever\s)(?<!never\s)(?<!yet\s)(recieved|received|arrived)", re.IGNORECASE)

    all_delivered_comments = []
    all_delivered_dates = []
    for i in range(len(df.comments)):
        delivered_comments = []
        delivered_dates = []
        for j in range(len(df.comments.iloc[i])):
            if delivered_regex.findall(df.comments.iloc[i][j]):
                delivered_comments.append(df.comments.iloc[i][j]) #A more efficient way to do this would be instead of making a copy of the comments with delivery, to record the index in the corrosponding comment list instead.
                delivered_dates.append(df.comment_dates.iloc[i][j])
                #print(df.comments.iloc[i][j],df.comment_dates.iloc[i][j])
                #time.sleep(500.5) 
        all_delivered_comments.append(delivered_comments)
        all_delivered_dates.append(delivered_dates)
    df['delivered_comments'] = all_delivered_comments
    df['delivered_comment_count'] = df.delivered_comments.apply(lambda x: len(x))
    df['delivered_dates'] = all_delivered_dates

def find_delays(df): 
    
    #Only successfully funded projects can possibly deliver
    df = df[df.state == 'successful']

    #Only sampling kickstarters with at least a given number of samples to test if the distribution is Gaussian or not. 
    #Scipy requires at least 20, but 50 is generally the minimum for normal_test.
    df = df[df.delivered_comment_count >= delivered_comment_cutoff]

    #From scipy: This function tests the null hypothesis that a sample comes from a normal distribution. It is based on D’Agostino and Pearson’s [R292], [R293] test that combines skew and kurtosis to produce an omnibus test of normality. 
    df['norm_test_pvalue'] = df.delivered_dates.apply(lambda x:stats.normaltest(x)[1])
    #If p > 0.05, not enough of a normal distribution for us.
    df = df[df.norm_test_pvalue <= 0.05]
 
    reward_delays = []
    for index, row in df.iterrows():
        dates_se = pd.to_datetime(pd.Series(row['delivered_dates']),unit='s')
        
        #Delay is measured from the per-month mode of delivery confirmed comments
        mode_month = dates_se.groupby([dates_se.dt.year,dates_se.dt.month]).count().argmax()
        mode_month_string = str(mode_month[0])  + '-' + str(mode_month[1]) + '-15' #Assume the exact date is in the middle of the month
        mode_month_unix = time.mktime(datetime.datetime.strptime(mode_month_string, "%Y-%m-%d").timetuple())
        delivery_gap = (mode_month_unix - row['reward_date'])/60/60/24/30.44 #convert to months
    
        reward_delays.append(delivery_gap)
    
    df['reward_delay'] = reward_delays
    df['confirmed_delivery'] = True

 
    print('STATS ON CONFIRMED DELIVERY DELAYS (MONTHS)',df.reward_delay.describe())

    #df[['id','delivered_comments','comments']].to_pickle('processed_dataframes/confirmed_deliveries_comments')
#    df.drop(['delivered_comments','comments'], axis=1,inplace=True)
    #df.to_pickle('processed_dataframes/confirmed_deliveries_df')
    
    return df

#Input is a list of linux dates
def plot_date_distribution(dates_se):
    
    dates_se = pd.to_datetime(pd.Series(dates_se),unit='s')
    
    hp = dates_se.groupby([dates_se.dt.year,dates_se.dt.month]).count().plot(fontsize=7,kind="bar", rot=80).get_figure()
   
    #plt.figure( dpi = 120)
    #plt.axvline(x = 11,linewidth=2, color = 'r')
    plt.title('Delivery Confirmations')
    plt.suptitle('')
    plt.ylabel('Number of Delivery Comments')
    #plt.xlabel('Date')
    #hp.savefig('comment_date.eps', figsize=(6,6),format='eps', dpi=1000)
    #plt.cla()
 
#plots funding level box plots on a per-category basis
def plotly_funding_boxes(df):
    
    dfsc = pd.concat([df.category,df.usd_pledged],axis = 1)
    dfsc.rename(columns={2:'category'},inplace=True)
    df_list = []
    for category, group in dfsc.groupby('category'):      
        df_list.append((group.usd_pledged.mean(),group.usd_pledged.rename(category)))
    df_list.sort(key=lambda x: x[0],reverse = True)
               
    # generate an array of rainbow colors by fixing the saturation and lightness of the HSL representation of colour and marching around the hue. 
    # Plotly accepts any CSS color format, see e.g. http://www.w3schools.com/cssref/css_colors_legal.asp.
    c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(df_list))]
    
    data = [{
        'y':df_list[i][1],
        'name':df_list[i][1].name ,
        'type':'box',
        'marker':{'color': c[i]}
        } for i in range(len(df_list))]
    
    layout = go.Layout(
        title='Successful Funds Raised Per Kickstarter Category',
        xaxis=dict(
            tickangle=60,
            autorange=True
        ),
        yaxis=dict(
            type='log',
            title='USD Raised (log scale)',
            autorange=True
        ))
    
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig,filename='funding_boxcharts')  
    
#plots single backer delay box plot
def plotly_delay_boxes(df):
 
    dfsc = pd.concat([df.category,df.reward_delay],axis = 1)
    dfsc.rename(columns={2:'category'},inplace=True)
    df_list = []
    for category, group in dfsc.groupby('category'):      
        df_list.append((group.reward_delay.mean(),group.reward_delay.rename(category)))
    df_list.sort(key=lambda x: x[0],reverse = True)
               
    # generate an array of rainbow colors by fixing the saturation and lightness of the HSL representation of colour and marching around the hue. 
    # Plotly accepts any CSS color format, see e.g. http://www.w3schools.com/cssref/css_colors_legal.asp.
    c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(df_list))]
    
    data = [{
        'y':df_list[i][1],
        'name':df_list[i][1].name ,
        'type':'box',
        'marker':{'color': c[i]}
        } for i in range(len(df_list))]
    
    layout = go.Layout(
        title='Delay (Months) Per Kickstarter Category',
        xaxis=dict(
            tickangle=60,
            autorange=True
        ),
        yaxis=dict(
            #type='log',
            title='Delivery Delay (Months)',
            autorange=True
        ))
    
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig,filename='delay_boxchart') 
    
    

