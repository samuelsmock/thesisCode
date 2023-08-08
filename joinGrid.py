import pandas as pd
import geopandas as gpd

drop_columns = ['Sonstige GebÃ¤ude mit Wohnraum', 'WohngebÃ¤ude (ohne Wohnheime)', 'Wohnheime', 'DoppelhaushÃ¤lfte', 'Freistehendes Haus', 'Gereihtes Haus']
test_area = gpd.read_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'smallTestArea')
grid_gdf = gpd.read_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'candidate_grid', encoding = 'cp1252')


def remove_prefix(column_name):
    prefix = "build_"
    if column_name.startswith(prefix):
        return column_name[len(prefix):]
    return column_name

grid_gdf.rename(columns=remove_prefix, inplace=True)


### Drop Irrelevant data from 'GEBAEUDEART_SYS', 'GEBTYPBAUWEISE' remarks in orginal census data###
grid_gdf.drop(columns = drop_columns, axis = 1, inplace =True)

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


######### Force the values to be integers###########
int_columns = [col for col in grid_gdf.columns if col not in (['Gitter_ID_100m', "geometry"])]
grid_gdf[int_columns] = grid_gdf[int_columns].astype('int')

########## Bring in apartment totals from the census' "wohnungen" data ##############
apart_df = pd.read_csv('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/2011census/csv_Wohnungen_100m_Gitter/apartment_totals_100m.csv')
apart_df.rename(columns={"Einheiten insgesamt": "count_apart"}, inplace=True)

grid_gdf = grid_gdf.merge(apart_df, on = 'Gitter_ID_100m', how ="left")

############ Calculate the total number of residential buildings as reflected by the "size" category
siz_columns = [col for col in grid_gdf.columns if col.split("_")[0] == "siz"]
grid_gdf["count_build_siz"] = grid_gdf[siz_columns].apply(lambda row: row.astype('int').sum(), axis = 1)


############ Calculate the total number of residential buildings as reflected by the "heat" category
heat_columns = [col for col in grid_gdf.columns if col.split("_")[0] == "hea"]
grid_gdf["count_build_hea"] = grid_gdf[heat_columns].apply(lambda row: row.astype('int').sum(), axis = 1)



grid_gdf.to_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = 'candidateGrids', driver = 'GPKG')