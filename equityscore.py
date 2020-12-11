# %% 
# get block group level data of Durham County, NC to compute equity score
# here: run it and see if it works
import numpy as np
import pandas as pd
import censusdata
import yaml
import cufflinks as cf
cf.go_offline() 
# %%
with open('config.yaml', 'r') as f:
  # load contents of config.yaml into a python dictionary
  config = yaml.safe_load(f.read())  

state = config['acs']['state']
county = config['acs']['county']
year = config['acs']['year']
key = config['web_resource']['key']

# %%
# store acs variable names
lowIncome = ['B19001_002E', 'B19001_003E', 'B19001_004E', 'B19001_005E', 'B19001_001E']
highRent = ['B25070_007E', 'B25070_008E', 'B25070_009E', 'B25070_010E', 'B25070_001E', 'B25070_011E']
minority = ['B02001_001E', 'B02001_002E']
senior = ['B11007_002E', 'B11007_001E']
children = ['B11005_002E', 'B11005_001E']
femaleHouseholder = ['B17010_016E', 'B17010_036E', 'B17010_001E']

variables = lowIncome + highRent + minority + senior + children + femaleHouseholder

#%%
def getStateGeo(state, year, key):
    """Return state identifier for ACS 5-year data."""
    allState = censusdata.geographies(censusdata.censusgeo([('state', '*')]), 'acs5', year, key=key)
    return allState[state].geo

def getCountyGeo(state, county, year, key):
    """Return county identifier for ACS 5-year data."""
    stateGeo = getStateGeo(state, year, key)
    allCounty = censusdata.geographies(censusdata.censusgeo(list(stateGeo) + 
            [('county', '*')]), 'acs5', year, key=key)
    return allCounty[f'{county}, {state}'].geo

def downloadBlockgroupData(state, county, year, key, variables):
    """Return data frame containing acs block group data."""
    countyGeo = getCountyGeo(state, county, year, key)
    table = censusdata.download('acs5', year, censusdata.censusgeo(list(countyGeo) + 
            [('block group', '*')]), variables, key=key)
    return table

#%%
def main():
    # download acs data for selected variables
    df = downloadBlockgroupData(state, county, year, key, variables)

    # compute variables

    # 1. pct of income below poverty level: HOUSEHOLD INCOME IN THE PAST 12 MONTHS
    # (Less than $10,000 + $10,000 to $14,999 + $15,000 to $19,999 + 
    # $20,000 to $24,999)/(Total)
    df['belowPovertyLevel'] = (df.B19001_002E + df.B19001_003E + df.B19001_004E + df.B19001_005E) / (df.B19001_001E)

    # 2. pct of income for rent greater than 30%: GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME IN THE PAST 12 MONTHS
    # (30.0 to 34.9 percent + ... + 50.0 percent or more)/(Total-Income not computed) 
    df['pctIncomeForRent'] = (df.B25070_007E + df.B25070_008E + df.B25070_009E + df.B25070_010E) / (df.B25070_001E - df.B25070_011E) 

    # 3. pct of minority
    # (Total - White)/(Total)
    df['minority'] = (df.B02001_001E - df.B02001_002E) / (df.B02001_001E) 

    # 4. pct of individuals 65 years and older: HOUSEHOLDS BY PRESENCE OF PEOPLE 65 YEARS AND OVER, HOUSEHOLD SIZE AND HOUSEHOLD TYPE
    # (Households with one or more people 65 years and over)/(Total) 
    df['senior'] = df.B11007_002E / df.B11007_001E 

    # 5. pct of minor: HOUSEHOLDS BY PRESENCE OF PEOPLE UNDER 18 YEARS BY HOUSEHOLD TYPE
    # (Households with one or more people under 18 years)/(Total)
    df['minor'] = df.B11005_002E / df.B11005_001E 

    # 6. pct of female householder: PPOVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES 
    # BY FAMILY TYPE BY PRESENCE OF RELATED CHILDREN UNDER 18 YEARS BY AGE OF RELATED CHILDREN
    # (Female householder income below + above poverty level)/(Total) 
    df['femaleHouseholder'] = (df.B17010_016E + df.B17010_036E) / df.B17010_001E 

    #%%
    # select computed variables only
    columns = ['belowPovertyLevel', 'pctIncomeForRent', 'minority', 'senior', 'minor', 'femaleHouseholder']
    df = df[columns]

    # compute equity score
    df['total'] = (df.belowPovertyLevel + df.pctIncomeForRent + df.minority + df.senior + df.minor + df.femaleHouseholder) / len(columns)
    df['equity'] = np.where(df['total']>.5, 'high', np.where(df['total']>.3, 'medium', 'low'))
    # conver index to column
    df.reset_index(inplace=True)
    # %%
    # create block group and census tract array
    rows = len(df)
    temp = np.empty((0, 4))
    for i in range(rows):
        blockGroup = df['index'][i].name.split(', Durham')[0].split(', ')[0].split('p ')[1]
        censusTract = df['index'][i].name.split(', Durham')[0].split(', ')[1].split('t ')[1]   
        group = df['index'][i].name.split(', Durham')[0]
        index = df['index'][i]
        temp = np.append(temp, [[blockGroup, censusTract, group, index]], axis=0) 

    # convert arrary to data frame
    temp = pd.DataFrame(temp, columns=['blockGroup', 'censusTract', 'group', 'index'])

    #%%
    # modify census tract to 4 digit number to use as a key
    temp['keyid'] = temp.censusTract.astype(float) 
    for i in range(len(temp)):
        if temp.keyid[i] < 100:
            temp.keyid[i] = (temp.keyid[i] * 100)
        else:
            temp.keyid[i] = temp.keyid[i]

    temp.keyid = temp.keyid.astype(int).astype(str)

    for i in range(len(temp)):
        if len(temp.keyid[i]) == 3:
            temp.keyid[i] = temp.keyid[i].zfill(4)

    temp.keyid = temp.blockGroup + temp.keyid
    # %%
    # merge temp with df on index
    df = pd.merge(temp, df, on='index')
    df.drop(columns='index')

    print(df)
    
    return df

if __name__ == '__main__':
    main()