from ftplib import FTP
import os
import sys
import time

#prettify the progressbar
try:
    import shutil #this module can get the terminal width
    console_width = shutil.get_terminal_size()[0]
except:
    print("Using 'shutil' failed, will assume console width of 80")
    console_width = 80 #default terminal width
progress_bar_width = console_width - 6

server = "ftp-cdc.dwd.de"

def get_modification_time(ftp):
    """
    For a directory on the server get a list of filenames and the modification
    date. Time format is like 'Tue May 29 10:03:06 2018'
    """
    mtimes = list()
    filenames = ftp.nlst(foldername)
    for i, filename in enumerate(filenames):
        mtimes.append(filename,time.ctime(os.path.getmtime(filename)))
    return mtimes

def compare_modification_times(mtimes,filepath):
    """
    Write the filenames and date modified of the contents of a directory on the
    server to a file for comparison later.
    """
    # with open filepath as save_file:
    pass

def open_mod_dates(filename):
    # open the file containing the modified stamps of all the files that have
    # already been downloaded
    pass

def get_mod_date():
    # get modified stamp of a file thats is candidate for download
    pass

def save_mod_dates(mod_dates,filename):
    # write list of mod dates to file
    pass

def download_folder(ftp, userpath,foldername, verbose):
    filenames = ftp.nlst(foldername)
    # mod_dates = open_mod_dates()
    for i, filename in enumerate(filenames):
        # if mod_dates[filename] == get_mod_date(): continue
        local_filename = os.path.join(userpath, filename)
        file = open(local_filename, 'wb')
        ftp.retrbinary('RETR '+ filename, file.write)
        file.close()
        if verbose:
            # what this actually does is to overwrite the last printout that was the statusbar
            # the ljust method pads the string with whitespaces, this is needed to remove
            # the previous statusbar
            sys.stdout.write(("downloaded {}".format(filename)).ljust(console_width))
            sys.stdout.write('\n')
            sys.stdout.flush()
        perc = int(100*i/len(filenames))
        pperc = int(progress_bar_width*i/len(filenames)) #percentage of progressbar thats done
        sys.stdout.write("[{}] {}%\r".format(('='*pperc).ljust(progress_bar_width), str(perc).zfill(2)))
        sys.stdout.flush()
    sys.stdout.write("[{}] {}%\n".format('='*(progress_bar_width-1), 100)) #write bar with 100%
    sys.stdout.flush()
    save_mod_dates(mod_dates,os.path.join(userpath,'mod_dates'))

def delete_folder(folder, verbose = True):
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    if verbose:
        print("deleted contents of folder "+folder)

def download_data(userpath, historical, recent, hourly, verbose):
    ftp = FTP(server)
    ftp.login()
    if verbose: print("logged in to server {}".format(server))
    if historical:
        if verbose: print("gonna get historical data")
        get_historical_data(userpath,ftp,verbose)
    if recent:
        if verbose: print("gonna get recent data")
        get_recent_data(userpath,ftp,verbose)
    if hourly:
        if verbose: print("gonna get hourly data")
        get_hourly_data(userpath,ftp,verbose)

def get_historical_data(userpath,ftp,verbose):
    histpath = os.path.join(userpath,'pub/CDC/observations_germany/climate/daily/kl/historical/')
    if verbose: print('directory for historical data: {}'.format(histpath))
    if not os.path.isdir(histpath):
        if verbose: print("directory did not exist, it will be created")
        os.makedirs(histpath)
        download_folder(ftp, userpath,'pub/CDC//observations_germany/climate/daily/kl/historical', verbose=verbose)

def get_recent_data(userpath,ftp,verbose):
    recentpath = os.path.join(userpath,'pub/CDC/observations_germany/climate/daily/kl/recent/')
    if verbose: print("directory for recent data: {}".format(recentpath))
    if not os.path.isdir(recentpath):
        if verbose: print("directory did not exist, it will be created")
        os.makedirs(recentpath)
    else:
        if verbose: print("deleting previous version of recent data")
        delete_folder(recentpath, verbose = True)

    download_folder(ftp, userpath, 'pub/CDC//observations_germany/climate/daily/kl/recent',verbose=verbose)

def get_hourly_data(userpath,ftp,verbose=True):
    hour_folders = ["air_temperature", "cloud_type", "precipitation", "pressure", "soil_temperature", "sun", "visibility", "wind"]
    if verbose: print("will now download hourly predictions")
    for folder in hour_folders:
        if verbose: print("now downloading {}".format(folder))
        hourpath = os.path.join('pub/CDC//observations_germany/climate/hourly/', folder)
        if verbose: print("the data will be saved in {}".format(hourpath))
        hourpath_hist = os.path.join(userpath, hourpath, 'historical')
        hourpath_recent = os.path.join(userpath, hourpath, 'recent')

        if not os.path.isdir(hourpath_hist):
            if verbose: print("downloading historical hourly data")
            os.makedirs(hourpath_hist)
            download_folder(ftp, userpath, hourpath+'/historical',verbose=verbose)

        if not os.path.isdir(hourpath_recent):
            if verbose: print("downloading recent hourly data")
            os.makedirs(hourpath_recent)
        else:
            if verbose: print("deleting previous version of recent data")
            delete_folder(hourpath_recent, verbose = True)

        download_folder(ftp, userpath, hourpath+'/recent',verbose=verbose)

    solarpath = 'pub/CDC/observations_germany/climate/hourly/solar'
    sp = os.path.join(userpath, solarpath)
    if verbose: print("now downloading solar hourly data into {}".format(solarpath))

    if not os.path.isdir(sp):
        if verbose: print("solarpath did not exist so it will be created")
        os.makedirs(sp)

    else:
        if verbose: print("deleting previous version of solar data")
        delete_folder(sp, verbose = True)
    download_folder(ftp, userpath, solarpath, verbose=verbose)
