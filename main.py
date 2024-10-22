from update_chromedriver import update_driver
from ClassObject import MarketSurvey

#Update the chrome drivers
update_driver('win64')

survey = MarketSurvey(headless = True, verbose = True, ncomps = 5)
#Do a market survey on the properties and criteria given in input csv
survey.full_survey(input_path = r".\Input.csv",rollup = True)
#Write the output to output.csv (ONLY APPEND TO RESET DATA, IF NO FILE APPEND WILL STILL FUNCTION)
survey.write_output(mode = "append",file_path = r".\Output.csv")