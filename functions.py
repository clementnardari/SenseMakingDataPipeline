#Task Functions (used to facilitate tasks)
import urllib. request
import time
import glob, os
import json

#create a data folder to store all the raw data
if not os.path.exists('data'):
    os.mkdir('data')
    print("Directory data created")   

  

# pull course catalog pages
# pull course catalog pages
def catalog():
    def pull(url):
        #Get the page data
        response = urllib.request.urlopen(url).read()

        #decode it and store it
        data = response.decode('utf-8')

        print(f'Connected to: {url}')
        
        return data
    def store(data,file):
        # Create path:
        path = os.path.join('./data', file)

        # Create a file a file
        page = os.open(path, os.O_RDWR|os.O_CREAT )

        # Write tp the file
        os.write(page, data.encode())

        # Close the file
        os.close(page)

        print('wrote file: ' + file)

url='http://student.mit.edu/catalog/m1a.html'
file=url.split("/")[-1]
print(file)