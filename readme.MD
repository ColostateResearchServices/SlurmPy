## Create new conda environment and install dependencies
Run this to install all dependencies:
pip install -r requirements.txt

## To generate plots:
python monthly_usage_report.py

## To generate html report:
python generate_html_report.py

The html report is saved in the same directory as the plots

To configure plots and report, modify the scripts accordingly

Plots use "project_data.csv" for getting project titles. The data can be scraped from rcamp using another script or manually entered.

