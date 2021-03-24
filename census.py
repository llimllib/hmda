#!/usr/bin/env python
# HMDA API docs: https://cfpb.github.io/hmda-platform/#hmda-api-documentation

# https://jtleider.github.io/censusdata/example1.html
import os

import numpy as np
import pandas as pd
import censusdata
import requests

pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.precision", 2)

# censusdata.search("acs5", 2015, "label", "race")
#
# leads to:
#
# In [5]: censusdata.printtable(censusdata.censustable('acs5', 2015, 'C02003'))
# Variable     | Table                          | Label                                                    | Type
# -------------------------------------------------------------------------------------------------------------------
# C02003_001E  | C02003.  Detailed Race         | Total:                                                   | int
# C02003_002E  | C02003.  Detailed Race         | Population of one race:                                  | int
# C02003_003E  | C02003.  Detailed Race         | !! Population of one race: White                         | int
# C02003_004E  | C02003.  Detailed Race         | !! Population of one race: Black or African American     | int
# C02003_005E  | C02003.  Detailed Race         | !! Population of one race: American Indian and Alaska Na | int
# C02003_006E  | C02003.  Detailed Race         | !! Population of one race: Asian alone                   | int
# C02003_007E  | C02003.  Detailed Race         | !! Population of one race: Native Hawaiian and Other Pac | int
# C02003_008E  | C02003.  Detailed Race         | !! Population of one race: Some other race               | int
# C02003_009E  | C02003.  Detailed Race         | Population of two or more races:                         | int
# C02003_010E  | C02003.  Detailed Race         | !! Population of two or more races: Two races including  | int
# C02003_011E  | C02003.  Detailed Race         | !! Population of two or more races: Two races excluding  | int
# C02003_012E  | C02003.  Detailed Race         | !! Population of two or more races: Population of two ra | int
# C02003_013E  | C02003.  Detailed Race         | !! !! Population of two or more races: Population of two | int
# C02003_014E  | C02003.  Detailed Race         | !! !! Population of two or more races: Population of two | int
# C02003_015E  | C02003.  Detailed Race         | !! !! Population of two or more races: Population of two | int
# C02003_016E  | C02003.  Detailed Race         | !! !! Population of two or more races: Population of two | int
# C02003_017E  | C02003.  Detailed Race         | !! !! Population of two or more races: Population of two | int
# C02003_018E  | C02003.  Detailed Race         | !! Population of two or more races: Population of three  | int
# C02003_019E  | C02003.  Detailed Race         | !! Population of two or more races: Population of four o | int
# -------------------------------------------------------------------------------------------------------------------
#
# there is also the B02001 (Race), B03002 (Hispanic or latino by race), and
# B25006 (race of householder) series; let's start by trying out the C02003
# series though

# note: how did I miss DP05_0031PE  | ACS DEMOGRAPHIC AND HOUSING ES | !! RACE One race?
# from https://jtleider.github.io/censusdata/example2.html
# might be a better one to use?
# statedata['percent_nonhisp_white'] = statedata['B03002_003E'] / statedata['B03002_001E'] * 100
# statedata['percent_nonhisp_black'] = statedata['B03002_004E'] / statedata['B03002_001E'] * 100
# statedata['percent_hispanic'] = statedata['B03002_012E'] / statedata['B03002_001E'] * 100

# the docs suggest looking up my county's fips code via:
# censusdata.geographies(censusdata.censusgeo([('state', '*')]), 'acs5', 2015) # states
# censusdata.geographies(censusdata.censusgeo([('state', '17'), ('county', '*')]), 'acs5', 2015) # county
#
# but I'm just going to grab it from wiki:
# https://en.wikipedia.org/wiki/List_of_United_States_FIPS_codes_by_county
# cumberland, me

# get all of the C02003 census variables
# census_variables = [key for key in censusdata.censustable("acs5", 2015, "C02003")]

# just grabbing the variables from the example instead of using my search
# from https://jtleider.github.io/censusdata/example2.html
census_variables = ["B03002_001E", "B03002_003E", "B03002_004E", "B03002_012E"]

cumberland_geo = censusdata.censusgeo(
    [("state", "23"), ("county", "005"), ("block group", "*")]
)

# this gets us a pandas table or data, 213 census tracts x 38 columns (19 race
# variables and 19 margins of error)
df = censusdata.download("acs5", 2015, cumberland_geo, census_variables)

df["percent_nonhisp_white"] = df["B03002_003E"] / df["B03002_001E"] * 100
df["percent_nonhisp_black"] = df["B03002_004E"] / df["B03002_001E"] * 100
df["percent_hispanic"] = df["B03002_012E"] / df["B03002_001E"] * 100

# pull geo from the index into columns
df["state"] = df.index.map(lambda x: dict(x.params())["state"])
df["county"] = df.index.map(lambda x: dict(x.params())["county"])
df["block group"] = df.index.map(lambda x: dict(x.params())["block group"])
df["census tract"] = df.index.map(lambda x: dict(x.params())["tract"])


