import argparse
import os
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("portfolio", help="(JSON file containing) portfolio to visualize")

    args = parser.parse_args()

    if os.path.isfile(args.portfolio) != True:
        sys.exit("failed to find portfolio file: '{}'".format(args.portfolio))

if __name__ == "__main__":
    main()
