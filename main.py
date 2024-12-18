"""
Import json to read the `config.json` file
Import update_driver function, ensuring that web-scraping driver is up to date
Import Market Survey class to manage the web-scraper
"""
import json
from ScraperFunctions.update_chromedriver import update_driver
from ScraperFunctions.survey import MarketSurvey, MarketSurveyParallel

#Get a config file from `config.json`
with open("config.json", "r",encoding='utf-8') as r:
    config = json.load(r)

#Read input variables from the config file
PLATFORM = config['platform']
HEADLESS = config['headless']
VERBOSE = config['verbose']
NCOMPS = config['ncomps']
INPUT_PATH = config['input_path']
ROLLUP = config['rollup']
OUTPUT_PATH = config['output_path']
OUTPUT_MODE = config['output_mode']
PARALLEL = config['parallel_members']

#Update the chrome drivers
update_driver(PLATFORM)
if PARALLEL == 0 or PARALLEL == 1:
    #Perform Market Survey Without Any Parallelism
    survey = MarketSurvey(headless = HEADLESS, verbose = VERBOSE, ncomps = NCOMPS)
    survey.full_survey(input_path = INPUT_PATH,rollup = ROLLUP)
    survey.to_csv(mode = OUTPUT_MODE,file_path = OUTPUT_PATH)
else:
    #Perform parallel Market Surveys. More Computationally demanding
    survey = MarketSurveyParallel(headless = HEADLESS,verbose = VERBOSE, ncomps = NCOMPS)
    survey.full_survey_parallel(input_path = INPUT_PATH,rollup = ROLLUP,max_workers=PARALLEL)
    survey.to_csv(OUTPUT_MODE,OUTPUT_PATH)
