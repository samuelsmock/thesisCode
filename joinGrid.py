import pandas as pd
import geopandas as gpd

drop_columns = ['featuretype_name', 'dataset_name','Sonstige GebÃ¤ude mit Wohnraum', 'WohngebÃ¤ude (ohne Wohnheime)', 'Wohnheime', 'DoppelhaushÃ¤lfte', 'Freistehendes Haus', 'Gereihtes Haus']
test_area = gpd.read_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'smallTestArea')
grid_gdf = gpd.read_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'resGridAllBlocks', encoding = 'cp1252')


def remove_prefix(column_name):
    prefix = "build_"
    if column_name.startswith(prefix):
        return column_name[len(prefix):]
    return column_name

grid_gdf.rename(columns=remove_prefix, inplace=True)


### Drop Irrelevant data from 'GEBAEUDEART_SYS', 'GEBTYPBAUWEISE' remarks in orginal census data###



# Translate from German into easier to use naming scheme 
new_columns = {
    'Anderer GebÃ¤udetyp': 'siz_other',
    'Blockheizung': 'hea_block',
    'Einfamilienhaus: DoppelhaushÃ¤lfte': 'siz_1_semi',
    'Einfamilienhaus: Reihenhaus': 'siz_1_row',
    'Einzel-/MehrraumÃ¶fen (auch Nachtspeicherheizung)': 'hea_room',
    'Etagenheizung': 'hea_storey',
    'Fernheizung (FernwÃ¤rme)': 'hea_dist',
    'Freistehendes Einfamilienhaus': 'siz_1_free',
    'Freistehendes Zweifamilienhaus': 'siz_2_free',
    'Keine Heizung im GebÃ¤ude oder in den Wohnungen': 'hea_none',
    'Mehrfamilienhaus: 13 und mehr Wohnungen': 'siz_13+_apart',
    'Mehrfamilienhaus: 3-6 Wohnungen': 'siz_3-6_apart',
    'Mehrfamilienhaus: 7-12 Wohnungen': 'siz_7-12_apart',
    'Zentralheizung': 'hea_cent',
    'Zweifamilienhaus: DoppelhaushÃ¤lfte': 'siz_2_semi',
    'Zweifamilienhaus: Reihenhaus': 'siz_2_row',
    'residential_count': 'count_old'
}

grid_gdf.rename(columns = new_columns, inplace = True)

colstoKeep = ['geometry','Gitter_ID_100m','siz_other','hea_block','siz_1_semi','siz_1_row','hea_room','hea_storey','hea_dist','siz_1_free','siz_2_free','hea_none','siz_13+_apart', 'siz_3-6_apart','siz_7-12_apart','hea_cent','siz_2_semi','siz_2_row','count_old']


colstoDrop = [col for col in grid_gdf.columns if col not in (colstoKeep)]


grid_gdf.drop(columns = colstoDrop, axis = 1, inplace =True)



######### Force the values to be integers###########
int_columns = [col for col in grid_gdf.columns if col not in (['Gitter_ID_100m', "geometry"])]
grid_gdf[int_columns] = grid_gdf[int_columns].astype('int')


############ Calculate the total number of residential buildings as reflected by the "size" category
siz_columns = [col for col in grid_gdf.columns if col.split("_")[0] == "siz"]
grid_gdf["count_build_siz"] = grid_gdf[siz_columns].apply(lambda row: row.astype('int').sum(), axis = 1)


## Calculate the total number of residential buildings as reflected by the "heat" category
heat_columns = [col for col in grid_gdf.columns if col.split("_")[0] == "hea"]
grid_gdf["count_build_hea"] = grid_gdf[heat_columns].apply(lambda row: row.astype('int').sum(), axis = 1)

grid_gdf.to_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'allGridCount', driver = 'GPKG')



