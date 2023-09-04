import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from plotPrices import plotPrice

candidateBuildings = gpd.read_file('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/consolidatedThesisData.gpkg', layer = "candidateEUBUCCO_MATCHED_CLEANED", rows = 50)


energyDict = pd.read_csv('/Users/sunshinedaydream/Desktop/thesis_data_local/non-spatial/codeDictionaries/energeticTotalsDict.csv')

priceDict = pd.read_csv('/Users/sunshinedaydream/Desktop/thesis_data_local/non-spatial/codeDictionaries/priceDict.csv')

#optionally view the price trajectories being used
#plotPrice(priceDict)

### Merge values from energyDict to candidateBuildings based on type ###
candidateBuildings = candidateBuildings.merge(energyDict, on = 'assigned_type', how = 'left')
print(len(candidateBuildings))


# alert user if the any buildings did not match #
if (len(candidateBuildings[candidateBuildings['SPF'].isnull()]) > 0):
    print(len(candidateBuildings[candidateBuildings['SPF'].isnull()]), " buildings were not matched with energy data")
 
### on each building loop through the 15 year period to sum the NPV and add it as a column to 
# candidate buuldings ###


def npv(building, energyPrices, scenario, discRate, termStart, termEnd, ffBoilerUsefulLife, upfrontSubsidy): ##building variable is a whole row in the buildings dataset

    if ffBoilerUsefulLife < termStart or (upfrontSubsidy !=0 & termStart != 0):
        print("Error - This function is intended to only consider subsidies in 2024 and FF boiler useful life must be greater than or equal to term start (HP installation date)")
        return NULL

    HPUpfront = 0
    ffUpfront = 0
    HPOngoing = 0
    ffOngoing = 0
    HPMaintenance = 0
    foregoneSavings =0
    npvSeries = []
    



    for i, year in energyPrices.iterrows():
        if i > termEnd:
            break

        ####### 1. Determine NPV of HP install allowing for a possibility where the homeowner doesnt install right away #######
        ## Here, it is assumed that the cost of a new HP will decline linearly to about 30% between 2024 and 2029 (BMWK, 2023)
        # furthermore, it is discounted to allow for scenarios where a homeowner waits for energyPrices
        # to come down  if termStart = 0 this equation simply evaluates to the cost of install today.
        # Finally if the termStart is immediate, the user has the option to see what effect subsidies can have 
        if (i == termStart and upfrontSubsidy == 0):
            HPUpfront = -1 * building['living_area'] * (building['upfrontCostPerM2'] * (1-0.06*(termStart))) * (1+discRate)**(-1*termStart) if termStart < 5 else -1 * building['living_area'] * (0.7 * building['upfrontCostPerM2']) * (1+discRate)**(-1*termStart)
        elif termStart == 0 and upfrontSubsidy != 0:
            HPUpfront = -1 * building['living_area'] * (building['upfrontCostPerM2']) * (1-upfrontSubsidy)
        ####### 2. Determine NPV of installing a new fossil fuel boiler instead as a counterfactual #######    
        ####### This is important to caputure the cost of early retirement and will be up to the user to determine useful life
        ####### If the existing infrastructure needs to replaced anyway, the difference in investment costs is the value we are interested in
        ####### Install costs are taken to be about 60% cheaper than a HP in 2024, and are taken as constant unlike the HP which 
        #######is assumed to get cheaper as time goes on. ###########################

        #######  IF the user does not want to consider this term,s et ffBoilerUSefulLife to infinity ######################
        
        if i == ffBoilerUsefulLife:
            ffUpfront = -1 * building['living_area'] * building['upfrontCostPerM2'] * 0.4 * (1+discRate)**(-1*(ffBoilerUsefulLife))

        ## discounted relative to how long between the boiler could have been used. If both are 0, the total upfront 
        # cost contribution is just the difference betwen investment costs today.     
        #                                                                
        if i < termStart:
            foregoneSavings +=  (year[scenario+'_Gas']/0.9)  * building['yearlySensHeatPerM2'] * building ['living_area'] * (1+ discRate)**(-1 * i) - (year[scenario + '_Elec']/building['SPF'])* building['yearlySensHeatPerM2'] * building ['living_area'] * (1+ discRate)**(-1 * i) 
                                
        
        
        
        

        # the diff in yearly cost for a HP and gas boiler specific SPF (weightedCOP)
        # and a gas boiler efficiency of 0.9. In euros #### 
        if i > termStart:
            ### Discount and add to npv ####
            HPOngoing += -1 * (year[scenario + '_Elec']/building['SPF'])* building['yearlySensHeatPerM2'] * building ['living_area'] * (1+ discRate)**(-1 * i)
            ffOngoing += -1 * (year[scenario+'_Gas']/0.9)  * building['yearlySensHeatPerM2'] * building ['living_area'] * (1+ discRate)**(-1 * i)
            HPMaintenance += -1 * building['living_area'] * building['upfrontCostPerM2'] *0.01 * (1+ discRate)**(-1 * i)

        npvSeries.append(HPUpfront- ffUpfront  + HPMaintenance + HPOngoing-ffOngoing - foregoneSavings )


    
    return npvSeries
    #return HPUpfront - ffUpfront + HPOngoing - ffOngoing
    
### Initialialize to make it easy to quickly run models

repDisc = 0.022  
remLife = 100000
start = 0
end = 20
subsidy = 0

candidateBuildings['scn1_npv'] = candidateBuildings.apply(npv, args = (priceDict, 'scn1', repDisc, start, end, remLife, subsidy), axis = 1)
candidateBuildings['scn2_npv'] = candidateBuildings.apply(npv, args = (priceDict, 'scn2', repDisc, start, end, remLife,subsidy), axis = 1)
candidateBuildings['scn3_npv'] = candidateBuildings.apply(npv, args = (priceDict, 'scn3', repDisc, start, end, remLife, subsidy), axis = 1)
candidateBuildings['hist_npv'] = candidateBuildings.apply(npv, args = (priceDict, 'hist', repDisc, start, end, remLife, subsidy), axis = 1)

# Plot the columns 'a', 'b', and 'c' on the same graph


def plotNPV():


    years = pd.to_datetime([num for num in range(2024, 2024 +len(candidateBuildings.loc[0,'scn2_npv']))], format = '%Y')

    plt.plot(years,  candidateBuildings.loc[42, 'scn1_npv'], label='Scenario 1', linewidth = 2.5,)
    plt.plot(years,  candidateBuildings.loc[42,'scn2_npv'], label='Scenario 2', linewidth = 2.5,)
    plt.plot(years,  candidateBuildings.loc[42, 'scn3_npv'], label='Scenario 3', linewidth = 2.5,)
    plt.plot(years,  candidateBuildings.loc[42, 'hist_npv'], label='Pre 2022 Historic Average', linewidth = 2.5,)

    plt.xlim(years[0], years[-1])
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    # Add labels and legend

    plt.grid(True) 
    plt.xlabel('Years Past 2024')
    plt.ylabel(f'NPV @ {round(repDisc *100, 2)}%')
    plt.title(f'NPV of Air/Water Heatpump in 140 m2 SFH Installed in {2024+start} \n under different Price Trajectories. \n {"Ignoring FF boiler replacement cost" if remLife > 100 else "Taking into account a fossil fuel boiler that needs to be replaced anyway in " + str(remLife) + " years"} \n {("Subsidy: " + str(100*subsidy) + "%")}')
    plt.legend()

    # Show the plot
    plt.show()

plotNPV()
#candidateBuildings.to_csv('/Users/sunshinedaydream/Desktop/thesis_data_local/spatial_data/scratch/test11.csv')