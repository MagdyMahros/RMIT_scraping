"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 09-11-20
    * description:This script extracts all the courses links and save it in txt file.
"""
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import time


option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# MAIN ROUTINE
courses_page_url = 'https://www.rmit.edu.au/search?authStatus=9;i=1;m_count_content=10;q=postgraduate;q1=program;q2=Domestic%7CInternational;q3=Postgraduate+study%7CResearch+programs;sp_cs=UTF-8;x1=pageType;x2=studenttype;x3=s_studytype'
list_of_links = []
browser.get(courses_page_url)
the_url = browser.page_source
delay_ = 15  # seconds

# KEEP CLICKING NEXT UNTIL THERE IS NO BUTTON COLLECT THE LINKS
condition = True
while condition:
    result_elements = browser.find_elements_by_class_name('pageResult--Title')
    for i, element in enumerate(result_elements):
        print(i, element.text)
        url = element.get_attribute('href')
        list_of_links.append(url)
    try:
        browser.execute_script("arguments[0].click();", WebDriverWait(browser, delay_).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.page-nummber.next > a'))))
    except TimeoutException:
        print('timeout')
        condition = False
    time.sleep(3)

# SAVE TO FILE
course_links_file_path = os.getcwd().replace('\\', '/') + '/RMIT_postgrad_links.txt'
course_links_file = open(course_links_file_path, 'w')
for link in list_of_links:
    if link is not None and link != "" and link != "\n":
        if link == list_of_links[-1]:
            course_links_file.write(link.strip())
        else:
            course_links_file.write(link.strip() + '\n')
course_links_file.close()
