#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests,json,sys,time,quopri,re, psycopg2
from psycopg2.extras import execute_values

from bs4 import BeautifulSoup

from datetime import datetime

import smtplib, imaplib, email


from os import environ
from flask import Flask


#replace with web url
SCRAP_URL = "WEB_URL"
#add token variable from OS
TELE_TOKEN = "https://api.telegram.org/bot" + "<OS_TOKEN>"
GET_TELE_SLUG = "/getMe"
UPDATE_TELE_SLUG = "/getUpdates"
SEND_TELE_SLUG = "/sendMessage"
SEND_PHOTO_SLUG = "/sendPhoto"

#IMAP MAIL ACCOUNT
user = 'test@gmail.com'
password = 'password'
#imap server
imap_url = 'imap.gmail.com'
con = imaplib.IMAP4_SSL(imap_url)  


title = []
verses = []
verses_content = []
messages = []

arranged_content = []

unique_group_ids = []

def retrieveIDFromDatabase():
	group_ids = []

	try:
		#fill details with 
		connection = psycopg2.connect(user="username", password="hashed_password", host="host_server", port="port_no", database="database_name")
		cursor = connection.cursor()
		cursor.execute( """select array(select chat_id from chat_ids);""")
		result = cursor.fetchall()
		for l in result:
			group_ids = l[0]

		group_ids = [str(i) for i in group_ids] 

	   	#group_ids = [n.strip() for n in group_ids]
	except (Exception, psycopg2.Error) as error :
	    if(connection):
	        print("Failed to insert record into mobile table", error)
	        
	finally:
	    #closing database connection.
	    if(connection):
	        cursor.close()
	        connection.close()
	        print("PostgreSQL connection is closed")

	return group_ids

def deleteIDOnDatabase(ids):
	if len(ids) != 0:
		try:
			connection = psycopg2.connect(user="username", password="hashed_password", host="host_server", port="port_no", database="database_name")
			cursor = connection.cursor()

			data = [str(i) for i in ids] 

			args_str = ', '.join(['%s' ] * len(data))
			sql = '''DELETE FROM chat_ids WHERE chat_id in ({})'''.format(args_str)
			#print (cursor.mogrify(sql, data).decode('utf8'))
			cursor.execute(sql,data)

			rows_deleted = cursor.rowcount

			print(str(rows_deleted) + " rows deleted.")

			connection.commit()

			#print (r)
		except (Exception, psycopg2.Error) as error :
		    if(connection):
		        print("Failed to insert record into mobile table", error)
		        
		finally:
		    #closing database connection.
		    if(connection):
		        cursor.close()
		        connection.close()
		        print("PostgreSQL connection is closed")

def updateIDOnDatabase(ids):
	if len(ids) != 0:
		try:
			connection = psycopg2.connect(user="username", password="hashed_password", host="host_server", port="port_no", database="database_name")
			cursor = connection.cursor()

			data = ids
			args_str = ', '.join(['(%s)' ] * len(data))
			sql = '''INSERT INTO chat_ids (chat_id) VALUES {} ON CONFLICT DO NOTHING'''.format(args_str)
			#print (cursor.mogrify(sql, data).decode('utf8'))
			cursor.execute(sql,data)

			connection.commit()
			#print (r)
		except (Exception, psycopg2.Error) as error :
		    if(connection):
		        print("Failed to insert record into mobile table", error)
		        
		finally:
		    #closing database connection.
		    if(connection):
		        cursor.close()
		        connection.close()
		        print("PostgreSQL connection is closed")

def getChatIDs():
	initial_lists = retrieveIDFromDatabase()

	#retrieve group chat IDs from the past 24 hours (if there are new)
	json_response = requests.get(TELE_TOKEN + UPDATE_TELE_SLUG).json()
	data = json_response["result"]

	all_results = [item.get('message').get('chat').get('id') for item in data] 
	all_results = [str(i) for i in all_results] 
	all_results = all_results + initial_lists

	unique_group_ids = set(all_results) 
	unique_group_ids = list(unique_group_ids)
	
	print (unique_group_ids)	

	return unique_group_ids


def getParent(parent):
    return ''.join(parent.find_all(text=True, recursive=False)).strip()

