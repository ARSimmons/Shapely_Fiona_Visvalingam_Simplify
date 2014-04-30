
<html>
<head>
</head>
<body>
# Table of Contents
[Team Members](#team-members)

[Project Summary](#project-summary)

# <a name="team-members"></a>Team Members
* "Arielle Simmons" <ari.ucb.fire@gmail.com>
	- Data Engineer 
	
# <a name="project-summary"></a>Project Summary

Fiona (1.1+) and Shapely libraries used to simplify lines, multilines, polygons, and multipolygons by an area threshold.

The simplification algorithm is based off of M. Visvalingam and J.D. Whyatt's algorithm (1993). More details about the 
Visvalingam-Whyatt algorithm can be found here: http://www2.dcs.hull.ac.uk/CISRG/publications/DPs/DP10/DP10.html .

Key points to note:

	- As of 4/29/14 there are NO TOPOLOGY preserving rules in place (!!user beware!!)
	- Polygons which are smaller then the area threshold CAN BE deleted 
	- Lines preserve their beginning and end point, thus lines CANNOT BE DELETED. The beginning and end points of a line feature
	  are static throughout the simplification process.
	- threshold units are determined by shapefile map units.  
	- to run from command line: python simplify.py <input file> <output file> <threshold>

*NOTE: THIS PROJECT IS STILL in progress as of 4/29/2014*
 
</body>
</html>