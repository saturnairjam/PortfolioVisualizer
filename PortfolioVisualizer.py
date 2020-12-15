import argparse
import json
import jsonschema
import os
import sys

from jsonschema import validate

class AssetClass:

    MonthOnMonthGrowth = []

    def __init__(self, name, startYear, startMonth):
        self.Name = name
        self.StartYear = startYear
        self.StartMonth = startMonth

    def CalculateMonthOnMonthGrowth(self, navList):
        self.MonthOnMonthGrowth.clear()
        for i in range(len(navList) - 1):
            self.MonthOnMonthGrowth.append((navList[i+1] / navList[i]) - 1)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("portfolio", help="(JSON file containing) portfolio to visualize")

    # parse command-line arguments

    args = parser.parse_args()

    # check if specified portfolio file exists

    if os.path.isfile(args.portfolio) != True:
        sys.exit("failed to find portfolio file: '{}'".format(args.portfolio))

    # load portfolio JSON from file

    with open(args.portfolio) as f:
        try:
            portfolio = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in portfolio file: {}".format(e))

    # load portfolio schema JSON from file

    with open('Data/Schemas/PortfolioSchema.json') as f:
        try:
            portfolioSchema = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in portfolio schema file: {}".format(e))

    # validate portfolio JSON against schema

    try:
        validate(instance = portfolio, schema = portfolioSchema)
    except jsonschema.exceptions.ValidationError as e:
        sys.exit("portfolio schema invalid: {}".format(e))

    print("portfolio loaded & validated: {}".format(portfolio['Name']), flush=True)

    # load asset class schema JSON from file

    with open('Data/Schemas/AssetClassSchema.json') as f:
        try:
            assetClassSchema = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in asset class schema file: {}".format(e))

    # iterate over all JSON files in 'asset classes' folder

    assetClassesDirectory = 'Data/AssetClasses'

    assetClasses = {}

    for filename in os.listdir(assetClassesDirectory):

        # load asset class JSON from file

        with open(os.path.join(assetClassesDirectory, filename)) as f:
            try:
                assetClass = json.load(f)
            except ValueError as e:
                sys.exit("invalid JSON in asset class file: {}".format(e))

        # validate asset class JSON against schema

        try:
            validate(instance = assetClass, schema = assetClassSchema)
        except jsonschema.exceptions.ValidationError as e:
            sys.exit("asset class schema invalid: {}".format(e))

        print("asset class loaded & validated: {}".format(assetClass['Name']), flush=True)

        assetClassObject = AssetClass(assetClass['Name'], assetClass['StartYear'], assetClass['StartMonth'])
        assetClassObject.CalculateMonthOnMonthGrowth(assetClass['NetAssetValueArray'])

        # add asset class to asset classes dictionary

        assetClasses[assetClass['Name']] = assetClassObject

    # verify that each asset class in portfolio exists

    for i in portfolio['AssetClassWeights']:
        if i[0] not in assetClasses:
            sys.exit("invalid asset class: '{}'".format(i[0]))

if __name__ == "__main__":
    main()
