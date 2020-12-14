import argparse
import json
import jsonschema
import os
import sys

from jsonschema import validate

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
            portfolio_schema = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in portfolio schema file: {}".format(e))

    # validate portfolio JSON against schema

    try:
        validate(instance = portfolio, schema = portfolio_schema)
    except jsonschema.exceptions.ValidationError as e:
        sys.exit("portfolio schema invalid: {}".format(e))

    # load asset class schema JSON from file

    with open('Data/Schemas/AssetClassSchema.json') as f:
        try:
            asset_class_schema = json.load(f)
        except ValueError as e:
            sys.exit("invalid JSON in asset class schema file: {}".format(e))

    # iterate over all JSON files in 'asset classes' folder

    asset_classes_directory = 'Data/AssetClasses'

    asset_classes = {}

    for filename in os.listdir(asset_classes_directory):

        # load asset class JSON from file

        with open(os.path.join(asset_classes_directory, filename)) as f:
            try:
                asset_class = json.load(f)
            except ValueError as e:
                sys.exit("invalid JSON in asset class file: {}".format(e))

        print(asset_class['Name'], flush=True)

        # validate asset class JSON against schema

        try:
            validate(instance = asset_class, schema = asset_class_schema)
        except jsonschema.exceptions.ValidationError as e:
            sys.exit("asset class schema invalid: {}".format(e))

        # add asset class to asset classes dictionary

        asset_classes[asset_class['Name']] = asset_class

    # verify that each asset class in portfolio exists

    for i in portfolio['AssetClassWeights']:
        if i[0] not in asset_classes:
            sys.exit("invalid asset class: '{}'".format(i[0]))

if __name__ == "__main__":
    main()
