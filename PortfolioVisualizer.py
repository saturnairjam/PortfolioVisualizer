import argparse
import json
import jsonschema
import os
import sys

from jsonschema import validate

class AssetClass:

    MonthOnMonthGrowth = []

    def __init__(self, assetClassJson):
        self.Name = assetClassJson['Name']
        self.StartDate = (assetClassJson['StartYear'] * 12) + (assetClassJson['StartMonth'] - 1)

        # calculate month-on-month growth from NAV array

        self.MonthOnMonthGrowth.clear()
        navList = assetClassJson['NetAssetValueArray']
        for i in range(len(navList) - 1):
            self.MonthOnMonthGrowth.append((navList[i+1] / navList[i]) - 1)

class Portfolio:

    def __init__(self, portfolioJson, startDate):

        self.Name = portfolioJson['Name']
        self.AssetClassWeights = portfolioJson['AssetClassWeights']
        self.RebalancingStrategy = portfolioJson['RebalancingStrategy']
        self.MonthsBetweenRebalancing = portfolioJson['MonthsBetweenRebalancing']
        self.RebalancingThreshold = portfolioJson['RebalancingThreshold']
        self.StartDate = startDate

        # normalize asset class weights

        totalWeight = 0
        for i in self.AssetClassWeights:
            totalWeight += i[1]
        for i in self.AssetClassWeights:
            i[1] = i[1] / totalWeight

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
            portfolioJson = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in portfolio file: {}".format(e))

    # load portfolio schema JSON from file

    with open('Data/Schemas/PortfolioSchema.json') as f:
        try:
            portfolioSchemaJson = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in portfolio schema file: {}".format(e))

    # validate portfolio JSON against schema

    try:
        validate(instance = portfolioJson, schema = portfolioSchemaJson)
    except jsonschema.exceptions.ValidationError as e:
        sys.exit("portfolio schema invalid: {}".format(e))

    print("portfolio loaded & validated: {}".format(portfolioJson['Name']), flush=True)

    # load asset class schema JSON from file

    with open('Data/Schemas/AssetClassSchema.json') as f:
        try:
            assetClassSchemaJson = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in asset class schema file: {}".format(e))

    # iterate over all JSON files in 'asset classes' directory

    assetClassesDirectory = 'Data/AssetClasses'

    assetClasses = {} # asset class dictionary

    for filename in os.listdir(assetClassesDirectory):

        # load asset class JSON from file

        with open(os.path.join(assetClassesDirectory, filename)) as f:
            try:
                assetClassJson = json.load(f)
            except ValueError as e:
                sys.exit("invalid JSON in asset class file: {}".format(e))

        # validate asset class JSON against schema

        try:
            validate(instance = assetClassJson, schema = assetClassSchemaJson)
        except jsonschema.exceptions.ValidationError as e:
            sys.exit("asset class schema invalid: {}".format(e))

        # add asset class to dictionary only if it is part of portfolio

        found = False

        for i in portfolioJson['AssetClassWeights']:
            if assetClassJson['Name'] == i[0]:
                found = True
                break

        if found:
            assetClasses[assetClassJson['Name']] = AssetClass(assetClassJson)
            print("asset class validated & loaded: {}".format(assetClassJson['Name']), flush=True)

    # verify that each asset class in portfolio exists
    # also compute portfolio start date (most recent start date of all asset classes in portfolio)

    portfolioStartDate = 0

    for i in portfolioJson['AssetClassWeights']:

        assetClassName = i[0]

        if assetClassName not in assetClasses:
            sys.exit("invalid asset class: '{}'".format(assetClassName))

        if assetClasses[assetClassName].StartDate > portfolioStartDate:
            portfolioStartDate = assetClasses[assetClassName].StartDate

    print("'{}' start date: {}-{}".format(portfolioJson['Name'], portfolioStartDate // 12, (portfolioStartDate % 12) + 1), flush=True)

    portfolioObject = Portfolio(portfolioJson, portfolioStartDate)

if __name__ == "__main__":
    main()
