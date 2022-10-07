#The DAG object (needed to instantiate a DAG)
from airflow import DAG
from datetime import timedelta
#Operators (needed to operate)
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
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
def catalog():
    #list of urls from the MIT course catalog
    file = open('./00_urls.txt')
    lines = file.readlines()
    url_list = [line.rstrip() for line in lines]
        
    def pull(url):
        response = urllib.request.urlopen(url).read()
        data = response.decode('utf-8')
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

    def combine():
        #init combo.txt file
        if os.path.exists('combo.txt'):
            os.remove('combo.txt')
            print("combo.txt removed") 
        page = os.open('combo.txt', os.O_RDWR|os.O_CREAT )
        os.close(page)
        print("combo.txt created") 

        with open('combo.txt','w') as outfile:
            for file in glob.glob("./data/*.html"):
                with open(file) as infile:
                    outfile.write(infile.read())
    
    #loop through all urls
    for url in url_list:
        try:
            #get page name
            file=url.split("/")[-1]
            data=pull(url)
            store(data,file)        
            print(f'Pulled: {url}')
            print('--- waiting ---')
            time.sleep(15)
        except:
            print(f'Not found: {url}')