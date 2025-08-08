# This code take the cwmap and ccap files, and overall sees how well they align with
# each other using confusion matrices. The overall workflow preprocesses them (easy step),
# applies logic via raster calculator for making binary change outputs (hard step, more complexity)
# and creates confusion matrices off of them (technically this part needs to be done manually-- read the note at the top of cwmapCCAPConfusionMatrixV1 to see what I mean). 


import arcpy
from arcpy.sa import *
import os

# Set environments
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD_1983_Contiguous_USA_Albers")

#Input Folders
ccap_folder = r"D:\user\CCAP Data"
cwmap_folder = r"D:\user\DiVit"

#Step 1 Folders: Preprocessing
ReclassCCAP = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step1Preprocessing\Step1aReclassification\ReclassCCAP"
PureReclasscwmap = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step1Preprocessing\Step1aReclassification\PureReclasscwmap"
MaskedMixedCCAP = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step1Preprocessing\Step1bMasking\MaskedMixedCCAP"
MaskedPureCCAP = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step1Preprocessing\Step1bMasking\MaskedPure"

#Step 2 Folders: Binary Change Maps
HeteroCCAPBinaryChange = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step2BinaryChange\HeteroCCAPBinaryChange"
HomoCCAPBinaryChange = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step2BinaryChange\HomoCCAPBinaryChange"
HeterocwmapBinaryChange = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step2BinaryChange\HeterocwmapBinaryChange"
HomocwmapBinaryChange = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step2BinaryChange\HomocwmapBinaryChange"

#Step 3 Folders: Confusion Matrices
MixedAccAssPoints = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step3ConfusionMatrix\MixedAccuracyAssessmentPoints"
PureAccAssPoints = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\12ConfusionMatrices\AttempttoAutomatebcIWasBored\Step3ConfusionMatrix\PureAccuracyAssessmentPoints"


# Reclassify mapping: {original: new}
reclass_ccap_map = RemapValue([
    [21, 2], [22, 2], [23, 2],                 # Open Water
    [15, 3], [18, 3],                          # Emergent Wetland
    [13, 4], [14,4], [16,4], [17,4],           # Forest/Scrub
    [2,5], [3,5], [20,5],                      # Barren/Developed
    [6,6], [7,6], [8,6],                       # Agriculture/Grassland
    [1,1], [4,1],[5,1],[9,1],[10,1],[11,1],[12,1],[19,1],[25,1]
])

years = [1996, 2001, 2006, 2010, 2016, 2021]

# CCAP Reclass
for year in years:
    input_raster = os.path.join(ccap_folder, f"CCAP{year}.tif")
    output_raster = os.path.join(ReclassCCAP, f"ReclassCCAP{year}.tif")
    
    reclassified = Reclassify(input_raster, "Value", reclass_ccap_map, "NODATA")
    reclassified.save(output_raster)
    print(f"Reclassified {year} CCAP saved.")

# cwmap Reclass
reclass_cwmap_map = RemapValue([
    [1, 1], [2, 2], [3,3],[4,4],[11,"NODATA"],[12,"NODATA"],[13,"NODATA"],[14,"NODATA"], 
    [15,"NODATA"], [16,"NODATA"]
    # I might have to also reclass all the other values to NODATA, like [3,"NODATA"] 
])

for year in years:
    input_raster = os.path.join(cwmap_folder, f"cwmap_{year}.tif")
    output_raster = os.path.join(PureReclasscwmap, f"PureReclasscwmap{year}.tif")
    
    reclassified = Reclassify(input_raster, "Value", reclass_cwmap_map, "NODATA")
    reclassified.save(output_raster)
    print(f"Reclassified {year} cwmap saved.") 

#==============Step 1.2: Mask CCAP with cwmap===================
for year in years:
    cwmap = os.path.join(r"D:\Owais Kamran\DiVit",f"cwmap_{year}.tif")
    ccap_reclass = os.path.join(ReclassCCAP, f"ReclassCCAP{year}.tif")
    output_masked = os.path.join(MaskedMixedCCAP, f"MaskedMixedCCAP{year}.tif")

    # If cwmap is null at a pixel, set CCAP to null there too
    masked = SetNull(IsNull(Raster(cwmap)), Raster(ccap_reclass))
    masked.save(output_masked)
    print(f"Masked Mixed CCAP {year} saved.")

