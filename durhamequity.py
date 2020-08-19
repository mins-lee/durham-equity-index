import pandas as pd
import censusdata
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.precision', 2)

# assign acs table numbers 
income = 'B19001'
rent = 'B03002'
minority = 'B03002'
vehicle = 'B08141'
older = 'B11007'
younger = 'B11005'
disability = 'B18101' 
language = 'B16001'
femaleHouseholder = 'B17010'

categories = [income, rent, minority, vehicle, older, younger, disability, 
                language, femaleHouseholder]

def genTable(table):
    return censusdata.printtable(censusdata.censustable('acs1', 2018, table))

def printTables():
    for name in categories: 
        genTable(name)

# printTables()
# print(genTable('B16002')) # here: why the package does not compatible with C  

income_var = ['B19001_002E', 'B19001_003E', 'B19001_004E', 'B19001_005E', 
            'B19001_001E']
rent_var = ['B25070_007E', 'B25070_008E', 'B25070_009E', 'B25070_010E', 
            'B25070_001E', 'B25070_011E']
minority_var = ['B03002_001E', 'B03002_003E', 'B03002_001E'] 
older_var = ['B11007_002E', 'B11007_001E']      
younger_var = ['B11005_002E', 'B11005_001E']  
femaleHouseholder_var = ['B17010_016E', 'B17010_036E', 'B17010_001E']

all_var = income_var + rent_var + minority_var + older_var + younger_var + femaleHouseholder_var
# durhambg = ""

year = 2018
nc = '37'
durham = '063'
def genBlockGroupData(var):
    return censusdata.download('acs5', year, censusdata.censusgeo([
        ('state', nc), ('county', durham), ('block group', '*')]), var)

# def printBlockGroupData(var):
#     durham = genBlockGroupData(var)
#     return durham.B25070_007E.head(5)

# print(printBlockGroupData(var1))

index = genBlockGroupData(all_var)

# compute variables
index['income'] = (index.B19001_002E + index.B19001_003E + 
        index.B19001_004E + index.B19001_005E) / (index.B19001_001E) * 100
index['rent'] = (index.B25070_007E + index.B25070_008E + index.B25070_009E + 
        index.B25070_010E) / (index.B25070_001E - index.B25070_011E) * 100
index['minority'] = (index.B03002_001E - index.B03002_003E) / (index.B03002_001E) * 100
index['older'] = (index.B11007_002E) / (index.B11007_001E) * 100
index['younger'] = (index.B11005_002E) / (index.B11005_001E) * 100
index['femaleHouseholder'] = (index.B17010_016E + index.B17010_036E) / (index.B17010_001E) * 100

index = index[['income', 'rent', 'minority', 'older', 'younger', 'femaleHouseholder']]

maxVal = []
percent = ['income', 'rent', 'minority', 'older', 'younger', 'femaleHouseholder']
for i in range(len(percent)): 
    maxVal += [index.describe()[percent[i]]['max']]

score = index.copy().div(maxVal)
score['mean'] = score.mean(axis=1)

# show 10 block groups with highest equity score
print(score.sort_values('mean', ascending=False).head(10))



# here: figure out the two other factors
# find block group names
# change table name from index to something else


# print(score.head(3))
# print(score.columns)













# 1-1. poverty: HOUSEHOLD INCOME IN THE PAST 12 months
# (Less than $10,000 + $10,000 to $14,999 + $15,000 to $19,999 + 
# $20,000 to $24,999)/(Total) * 100
# (B19001_002E+B19001_003E+B19001_004E+B19001_005E)/(B19001_001E) * 100

var1 = ['B19001_002E', 'B19001_003E', 'B19001_004E', 'B19001_005E', 'B19001_001E']

# 1-2. GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME IN THE PAST 12 MONTHS
# (30.0 to 34.9 percent + ... + 50.0 percent or more)/ (Total-not computed) * 100
# (B25070_007E + B25070_008E + B25070_009E + B25070_010E)/(B25070_001E - B25070_011E) * 100

