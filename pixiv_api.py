import urllib
import urllib2
import csv
import random

base_url="http://spapi.pixiv.net/"
attributes=['id', 'artist_id', 'format', 'title', 'img_folder', 'artist_name',
            'thumbnail_url', '', '', 'preview_url', '', '', 'upload_time', 'tags',
            'application', 'ratings', 'total_rating', 'views', 'description',
            'novel_pages', '', '', '', '', 'artist_nickname', '', '', '',
            '', 'artist_avatar_url', '']

class Work:
    def __init__(self,line):
        self.line=line
        for i in range(len(line)):
            if attributes[i]=='' : continue
            else: setattr(self,attributes[i],line[i])
        self.img_folder=self.img_folder.zfill(2)
    
    def get_full_url(self,page=None):
        single_fmt="http://i{}.pixiv.net/img{}/img/{}/{}.{}"
        if int(self.id)>11320000: #ID 11320066 uses new URL, 11319887 uses old URL, 11319948 uses old URL, but site thinks it uses new URL.
            novel_fmt="http://i{}.pixiv.net/img{}/img/{}/{}_big_p{}.{}"
        else:
            novel_fmt="http://i{}.pixiv.net/img{}/img/{}/{}_p{}.{}"
        if len(self.preview_url.split('/')[-1].split('_'))==3:
            private_salt=self.preview_url.split('/')[-1].split('_')[1]
            work_id="{}_{}".format(self.id,private_salt)
        else:
            work_id=self.id
            
        if page==None:
            return single_fmt.format(random.choice([1,2]),self.img_folder,self.artist_nickname,work_id,self.format)
        else:
            return novel_fmt.format(random.choice([1,2]),self.img_folder,self.artist_nickname,work_id,page,self.format)
    
    def get_files(self):
        files=[]
        if self.novel_pages=='':
            request=urllib2.Request(self.get_full_url(),headers={'Referer': "http://www.pixiv.net/"})
            files.append(request)
        else:
            for i in range(int(self.novel_pages)):
                request=urllib2.Request(self.get_full_url(i),headers={'Referer': "http://www.pixiv.net/"})
                files.append(request)
        return files

class Pixiv:
    def __init__(self,session_id=''):
        self.set_session_id(session_id)
    
    def set_session_id(self,session_id=''):
        self.session_id=session_id
    
    def make_request(self,url,query={}):
        query["PHPSESSID"]=self.session_id
        query_string=urllib.urlencode(query)
        url=base_url+url+"?"+query_string
        return urllib2.urlopen(url)
    
    def get_works_page(self,member_id,page=1):
        query={
            'id': member_id,
            'p': page,
        }
        data=self.make_request("iphone/member_illust.php",query)
        lines=csv.reader(data)
        works=[]
        for line in lines:
            works.append(Work(line))
        return works
        
    
    def get_works_all(self,member_id):
        page=1
        works=[]
        while True:
            current_works=self.get_works_page(member_id,page)
            if len(current_works)==0: break
            works.extend(current_works)
            page+=1
        return works