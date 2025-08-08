# Attempted to compare uvvr files to changetype.tif with different change thresholds for changetype.tif. However, I think that since uvvr is a ratio that could proxy stability of wetlands, 
# whereas changetype.tif looks at... well, change types, these are two separate topics and can't really be compared like in the way I did so in this code.

import arcpy
import os
from arcpy.sa import *

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# Paths
AtlanticUVVR = r"D:\user\UVVR Data\AtlanticUVVR"
GulfUVVR = r"D:\user\UVVR Data\GulfUVVR"
Band2Merge = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\PreprocessedUVVR\MergedUVVR\Band2Merge"
clip_raster = r"D:\user\DiVit\DiVitchangeType.tif"
CompositeFolder = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\1985to2022UVVRComposite"
spatial_ref = arcpy.SpatialReference(5070)

# Set environment
arcpy.env.snapRaster = clip_raster
arcpy.env.mask = clip_raster
arcpy.env.outputCoordinateSystem = spatial_ref
arcpy.env.cellSize = clip_raster

# Process each year
for year in range(1985, 1986):
    print(f"Processing {year}...")

    atlantic_file = os.path.join(AtlanticUVVR, f"{year}AtlanticUVVR.tif")
    gulf_file = os.path.join(GulfUVVR, f"{year}GulfUVVR.tif")

    if not arcpy.Exists(atlantic_file) or not arcpy.Exists(gulf_file):
        print(f"  Missing data for {year}. Skipping.")
        continue

    try:
        # Extract Band 2
        atlantic_band2 = ExtractBand(atlantic_file, [2])
        gulf_band2 = ExtractBand(gulf_file, [2])

        # Apply SetNull to mask out areas outside clip_raster
        masked_atlantic = SetNull(IsNull(clip_raster), atlantic_band2)
        masked_gulf = SetNull(IsNull(clip_raster), gulf_band2)
        #If the setnull doesn't get picked up for some reason, then I might have to save it 
        # and then arcpy.management.Delete the files

        # Merge the masked bands
        merged_output = os.path.join(Band2Merge, f"{year}MergedFv.tif")
        arcpy.management.MosaicToNewRaster(
            input_rasters=[masked_atlantic, masked_gulf],
            output_location=Band2Merge,
            raster_dataset_name_with_extension=os.path.basename(merged_output),
            coordinate_system_for_the_raster=spatial_ref,
            pixel_type="32_BIT_FLOAT",
            number_of_bands=1,
            mosaic_method="MEAN",
            mosaic_colormap_mode="FIRST"
        )

        print(f"  Saved merged Fv: {merged_output}")

    except Exception as e:
        print(f"  Error processing {year}: {e}")

print("All years processed.")

# === STEP 2: Mosaic all merged years into a multi-year composite ===
merged_rasters = []
for year in range(1985, 2023):
    merged_path = os.path.join(Band2Merge, f"{year}MergedFv.tif")
    if arcpy.Exists(merged_path):
        merged_rasters.append(merged_path)
    else:
        print(f"{merged_path} not found")

if not merged_rasters:
    raise Exception("No valid yearly merged rasters found.")

composite_raster_name = "CompositeFv1985to2022_Mean.tif"
composite_raster_path = os.path.join(CompositeFolder, composite_raster_name)

arcpy.management.MosaicToNewRaster(
    input_rasters=merged_rasters,
    output_location=CompositeFolder,
    raster_dataset_name_with_extension=composite_raster_name,
    coordinate_system_for_the_raster=spatial_ref,
    pixel_type="32_BIT_FLOAT",
    number_of_bands=1,
    mosaic_method="MEAN"
)

