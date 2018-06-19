#!/usr/bin/env python3

import os
import sys
import getopt

from useftp import download_data
from unzip_all import unzip_folder

def get_data(userpath, historical, recent, hourly, verbose):
    #download the files
    print("getting data")
    download_data(userpath = userpath,
                  historical = historical,
                  recent = recent,
                  hourly = hourly,
                  verbose = verbose)

    #unzip the files
    print("unzipping data")
    if historical or recent:
        localdir = os.path.join(userpath,'pub','CDC','observations_germany',
                                'climate','daily','kl')
        if historical:
            unzip_folder(os.path.join(localdir, 'historical'),verbose=verbose)
        if recent:
            unzip_folder(os.path.join(localdir, 'recent'),verbose=verbose)

    if hourly:
        hour_folders = ["air_temperature", "cloud_type", "precipitation",
                        "pressure", "soil_temperature", "solar", "sun",
                        "visibility", "wind"]
        for folder in hour_folders:
            localdir = os.path.join(userpath, 'pub','CDC',
                                    'observations_germany','climate','hourly',
                                    folder)
            if folder!="solar":
                unzip_folder(os.path.join(localdir, 'historical'),
                            verbose=verbose)
                unzip_folder(os.path.join(localdir, 'recent'),verbose=verbose)
            else:
                unzip_folder(localdir)


def main():
    """
    This method is called if this file is executed.
    It takes commandline arguments and options that specify which data should
    be downloaded.
    """
    try:
        options, args = getopt.getopt(sys.argv[1:], "vgrsh", ["verbose",
                                                              "historical",
                                                              "recent",
                                                              "hourly",
                                                              "help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    verbose = False
    historical = False
    recent = False
    hourly = False
    help = False
    for opt, arg in options:
        if opt in ("-v", "--verbose"):
            verbose = True
            print('verbose is {}'.format(verbose))
        elif opt in ("-h", "--help"):
            help = True
            usage()
        elif opt in ("-g","--historical"):
            historical = True
            print('historical is {}'.format(historical))
        elif opt in ("-r", "--recent"):
            recent = True
            print('recent is {}'.format(recent))
        elif opt in ("-s","--hourly"):
            hourly = True
            print('hourly is {}'.format(hourly))
        else: assert False, "unhandled option"

    try: path = args[0]
    except IndexError:
        if not help:
            print("Must provide a path.")
            usage()
        sys.exit(2)

    get_data(userpath = path,
             historical = historical,
             recent = recent,
             hourly = hourly,
             verbose = verbose)

def usage():
    """
    Help function for the command line. Displays all the options/arguments and
    their use.
    """
    print("""Usage: 'python get_data -vgrsh path'\n
    arguments:\n
    \t path : the path where you want to save the data \n
    options:\n
    \t -v/--verbose : verbose mode
    \t -g/--historical : download historical data
    \t -r/--recent : download recent data
    \t -s/--hourly : download recent and historical hourly data
    \t -h/--help
    """)

if __name__ == "__main__":
    main()
