import csv
import re
import time
from pathlib import Path
from selenium import webdriver
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
course_links_file_path = course_links_file_path.__str__() + '/RMIT_postgrad_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/RMIT_postgrad.csv'

course_data = {'Level_Code': '', 'University': 'RMIT University', 'City': '', 'Country': '',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': 'yes', 'Part_Time': 'yes', 'Prerequisite_1': 'IELTS',
               'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '6.5', 'Prerequisite_2_grade': '',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': '', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': 'no', 'Face_to_Face': '',
               'Blended': 'no', 'Remarks': ''}

possible_cities = {'canberra': 'Canberra', 'bruce': 'Bruce', 'mumbai': 'Mumbai', 'melbourne': 'Melbourne',
                   'brisbane': 'Brisbane', 'sydney': 'Sydney', 'queensland': 'Queensland', 'ningbo': 'Ningbo',
                   'shanghai': 'Shanghai', 'bhutan': 'Bhutan', 'online': 'Online', 'hangzhou': 'Hangzhou',
                   'hanoi': 'Hanoi', 'bundoora': 'Bundoora', 'brunswick': 'Brunswick', 'bendigo': 'Victoria'}

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

    # CITY
    location_tag = soup.find('div', class_='description-1 quick-lcl-location')
    if location_tag:
        location_text = location_tag.get_text().lower()
        print('location test: ', location_text)
        if 'city campus' in location_text or 'melbourne' in location_text:
            actual_cities.append('melbourne')
            course_data['Offline'] = 'yes'
            course_data['Face_to_Face'] = 'yes'
        else:
            course_data['Offline'] = 'no'
            course_data['Face_to_Face'] = 'no'
        if 'brunswick' in location_text:
            actual_cities.append('brunswick')
            course_data['Offline'] = 'yes'
            course_data['Face_to_Face'] = 'yes'
        else:
            course_data['Offline'] = 'no'
            course_data['Face_to_Face'] = 'no'
        if 'bundoora' in location_text:
            actual_cities.append('bundoora')
            course_data['Offline'] = 'yes'
            course_data['Face_to_Face'] = 'yes'
        else:
            course_data['Offline'] = 'no'
            course_data['Face_to_Face'] = 'no'
        if 'online' in location_text:
            actual_cities.append('online')
            course_data['Online'] = 'yes'
        else:
            course_data['Online'] = 'no'
        print('CITY: ', actual_cities)

    # DURATION / FULL-TIME, PART-TIME
    info_table = soup.find('table', class_='table program-table')
    if info_table:
        table_body = info_table.find('tbody')
        if table_body:
            table_row = table_body.find('tr')
            if table_row:
                table_columns = table_row.find_all('td')
                if table_columns:
                    for i, column in enumerate(table_columns):
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

    # CAREER OUTCOMES
    career_tag = soup.find('h2', class_='section-title-wrapper__header', text=re.compile('Career', re.IGNORECASE))
    if career_tag:
        career_list = []
        career_tag_parent = career_tag.find_parent('div')
        if career_tag_parent:
            c_parent = career_tag_parent.find_parent('div')
            if c_parent:
                c_parent_1 = c_parent.find_parent('div')
                if c_parent_1:
                    c_section = c_parent_1.find_parent('section')
                    if c_section:
                        career_tag_container = c_section.find_parent('div', class_='MainSectionPad')
                        if career_tag_container:
                            caree_tag = career_tag_container.find_next_sibling('div')
                            if caree_tag:
                                caree_ul = caree_tag.find('ul')
                                if caree_ul:
                                    caree_li_list = caree_ul.find_all('li')
                                    if caree_li_list:
                                        for li in caree_li_list:
                                            career_list.append(li.get_text())
                                        career_list = ' / '.join(career_list)
                                        course_data['Career_Outcomes'] = career_list
                                        print('CAREER OUTCOMES: ', career_list)

    # AVAILABILITY + INT FEES
    int_fees = soup.find('div', class_='description-1 fee-int-details')
    course_data['Int_Fees'] = ''
    if int_fees:
        fee_p = int_fees.find('p')
        if fee_p:
            fee_text = fee_p.get_text().lower()
            print(fee_text)
            if 'not applicable' in fee_text:
                course_data['Availability'] = 'D'
                remarks_list.append('int_fee is: ' + str(fee_text))
            else:
                course_data['Availability'] = 'A'
                fee_n = re.search(r"\d+(?:,\d+)|\d+", fee_text)
                if fee_n:
                    fee = fee_n.group()
                    course_data['Int_Fees'] = fee
                    print('INR_FEE: ', fee)

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities
    course_data['Remarks'] = remarks_list
    del remarks_list
    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance',
                          'Face_to_Face',
                          'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('RMIT_postgrad_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)

