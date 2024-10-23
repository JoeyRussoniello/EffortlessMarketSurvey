from ScraperFunctions.update_chromedriver import update_driver
from ScraperFunctions.survey import MarketSurvey
#Update the chrome drivers
update_driver('win64')

survey = MarketSurvey(headless = True, verbose = True, ncomps = 5) #Initialize Market Survey with parameter inputs

#Perform market survey on the properties and criteria given in input csv
survey.full_survey(input_path = r"Examples\ExamplePortfolio.csv",rollup = True)
#survey.full_survey(input_path = "Input.csv",rollup = True)
#Write the output to output.csv (ONLY APPEND TO COMPLETELY RESET DATA, IF NO FILE APPEND WILL STILL FUNCTION)
#survey.write_output(mode = "append",file_path = "Output.csv")
survey.write_output(mode = "append",file_path = r"Examples\PortfolioOutput.csv")