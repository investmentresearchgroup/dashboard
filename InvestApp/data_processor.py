# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 16:11:31 2020

@author: dswir
"""

import pandas as pd
import numpy as np
import sys

def process_data(data):
    df = data.drop_duplicates(
        subset=['name','Date']).set_index('Date').sort_index()
    max_dt = df.index.max()
    min_dt = df.index.min()
    new_dates = pd.date_range(min_dt,max_dt,freq='D')
    df_processed = df.groupby('name').apply(
        lambda x: reindexframe(x,new_dates))\
        .rename_axis(
        ('name','Date')).drop('name',1).reset_index().set_index('Date')
    return df_processed



def reindexframe(data,date_range):
    df = data.reindex(date_range)
    for col in ['price','change','volume',
                'industry','fullname','sector']:
        df.loc[:,col] = df[col].fillna(method='ffill').fillna(
        method='bfill')
    return df

def get_inception_date(df):
    df.loc[:,'inception_date'] = df.Date == df.Date.min()
    df.loc[:,'inception_date'] = df['inception_date'].replace(False,np.nan)
    return df

def process_inception(df):
    df_processed = df.groupby('name').apply(
        get_inception_date)
    return df_processed
    

if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1],
                     parse_dates=['Date'])
    df_inception = process_inception(df)
    df_clean = process_data(df_inception)
    
    
    
    
    
    