# Modeling County-level election data

This repo contains code for the Data Mining II project at Rowan University

## Dependencies 

Python 3.7+

```bash
pip3 install -r requirements.txt
```

## Predicting a County Result

```bash
# predict a 2020 result for a county using the specified model
./etl/classification.py -m [MODEL] -c [COUNTY FIPS]

# predict all 2020 results using specified model
./etl/classification.py -m [MODEL] -c "ALL"

# predict all 2020 results using specified model, output to csv
./etl/classification.py -m [MODEL] -c "ALL" -f /some/file/path.csv
```

## Models

To see the models being used, log into the ```sqlite``` database at ./etl/election.db 
and run the following query:

```select * from model```

To get descriptions of what each model actually is:

```select * from model_code```

## GIS
Unfortunately, the spatial data files eclipsed GitHub's file size limit. So contact
me if you want my local version of this repo that has these files.

When obtained, unzip ```./etl/spatial-data/predictions/county-predictions.zip``` and then open ```./etl/spatial-data/predictions/styled-predictions.qlr```