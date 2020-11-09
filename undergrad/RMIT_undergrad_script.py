import csv
import re
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import bs4 as bs4
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/RMIT_undergrad_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/RMIT_undergrad.csv'

course_data = {'Level_Code': '', 'University': 'RMIT University', 'City': '', 'Country': '',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': 'yes', 'Part_Time': 'yes', 'Prerequisite_1': '',
               'Prerequisite_2': 'IELTS', 'Prerequisite_3': '', 'Prerequisite_1_grade': '', 'Prerequisite_2_grade': '6.0',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': 'A', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': '', 'Face_to_Face': '',
               'Blended': '', 'Remarks': ''}

possible_cities = {'canberra': 'Canberra', 'bruce': 'Bruce', 'mumbai': 'Mumbai', 'melbourne': 'Melbourne',
                   'brisbane': 'Brisbane', 'sydney': 'Sydney', 'queensland': 'Queensland', 'ningbo': 'Ningbo',
                   'shanghai': 'Shanghai', 'bhutan': 'Bhutan', 'online': 'Online', 'hangzhou': 'Hangzhou',
                   'hanoi': 'Hanoi', 'bundoora': 'melbourne', 'brunswick': 'melbourne', 'bendigo': 'Victoria'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    remarks_list = []
    actual_cities = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # SAVE COURSE TITLE
    course_title = soup.find('h1', class_='highLight program-header')
    if course_title:
        title_text = course_title.get_text().strip()
        course_data['Course'] = title_text
        print('COURSE TITLE: ', title_text)

    # DECIDE THE LEVEL CODE
    for i in level_key:
        for j in level_key[i]:
            if j in course_data['Course']:
                course_data['Level_Code'] = i
    print('COURSE LEVEL CODE: ', course_data['Level_Code'])

    # DECIDE THE FACULTY
    for i in faculty_key:
        for j in faculty_key[i]:
            if j.lower() in course_data['Course'].lower():
                course_data['Faculty'] = i
    print('COURSE FACULTY: ', course_data['Faculty'])

    # COURSE LANGUAGE
    for language in possible_languages:
        if language in course_data['Course']:
            course_data['Course_Lang'] = language
        else:
            course_data['Course_Lang'] = 'English'
    print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # COURSE DESCRIPTION
    overview_tag = soup.find('h2', class_='section-title-wrapper__header', text=re.compile('Overview', re.IGNORECASE))
    if overview_tag:
        des_list = []
        overview_tag_parent = overview_tag.find_parent('div')
        if overview_tag_parent:
            parent = overview_tag_parent.find_parent('div')
            if parent:
                parent_1 = parent.find_parent('div')
                if parent_1:
                    section = parent_1.find_parent('section')
                    if section:
                        overview_tag_container = section.find_parent('div', class_='MainSectionPad')
                        if overview_tag_container:
                            desc_tag = overview_tag_container.find_next_sibling('div')
                            if desc_tag:
                                desc_p_list = desc_tag.find_all('p')
                                if desc_p_list:
                                    for p in desc_p_list:
                                        des_list.append(p.get_text())
                                    des_list = ' '.join(des_list)
                                    course_data['Description'] = des_list
                                    print('COURSE DESCRIPTION: ', des_list)

    # CITY / DURATION
    info_table = soup.find('table', class_='table program-table')
    if info_table:
        table_body = info_table.find('tbody')
        if table_body:
            table_row = table_body.find('tr')
            if table_row:
                table_columns = table_row.find_all('td')
                if table_columns:
                    for i, column in enumerate(table_columns):
                        if i == 1:
                            location = column.get_text().lower().strip()
                            if 'city campus' in location:
                                actual_cities.append('melbourne')
                            if 'brunswick' in location:
                                actual_cities.append('brunswick')
                            if 'bundoora' in location:
                                actual_cities.append('bundoora')
                            print('CITY: ', actual_cities)
                        if i == 2:
                            duration_text = column.get_text().lower()
                            converted_duration = dura.convert_duration(duration_text)
                            if converted_duration is not None:
                                duration_list = list(converted_duration)
                                if duration_list[0] == 1 and 'Years' in duration_list[1]:
                                    duration_list[1] = 'Year'
                                if duration_list[0] == 1 and 'Months' in duration_list[1]:
                                    duration_list[1] = 'Month'
                                course_data['Duration'] = duration_list[0]
                                course_data['Duration_Time'] = duration_list[1]
                                print('Duration: ', str(duration_list[0]) + ' / ' + duration_list[1])
                            if 'full-time' in duration_text or 'full time' in duration_text:
                                course_data['Full_Time'] = 'yes'
                            else:
                                course_data['Full_Time'] = 'no'
                            if 'part-time' in duration_text or 'part time' in duration_text:
                                course_data['Part_Time'] = 'yes'
                            else:
                                course_data['Part_Time'] = 'no'
                            print('PART-TIME/FULL-TIME: ', course_data['Part_Time'] + ' / ' + course_data['Full_Time'])

    #ATAR
    atar_tag = soup.find('div', class_='atar-number atrNumber-medium quick-lcl-entry-score')
    if atar_tag:
        atar_number = re.search(r"\d+(?:.\d+)|\d+",  atar_tag.get_text())
        if atar_number:
            atar = atar_number.group()
            course_data['Prerequisite_1'] = 'year 12'
            course_data['Prerequisite_1_grade'] = atar
            print('ATAR: ', atar)
        else:
            remarks_list.append('ATAR IS: ' + str(atar_tag.get_text().strip()))
            print(remarks_list)