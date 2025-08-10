# Finds the median and mean UVVR value for pixels from cwmap that change from emergent wetland to either emergent wetland, mixed emergent wetland-water, or water.
# Very similar as the UVVRMeanandMedian.py code, but now compares y1=cwmap_{year}.tif with y2=cwmap_{year+1}.tif, and the first paramter of the SetNull code is like this:
# SetNull(not(y1 == 2 and y2 == 2 (or can be changed to 11 or 1)),y1). We want to keep pixels where y1 == 2 and y2 == 2, so if pixels are NOT following this condition, we set them as null

import os
import arcpy # Not sure if this import works in a regular IDE, may need to be done within arcgis pro itself

# Some of the code is commented out. This is because in the UVVR paper, https://link.springer.com/article/10.1007/s12237-022-01081-x, 
# they say that since UVVR is unitless, one should first do calculations and averages and aggregates with Fv first, (which is band 2 in the UVVR files), and then convert to UVVR using UVVR = 1/(F_v) - 1
# However I initially did means with UVVR directly, leading to some really high uvvr numbers (40-200) that were very wrong. The real UVVR means were around 0-2 instead. 
# Therefore, DO NOT AVERAGE UVVR DIRECTLY!!!! Do calculations and averages with Fv first, then convert to UVVR.

for year in range(1985,2022):
    cwmap1 = Raster(os.path.join(r"path_to_parent_folder_here",f"cwmap_{year}.tif"))
    cwmap2 = Raster(os.path.join(r"path_to_parent_folder_here",f"cwmap_{year+1}.tif"))
    mergedfvpath = os.path.join(r"path_to_band2 (atlantic & gulf uvvr merged)",f"{year}MergedFv.tif") # Look at UVVRchangeTypeComparision.py to understand where MergedFv is coming from. 
    # MergedFv takes the Fv bands (Band 2) of the Atlantic and Gulf files for each year, merges them together using MosaicToNewRaster, and does other preprocessing like reprojecting and snap raster.
    # MergedFv could be made better because the conditional raster used in SetNull was changeType.tif, but to make it better, the corresponding cwmap_{year}.tif should be used instead. This 
    # reduces the -9999 values in the attribute table. These -9999 values are why the "row[0] > -9990" line exists. This isn't a huge issue, but it would be nice to have sample sizes be more consistent.
#     UVVRfromMergedFv = os.path.join(r"C:\Users\kamrmo24\Documents\ArcGIS\Projects\MyProject\UVVRcwmap\UVVRfromMergedFv",f"{year}UVVRfromFv.tif")
 
    if not arcpy.Exists(mergedfvpath):
        print(f"Couldn't find {year} mergedfv")
        continue
#     mergedfv = Raster(mergedfvpath)
    
#     print(f"Converting {year} to uvvr")
#     uvvr = (1/mergedfv) -1
#     uvvr.save(UVVRfromMergedFv)
#     print(f"Converted {year} uvvr")

    print(f"Nulling cwmap {year}")
    emergent = SetNull( not (cwmap1==2 & cwmap2==2),cwmap)
  # The important class codes are as follows: 1 is water, 2 is emergent wetland, 11 is mixed emergent wetland water. 
    print(f"Nulled cwmap {year}")

    # Assuming the raster is categorical:
    print(f"Making acc ass points {year}")
    sample_pts = os.path.join(r"path",f"{year}AccAssPoints")
    CreateAccuracyAssessmentPoints(
    in_class_data=emergent,
    out_points=sample_pts,
    target_field="Classified",
    num_random_points=2500
    )
    print("Made acc ass points")

    print(f"Extract multi values to points for {year}")
    try:
        ExtractMultiValuesToPoints(
            in_point_features=sample_pts,
            in_rasters=[[mergedfvpath, "fv"]], #ExtractMultiValuesToPoints needs a file path, not the raster object. This is why mergedfvpath is used instead of Raster(mergedfvpath)
            bilinear_interpolate_values="NONE"
        )
        print(f"Calculating mean {year} fv for mixed emergent wetlands...")
        
        # Use SearchCursor to compute the mean manually
        with arcpy.da.SearchCursor(sample_pts, ["fv"]) as cursor:
            values = [row[0] for row in cursor if row[0] is not None and row[0] > -9990]

        mean_fv = sum(values) / len(values)
        print(f"{year} Mean fv: {mean_fv}")
        
#         print(f"Done, now delete {year} uvvr file")
#         arcpy.management.Delete(UVVRfromMergedFv)

    except Exception as e:
        print(f"Error: {e}")


import statistics
for year in range(1985,2023):
    sample_pts = os.path.join(r"C:\Users\kamrmo24\Documents\ArcGIS\Projects\MyProject\UVVRcwmap\AccAssPoints",f"{year}AccAssPoints.shp")

    if not arcpy.Exists(sample_pts):
        print(f"Couldn't get {year}")
        continue
    
    print(f"Getting acc ass points {year}")
    
    print(f"Get median for {year}")
    try:
        # Use SearchCursor to compute the mean manually
        with arcpy.da.SearchCursor(sample_pts, ["fv"]) as cursor:
            values = [row[0] for row in cursor if row[0] is not None and row[0] > -9990]

        median_uvvr = statistics.median(values)
        print(f"{year} Meidan UVVR: {median_uvvr}")

    except Exception as e:
        print(f"Error: {e}")