for year in years:
    cwmap_pure = os.path.join(PureReclasscwmap, f"PureReclasscwmap{year}.tif")
    ccap_reclass = os.path.join(ReclassCCAP, f"ReclassCCAP{year}.tif")
    output_masked = os.path.join(MaskedPureCCAP, f"MaskedPureCCAP{year}.tif")

    # If cwmap is null at a pixel, set CCAP to null there too
    masked = SetNull(IsNull(Raster(cwmap_pure)), Raster(ccap_reclass))
    masked.save(output_masked)
    print(f"Masked Pure CCAP {year} saved.")
  
#=========================STEP 2: Binary Change Maps======================================
# Year pairs to compare
year_pairs = [(1996, 2001), (2001, 2006), (2006, 2010), (2010, 2016), (2016, 2021), (1996, 2021)]

# Binary change maps for CCAP (masked)
for y1, y2 in year_pairs:
    r1 = os.path.join(MaskedMixedCCAP, f"MaskedMixedCCAP{y1}.tif")
    r2 = os.path.join(MaskedMixedCCAP, f"MaskedMixedCCAP{y2}.tif")
    out = os.path.join(HeteroCCAPBinaryChange, f"HeteroCCAPBinaryChange{y1}to{y2}.tif")

    change_map = Con(Raster(r1) != Raster(r2), 1, 0)
    change_map.save(out)
    print(f"HeteroCCAPBinaryChange{y1}to{y2} saved.")
    
for y1, y2 in year_pairs:
    r1 = os.path.join(MaskedPureCCAP, f"MaskedPureCCAP{y1}.tif")
    r2 = os.path.join(MaskedPureCCAP, f"MaskedPureCCAP{y2}.tif")
    out = os.path.join(HomoCCAPBinaryChange, f"HomoCCAPBinaryChange{y1}to{y2}.tif")

    change_map = Con(Raster(r1) != Raster(r2), 1, 0)
    change_map.save(out)
    print(f"HomoCCAPBinaryChange{y1}to{y2} saved.")
    
for y1, y2 in year_pairs:
    r1 = os.path.join(PureReclasscwmap, f"PureReclasscwmap{y1}.tif")
    r2 = os.path.join(PureReclasscwmap, f"PureReclasscwmap{y2}.tif")
    out = os.path.join(HomocwmapBinaryChange, f"HomocwmapBinaryChange{y1}to{y2}.tif")

    change_map = Con(Raster(r1) != Raster(r2), 1, 0)
    change_map.save(out)
    print(f"HomocwmapBinaryChange{y1}to{y2} saved.")
    
for y1, y2 in year_pairs:
    r1 = os.path.join(cwmap_folder, f"cwmap_{y1}.tif")
    r2 = os.path.join(cwmap_folder, f"cwmap_{y2}.tif")
    out = os.path.join(HeterocwmapBinaryChange, f"HeterocwmapBinaryChange{y1}to{y2}.tif")

    change_map = Con(Raster(r1) != Raster(r2), 1, 0)
    change_map.save(out)
    print(f"HeterocwmapBinaryChange{y1}to{y2} saved.")


#======================STEP 3: Accuracy Assessment Points======================

for y1, y2 in year_pairs:
    file_in = os.path.join(HeteroCCAPBinaryChange,f"HeteroCCAPBinaryChange{y1}to{y2}.tif")
    out = os.path.join(MixedAccAssPoints,f"MixedAccAssPoints{y1}to{y2}.tif")
    points = CreateAccuracyAssessmentPoints(test, out, "CLASSIFIED", 1000)
    
    points.save(out)
    print(f"MixedAccAssPoints{y1}to{y2} saved")
          
for y1, y2 in year_pairs:
    file_in = os.path.join(HomoCCAPBinaryChange,f"HomoCCAPBinaryChange{y1}to{y2}.tif")
    out = os.path.join(PureAccAssPoints,f"PureAccAssPoints{y1}to{y2}.tif")
    points = CreateAccuracyAssessmentPoints(test, out, "CLASSIFIED", 1000)
    
    points.save(out)
    print(f"PureAccAssPoints{y1}to{y2} saved")
