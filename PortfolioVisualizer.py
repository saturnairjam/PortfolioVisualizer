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
        portfolio = json.load(f)

    # load portfolio schema JSON from file

    with open('Data/Schemas/PortfolioSchema.json') as f:
        portfolio_schema = json.load(f)

    # validate portfolio JSON against schema

    try:
        validate(instance = portfolio, schema = portfolio_schema)
    except jsonschema.exceptions.ValidationError as err:
        sys.exit("portfolio schema invalid: {}".format(err))

if __name__ == "__main__":
    main()
