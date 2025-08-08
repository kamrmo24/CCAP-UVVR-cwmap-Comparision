This code is mostly for arcpy (maybe a little bit of matlab). I am not sure if one can use arcpy code without the arcgis pro license. I've been using this in arcgis pro in their python jupyter notebook environment. 

Get Dr. Di Vittorio's cwmap and changetype.tif files here: https://zenodo.org/records/13525004

Get uvvr files here: https://www.sciencebase.gov/catalog/item/668569d6d34e8a8b016cd00d

Get CCAP files here: https://www.sciencebase.gov/catalog/item/668569d6d34e8a8b016cd00d (it seems they have recently added files for 1975, 1985, and 1992)

Class codes for Dr. Di Vittorio
Wetland Class Labels  (cwmap_YYYY.tif)
Label
Class
1
Water
2
Emergent Wetland
3
Forest/Scrub Wetland 
4
Other (agricultural, grassland, barren land, developed land)
11
Mixed Water and Emergent Wetland
12
Mixed Water and Forest/Scrub Wetland
13
Mixed Water and Other
14
Mixed Emergent and Forest/Scrub Wetland
15
Mixed Emergent Wetland and Other
16
Mixed Forest/Scrub Wetland and Other


Change Type Labels and Explanation (changeType.tif)
Label
Short Description
Explanation
0
No changes
No transitions in entire time series.
1
Mixed change - temporary
Transition between full and mixed class. Class at the beginning and end match.
2
Mixed change - permanent
Transition between full class and mixed class. Class at the beginning and end are different.
3
Gradual full change - temporary
Full class transition with a mixed class in between. Class at beginning and end match.
4
Gradual full change - permanent
Full class transition with a mixed class in between. Class at beginning and end are different.
5
Abrupt change - temporary
Full class transition with no mixed class in between. Class at beginning and end match.
6
Abrupt change - permanent
Full class transition with no mixed class in between. Class at beginning and end are different.
7
Abrupt and gradual change - temporary
Both gradual and abrupt changes are present. Class at beginning and end match.
8
Abrupt and gradual change - permanent
Both gradual and abrupt changes are present. Class at beginning and end are different.

