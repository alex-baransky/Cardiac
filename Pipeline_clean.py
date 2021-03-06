%load_ext autoreload
%autoreload 2
import pandas as pd
import numpy as np
from data_merge import *
from Clean_Fun import *

# NOTE have to use remove_invalid_rows() inside ALex's function,
# before we remove patient name
# %% Load dataset

live_path='Data/Cardiac Program_M.xlsx'
archive_path='Data/Cardiac Program_Archive.xlsx'
live_sheet_pkl='pickle_jar/live_sheets.pkl'
archive_sheet_pkl='pickle_jar/archive_sheets.pkl'
datecol_pkl='pickle_jar/datecols.pkl'
df = sheet_merge(live_path, archive_path,
    live_sheet_pkl, archive_sheet_pkl, datecol_pkl)
# %% test patients, determing Response Value

# NOTE have to remove invalid rows
df['outcome']=df.apply(lambda row: determine_outcome(row['status'],row['discharge'],row['discharge_date']),axis=1)
train_df,test_df=train_test_split_sg(df)
df=train_df.copy() # for now
del test_df

# %% Clean effusion rate

df['ef']=df['ef'].apply(lambda x: clean_EF_rows(x))

# Clean Blood Pressure rows
df['diastolic']=df.apply(lambda row: clean_diastolic_columns(
    row['diastolic'],row['resting_bp'],col_type='di'),axis=1)
df['systolic']=df.apply(lambda row: clean_diastolic_columns(
    row['systolic'],row['resting_bp'],col_type='sys'),axis=1)

# Dummify the diagnoses
uniq_diag=find_unique_diag(df.diagnosis_1)
dummy_df_diag=dummify_diagnoses(df,uniq_diag,diagnosis_col='diagnosis_1')
df.drop('diagnosis_1',axis=1,inplace=True)
dummy_df_diag.columns=pd.Series(uniq_diag).apply(lambda x: remove_paren(x)).append(pd.Series('enrollId'))
df=df.merge(dummy_df_diag,on='enrollId',how="inner")

# clean HR
df['resting_hr']=df.resting_hr.apply(lambda x: hand_dates(x))

# Clean Meds and aicd
# acute or chronic
med_aicd_clean(df,'ace', 0)
med_aicd_clean(df,'bb', 0)
med_aicd_clean(df,'diuretics', 0)
med_aicd_clean(df,'anticoagulant', 0)
med_aicd_clean(df,'ionotropes', 0)
med_aicd_clean(df,'aicd', 0)

# weight_dur_age_clean(df,dur_na=9999,age_na=9999,weight_perc_cutoff=0.2)
df['duration']=df.apply(lambda row: find_duration(row['discharge'],
    row['enrollment_date'],row['discharge_date']),axis=1)
df['age'] = df['date_of_birth'].apply(find_age)
df['weight_change_since_admit'] = df.apply(lambda row: clean_weight_change(
    row['weight'],row['weight_change_since_admit']),axis=1)

remove_invalid_rows(df)

df.loc[df['duration']==9999, 'duration'] = None
df.loc[df['age']==9999, 'age'] = None

# %%
pd.set_option('display.max_columns', 60)
df.drop_duplicates(inplace=True)
df.reset_index(inplace=True, drop=True)
df.columns = [x.replace(" ", "_") for x in df.columns]
df = drop_date_cols(df)
df

df.to_csv('Data/clean_test.csv')
