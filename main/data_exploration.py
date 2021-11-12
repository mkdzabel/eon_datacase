import pandas as pd
import sqlite3
import numpy as np
import plotly.graph_objects as go
import re

# import data from csv (bad way)
path = "/home/dominik/Downloads/interview_signup.csv"
data = pd.read_csv(path, low_memory=False, encoding="utf-8")

# check dtypes
data.dtypes


# clean postcode
data["postcode"].value_counts()
data_cleaned = data.copy(deep=True)

# problem 1: zipcode needs to consist of 5 characters (digits)
data_cleaned["no_chars"] = data_cleaned["postcode"].str.len()
data_cleaned["no_chars"].value_counts()
df_problematic_zipcodes = data_cleaned.loc[data_cleaned["no_chars"] != 5, :]

# quick visualiation
fig = go.Figure(data=[go.Bar(name="No Digits",
                             x=np.sort(data_cleaned["no_chars"].unique()),
                             y=data_cleaned["no_chars"].value_counts().sort_index())])
fig.show(renderer="browser")


# problem 1a: some postcodes contain ".0", remove that
data_cleaned["postcode"] = data.loc[:, "postcode"].replace(regex=['\.0'], value='')
data_cleaned["no_chars_after_first_cleaning"] = data_cleaned["postcode"].str.len()

# still problematic
data_cleaned.loc[data_cleaned["no_chars_after_first_cleaning"] != 5, :]

# problem 1b: for eastern germany leading 0 is missing and has to be added
affectec_countries = ["Sachsen", "Thüringen", "Sachsen-Anhalt", "Brandenburg"]
mask = (data_cleaned["no_chars_after_first_cleaning"] == 4) & (data_cleaned["bundesland"].isin(affectec_countries))
data_cleaned.loc[mask, "postcode"] = '0' + data_cleaned.loc[mask, "postcode"]


# still problematic
data_cleaned["no_chars_after_second_cleaning"] = data_cleaned["postcode"].str.len()
still_problematic_2 = data_cleaned.loc[data_cleaned["no_chars_after_second_cleaning"] != 5, :]
print(f"number of remaining unclear cases {len(still_problematic_2)}")

# fix single case
special_customer = data_cleaned.loc[data_cleaned["no_chars_after_second_cleaning"] == 10, :]
identified_postcode = re.findall(r"\D(\d{5})\D", " "+str(special_customer["postcode"])+" ")
data_cleaned.loc[data_cleaned["no_chars_after_second_cleaning"] == 10, "postcode"] = identified_postcode[0]


# format date time of order_date
data_cleaned["order_date"] = pd.to_datetime(data_cleaned["order_date"])
data_cleaned.dtypes


# data cleaning product name
data_cleaned["original_product_name"].value_counts()
valid_products = ["E.ON STROM", "E.ON STROM 24", "E.ON STROM ÖKO", "E.ON STROM ÖKO 24", "E.ON STROM PUR"]
mask_problematic_products = ~data_cleaned["original_product_name"].isin(valid_products)
df_problematic_products = data_cleaned[mask_problematic_products]

# case 1: assume E.ON STROM Ã–KO == E.ON STROM ÖKO
data_cleaned.loc[data_cleaned["original_product_name"] == "E.ON STROM Ã–KO", "original_product_name"] = "E.ON STROM ÖKO"

# case 2: remove additional 24's
from collections import OrderedDict
mask_24 = data_cleaned["original_product_name"].str.contains("24")
data_cleaned.loc[mask_24, "original_product_name"] = (data_cleaned.loc[mask_24, "original_product_name"].str.split().apply(lambda x: OrderedDict.fromkeys(x).keys()).str.join(' '))
data_cleaned["original_product_name"].value_counts()

# case 3: assume E.ON STROM ÖO is typo
data_cleaned.loc[data_cleaned["original_product_name"] == "E.ON STROM ÖO", "original_product_name"] = "E.ON STROM ÖKO"
data_cleaned["original_product_name"].value_counts()






# Read sqlite query results into a pandas DataFrame and plot
con = sqlite3.connect("data/postcodes.db")
df_geo_data = pd.read_sql_query("SELECT * from postcodes", con)
con.close()

df_geo_data_wo_dups = df_geo_data.loc[~df_geo_data["zipcode"].duplicated(keep="first"), :]

data_cleaned_merged = data_cleaned.merge(right=df_geo_data_wo_dups[["zipcode", "name", "lat", "lon"]],
                                         how="left",
                                         left_on="postcode",
                                         right_on="zipcode")
