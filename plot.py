#%%
import equityscore
import geopandas as gpd
import json
import cufflinks as cf
import pandas as pd
cf.go_offline() 

df = equityscore.main()
#%%
# plot histogram
df['equity'].value_counts().iplot(kind='bar',
    title='Equity score distribution for Durham County, NC',
    xTitle='Equity Score', yTitle='Num of block groups')

#%%
# plot equity score by block group
low = df[df['equity'] == 'low'].censusTract.value_counts()
medium = df[df['equity'] == 'medium'].censusTract.value_counts()
high = df[df['equity'] == 'high'].censusTract.value_counts()
temp = pd.DataFrame([low, medium, high], index=['low', 'medium', 'high'])
temp.iplot(kind='bar', barmode='stack', title='Equity Score by Census Area')
