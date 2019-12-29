'''
For generating summary statistics and analysis not directly related to machine learning.
~Zac Bullard
'''

import params #Importing project-specific parameters
import os #directory managment
import pandas as pd #Dataframes
import scipy.stats as stats #For normal test
import matplotlib.pyplot as plt
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn', for disabling "A value is trying to be set on a copy of a slice from a DataFrame."


#import plotly.plotly as py
#from plotly.graph_objs import *
#import plotly.graph_objs as go
#import plotly.tools as tls
#import cufflinks as cf
#from operator import itemgetter

def find_delays(cmdf,outcome_var):

    #Only sampling kickstarters with at least a given number of samples to test if the distribution is Gaussian or not.
    #Scipy requires at least 20, but 50 is generally the minimum for normal_test.
    delivered_ksdf = cmdf[["project_id","comment_date","reward_date"]][cmdf[params.outcome_var]==True].groupby(["project_id","reward_date"],as_index=False).count().rename(columns={"comment_date": "delivered_count"})
    delivered_ksdf = delivered_ksdf[delivered_ksdf.delivered_count >= params.delivery_comment_cutoff]

    #Quick filter for confirmed delivery comments of projects that have at least the minimum number of delivery comments
    delivered_cmdf = cmdf[cmdf.project_id.isin(delivered_ksdf.project_id) & cmdf[params.outcome_var]==True]

    #Normal distribution test
    #From scipy: This function tests the null hypothesis that a sample comes from a normal distribution. It is based on D’Agostino and Pearson’s test that combines skew and kurtosis to produce an omnibus test of normality.
    delivered_ksdf = delivered_ksdf.join(pd.DataFrame(data=delivered_cmdf.groupby("project_id").apply(lambda x:stats.normaltest(x.comment_date)[1]).reset_index(name="norm_p_value").set_index("project_id")),on = "project_id")
    #If p > 0.05, not enough of a normal distribution.
    delivered_ksdf = delivered_ksdf[delivered_ksdf.norm_p_value <= 0.05]

    #Quick filter for comments of projects that have passed our normal test
    delivered_cmdf = cmdf[cmdf.project_id.isin(delivered_ksdf.project_id)]

    delivered_cmdf["comment_datetime"] = pd.to_datetime(pd.Series(delivered_cmdf['comment_date']),unit='s')
    delivered_cmdf["comment_yrmon"] = delivered_cmdf.apply(lambda x: str(x.comment_datetime.year)+"-"+'{:02d}'.format(x.comment_datetime.month)+"-15", axis = 1) #Assume the exact date is in the middle of the month
    delivered_cmdf["comment_unix"] = delivered_cmdf.apply(lambda x: time.mktime(datetime.datetime.strptime(x.comment_yrmon, "%Y-%m-%d").timetuple()), axis = 1)

    #Find delivered comment count per yrmon
    delivered_count_cmdf = delivered_cmdf[["project_id","comment_yrmon","comment_unix","comment_date"]].groupby(["project_id","comment_yrmon","comment_unix"],as_index=False).count().rename(columns={"comment_date":"comment_count"})

    #Return the yrmon of greatest count per project.
    delivered_count_cmdf = delivered_count_cmdf.iloc[delivered_count_cmdf.groupby(["project_id"]).idxmax("comment_count").rename(columns={"comment_date":"comment_count"}).comment_count].rename(columns={"comment_yrmon":"delivery_yrmon","comment_unix":"delivery_unix"})
    delivered_ksdf = delivered_ksdf.join(delivered_count_cmdf[["project_id","delivery_yrmon","delivery_unix"]].set_index("project_id"),on="project_id")

    #Delay is measured from the per-month mode of delivery confirmed comments
    delivered_ksdf["reward_delay_months"] =  (delivered_ksdf.delivery_unix - delivered_ksdf.reward_date)/60/60/24/30.44 #convert to months

    return delivered_ksdf

'''
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
'''

if __name__ == "__main__":

    #Import tagged dataframes
    #ksdf = pd.read_pickle(params.cleaned_kickstarter_pickle)
    if params.sampling_method == "none":
        cmdf = pd.read_pickle(params.tagged_comments_pickle)
    else:
        cmdf = pd.read_pickle(params.tagged_comments_pickle_sampled)

    #Find projects that deliver, and associated delays
    delivered_ksdf = find_delays(cmdf,params.outcome_var)

    #Create output directory and save
    if not os.path.exists(params.output_dir):
        os.makedirs(params.output_dir)
    delivered_ksdf.to_csv(params.delivered_ksdf_csv, index=False)

    f = open(params.delivered_stats_text,"w")
    print('STATS ON CONFIRMED DELIVERY DELAYS (MONTHS)\n',delivered_ksdf["reward_delay_months"].describe(),file=f)
    f.close()


