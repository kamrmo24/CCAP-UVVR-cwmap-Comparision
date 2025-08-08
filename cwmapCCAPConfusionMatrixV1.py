# This code analyzes emergent wetland to water change over time for cwmap and ccap, and 
# analyzes how well ccap and cwmap align with each other using confusion matrices.
# To save on spaace, not every file needs to be saved. This will take some refactoring, but one could say "null = SetNull(IsNull(cwmap), input_raster)" and then not save null to any output file. 
# Note: Even though the accuracy assessment points were made, 2-3 more steps are needed to make the confusion matrices. ArcGIS Pro prepopulates the attribute table with a GrndTruth column, all filled as "-1". 
# For the confusion matrix tool to work, these GrndTruth values have to be replaced. In this code, the cwmap files are being sampled, so the CCAP files would be GrndTruth. 
# There is a tool called "ExtractMultiValuesToPoints" which can do this, but the original GrndTruth column has to be deleted first. I don't think ExtractMultiValuesToPoints can override GrndTruth. In my attempts, I ended up making a new 
# column called GrndTruth_1. But I think this is bad, because the next step is to use the ConfusionMatrix tool on these accuracy assessment points, but I believe that tool recognizes GrndTruth as a special name, so GrndTruth_1 doesn't work.
# So delete the GrndTruth column, run the "ExtractMultiValuesToPoints" tool with GrndTruth as the output field name, then run the ConfusionMatrix tool.

# Also, this is version 1 of my attempt to do this. I made a version 2 as well. 
 
import os
from arcpy.sa import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD_1983_Contiguous_USA_Albers")

#Input Folders
ccap_folder = r"D:\User\CCAP Data"
cwmap_folder = r"D:\User\cwmap"

#Step 1 Files
ccap_reclass = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step1Preprocessing\Step1aReclass\ccap_reclass"
cwmap_reclass_mixed = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step1Preprocessing\Step1aReclass\cwmap_reclass_mixed"
cwmap_reclass_pure = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step1Preprocessing\Step1aReclass\cwmap_reclass_pure"

MaskedMixedCCAP = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step1Preprocessing\Step1bMasking\MaskedMixedCCAP"
MaskedPureCCAP = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step1Preprocessing\Step1bMasking\MaskedPureCCAP"

#Step 2 Files --> i named them ternary change but now they reflect septenary change but i don't feel like renaming them
PurecwmapTernaryChange = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step2TernaryChange\PurecwmapTernaryChange"
MixedcwmapTernaryChange = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step2TernaryChange\MixedcwmapTernaryChange"
PureCCAPTernaryChange  = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step2TernaryChange\PureCCAPTernaryChange"
MixedCCAPTernaryChange = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step2TernaryChange\MixedCCAPTernaryChange"

#Step 3 Files
PureAccAssPointscwmap = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step3ConfMatrix\PureAccAssPointscwmap"
MixedAccAssPointscwmap = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\WetlandToWater\Attempt 3 ccap is now reference\Step3ConfMatrix\MixedAccAssPointscwmap"

ccap_remap = RemapValue([
    [21, 1], [22, 1], [23, 1],                 # Open Water
    [15, 2], [18, 2],                          # Emergent Wetland
    [13, 3], [14,3], [16,3], [17,3],          
    [2,4], [3,4], [20,4],                     
    [6,4], [7,4], [8,4],                  
    [1,"NODATA"], [4,"NODATA"],[5,"NODATA"],[9,"NODATA"],[10,"NODATA"],
    [11,"NODATA"],[12,"NODATA"],[19,"NODATA"],[25,"NODATA"]
])

cwmap_remap_pure = RemapValue([
    [1, 1], [2, 2], #Water stays as water, same for emergent wetland and the others which are not mixed pixels
    [3,3],[4,4],[11,"NODATA"],
    [12,"NODATA"],[13,"NODATA"],[14,"NODATA"], 
    [15,"NODATA"], [16,"NODATA"]
])


years = [1996,2001,2006,2010,2016,2021]


#Remap cwmap pure
for year in years:
    input_raster = os.path.join(cwmap_folder,f"cwmap_{year}.tif")
    output_raster = os.path.join(cwmap_reclass_pure,f"cwmap_reclass_pure{year}.tif")
    
    reclass = Reclassify(input_raster,"Value",cwmap_remap_pure,"NODATA")
    reclass.save(output_raster)
    print(f"Remapped mixed pure cwmap {year}")

#Remap ccap
for year in years:
    input_raster = os.path.join(ccap_folder,f"CCAP{year}.tif")
    output_raster = os.path.join(ccap_reclass,f"ccap_reclass{year}.tif")
    
    reclass = Reclassify(input_raster,"Value",ccap_remap,"NODATA")
    reclass.save(output_raster)
    print(f"Remapped CCAP {year}")
    
