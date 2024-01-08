from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import MongoClient

option = webdriver.ChromeOptions()
option.add_argument('headless')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# driver.get method() will navigate to a page given by the URL address
driver.get('https://in.indeed.com/jobs?q=python+developer&l=')
sleep(3)

s = driver.page_source
soup = BeautifulSoup(s, "html.parser")
driver.close()

job_listings_container = soup.find('div', id='mosaic-provider-jobcards')
job_list = job_listings_container.find_all('li')

data = []

for job in job_list:
    job_title_element = job.find('h2', class_='jobTitle')
    company_location_element = job.find('div', class_='company_location')
    salary_element = job.find(lambda tag: tag.name == 'StaticText' and '₹' in tag.text)

    if job_title_element and company_location_element:
        job_title = job_title_element.text.strip()
        company_name = company_location_element.find('span').text.strip()
        location = company_location_element.find('div').text.strip()

        salary = None
        if salary_element:
            salary = salary_element.text.strip()

        data.append({
            'Job Title': job_title,
            'Company Name': company_name,
            'Location': location,
            'Salary': salary  # Add the extracted salary to the data dictionary
        })

df = pd.DataFrame(data)
print(df)

# Extract numeric values from the 'Salary' column and calculate the average
numeric_salaries = df['Salary'].str.extractall(r'(\d+\.\d+|\d+)').astype(float).unstack()
average_salary = numeric_salaries.mean().mean()

print(f'\nAverage Salary: ₹{average_salary:.2f}')

client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
collection = db['_my_Database']

data_dict = df.to_dict(orient='records')

collection.insert_many(data_dict)
