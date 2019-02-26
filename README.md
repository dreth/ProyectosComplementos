# ProyectosComplementos
Proyectos realizados en complementos de mat financiera.

Explanation of each file in the master branch:

---> intereses.py
It's a very basic and simple set of functions to calculate the end result of an investment depending on the type of interest used.

Probably doesn't have annotations 'cause I was lazy.

---> symbolgetinfo.py
Using a python library called alpha_vantage I obtain information about the daily stock price of a company and using a montecarlo
simulation we calculate the estimated price of the stock up to a certain date set by the user.

It also provides a histogram at the end separated by price sections to determine the probability of obtaining a specific price
all distributed normally.

Has annotations in Spanish.

---> Proyeccion de reservas nacionales.py
uses the two files tasaref6m.csv and datainflmens.csv to provide the necessary data for the script, these two should be in the
folder where the script is before running it.

Calculates the value of the reserves of the central bank of the Dominican Republic utilizing multiple regression of 7 variables
that are relevant to DR's investments.

Uses an ARIMA model to estimate these variables and then applies the multiple regression on the information provided by the 
ARIMA estimation.

The ARIMA is calculated by providing all the possible parameters for the function and then selecting the model with the best AIC
which is a coefficient that according to wikipedia: "The Akaike information criterion (AIC) is an estimator of the relative quality
of statistical models for a given set of data."
