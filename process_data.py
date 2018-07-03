import os
import glob

import numpy as np
import pandas as pd

def process_data(userpath,stationnumber,time_interval,folder=False):
    #function for database group to call
    if time_interval=='daily':
        merged = merge_hisrec_daily(userpath,stationnumber)
    elif time_interval=='hourly':
        merged = merge_hisrec_hourly(userpath,stationnumber,folder)

    if merged.empty:
        clean_data = merged
    else:
        clean_data = clean_merged(merged, time_interval)

    return clean_data

def merge_hisrec_daily(userpath,stationnumber):
    histpath = os.path.join(userpath, 'pub','CDC','observations_germany',
                            'climate','daily','kl','historical')
    recpath  = os.path.join(userpath, 'pub','CDC','observations_germany',
                            'climate','daily','kl','recent')

    #list of filenames
    histfile_tmp = os.path.join(histpath, "produkt_klima_tag_*")
    histfile_tmp += str(stationnumber).zfill(5)+'.txt'
    histlist = glob.glob(histfile_tmp)
    if histlist:
        histfile = glob.glob(histfile_tmp)[0]
        histdata = pd.read_table(histfile, sep=";", low_memory=False)
    else:
        histdata = pd.DataFrame()

    recfile_tmp = os.path.join(recpath, "produkt_klima_tag_*")
    recfile_tmp += str(stationnumber).zfill(5)+'.txt'
    reclist = glob.glob(recfile_tmp)
    if reclist:
        recfile = glob.glob(recfile_tmp)[0]
        recentdata = pd.read_table(recfile, sep=";", low_memory=False)
    else:
        recentdata = pd.DataFrame()

    merged=pd.concat([histdata,recentdata])

    return merged

def merge_hisrec_hourly(userpath,stationnumber,folder):
    hour_folders = ["air_temperature", "cloud_type", "precipitation",
                    "pressure", "soil_temperature", "sun", "visibility", "wind", "solar"]

    if folder not in hour_folders:
        print('wrong folder')
    elseif folder=="solar":
        print(folder)
        solarpath = os.path.join(userpath, 'pub','CDC','observations_germany',
                                'climate','hourly', folder)
        solarfile_tmp = os.path.join(solarpath, "produkt*")
        solarfile_tmp += str(stationnumber).zfill(5)+'.txt'
        solarlist = glob.glob(solarfile_tmp)
        if solarlist:
            print('solar exists')
            solarfile = glob.glob(solarfile_tmp)[0]
            merged_all = pd.read_table(solarfile, sep=";", low_memory=False)
            merged_all = merged_all.drop(['eor'],axis=1)
        else:
            print('no solar')
            merged_all = pd.DataFrame()
    else:
        print(folder)
        histpath = os.path.join(userpath, 'pub','CDC','observations_germany',
                                'climate','hourly', folder, 'historical')
        recpath  = os.path.join(userpath, 'pub','CDC','observations_germany',
                                'climate','hourly', folder, 'recent')

        histfile_tmp = os.path.join(histpath, "produkt*")
        histfile_tmp += str(stationnumber).zfill(5)+'.txt'
        histlist = glob.glob(histfile_tmp)
        if histlist:
            print('hist exists')
            histfile = glob.glob(histfile_tmp)[0]
            histdata = pd.read_table(histfile, sep=";", low_memory=False)
            histdata = histdata.drop(['eor'],axis=1)
        else:
            print('no hist')
            histdata = pd.DataFrame()

        recfile_tmp = os.path.join(recpath, "produkt*")
        recfile_tmp += str(stationnumber).zfill(5)+'.txt'
        reclist = glob.glob(recfile_tmp)
        if reclist:
            print('rec exists')
            recfile = glob.glob(recfile_tmp)[0]
            recentdata = pd.read_table(recfile, sep=";", low_memory=False)
            recentdata = recentdata.drop(['eor'],axis=1)
        else:
            print('no rec')
            recentdata = pd.DataFrame()

        merged_all=pd.concat([histdata,recentdata])

    return merged_all

def clean_merged(merged, time_interval):
    merged_clean = merged.replace('-999', np.nan, regex=True)
    merged_clean.columns = [c.strip().lower() for c in merged_clean.columns]
    merged_clean = merged_clean.drop_duplicates(subset = ['stations_id',
                                                          'mess_datum'],
                                                keep='first')

    if time_interval=='hourly':
        merged_clean['mess_datum'] =\
                           pd.to_datetime(merged_clean['mess_datum'].apply(str), format='%Y%m%d%H')

    if time_interval=='daily':
        merged_clean = merged_clean.drop(['eor'],axis=1)
        merged_clean['mess_datum'] =\
                           pd.to_datetime(merged_clean['mess_datum'].apply(str))
        merged_clean['mess_datum'] =\
                            merged_clean['mess_datum'].apply(lambda x: x.date())

    return merged_clean