#SetNull the ccap maps
#Mixed
for year in years:
    input_raster = os.path.join(ccap_reclass,f"ccap_reclass{year}.tif")
    output_raster = os.path.join(MaskedMixedCCAP,f"MaskedMixedCCAP{year}.tif")
    cwmap = os.path.join(cwmap_folder,f"cwmap_{year}.tif")
    
    nulled = SetNull(IsNull(cwmap),input_raster) #IsNull creates a raster of 1s and 0s (1 if cwmap is null, 0 if not). If the first parameter for SetNull is 1, then the output of the raster will be null at that pixel. Else, the pixel will be the input_raster
    nulled.save(output_raster)
    print(f"SetNull Mixed CCAP {year}")
    
#Pure
for year in years:
    input_raster = os.path.join(ccap_reclass,f"ccap_reclass{year}.tif")
    output_raster = os.path.join(MaskedPureCCAP,f"MaskedPureCCAP{year}.tif")
    cwmap = os.path.join(cwmap_reclass_pure,f"cwmap_reclass_pure{year}.tif")
    
    nulled = SetNull(IsNull(cwmap),input_raster)
    nulled.save(output_raster)
    print(f"SetNull Pure CCAP {year}")


#Step 2: Relies more on raster calculator logic 
for y1, y2 in year_pairs: 
    #Pure septenary change logic without looking into the mixed cases
    #cwmap pure

    # Define raster objects
    r1 = Raster(os.path.join(cwmap_reclass_pure, f"cwmap_reclass_pure{y1}.tif"))
    r2 = Raster(os.path.join(cwmap_reclass_pure, f"cwmap_reclass_pure{y2}.tif"))

    # Build septenary logic using nested Con statements
    change_map = Con((r1 == 1) & (r2 == 1), 1,                          # Stays water
    Con((r1 == 2) & (r2 == 2), 2,                                  # Stays emergent wetland
    Con((r1 == 3) & (r2 == 3), 3,                                  # Stays forest/scrub
    Con((r1 == 4) & (r2 == 4), 3,                                  # Stays other → same as forest/scrub
    Con((r1 == 2) & (r2 == 1), 4,                                  # Emergent wetland → water
    Con((r1 == 2) & (r2 != 1), 5,                                  # Emergent wetland → non-water
    Con((r1 != 2) & (r2 == 1), 6,                                  # Non-emergent → water
    Con((~((r1 == 1) | (r1 == 2))) & (~((r2 == 1) | (r2 == 2))), 7 # Neither is water or wetland
    ))))))))  # Default (fallback) value, optional

    out_raster = os.path.join(PurecwmapTernaryChange, f"PurecwmapTernaryChange{y1}to{y2}.tif")
    change_map.save(out_raster)
    print(f"PurecwmapTernaryChange{y1}to{y2} saved")
    
    #ccap pure

for y1, y2 in year_pairs: 
    
    # Define raster objects
    r1 =Raster(os.path.join(MaskedPureCCAP,f"MaskedPureCCAP{y1}.tif"))
    r2 = Raster(os.path.join(MaskedPureCCAP,f"MaskedPureCCAP{y2}.tif"))

    # Build septenary logic using nested Con statements
    change_map = Con((r1 == 1) & (r2 == 1), 1,                          # Stays water
    Con((r1 == 2) & (r2 == 2), 2,                                  # Stays emergent wetland
    Con((r1 == 3) & (r2 == 3), 3,                                  # Stays forest/scrub
    Con((r1 == 4) & (r2 == 4), 3,                                  # Stays other → same as forest/scrub
    Con((r1 == 2) & (r2 == 1), 4,                                  # Emergent wetland → water
    Con((r1 == 2) & (r2 != 1), 5,                                  # Emergent wetland → non-water
    Con((r1 != 2) & (r2 == 1), 6,                                  # Non-emergent → water
    Con((~((r1 == 1) | (r1 == 2))) & (~((r2 == 1) | (r2 == 2))), 7 # Neither is water or wetland
    ))))))))  # Default (fallback) value, optional


    out_ccap_raster = os.path.join(PureCCAPTernaryChange, f"PureCCAPTernaryChange{y1}to{y2}.tif")
    change_map.save(out_ccap_raster)
    print(f"PureCCAPTernaryChange{y1}to{y2} saved")

#Mixed septenary change logic 
year_pairs = [(1996, 2001), (2001, 2006), (2006, 2010), 
              (2010, 2016), (2016, 2021), (1996, 2021)]
