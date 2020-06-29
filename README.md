# WaterUP API code repository 

This repository contains scripts for WaterUP front end & API, pickled XGBoost model for 
grapevine trained on weather, soil and micro-tensiometer data at Mt. George, Napa Valley.


## Summary

  - [Getting Started](#getting-started)
  - [Deployment](#deployment)
  - [Authors](#authors)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)

## Getting Started



### Prerequisites

To get started you need to install Python 3.7 and create an virtual environment.
The prequirments.txt file contains all the PyPi packages to install. 

To install:

    pip install -r requirments.txt



## Testing

To run this API on your local machine, go to api directory, in the command line enter: 

     uvicorn main:app --reload

Then in your browser, you can visit the front end at port 8000

     localhost:8000

For water stress forecast, go to the endpoint: 

     /forecast/period=[time period of prediction to return]


## Authors

  - **Hanwen Lu**

### data sources:
  - weather data: CIMIS: https://cimis.water.ca.gov/WSNReportCriteria.aspx
  - soil data: MeteoBlue history+ service: https://www.meteoblue.com/en/historyplus
  - water potential/stress ground truth: FloraPulse: https://www.florapulse.com/
  
