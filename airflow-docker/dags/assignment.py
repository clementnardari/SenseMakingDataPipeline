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

# pull course catalog pages
def catalog():

    print("Path at terminal when executing this file")
    print(os.getcwd() + "\n")
    if not os.path.exists('data'):
        os.mkdir('data')
        print("Directory data created") 

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

def combine():
    #init combo.txt file
    page = os.open('combo.txt', os.O_RDWR|os.O_CREAT )
    os.close(page)
    print("combo.txt created") 

    with open('combo.txt','w') as outfile:
        for file in glob.glob("./data/*.html"):
            with open(file) as infile:
                outfile.write(infile.read())

def titles():
    from bs4 import BeautifulSoup
    def store_json(data,file):
        with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print('wrote file: ' + file)

    #Open and read the large html file generated by combine()
    with open('combo.txt') as file:
        html=file.read()

    #the following replaces new line and carriage return char
    html = html.replace('\n', ' ').replace('\r', '')
    #the following create an html parser
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all('h3')
    titles = []

    # tag inner text
    for item in results:
        titles.append(item.text)
    store_json(titles, 'titles.json')


def clean():
    #complete helper function definition below
    def store_json(data,file):
        with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print('wrote file: ' + file)
                
    with open('titles.json') as file:
        titles = json.load(file)
        # remove punctuation/numbers
        for index, title in enumerate(titles):
            punctuation= '''!()-[]{};:'"\,<>./?@#$%^&*_~1234567890'''
            translationTable= str.maketrans("","",punctuation)
            clean = title.translate(translationTable)
            titles[index] = clean

        # remove one character words
        for index, title in enumerate(titles):
            clean = ' '.join( [word for word in title.split() if len(word)>1] )
            titles[index] = clean

        store_json(titles, 'titles_clean.json')

def count_words():
    from collections import Counter
    def store_json(data,file):
        with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print('wrote file: ' + file)
    with open('titles_clean.json') as file:
        titles = json.load(file)
        words = []

        # extract words and flatten
        for title in titles:
            words.extend(title.split())

        # count word frequency
        counts = Counter(words)
        store_json(counts, 'words.json')

with DAG(
    "assignment",
    start_date=days_ago(1),
    schedule_interval="@daily",catchup=False,
) as dag:

    # INSTALL BS4 BY HAND THEN CALL FUNCTION

    # ts are tasks
    t0 = BashOperator(
        task_id='task_zero',
        bash_command='pip install beautifulsoup4',
        retries=2
    )
    t1 = PythonOperator(
        task_id='task_one',
        depends_on_past=False,
        python_callable=catalog
    )
    t2 = PythonOperator(
        task_id='task_two',
        depends_on_past=False,
        python_callable=combine
    )
    t3 = PythonOperator(
        task_id='task_three',
        depends_on_past=False,
        python_callable=titles
    )
    t4 = PythonOperator(
        task_id='task_four',
        depends_on_past=False,
        python_callable=clean
    )
    t5 = PythonOperator(
        task_id='task_five',
        depends_on_past=False,
        python_callable=count_words
    )
    #define tasks from t2 to t5 below


    t0>>t1>>t2>>t3>>t4>>t5