def unicodetoascii(text):
    TEXT = (text.
            replace('\\xe2\\x80', '').
    		replace('\\xe2\\x80\\x99', "'").
            replace('\\xc3\\xa9', 'e').
            replace('\\xe2\\x80\\x90', '-').
            replace('\\xe2\\x80\\x91', '-').
            replace('\\xe2\\x80\\x92', '-').
            replace('\\xe2\\x80\\x93', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x98', "'").
            replace('\\xe2\\x80\\x9b', "'").
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9d', '"').
            replace('\\xe2\\x80\\x9e', '"').
            replace('\\xe2\\x80\\x9f', '"').
            replace('\\xe2\\x80\\xa6', '...').#
            replace('\\xe2\\x80\\xb2', "'").
            replace('\\xe2\\x80\\xb3', "'").
            replace('\\xe2\\x80\\xb4', "'").
            replace('\\xe2\\x80\\xb5', "'").
            replace('\\xe2\\x80\\xb6', "'").
            replace('\\xe2\\x80\\xb7', "'").
            replace('\\xe2\\x81\\xba', "+").
            replace('\\xe2\\x81\\xbb', "-").
            replace('\\xe2\\x81\\xbc', "=").
            replace('\\xe2\\x81\\xbd', "(").
            replace('\\xe2\\x81\\xbe', ")").

           
			replace('\\x9c', '"').
			replace('\\x80', '').
    		replace('\\x99', "'").
            replace('\\xa9', 'e').
            replace('\\x90', '-').
            replace('\\x91', '-').
            replace('\\x92', '-').
            replace('\\x93', '-').
            replace('\\x94', '-').
            replace('\\x94', '-').
            replace('\\x98', "'").
            replace('\\x9b', "'").
            replace('\\x9c', '"').
            replace('\\x9c', '"').
            replace('\\x9d', '"').
            replace('\\x9e', '"').
            replace('\\x9f', '"').
            replace('\\xa6', '...').
            replace('\\xb2', "'").
            replace('\\xb3', "'").
            replace('\\xb4', "'").
            replace('\\xb5', "'").
            replace('\\xb6', "'").
            replace('\\xb7', "'").
            replace('\\xba', "+").
            replace('\\xbb', "-").
            replace('\\xbc', "=").
            replace('\\xbd', "(").
            replace('\\xbe', ")").
            
            replace('=\\r\\n', '').
            replace('=\\\\r\\\\n', '').
            replace('\\r\\n', '').
            replace('\\\\r\\\\n', '').
            replace('=', '').
            replace("\\t", '')
           
         )

    return TEXT


def craftTelegramContentFromEmailOnServer(html_content):

	soup = BeautifulSoup(html_content, 'html.parser')

	elements_order = []


	#get devo title
	title = soup.findAll('th')
	#print(title)

	content = soup.findAll('p')

	#EMAIL INDEX FORMAT: 0 = date, 1=title, content = 2 onwards
	title_string = content[1].text.rstrip().lstrip()
	verse_content = content[2].text.rstrip().lstrip()
	verse =  content[2].find_parent('div').find_all(text=True,recursive=False)[-2].rstrip().lstrip()
	messages = ""

	title_string = " ".join(title_string.split())
	verse_content = " ".join(verse_content.split())
	verse = " ".join(verse.split())

	title_string = title_string.replace('\\\\r\\\\n', '')
	verse_content = verse_content.replace('\\\\r\\\\n', '')
	verse = verse.replace('\\\\r\\\\n', '')


	for i in range(3,len(content)-3):
		messages += content[i].text.rstrip() + "\n\n"


	crafted_message = ""

	crafted_message += "`" + title_string.strip() + "` \n\n"

	crafted_message += "*" + verse.strip() + "* \n" + "_" + verse_content.strip() + "_ \n\n"

	crafted_message += messages + "\n"

	crafted_message += 'Retrieved from: [URL_TEXT](URL)'

	crafted_message = unicodetoascii(crafted_message)

	print(crafted_message)

	return crafted_message.strip()

def retrieveMailContent():
	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(user, password)
	mail.list()

	print("login email STMP here")

	# Out: list of "folders" aka labels in gmail.
	mail.select("inbox") # connect to inbox.
	result, data = mail.search(None, 'FROM', '"{}"'.format('sender@gmail.com')) 

	print("data retrieved here")

	ids = data[0] # data is a list.
	id_list = ids.split() # ids is a space separated string
	latest_email_id = id_list[-1] # get the latest

	# fetch the email body (RFC822) for the given ID
	result, data = mail.fetch(latest_email_id, "(RFC822)") 


	mail.close()
	mail.logout()

	raw_email = data[0][1] # here's the body, which is raw text of the whole email
	# including headers and alternate payloads

	email_message = email.message_from_string(str(raw_email))


	print("RAW EMAIL")

	email_message = str(email_message)

	#CONTENT STRUCTURE MIGHT DIFFER ON DIFF EMAILS

	start_pos = email_message.find("<!DOCTYPE html>")
	end_pos = email_message.rfind("</html>")
	content = email_message[start_pos:end_pos+len("</html>")]

	filtered_tags = content.replace("=0A", " ")
	filtered_tags = filtered_tags.replace("<em>", "")
	filtered_tags = filtered_tags.replace("</em>", "")

	decoded_string = str(quopri.decodestring(filtered_tags))
	
	message = craftTelegramContentFromEmailOnServer(decoded_string)

	return message



def arrangeTelegramContent(title, verses, verses_content, collated_para):
	crafted_message = ""

	crafted_message += "`" + title + "` \n\n"

	crafted_message += "*" + verses + "* \n" + "_" + verses_content + "_ \n\n"

	crafted_message += collated_para + "\n"

	crafted_message += 'Retrieved from: [URL_TEXT](URL)'

	return crafted_message

def postToTelegramChats(title, verses, verses_content, collated_para):
	print('Morning')

	telegram_ids = getChatIDs()

	message = arrangeTelegramContent(title, verses, verses_content, collated_para)
	
	delete_ids = []
	functional_ids = []

	# sending message to groups
	for group_id in telegram_ids: 
		PARAMS = {'chat_id': group_id, 'text': message,  'parse_mode': 'Markdown'}
		r = requests.get(url = TELE_TOKEN + SEND_TELE_SLUG, params = PARAMS)
		status = r.json()
		if 'error_code' in status:
			delete_ids.append(group_id)
		else:
			functional_ids.append(group_id)
		time.sleep(1)

	#delete ids
	deleteIDOnDatabase(delete_ids)

	#update group ids
	updateIDOnDatabase(functional_ids)
	
	print("Message sent to groups")
	return 0

def prepareDailyVerseMessage():
	#My own ID from OS ENV

	YOUVERSION_DEVELOPER_TOKEN = "AAAA"


	headers = {
	    "accept": "application/json",
	    "x-youversion-developer-token": YOUVERSION_DEVELOPER_TOKEN,
	    "accept-language": "en",
	}

	day_of_year = datetime.now().timetuple().tm_yday

	#API LINKS with token
	request_url = "https://developers.youversionapi.com/1.0/verse_of_the_day/" + str(day_of_year) + "?version_id=1"

	response = requests.get(
	    request_url,
	    headers=headers
	)

	#=== FILTER RESPONSES (MIGHT DIFFER FRO DIFF APIS)
	print(response.content)
	content  = response.json()

	message = content["verse"]["text"]
	print(message)

	verse = content["verse"]["human_reference"]
	print(verse)

	url = content["verse"]["url"]
	print(url)

	img_url = content["image"]["url"]
	start_pos = img_url.find("https://")
	img_url = img_url[start_pos:]
	print(img_url)

	attribution = content["image"]["attribution"]
	print(attribution)

	crafted_message = ""

	crafted_message += "`Today's Daily Verse` \n\n"

	crafted_message += "*" + verse + "* \n" + "_" + message + "_ \n\n"

	crafted_message += 'Retrieved from: [' + attribution +']('+ url+ ')'


	telegram_ids = getChatIDs()

	delete_ids = []
	functional_ids = []

	# sending message to groups
	for group_id in telegram_ids: 
		PARAMS = {'chat_id': group_id, 'caption': crafted_message,'photo': img_url, 'parse_mode': 'Markdown'}
		r = requests.get(url = TELE_TOKEN + SEND_PHOTO_SLUG, params = PARAMS)

		status = r.json()
		if 'error_code' in status:
			delete_ids.append(group_id)
		else:
			functional_ids.append(group_id)
		time.sleep(1)

	#delete ids
	deleteIDOnDatabase(delete_ids)

	#update group ids
	updateIDOnDatabase(functional_ids)

	return crafted_message	

#Retrieve via api
def launch_noon():
	print("launching noon script...")

	prepareDailyVerseMessage()

	print("Message sent to groups")
	return 0

#Crawl from email
def launch_evening():
	temp = getChatIDs()

	selected_message = retrieveMailContent()

	delete_ids = []
	functional_ids = []

	# sending message to groups
	for group_id in temp: 
		PARAMS = {'chat_id': group_id, 'text': selected_message,  'parse_mode': 'Markdown'}
		r = requests.get(url = TELE_TOKEN + SEND_TELE_SLUG, params = PARAMS)
		status = r.json()
		if 'error_code' in status:
			delete_ids.append(group_id)
		else:
			functional_ids.append(group_id)
		time.sleep(1)

	#delete ids
	deleteIDOnDatabase(delete_ids)

	#update group ids
	updateIDOnDatabase(functional_ids)

	print("Message sent to groups")
	return 0

#Crawl from website
def launch_morning():
	print("launching script...")
	# try:

	page = requests.get(SCRAP_URL)
	soup = BeautifulSoup(page.text, 'html.parser')

	#scrapping methods (elements: Class, div, tags) will differ on website and possibly changes upon website update. Change accordingly (General idea/method is here)
	
	#retrieve titles 
	find_titles = soup.find(class_='title-section')
	title_element = find_titles.find('p')
	title = title_element.text
	print(title)

	#retrieve verses
	find_contents = soup.find(class_='c-one-column-section')

	#retrieve verse 
	verse_element = find_contents.find('h4')
	verses = verse_element.text

	#retrieve verse contents
	verse_content_element = find_contents.find('h3')
	unwanted = verse_content_element.find('sup')
	unwanted.extract()
	verses_content = verse_content_element.text


	#retrieve contents
	paragraphs_content = find_contents.find_all('p')

	collated_para = "\n"
	for para in paragraphs_content:
		collated_para += para.text + "\n\n"


	postToTelegramChats(title, verses, verses_content, collated_para)