for y1, y2 in year_pairs: 
    #cwmap mixed
    r1 = Raster(os.path.join(cwmap_folder, f"cwmap_{y1}.tif"))
    r2 = Raster(os.path.join(cwmap_folder, f"cwmap_{y2}.tif"))

    change_map = Con((r1 == 1) & (r2 == 1), 1,  # No change: Water
    Con(((r1 == 2) & (r2 == 2)), 2,  # No change: Emergent or mixed emergent
    Con(((r1 == 3) & (r2 == 3)) | ((r1 == 4) & (r2 == 4)) | ((r1 == 16) & (r2 == 16)), 3,  # No change: Forest/Other

    Con(((r1 == 2) & (r2 == 1)) | ((r1 == 11) & (r2 == 1)) | ((r1 == 2) & (r2 == 11)), 4,  # Emergent → Water/mixed

    Con(
        ((r1 == 2) & ~((r2 == 1) | (r2 == 11) | (r2 == 12) | (r2 == 13))) |
        ((r1 == 11) & ~((r2 == 1) | (r2 == 11) | (r2 == 12) | (r2 == 13))) |
        ((r1 == 14) & ~((r2 == 1) | (r2 == 11) | (r2 == 12) | (r2 == 13))) |
        ((r1 == 15) & ~((r2 == 1) | (r2 == 11) | (r2 == 12) | (r2 == 13))), 5,  # Emergent/mixed → non-water

    Con(
        ~((r1 == 2) | (r1 == 11) | (r1 == 14) | (r1 == 15)) & 
        ((r2 == 1) | (r2 == 11) | (r2 == 12) | (r2 == 13)), 6,  # Non-emergent → Water

    Con(
        ((r1 == 3) | (r1 == 4) | (r1 == 16)) & ((r2 == 3) | (r2 == 4) | (r2 == 16)) & (r1 != r2), 7  # Other-to-Other Change

      # Default fallback
)))))))

    
    out_raster = os.path.join(MixedcwmapTernaryChange, f"MixedcwmapTernaryChange{y1}to{y2}.tif")
    change_map.save(out_raster)
    print(f"MixedcwmapTernaryChange{y1}to{y2} saved")
 
    #ccap mixed, which i now realize in retrospect is the same logic as ccap pure but oh well

for y1, y2 in year_pairs: 
    
    # Define raster objects
    r1 =Raster(os.path.join(MaskedMixedCCAP,f"MaskedMixedCCAP{y1}.tif"))
    r2 = Raster(os.path.join(MaskedMixedCCAP,f"MaskedMixedCCAP{y2}.tif"))

    # Build septenary logic using nested Con statements
    change_map = Con((r1 == 1) & (r2 == 1), 1,                          # Stays water
    Con((r1 == 2) & (r2 == 2), 2,                                  # Stays emergent wetland
    Con((r1 == 3) & (r2 == 3), 3,                                  # Stays forest/scrub
    Con((r1 == 4) & (r2 == 4), 3,                                  # Stays other → same as forest/scrub
    Con((r1 == 2) & (r2 == 1), 4,                                  # Emergent wetland → water
    Con((r1 == 2) & (r2 != 1), 5,                                  # Emergent wetland → non-water
    Con((r1 != 2) & (r2 == 1), 6,                                  # Non-emergent → water
    Con((~((r1 == 1) | (r1 == 2))) & (~((r2 == 1) | (r2 == 2))), 7 # Neither is water or wetland
    ))))))))  # Default (fallback) value, optional


    out_ccap_raster = os.path.join(MixedCCAPTernaryChange, f"MixedCCAPTernaryChange{y1}to{y2}.tif")
    change_map.save(out_ccap_raster)
    print(f"MixedCCAPTernaryChange{y1}to{y2} saved")
  

for y1, y2 in year_pairs:
    file_in = os.path.join(MixedcwmapTernaryChange,f"MixedcwmapTernaryChange{y1}to{y2}.tif")
    out = os.path.join(MixedAccAssPointscwmap,f"MixedAccAssPointscwmap{y1}to{y2}.tif")
    points = CreateAccuracyAssessmentPoints(file_in, out, "CLASSIFIED", 2000)
    
    print(f"MixedAccAssPoints{y1}to{y2} saved")


for y1, y2 in year_pairs:
    file_in = os.path.join(PurecwmapTernaryChange,f"PurecwmapTernaryChange{y1}to{y2}.tif")
    out = os.path.join(PureAccAssPointscwmap,f"PureAccAssPointscwmap{y1}to{y2}.tif")
    points = CreateAccuracyAssessmentPoints(file_in, out, "CLASSIFIED", 2000)
    
    print(f"PureAccAssPoints{y1}to{y2} saved")
