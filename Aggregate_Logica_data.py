import shapefile, sys
import pandas as pd

Path = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Jumbo_2009_YKR_join.dbf'
output = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Jumbo_2009_meanAggre.txt'

#Path = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Itakeskus_2009_YKR_join.dbf'
#output = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Itakeskus_2009_meanAggre.txt'

#Path = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Forum_2009_YKR_join.dbf'
#output = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Forum_2009_meanAggre.txt'

#Path = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Lippulaiva_2009_YKR_join.dbf'
#output = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Lippulaiva_2009_meanAggre.txt'

sf = shapefile.Reader(Path)
recs = sf.records()

#Make pandas dataframe
dataIn = pd.DataFrame(recs)

print dataIn[0:5]
#sys.exit()

#Select only interesting columns 
data = dataIn[[2,3,4,8]]
data.columns = ['x', 'y', 'time', 'YKR_id']

#Group by YKR_id
grouped = data.groupby('YKR_id')

#Empty list for results
results = []

for group in grouped:
    ykr_id = group[0]
    time = group[1]['time']
    meanTime = int(round(time.mean(),0))

    results.append([ykr_id, meanTime])
    #sys.exit()

#Create pandas dataFrame from results
rdata = pd.DataFrame(results)
rdata.columns = ['YKR_ID', 'time']
print rdata[0:5]

rdata.to_csv(output, sep=';', index=False)

#print rdata[0:5]