def download_file(url, fname):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(fname, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return open(fname)


# action_taken
# Description: The action taken on the covered loan or application
# Values:
# 1 - Loan originated
# 2 - Application approved but not accepted
# 3 - Application denied
# 4 - Application withdrawn by applicant
# 5 - File closed for incompleteness
# 6 - Purchased loan
# 7 - Preapproval request denied
# 8 - Preapproval request approved but not accepted
# https://ffiec.cfpb.gov/documentation/2020/data-browser-filters/
fname = "data.csv"
if not os.path.isfile(fname):
    API = "https://ffiec.cfpb.gov/v2/data-browser-api"
    res = requests.get(f"{API}/view/csv?states=ME&years=2018&actions_taken=1,2,3,4,5")
    f = download_file(
        f"{API}/view/csv?states=ME&years=2018&actions_taken=1,2,3,4,5", fname
    )

# available columns:
# activity_year lei derived_msa-md state_code county_code census_tract
# conforming_loan_limit derived_loan_product_type derived_dwelling_category
# derived_ethnicity derived_race derived_sex action_taken purchaser_type
# preapproval loan_type loan_purpose lien_status reverse_mortgage
# open-end_line_of_credit business_or_commercial_purpose loan_amount
# loan_to_value_ratio interest_rate rate_spread hoepa_status total_loan_costs
# total_points_and_fees origination_charges discount_points lender_credits
# loan_term prepayment_penalty_term intro_rate_period negative_amortization
# interest_only_payment balloon_payment other_nonamortizing_features
# property_value construction_method occupancy_type
# manufactured_home_secured_property_type
# manufactured_home_land_property_interest total_units
# multifamily_affordable_units income debt_to_income_ratio
# applicant_credit_score_type co-applicant_credit_score_type
# applicant_ethnicity-1 applicant_ethnicity-2 applicant_ethnicity-3
# applicant_ethnicity-4 applicant_ethnicity-5 co-applicant_ethnicity-1
# co-applicant_ethnicity-2 co-applicant_ethnicity-3 co-applicant_ethnicity-4
# co-applicant_ethnicity-5 applicant_ethnicity_observed
# co-applicant_ethnicity_observed applicant_race-1 applicant_race-2
# applicant_race-3 applicant_race-4 applicant_race-5 co-applicant_race-1
# co-applicant_race-2 co-applicant_race-3 co-applicant_race-4
# co-applicant_race-5 applicant_race_observed co-applicant_race_observed
# applicant_sex co-applicant_sex applicant_sex_observed
# co-applicant_sex_observed applicant_age co-applicant_age
# applicant_age_above_62 co-applicant_age_above_62 submission_of_application
# initially_payable_to_institution aus-1 aus-2 aus-3 aus-4 aus-5
# denial_reason-1 denial_reason-2 denial_reason-3 denial_reason-4
# tract_population tract_minority_population_percent
# ffiec_msa_md_median_family_income tract_to_msa_income_percentage
# tract_owner_occupied_units tract_one_to_four_family_homes
# tract_median_age_of_housing_units
usecols = [
    "census_tract",
    "derived_ethnicity",
    "derived_race",
    "action_taken",
    "loan_type",
    "tract_population",
    "tract_minority_population_percent",
]
loandf = pd.read_csv(
    fname,
    usecols=usecols,
    dtype={
        # this doesn't work because the census tract is null sometimes (!)
        # "census_tract": pd.Int32Dtype()
    },
)

# here's how to show the null census tract rows that blow up the int conversion:
# loandf.loc[loandf['census_tract'].isnull()]
# So, let's drop null census tract rows, they're not useful to us.
# there are 297 rows iwth null census tracts out of 54594 rows, so we should end up with 54297 rows
#
# In [181]: test = loandf.dropna(subset=['census_tract'])
#
# In [182]: test.shape
# Out[182]: (54297, 7)
loandf = loandf.dropna(subset=["census_tract"])
loandf = loandf.astype({"census_tract": int})


# sometimes we get redirected to an s3 URL, if you redo a query
# $ curl 'https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?states=ME&years=2018&actions_taken=1,2,3,4,5'| head
#   % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
#                                  Dload  Upload   Total   Spent    Left  Speed
# 100   188    0   188    0     0    878      0 --:--:-- --:--:-- --:--:--   878
# This and all future requests should be directed to <a href="https://cfpb-hmda-public.s3.amazonaws.com/prod/data-browser/filtered-queries/26d4e98da72236de6733618cac2d8e95.csv">this URI</a>.10:25 AM threebody:~/adhoc/capabilities/hmdasprint

# ok, now I have two dataframes with the data I want! I have Maine census
# tracts and Maine loan data. Now I want to aggregate it by census block, and
# then map that

# oh hey I just realized that the HMDA data actually already aggregates
# minority percent and tract population! so all I have to do is use the HMDA
# data to make a map!
