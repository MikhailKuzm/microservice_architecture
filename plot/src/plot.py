import pandas as pd 


def plot_df(series):
    ax = series.hist()   
    fig = ax.get_figure()
    fig.savefig('.\logs\error_distribution.png')

while True:
    plot_df(pd.read_csv('.\logs\metric_log.csv')['absolute_error'])