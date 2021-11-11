import pandas as pd

# import data from csv (bad way)
path = "/home/dominik/Downloads/interview_signup.csv"
data = pd.read_csv(path, low_memory=False)

# check dtypes
data.dtypes


# clean postcode
data["postcode"].value_counts()
data_cleaned = data.copy(deep=True)
data_cleaned["postcode"] = data.loc[:, "postcode"].replace(regex=['\.0'], value='')


