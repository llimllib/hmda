SHAPEFILE=maine_shapefile/cb_2018_23_tract_500k.shp

maine.json: $(SHAPEFILE) install
	# https://github.com/mattijn/topojson/issues/120
	echo "this script throws an AttributeError, but still works:"
	python convert.py $(SHAPEFILE) maine.json

$(SHAPEFILE):
	if [ ! -f cb_2018_23_tract_500k.zip ]; then wget https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_23_tract_500k.zip; fi
	unzip -d maine_shapefile cb_2018_23_tract_500k.zip

.PHONY: install
install:
	pip install topojson simplification altair geopandas ipywidgets pyshp geojson fiona vincent
