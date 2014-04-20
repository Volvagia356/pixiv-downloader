#!/usr/bin/env python

import os,sys
import pickle
import threading
from Queue import Queue
from pixiv_api import Pixiv
import pixivdl
import Tkinter
import ttk
import tkFileDialog
import tkMessageBox

class Application(Tkinter.Frame):
    def __init__(self,master=None):
        Tkinter.Frame.__init__(self,master)
        master.title("pixiv Downloader GUI")
        master.resizable(0,0)
        self['padx']=10
        self['pady']=10
        self.pack()
        self.create_widgets()
        self.cancel_download=threading.Event()
        self.event_queue=Queue()
        sys.stdout=OutputHandler(self,sys.stdout)
        pixivdl.print_welcome()
        self.state="waiting"
    
    def create_widgets(self):
        self.pack({'side':'top', 'fill':'x', 'expand':1})
        self.target_field=TargetField(self)
        self.directory_field=DirectoryField(self)
        self.progress_indicator=ProgressIndicator(self)
    
    def download(self):
        thread_args=(self.target_field.field.get(),self.directory_field.field.get(),self)
        thread=threading.Thread(target=download_thread,args=thread_args)
        thread.daemon=True
        thread.start()
    
    def set_state(self,state):
        self.state=state
        if state=="waiting":
            self.target_field.field['state']='normal'
            self.target_field.button['text']="Download"
            self.target_field.button['state']='normal'
            self.directory_field.field['state']='normal'
            self.directory_field.button['state']='normal'
        elif state=="downloading":
            self.target_field.field['state']='disabled'
            self.target_field.button['text']="Cancel"
            self.target_field.button['state']='normal'
            self.directory_field.field['state']='disabled'
            self.directory_field.button['state']='disabled'
        elif state=="cancelling":
            self.target_field.field['state']='disabled'
            self.target_field.button['text']="Cancel"
            self.target_field.button['state']='disabled'
            self.directory_field.field['state']='disabled'
            self.directory_field.button['state']='disabled'
            self.progress_indicator.status['text']="Waiting for current Work to complete..."

class TargetField(Tkinter.Frame):
    def __init__(self,master=None):
        Tkinter.Frame.__init__(self,master)
        self.pack({'side':'top', 'anchor':'w', 'fill':'x', 'expand':1})
        self.label=Tkinter.Label(self)
        self.label['text']="Artist: "
        self.label.pack({'side':'left'})
        self.field=Tkinter.Entry(self)
        self.field.pack({'side':'left', 'fill':'x', 'expand':1})
        self.button=DownloadButton(master,self)
        self.button.pack({'side':'left'})

class DownloadButton(Tkinter.Button):
    def __init__(self,app,master=None):
        Tkinter.Button.__init__(self,master)
        self['text']="Download"
        self['command']=self.click
        self.app=app
    
    def click(self):
        if self.app.state=="waiting":
            if not os.path.isdir(self.app.directory_field.field.get()):
                tkMessageBox.showerror("Error","Invalid directory!")
                return 0
            if len(self.app.target_field.field.get())==0:
                tkMessageBox.showerror("Error","Empty artist!")
                return 0
            self.app.download()
            self.app.set_state("downloading")
        elif self.app.state=="downloading":
            self.app.cancel_download.set()
            self.app.set_state("cancelling")

class DirectoryField(Tkinter.Frame):
    def __init__(self,master=None):
        Tkinter.Frame.__init__(self,master)
        self.pack({'side':'top', 'anchor':'w', 'fill':'x', 'expand':1})
        self.label=Tkinter.Label(self)
        self.label['text']="Directory: "
        self.label.pack({'side':'left'})
        self.field=Tkinter.Entry(self)
        self.field.pack({'side':'left', 'fill':'x', 'expand':1})
        self.button=Tkinter.Button(self)
        self.button['text']="Browse"
        self.button['command']=self.browse
        self.button.pack({'side':'left'})
    
    def browse(self):
        directory=tkFileDialog.askdirectory()
        self.field.delete(0,Tkinter.END)
        self.field.insert(0,directory)

