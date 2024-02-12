# BLS-CPI-Forecast-Model
This is a model I developed to forecast the official BLS YoY CPI reading using Truflation's YoY CPI data. I first developed and used this model in excel but decided to rewrite it using Python for others to integrate into any projects they are working on, or tweak it to attempt to produce better results. The accuracy of the model has been +/- 0.3% since May 2022.

# CPI Data Analysis Tool

This tool fetches CPI (Consumer Price Index) data, processes the data, and generates a forecast based on user inputs. It's built with Python and uses several libraries to handle HTTP requests, data manipulation, and date calculations.

## Requirements

To run this script, you'll need Python installed on your system along with the following packages:
- `requests`
- `pandas`

These can be installed via pip if you don't already have them:

```bash
pip install requests pandas
