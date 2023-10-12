import geopandas as gpd
import pandas as pd
import json
import matplotlib.pyplot as plt
from tqdm import tqdm


scenario = 'scn1'
param = 0
buildType = 'siz_1_free'
candidateBuildings = gpd.read_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'buildingsFinal', rows = 10000)

tqdm.pandas()

def jsonLoader(row): #some rows have the trailing '}' dropped
    if row[-1] != '}':
        row = row + '}'
    return json.loads(row)

candidateBuildings['npvs']=candidateBuildings['npvs'].progress_apply(jsonLoader)
candidateBuildings['subsidynpv']=candidateBuildings['subsidynpv'].progress_apply(jsonLoader)

candidateBuildings = candidateBuildings.drop(columns = 'geometry')

sfhs = candidateBuildings[candidateBuildings['assigned_t'] == buildType]

npvUnsub = candidateBuildings.progress_apply(lambda x: x['npvs'][scenario][param] + x['subsidynpv'][scenario][param], axis = 1).to_list()
npvSub = candidateBuildings['subsidynpv'].progress_apply(lambda x: x[scenario][param]*-1).to_list()


plt.hist([npvUnsub, npvSub], label = ['Value to Building Owner', 'Portion Deriving from Public Subsidy'], bins=10, edgecolor='k')
plt.xlabel('NPV over 20 years @ 2.8% Discount')
plt.ylabel('# of Structures')
plt.title('NPV of Single Family Detached Homes in Saxony')
plt.grid(True)


plt.show()
