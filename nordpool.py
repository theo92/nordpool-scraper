import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

# Define the chrome webdriver options

options = webdriver.ChromeOptions()
options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability.

# By default, Selenium waits for all resources to download before taking actions.
# However, we don't need it as the page is populated with dynamically generated JavaScript code.
options.page_load_strategy = "none"

# Pass the defined options objects to initialize the webdriver
driver = Chrome(options = options)

# Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
driver.implicitly_wait(1)

url = 'https://www.nordpoolgroup.com/en/Market-data1/Dayahead/Area-Prices/NO/Hourly/?view=table'
response = driver.get(url)
time.sleep(1)

content = driver.find_element(By.CSS_SELECTOR, "div[class*='table-wrapper']")
table = content.find_element(By.CSS_SELECTOR, "table[id*='datatable']")

table_html = table.get_attribute('outerHTML') # Gets the HTML of the table
table_text = table.text # Gets the text content of the table

table_text = table.get_attribute('innerText')

lines = table_text.strip().split('\n')

date = lines[0]

columns = ['Time', 'Oslo', 'Kr.sand', 'Bergen', 'Tr.heim', 'Molde', 'Tromsø']

data_rows = []
first_time_range = lines[2].strip()
first_data_line = lines[3].strip().split('\t')
if first_time_range and first_data_line:
    first_full_row = [first_time_range] + first_data_line
    data_rows.append(first_full_row)

# Process the lines into a DataFrame, skipping the header and the first data row which is already processed
for i in range(3, len(lines), 1):  # Start from the fourth line and step by 1
    # Check if we have a pair of lines (time range and data)
    if i + 1 < len(lines):
        time_range = lines[i].strip()
        data_line = lines[i + 1].strip().split('\t')
        if time_range and data_line:
            full_row = [time_range] + data_line
            data_rows.append(full_row)
    else:
        # This could be a summary row, so process it separately
        summary_row = lines[i].strip().split('\t')
        if summary_row and len(summary_row) == len(columns):
            data_rows.append(summary_row)



df = pd.DataFrame(data_rows, columns=columns)
for col in columns[1:]:  # Skip the first column which is 'Time'
    df[col] = pd.to_numeric(df[col].str.replace(',', '.').str.strip(), errors='coerce')


df = df[~df['Time'].isna()]
print(table and str("Content found."))
df.dropna(inplace=True)
print(df)