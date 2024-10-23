## EffortlessMarketSurvey
# Project Description
This project is a real-estate web scraper designed to extract compset data from apartments.com. It uses requests and Selenium to automate the process of collecting and parsing data for an input area to streamline the Market Survey process and make competitor comparison easy, efficient, and free. The data is saved into Outputs.csv by default, but export paths can be changed in the main.py function.

# Features
- Dynamic Competitor Fetching/Filtering from an apartments.com search
- Automatic data collection with customizable compset sizes
- Built-in data formatting procedures w/ two options: 
    - Data roll-up condensing apartment.com listings into smaller, competitor descriptions (useful for large portfolios)
    - Individual Unit Availability list (useful for small portfolios to see the niche details)
# Requirements 
The following dependencies must be installed to run the project:
    beautifulsoup4==4.12.0
    requests==2.31.0
    pandas==2.1.1
    selenium==4.14.0
    numpy==1.26.0
You can install the required packages by running

``` bash
pip install -r requirements.txt
```

# Installation
1. Clone this repository
``` bash
git clone https://github.com/JoeyRussoniello/EffortlessMarketSurvey
```
2. Navigate to this repository
``` bash
cd EffortlessMarketSurvey
```
3. Install the required python packages
``` bash
pip install -r requirements.txt
```