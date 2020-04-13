# coding: utf-8

import os
import sys
import dropbox

# get an access token, local (from) directory, and Dropbox (to) directory
# from the command-line example: 
# python upload_dbx.py key access _token /local/folder/to/upload /path/in/Dropbox 
access_token, local_directory, dropbox_destination = sys.argv[1:4]
dbx = dropbox.Dropbox(access_token)

# enumerate local files recursively
for root, dirs, files in os.walk(local_directory):

    for filename in files:

        # construct the full local path
        local_path = os.path.join(root, filename)

        # construct the full Dropbox path
        relative_path = os.path.relpath(local_path, local_directory)
        dropbox_path = os.path.join(dropbox_destination, relative_path)

        # upload the file
        print(local_path)
        try:
                with open(local_path, 'rb') as f:
                        dbx.files_upload(f.read(), dropbox_path)
                print('try success:', local_path)
        except:
                print('except:  ', local_path)
                continue

