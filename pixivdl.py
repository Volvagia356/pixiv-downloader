#!/usr/bin/env python

import os,sys
import urllib2
import pickle
from pixiv_api import Pixiv

config_dir=os.environ.get("XDG_CONFIG_HOME",os.path.expanduser("~/.config"))

def print_welcome():
    print 'pixiv Downloader (C) 2013 Volvagia356'
    print ''

def print_usage():
    print "Usage: {} artist_id|tag [directory]".format(sys.argv[0].split('/')[-1])
    print ''

def check_version():
    if sys.hexversion<0x02070000:
        print "Python 2.7 is required!"
        print ''
        sys.exit()

def get_session_config():
    session_file=config_dir+"/pixivdl/session"
    try:
        session_id=open(session_file).readline().strip()
        return session_id
    except IOError:
        print "Login information not found."
        print "Please refer to 'Logging in' in README"
        print ''

def download_work(work,prefix):
    requests=work.get_files()
    page=0
    for request in requests:
        if len(requests)>1:
            filename="{}_p{}.{}".format(work.id,page,work.format)
            page+=1
        else:
            filename="{}.{}".format(work.id,work.format)
        full_path=prefix+'/'+filename
        if os.path.isfile(full_path):
            print filename, "already exists."
            continue
        print "Downloading", filename
        try:
            img=urllib2.urlopen(request)
            f=open(full_path,'wb')
            f.write(img.read())
        except urllib2.HTTPError as e:
            print e
            print request.get_full_url()

def main():
    print_welcome()
    check_version()
    if len(sys.argv)<2:
        print_usage()
        sys.exit()
    input_str=sys.argv[1]
    if len(sys.argv)==3:
        directory=sys.argv[2]
    else:
        directory='.'
    session_id=get_session_config()
    p=Pixiv(session_id)
    if input_str.isdigit():
        works=p.get_works_all(input_str)
        total_works = works
        for work in works:
            download_work(work,directory)
    else:
        total_works = []
        for works in p.get_tagged_all(input_str):
            total_works += works
            for work in works:
                download_work(work,directory)
    pickle.dump(total_works,open(directory+"/metadata.pickle",'wb'))
    print ''

if __name__=="__main__":
    main()