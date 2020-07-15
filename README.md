# WaterUP API code repository 

This repository contains scripts for WaterUp front end, API and the ML model for 
grapevine trained on weather, soil and micro-tensiometer data at Mt. George, Napa Valley.
You can access this api from the following url: http://hanweninsightproject.xyz/


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

To install, go to api folder directory:

    pip install -r requirments.txt

## Deployment

### Modeling

The current water stress inference model uses XGBoost regression tree trained on weather, soil and water stress dataset from grapevine in Napa Valley, CA from May 2019 to Dec 2019 during the growing season. This model is validated with hold out test set from May to June 2020. The water stress of model prediction and test are as shown:

![train_vs_test](https://user-images.githubusercontent.com/54079574/87502673-259d0a00-c630-11ea-97e2-c37362680384.png)


And the daily maximum stress are as shown:

![daily_max_train_vs_test](https://user-images.githubusercontent.com/54079574/87502757-73b20d80-c630-11ea-9c4b-0373d32a17a7.png)

### Testing

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
  
### Disclaimers
  - The real time water stress prediction shown in this codebase is a dummy value for grapevine data from California over the period from 05-01-2019 to 06-01-2020. Due to the prepriotary water stress data ownership by FloraPulse, only historical water stress data are included. 
  - The weather and soil data from MeteoBlue is not free! Sincce I did not pay for the forecast service, the inference shown on the website is a prediction with weather and soil data from the exact same time from the previous year. The actual real time inference is not available
  - This model has not been trained on water stress data from other speices or on other geo-locations, the water stress inference should not be applied to other species. 
  
