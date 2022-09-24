import requests
import pandas as pd
import os
from datetime import datetime, timedelta

df1 = pd.read_csv('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

confirmed = df1.drop(['Lat','Long'],axis=1).groupby('Country/Region').sum()

confirmed.columns = pd.to_datetime(confirmed.columns,format='%m/%d/%y')

df2 = pd.read_csv('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

deaths = df2.drop(['Lat','Long'],axis=1).groupby('Country/Region').sum()

deaths.columns = pd.to_datetime(deaths.columns,format='%m/%d/%y')

countries = pd.read_csv('https://github.com/kazuhirokida/covid-19/raw/master/countries.csv')

confirmed.index = confirmed.index.map(countries.set_index('Country').Japanese.to_dict())

deaths.index = deaths.index.map(countries.set_index('Country').Japanese.to_dict())

confirmed.loc['世界'] = confirmed.sum()

new_confirmed = confirmed.diff(1,axis=1).dropna(axis=1)

deaths.loc['世界'] = deaths.sum()

new_deaths = deaths.diff(1,axis=1).dropna(axis=1)

table = pd.concat([confirmed[~confirmed.index.isna()].iloc[:,-1].sort_values(ascending=False).rename('感染者数'),
           new_confirmed[~new_confirmed.index.isna()].iloc[:,-1].sort_values(ascending=False).rename('前日比'),
           deaths[~deaths.index.isna()].iloc[:,-1].sort_values(ascending=False).rename('死者数'),
           new_deaths[~new_deaths.index.isna()].iloc[:,-1].sort_values(ascending=False).rename('前日比')],axis=1).head(16)

table.loc['日本時間'+str(datetime.today().day)+'日時点、出所は米ジョンズ・ホプキンス大。データは毎日公表とは限らず公表後修正される可能性がある'] = ''

table1 = table.rename_axis('').reset_index()

table1.columns = pd.MultiIndex.from_product([['世界各国・地域の新型コロナ感染者・死者数'],table1.columns])

table2 = table.rename_axis('').reset_index()

table2.columns = pd.MultiIndex.from_product([[''],table2.columns])

table = pd.concat([table1.iloc[:,0],table2.iloc[:,1:]],axis=1)

table.to_csv('data/'+(datetime.today() - timedelta(days=1)).strftime('%Y%m%d')+'_JHU_Update.csv',encoding='utf-8-sig',index=False,line_terminator='\r\n')

response = requests.post(
        'https://api.mailgun.net/v3/mg.dataeditor.work/messages',
        auth=('api',os.environ.get('MAILGUN_API_KEY')),
        files=[('attachment',open('data/'+(datetime.today() - timedelta(days=1)).strftime('%Y%m%d')+'_JHU_Update.csv','rb'))],
        data={'from':os.environ.get('EMAIL_SENDER'),
              'to':[os.environ.get('EMAIL_RECIPIENT')],
              'subject': 'JHU Update '+(datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
              'text': 'Updated at '+(datetime.today() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')+'JST'})
