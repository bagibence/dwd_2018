import os, zipfile, sys

try:
    import shutil #this module can get the terminal width
    console_width = shutil.get_terminal_size()[0]
except:
    print("Using 'shutil' failed, will assume console width of 80")
    console_width = 80 #default terminal width
progress_bar_width = console_width - 6

def unzip_folder(dir_name,verbose=True):
    extension = ".zip"
    for i, item in enumerate(os.listdir(dir_name)): # loop through items in dir
        if item.endswith(extension): # check for ".zip" extension
            file_name = dir_name + "/" + item
            #file_name = os.path.abspath(item) # get full path of files
            zip_ref = zipfile.ZipFile(file_name) # create zipfile object
            zip_ref.extractall(dir_name) # extract file to dir
            zip_ref.close() # close file
            os.remove(file_name) # delete zipped file
            if verbose:
                # what this actually does is to overwrite the last printout that was the statusbar
                # the ljust method pads the string with whitespaces, this is needed to remove
                # the previous statusbar
                sys.stdout.write(("unzipped {}".format(item)).ljust(console_width))
                sys.stdout.write('\n')
                sys.stdout.flush()
            perc = int(100*i/len(os.listdir(dir_name)))
            pperc = int(progress_bar_width*i/len(os.listdir(dir_name))) #percentage of progressbar thats done
            sys.stdout.write("[{}] {}%\r".format(('='*pperc).ljust(progress_bar_width), str(perc).zfill(2)))
            sys.stdout.flush()
    sys.stdout.write("[{}] {}%\n".format('='*(progress_bar_width-1), 100)) #write bar with 100%
    sys.stdout.flush()
