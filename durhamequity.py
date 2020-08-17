import pandas as pd
import censusdata
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.precision', 2)
# variables: 
# People with Disabilities, People in Poverty, Minority Race and Ethnicity 
# Persons, Households without Vehicles, Older Adults, Persons under Age 18, 
# Persons with Limited English Proficiency, Female Householders 

def showVar(table):
    return censusdata.printtable(censusdata.censustable('acs5', 2018, table))

# here
poverty = 'B19001'
minority = 'B03002'
transToWork = 'B08141'
older = 'B11007'
younger = 'B11005'
# disability
# engProficienty
# femaleHouseholder

var = [poverty, minority, transToWork, older, younger]

def printTables():
    for name in var: 
        showVar(name)

# printTables()

# print(showVar(poverty))  

# household income in the past
# people in poverty = less than poverty level/total
# censusdata.printtable(censusdata.censustable('acs5', 2018, 'B19001'))

# hispanic or latino origin by race
# censusdata.printtable(censusdata.censustable('acs5', 2018, 'B03002'))

# here: check
# means of transportation to work
# censusdata.printtable(censusdata.censustable('acs5', 2018, 'B08141'))

# household by presence of people 65 years and over
# censusdata.printtable(censusdata.censustable('acs5', 2018, 'B11007'))

# household by presence of people under 18 years by household type
# censusdata.printtable(censusdata.censustable('acs5', 2018, 'B11005'))


# download durham data 
durhambg = censusdata.download('acs5', 2018, 
            censusdata.censusgeo([('state', '37'), ('county', '063'), ('block group', '*')]),
            ['B23025_003E', 'B23025_005E', 'B15003_001E', 'B15003_002E', 'B15003_003E'])

# compute variables
durhambg['percent_unemployed'] = durhambg.B23025_005E / durhambg.B23025_003E * 100
durhambg['percent_nohs'] = (durhambg.B15003_002E + durhambg.B15003_003E) / durhambg.B15003_001E * 100
durhambg = durhambg[['percent_unemployed', 'percent_nohs']]
durhambg.describe()

# show 30 block groups with highest rate of unemployment 
durhambg.sort_values('percent_unemployed', ascending=False).head(30)

acsTable = pd.read_excel('ACS2018_Table_Shells.xlsx', index_col=0)
print(acsTable)