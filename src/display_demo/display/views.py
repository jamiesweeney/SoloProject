from django.http import HttpResponse
import google.cloud.storage
import os
import time

bucket_name = 'bluetoothscanner'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/Workspace/SoloProject/src/creds.json"
timeout = 600
page_list = []

def index(request):
    global page_list
    page_list  = []

    storage_client = google.cloud.storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    def unpack_pages(pages):
        next_page = pages.next()
        while (next_page != None): 
            unpack_page(next_page)
            try:
                next_page = pages.next()
            except:
                break

    def unpack_page(page):
        global page_list
        while (page.remaining > 0):
            entry = page.next()
            page_list += [entry.name]
            

    pages = bucket.list_blobs().pages
    unpack_pages(pages)
    curr_time = time.time()

    new_list = {}
    for page in page_list:
        p = str(page.split(os.sep)[0])  
        t = int(page.split(os.sep)[1])
        if (p not in new_list):
            new_list[p] = None
            if ((t + timeout) > curr_time):
                new_list[p] = t
        else:
            if ((t + timeout) > curr_time):
                new_list[p] = t

    resp = "<html><body>"

    for room in sorted(new_list):

        resp += "<b> Room " + room + "</b>"
        resp += "<ul>"
        if new_list[room] == None:
            resp += "<li><b>No data</b></li>"
        else:    
            data = bucket.get_blob(room+"/"+str(new_list[room])).download_as_string().replace('\r', '').split("\n")[:-1]
            for entry in data:
                address = entry.split(',')
                resp += "<li>" + str(address[1]) + "</li>"

        resp += "</ul>"


    resp += "</body></html>"

    return HttpResponse(resp)