class ProgressIndicator(Tkinter.Frame):
    def __init__(self,master=None):
        Tkinter.Frame.__init__(self,master)
        self.pack({'side':'top', 'fill':'both', 'expand':1})
        self.status=ttk.Label(self)
        self.status.pack({'side':'top', 'anchor':'e'})
        self.status['text']="Inactive"
        self.progress_bar=ttk.Progressbar(self)
        self.progress_bar.pack({'side':'top', 'fill':'x', 'expand':1})
        self.console=Console(self)
        self.console['pady']=5
        self.console.pack({'side':'top', 'fill':'both', 'expand':1})
    
    def update(self,current_work,total_work):
        self.status['text']="Downloading {} of {}".format(current_work+1,total_work)
        self.progress_bar['max']=total_work
        self.progress_bar['value']=current_work
    
    def complete(self):
        self.status['text']="Completed"
        self.progress_bar['max']=0
    
    def console_write(self,data):
        console=self.console.textbox
        console['state']='normal'
        console.insert(Tkinter.END,data)
        console.see(Tkinter.END)
        console['state']='disabled'

class Console(Tkinter.Frame):
    def __init__(self,master=None):
        Tkinter.Frame.__init__(self,master)
        self.textbox=Tkinter.Text(self)
        self.textbox['state']='disabled'
        self.textbox.pack({'side':'left', 'fill':'both', 'expand':1})
        self.scrollbar=Tkinter.Scrollbar(self)
        self.scrollbar.pack({'side':'left', 'fill':'y', 'expand':1})
        self.textbox['yscrollcommand']=self.scrollbar.set
        self.scrollbar['command']=self.textbox.yview

class OutputHandler():
    def __init__(self,app,stdout):
        self.app=app
        self.stdout=stdout
    
    def write(self,data):
        self.app.event_queue.put({'type':'console','data':data})
        self.stdout.write(data)
        
def download_thread(target,directory,app):
    try:
        app.event_queue.put({'type':'progress', 'data':(0,1)})
        app.event_queue.put({'type':'status', 'data':"Getting data..."})
        session_id=pixivdl.get_session_config()
        p=Pixiv(session_id)
        works=p.get_works_all(target)
        for i in range(len(works)):
            work=works[i]
            app.event_queue.put({'type':'progress', 'data':(i,len(works))})
            pixivdl.download_work(work,directory)
            if app.cancel_download.is_set():
                app.cancel_download.clear()
                app.event_queue.put({'type':'state', 'data':"waiting"})
                app.event_queue.put({'type':'status', 'data':"Download cancelled"})
                print "\nCancelled"
                return 0
        pickle.dump(works,open(directory+"/metadata.pickle",'wb'))
        print ''
        app.event_queue.put({'type':'function', 'data':app.progress_indicator.complete})
        app.event_queue.put({'type':'state', 'data':"waiting"})
    except:
        app.event_queue.put({'type':'error', 'data':"An unknown error occured!"})
        app.event_queue.put({'type':'status', 'data':"Unknown error occured"})
        app.event_queue.put({'type':'state', 'data':"waiting"})

def eventloop(app):
    while not app.event_queue.empty():
        event=app.event_queue.get()
        if event['type']=="console":
            app.progress_indicator.console_write(event['data'])
        elif event['type']=="error":
            tkMessageBox.showerror("Error",event['data'])
        elif event['type']=="progress":
            app.progress_indicator.update(*event['data'])
        elif event['type']=="status":
            app.progress_indicator.status['text']=event['data']
        elif event['type']=="state":
            app.set_state(event['data'])
        elif event['type']=="function":
            event['data']()
    app.after(100,eventloop,app)

root=Tkinter.Tk()
app=Application(master=root)
eventloop(app)
app.mainloop()