print(f"{composite_raster_name} made)


#=== STEP 3: Convert Fv to UVVR using formula UVVR = (1 / Fv) - 1 === 
composite_raster = arcpy.sa.Raster(composite_raster_path)
uvvr_from_fv = (1 / composite_raster) - 1

uvvr_output_path = os.path.join(CompositeFolder, "UVVR_from_Fv_Composite.tif")
uvvr_from_fv.save(uvvr_output_path)

print("Converted composite Fv to UVVR.")


# === STEP 4: Reclassify the composite ===
Band2Thresholds = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\1985to2022UVVRComposite\Band2Thresholds"
reclass_input = arcpy.sa.Raster(uvvr_output_path)
reclass_range = arcpy.sa.RemapRange([[0, 0.1300001, 0], [0.1300001, 1000000000, 1]])
reclassified = arcpy.sa.Reclassify(reclass_input, "VALUE", reclass_range, "NODATA")
reclass_output_path = os.path.join(Band2Thresholds, "013CompositeUVVR_from_Fv_Reclassified.tif")
reclassified.save(reclass_output_path)
print("Reclassified composite 0.13 raster.")

reclass_input = arcpy.sa.Raster(uvvr_output_path)
reclass_range = arcpy.sa.RemapRange([[0, 0.1500001, 0], [0.1500001, 1000000000, 1]])
reclassified = arcpy.sa.Reclassify(reclass_input, "VALUE", reclass_range, "NODATA")
reclass_output_path = os.path.join(Band2Thresholds, "015CompositeUVVR_from_Fv_Reclassified.tif")
reclassified.save(reclass_output_path)
print("Reclassified composite 0.15 raster.")

reclass_input = arcpy.sa.Raster(uvvr_output_path)
reclass_range = arcpy.sa.RemapRange([[0, 0.2000001, 0], [0.2000001, 1000000000, 1]])
reclassified = arcpy.sa.Reclassify(reclass_input, "VALUE", reclass_range, "NODATA")
reclass_output_path = os.path.join(Band2Thresholds, "020CompositeUVVR_from_Fv_Reclassified.tif")
reclassified.save(reclass_output_path)
print("Reclassified composite 0.20 raster.")

reclass_input = arcpy.sa.Raster(uvvr_output_path)
reclass_range = arcpy.sa.RemapRange([[0, 0.5000001, 0], [0.5000001, 1000000000, 1]])
reclassified = arcpy.sa.Reclassify(reclass_input, "VALUE", reclass_range, "NODATA")
reclass_output_path = os.path.join(Band2Thresholds, "050CompositeUVVR_from_Fv_Reclassified.tif")
reclassified.save(reclass_output_path)
print("Reclassified composite 0.50 raster.")

reclass_input = arcpy.sa.Raster(uvvr_output_path)
reclass_range = arcpy.sa.RemapRange([[0, 1.000001, 0], [1.000001, 1000000000, 1]])
reclassified = arcpy.sa.Reclassify(reclass_input, "VALUE", reclass_range, "NODATA")
reclass_output_path = os.path.join(Band2Thresholds, "100CompositeUVVR_from_Fv_Reclassified.tif")
reclassified.save(reclass_output_path)
print("Reclassified composite 1.00 raster.")





# Folder to save output points
AccAssPoints = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\ConfusionMatrix\AccAssPoints"
os.makedirs(AccAssPoints, exist_ok=True)

thresholds = ["013", "015", "020", "050", "100"]
for t in thresholds:
    in_class_data = os.path.join(Band2Thresholds, f"{t}CompositeUVVR_from_Fv_Reclassified.tif")
    out_points = os.path.join(AccAssPoints, f"c{t}FvAccAssPoints.shp")

    if arcpy.Exists(in_class_data):
        print(f"Creating Accuracy Assessment Points for threshold {t}...")
        arcpy.sa.CreateAccuracyAssessmentPoints(
            in_class_data=in_class_data,
            out_points=out_points,
            target_field="Classified",
            num_random_points="2000"
        )
        print(f"Saved: {out_points}")
    else:
        print(f"Missing raster: {in_class_data}")]




        
grnd_truth_raster = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\ConfusionMatrix\ChangeType0to4_5to8GrndTruth.tif"

for t in thresholds:
    points_path = os.path.join(AccAssPoints, f"c{t}FvAccAssPoints.shp")

    if arcpy.Exists(points_path):
        print(f"Extracting ground truth to points for {t}...")
        arcpy.sa.ExtractMultiValuesToPoints(
            in_point_features=points_path,
            in_rasters=[[grnd_truth_raster, "GrndTruth"]],
            bilinear_interpolate_values="NONE"
        )
        print(f"Extracted values to: {points_path}")
    else:
        print(f"Missing assessment points for {t}")




ConfusionOutputFolder = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\ConfusionMatrix"

for t in thresholds:
    points = os.path.join(AccAssPoints, f"c{t}FvAccAssPoints.shp")
    out_matrix = os.path.join(ConfusionOutputFolder, f"ConfusionMatrix_{t}.dbf")

    if arcpy.Exists(points):
        print(f"Creating confusion matrix for {t}...")
        arcpy.sa.ComputeConfusionMatrix(
            in_accuracy_assessment_points=points,
            out_confusion_matrix=out_matrix
        )
        print(f"Saved confusion matrix: {out_matrix}")
    else:
        print(f"Missing point shapefile for {t}")




output_folder = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\ConfusionMatrix"

# Reclassify 0–3 as 0, 4–8 as 1
remap_0to3_4to8 = RemapRange([[0, 3.9999, 0], [4, 8.0001, 1]])
reclass_0to3_4to8 = Reclassify(clip_raster, "VALUE", remap_0to3_4to8, "NODATA")
reclass_0to3_4to8.save(r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\ConfusionMatrix\ChangeType0to3_4to8GrndTruth.tif")
print("0 to 3 4 to 8 threshold remapped")
# Reclassify 0–5 as 0, 6–8 as 1
remap_0to5_6to8 = RemapRange([[0, 5.9999, 0], [6, 8.0001, 1]])
reclass_0to5_6to8 = Reclassify(clip_raster, "VALUE", remap_0to5_6to8, "NODATA")
reclass_0to5_6to8.save(r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\ConfusionMatrix\ChangeType0to5_6to8GrndTruth.tif")
print("0to5, 6to8 threshold remapped")



ChangeType0to4_5to8GrndTruth = r"C:\Users\user\Documents\ArcGIS\Projects\MyProject\UVVRandChangeType\ConfusionMatrix\ChangeType0to4_5to8GrndTruth.tif"
for t in thresholds:
    points_path = os.path.join(AccAssPoints, f"c{t}FvAccAssPoints.shp")

    if arcpy.Exists(points_path):
        print(f"Extracting ground truth to points for {t}...")
        arcpy.sa.ExtractMultiValuesToPoints(
            in_point_features=points_path,
            in_rasters=[[ChangeType0to4_5to8GrndTruth, "GrndTruth"]],
            bilinear_interpolate_values="NONE"
        )
        print(f"Extracted values to: {points_path} for 04 58")
    else:
        print(f"Missing assessment points for {t}")