var2 = ['B25070_007E', 'B25070_008E', 'B25070_009E', 'B25070_010E', 'B25070_001E', 'B25070_011E']

# 2. minority: HISPANIC OR LATINO ORIGIN BY RACE
# (Total - White alone)/Total * 100
# ('B03002_001E' - 'B03002_003E')/('B03002_001E') * 100

var3 = ['B03002_001E', 'B03002_003E', 'B03002_001E']

# here: check
# 3. vehicle: MEANS OF TRANSPORTATION TO WORk
# (No vehicle available)/(Total) * 100
# ('B08141_002E')/('B08141_001E') * 100 
# Total = (No vehicle available + 1 vehicle available + 
#       2 vehicles available + 3 or more vehicles available)  
# 'B08141_001E' = ('B08141_002E' + 'B08141_003E' + 'B08141_004E' + 'B08141_005E')

var4 = ['B08141_002E', 'B08141_001E']
test_var = ['B08141_001E', 'B08141_002E', 'B08141_003E', 'B08141_004E', 'B08141_005E']

# 4. older: HOUSEHOLDS BY PRESENCE OF PEOPLE 65 YEARS AND OVER, HOUSEHOLD SIZE AND HOUSEHOLD TYPE
# (Households with one or more people 65 years and over)/ (Total) * 100
# ('B11007_002E')/('B11007_001E') * 100

var5 = ['B11007_002E', 'B11007_001E']

# 5. younger: HOUSEHOLDS BY PRESENCE OF PEOPLE UNDER 18 YEARS BY HOUSEHOLD TYPE
# (Households with one or more people under 18 years)/(Total) * 100
# ('B11005_002E')/('B11005_001E') * 100

var6 = ['B11005_002E', 'B11005_001E']

# 6. disability: SEX BY AGE BY DISABILITY STATUS
# (Male with disability by age + Female with disability by age)/Total * 100
# (('B18101_004E' + 'B18101_007E' + 'B18101_010E' + 'B18101_013E' + 'B18101_016E' + 'B18101_019E')+
# ('B18101_023E' + 'B18101_026E' + 'B18101_029E' + 'B18101_032E' + 'B18101_035E' + 'B18101_038E'))/
# ('B18101_001E') * 100

var7 = ['B18101_004E', 'B18101_007E', 'B18101_010E', 'B18101_013E', 'B18101_016E', 'B18101_019E', 
'B18101_023E', 'B18101_026E', 'B18101_029E', 'B18101_032E', 'B18101_035E', 'B18101_038E',
'B18101_001E']

# 7. language: LANGUAGE SPOKEN AT HOME BY ABILITY TO SPEAK ENGLISH FOR THE POPULATION 5 YEARS AND OVER
# (Speak eng less than very well by language other than eng)/Total * 100
# (B16001_005E + B16001_008E + B16001_011E + B16001_014E + B16001_017E + B16001_020E + 
# B16001_023E + B16001_026E + B16001_029E + B16001_032E + B16001_035E + B16001_038E 
# + B16001_041E + B16001_044E + B16001_047E + B16001_050E + B16001_053E + ... + B16001_128E)
# /Total * 100

# 8. female householder: PPOVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES 
# BY FAMILY TYPE BY PRESENCE OF RELATED CHILDREN UNDER 18 YEARS BY AGE OF RELATED CHILDREN
# (Female householder income below + above poverty level)/(Total) * 100
# ('B17010_016E' + 'B17010_036E')/('B17010_001E') * 100

var9 = ['B17010_016E', 'B17010_036E', 'B17010_001E']

var8 = []


# var = var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 

def generateVarNames(): 
    result = ""
    for i in range(1, 10):
        if i < 10:
            result += 'var' + str(i) + ' + '
        else:
            result += 'var' + str(i)
    return(result)

var = generateVarNames()









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


# test_var = ['B08141_001E', 'B08141_002E', 'B08141_003E', 'B08141_004E', 'B08141_005E']








acsTable = pd.read_excel('ACS2018_Table_Shells.xlsx')



# print(acsTable[acsTable['Table ID'].str.contains('B99181')])
