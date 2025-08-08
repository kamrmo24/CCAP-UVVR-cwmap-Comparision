import os
import arcpy # Not sure if this import works, may need to be done within arcgis pro itself

# Some of the code is commented out. This is because in the UVVR paper, https://link.springer.com/article/10.1007/s12237-022-01081-x, 
# they say that since UVVR is unitless, one should first do calculations and averages and aggregates with Fv first, (which is band 2 in the UVVR files), and then convert to UVVR using
# UVVR = 1/(F_v) - 1
# However I initially did means with UVVR directly, leading to some really high uvvr numbers
for year in range(1985,2023):
    cwmap = Raster(os.path.join(r"path_to_parent_folder_here",f"cwmap_{year}.tif")) #or however you named cwmap, replace it as so
    mergedfvpath = os.path.join(r"path_to_band2 (atlantic & gulf uvvr merged)",f"{year}MergedFv.tif")
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
    emergent = SetNull(cwmap!=11,cwmap)
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
        print(f"Calculating mean {year} fv for emergent wetlands...")
        
        # Use SearchCursor to compute the mean manually
        with arcpy.da.SearchCursor(sample_pts, ["fv"]) as cursor:
            values = [row[0] for row in cursor if row[0] is not None and row[0] > -9990]

        mean_fv = sum(values) / len(values)
        print(f"{year} Mean fv: {mean_fv}")
        
#         print(f"Done, now delete {year} uvvr file")
#         arcpy.management.Delete(UVVRfromMergedFv)

    except Exception as e:
        print(f"Error: {e}")


