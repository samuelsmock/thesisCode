### displays a bar graph of NPVs under the stipulated price scenario and parametert set displays the total value
## and the portion that is subsidized

import geopandas as gpd
import pandas as pd
import json
import matplotlib.pyplot as plt
from tqdm import tqdm


scenario = 'scn1'
param = 1

candidateBuildings = gpd.read_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'buildingsFinalFormatted', rows = 10000)
candidateBuildings = candidateBuildings.drop(columns = 'geometry')

tqdm.pandas()

def jsonLoader(row): #some rows have the trailing '}' dropped
    if row[-1] != '}':
        row = row + '}'
    return json.loads(row)

candidateBuildings['npvs']=candidateBuildings['npvs'].progress_apply(jsonLoader)
candidateBuildings['subsidynpvFormat']=candidateBuildings['subsidynpvFormat'].progress_apply(jsonLoader)


##assign the value for the specific scenario and parameter to a temporary column to build histograms
candidateBuildings['tempNPV'] = candidateBuildings['npvs'].apply(lambda x : x[scenario][param])
candidateBuildings['tempSubCost'] = candidateBuildings['subsidynpvFormat'].apply(lambda x : x[scenario][param])

#group by assigned_t (size attribute), take the average and convert to a dataframe
avgNPV = candidateBuildings.groupby('assigned_t')['tempNPV'].mean().round().reset_index()
avgSubsidyCost = candidateBuildings.groupby('assigned_t')['tempSubCost'].mean().reset_index()

## make subsidy cost positive to show value to building owner not cost to govt
avgSubsidyCost['tempSubCost']= avgSubsidyCost['tempSubCost'].apply(lambda x: abs(x)) 



combinedAvgs = avgNPV.merge(avgSubsidyCost, on='assigned_t')

# make a new value unsubsidized cost, then plot unsub + sub = total avgNPV
# if sub cost is higher than NPV print 0 and olnly show the subsidy cost
combinedAvgs['tempUnsubNPV']= combinedAvgs.apply(lambda x: x['tempNPV']- x['tempSubCost'] if (x['tempSubCost'] < x['tempNPV']) else 0, axis =1) 

#move 13+ to the end
combinedAvgs = pd.concat([combinedAvgs.iloc[1:10], combinedAvgs.iloc[0:1],combinedAvgs.iloc[10:0]])

print(combinedAvgs)

plt.bar(combinedAvgs['assigned_t'], combinedAvgs['tempUnsubNPV'], label = "Average NPV to Building Owner", zorder = 1, bottom = combinedAvgs['tempSubCost'])

plt.bar(combinedAvgs['assigned_t'], combinedAvgs['tempSubCost'], label = "Of Which From Subsidy / HPT guarantee", zorder = 0)



plt.xlabel('Building Size Category')
plt.ylabel('NPV')
plt.title('Average Total NPV by Residential Building Type; '+ str(scenario) + "; test parameter set " + str(param))
plt.legend()

plt.show()

##sfhs = candidateBuildings[candidateBuildings['assigned_t'] == buildType]

#npvUnsub = candidateBuildings.progress_apply(lambda x: x['npvs'][scenario][param] + x['subsidynpv'][scenario][param], axis = 1).to_list()
#npvSub = candidateBuildings['subsidynpv'].progress_apply(lambda x: x[scenario][param]*-1).to_list()

# plt.hist([npvUnsub, npvSub], label = ['Value to Building Owner', 'Portion Deriving from Public Subsidy'], bins=10, edgecolor='k')
# plt.xlabel('NPV over 20 years @ 2.8% Discount')
# plt.ylabel('# of Structures')
# plt.title('NPV of Single Family Detached Homes in Saxony')
# plt.grid(True)


# plt.show()
