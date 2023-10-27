#########################################################################################
#                                                                                       #
# Script to auto-update publications, people, and news for the ssv website.             #
# This script pulls data from ORCID using their public APIs. To use them, it            #
# is necessary to define an application that can interact with the APIs.                #
#                                                                                       #
# Follow the insructions at https://info.orcid.org/documentation/features/public-api/   #
# to generate an application, and retrieve its ID and SECRET.                           #
#                                                                                       #
# The, use the following command to generate a token for using the API:                 #
# curl -i -L -H 'Accept: application/json' -d 'client_id=[APP ID]' -d 'client_secret=[APP SECRET]' -d 'scope=/read-public' -d 'grant_type=client_credentials' 'https://orcid.org/oauth/token'
#                                                                                       #
# The response will have the following structure:                                       #
# {                                                                                     #
#   "access_token": "[ACCESS_TOKEN]",                                                   #
#   "token_type": "bearer",                                                             #
#   "refresh_token": "[REFRESH_TOKEN]",                                                 #
#   "expires_in": [EXPIRATION],                                                         #
#   "scope": "/read-public",                                                            #
#   "orcid":null                                                                        #
# }                                                                                     #
# Note that the access token lasts ~20 years.                                           #
#                                                                                       #
# You can then use the generated access token as argument for this script:              #
# python3 orcid-crawl.py [ACCESS_TOKEN]                                                 #
#                                                                                       #
# The script will use such token to issue requests to the ORCID web API:                #
# https://github.com/ORCID/ORCID-Source/tree/main/orcid-api-web                         #
#                                                                                       #
# This script works by taking information out of the 'users.yaml' file located          #
# in the same directory. Such a file should be split in two sections, each              #
# containing a list of user information with <orcid, photo, from, to> where             #
# - <orcid> is the user's identifiaction number on ORCID                                #
# - <photo> is the filename of the image living under website_root/images/ to           #
#   use as profile picture for them                                                     #
# - <from> is the date (YYYY-MM-DD) when they joined the lab, used to filter out        #
#   publications published before they joined                                           #
# - <to> is the date (YYYY-MM-DD) when they left the lab, used to filter out            #
#   publications published after they joined (if they are still part of the lab,        #
#   'today' can be used)                                                                #
#                                                                                       #
# An example file is:                                                                   #
# users:                                                                                #
#   - id: 0000-0000-0000-0000                                                           #
#     photo: img1.png                                                                   #
#     from: 2019-01-01                                                                  #
#     to: today                                                                         #
#   - id: 0000-0000-0000-0001                                                           #
#     photo: img2.png                                                                   #
#     from: 2019-09-15                                                                  #
#     to: today                                                                         #
# past_users:                                                                           #
#   - id: 0000-0000-0000-0002                                                           #
#     photo: img3.png                                                                   #
#     from: 2019-09-01                                                                  #
#     to: 2021-09-30                                                                    #
#                                                                                       #
# The script then will:                                                                 #
# - fill up '../people.md' with the info crawled for each entry in 'users' and          #
#   'past_users', placing them in their respective sections                             #
# - fill up '../publications.md' with works from both present and past users that       #
#   were published within the time window of at least one of the autors (to avoid       #
#   duplicates, we discriminate publications based on DOI)                              #
# - generate a news page under '../news/_posts/' named after the publication date       #
#   and the hash of the publication's title, containing a brief text to illustrate      #
#   what was published                                                                  #
#                                                                                       #
#########################################################################################

import requests
import json
import yaml
import sys
from datetime import *
import hashlib
import os
import shutil

class User:
	def __init__(self, name, surname, photo, mail, website, role, org, bio, raw_works):
		self.name = name
		self.surname = surname
		self.photo = photo
		self.mail = mail
		self.website = website
		self.role = role
		self.org = org
		self.bio = bio
		self.raw_works = raw_works

	def has_necessary_fields(self):
		return self.name is not None and self.surname is not None and self.photo is not None

	def dump(self):
		position = f'{self.role} @ {self.org}' if self.role is not None and self.org is not None else ''
		email = f'Email: <a href="mailto:{self.mail}">{self.mail}</a>' if self.mail is not None else ''
		website = f'Website: <a href="{self.website}">{self.website}</a>' if self.website is not None else ''
		bio = f'{self.bio}' if self.bio is not None else ''
		return f'''
<div class="div-person-table">
	<div class="div-person-table">
		<img class="div-person-table-col" src="{{{{ site.baseurl }}}}/images/{self.photo}"/>
		<div class="div-person-table-multicol">
			<h3>{self.name} {self.surname}</h3>
			<h5>{position}</h5>
			{email}<br/>
			{website}
		</div>
	</div>  
</div>
{bio}
<br/><br/>
'''

class Pub:
	def __init__(self, title, pub_date, pub_type, where, doi, contribs):
		self.title = title
		self.pub_date = pub_date
		self.pub_type = pub_type
		self.where = where
		self.doi = doi
		self.contribs = contribs

	def is_out_of_date_period(self):
		return self.pub_date is None

	def has_necessary_fields(self):
		return self.title is not None and self.pub_type is not None and self.where is not None

	def readable_kind(self):
		r = self.pub_type.lower().replace('_', ' ')
		if r == 'book':
			r = 'book chapter'
		elif r == 'other':
			r = 'article'
		return r    

	def dump(self):
		authors = ', '.join(self.contribs)
		return f'{authors}: _"{self.title}"_, in {self.where} [[DOI]](https://doi.org/{self.doi})\n\n'

	def to_news_page(self):
		authors = ', '.join(self.contribs)
		kind = self.readable_kind()
		starting_kind = kind.capitalize()
		return f'''---
layout: page
title: '{starting_kind} published in "{self.where}"'
---

<small>{{{{ page.date | date: "%-d %B %Y" }}}}</small>

The {kind} "{self.title}", by {authors}, has just been published in "{self.where}"! Available [here](https://doi.org/{self.doi}).
'''

def query_api(access_token, user_id, method, log=False):
	return query_path(access_token, '/' + user_id + '/' + method, log)

def query_path(access_token, path, log=False):
	headers_dict = {
		'Accept': 'application/vnd.orcid+json',
		'Authorization':'Bearer ' + access_token
	}
	response = requests.get('https://pub.orcid.org/v2.1' + path, headers=headers_dict) 
	if log:
		print('## Result of querying', path, '##')
		print(response.text)
	return json.loads(response.text)

def access_field(accessor, element, field, default=None, log=True):
	try:
		el = accessor(element)
		if log:
			print('\t' + field + ':', el)
		return el
	except Exception as e:
		print('\tUnable to retrieve value for', field, ', will use default value', default, '. Reason:', str(e))
		return default

def parse_user(access_token, user):
	user_id = user['id']
	print('Processing', user_id)

	record = query_api(access_token, user_id, 'person')
	name = access_field(lambda r: r['name']['given-names']['value'], record, 'name')
	surname = access_field(lambda r: r['name']['family-name']['value'], record, 'surname')
	bio = access_field(lambda r: r['biography']['content'], record, 'bio')
	mail = access_field(lambda r: r['emails']['email'][0]['email'], record, 'mail')
	website = access_field(lambda r: r['researcher-urls']['researcher-url'][0]['url']['value'], record, 'website')

	try:
		record = query_api(access_token, user_id, 'activities')
		role = access_field(lambda r: r['employments']['employment-summary'][0]['role-title'], record, 'role')
		org = access_field(lambda r: r['employments']['employment-summary'][0]['organization']['name'], record, 'org')
	except:
		# if no employment, this is a student
		role = 'PhD Student'
		org = 'Università Ca\' Foscari Venezia'

	raw_works = access_field(lambda r: r['works']['group'], record, 'works', default=list(), log=False)
	return User(name, surname, user['photo'], mail, website, role, org, bio, raw_works)

def parse_work(access_token, min_date, max_date, work):
	workrecord = query_path(access_token, access_field(lambda r: r['work-summary'][0]['path'], work, 'work path', log=False))
	title = access_field(lambda r: r['title']['title']['value'], workrecord, 'title', log=False)
	print('Processing', title)

	year = int(access_field(lambda r: r['work-summary'][0]['publication-date']['year']['value'], work, 'year'))
	month = int(access_field(lambda r: r['work-summary'][0]['publication-date']['month']['value'], work, 'month', default=1))
	day = int(access_field(lambda r: r['work-summary'][0]['publication-date']['day']['value'], work, 'day', default=1))
	
	pub_date = date(year, month, day)
	if pub_date < min_date or pub_date > max_date:
		# exclude the publication
		return Pub(None, None, None, None, None, None)

	pub_type = access_field(lambda r: r['type'], workrecord, 'type')
	where = access_field(lambda r: r['journal-title']['value'], workrecord, 'venue')
	doi = None
	for extid in access_field(lambda r: r['external-ids']['external-id'], workrecord, 'external ids', default=list(), log=False):
		#print(extid)
		if access_field(lambda r: r['external-id-type'], extid, 'external id type', log=False) == 'doi':
			doi = access_field(lambda r: r['external-id-value'], extid, 'external id')
			break
	contribs = list()
	for contributor in access_field(lambda r: r['contributors']['contributor'], workrecord, 'contributors', default=list(), log=False):
		contribs += [access_field(lambda r: r['credit-name']['value'], contributor, 'contributor name')]
	return Pub(title, pub_date, pub_type, where, doi, contribs)

def add_news(publication):
	name_hash = hashlib.md5(publication.title.encode('utf-8')).hexdigest()
	news_name = f'{publication.pub_date.year}-{publication.pub_date.month}-{publication.pub_date.day}-paper-{name_hash}'
	print('Generating news for', publication.title, '(', news_name, ')')        
	with open(f'../news/_posts/{news_name}.md', 'w') as news:
		news.write(publication.to_news_page())

def populate_publications_page(publications):
	with open('../publications.md', 'w') as file:
		file.write("""---
layout: page
title: Publications
---
""")
		curryear = None
		for publication in publications:
			year = publication.pub_date.year
			if curryear is None:
				curryear = year
				file.write(f'## {curryear}\n\n')
			elif year != curryear:
				curryear = year
				file.write(f'## {curryear}\n\n')

			print("Adding", publication.title, "to the Publications page")
			file.write(publication.dump())

def populate_people_page(people, past_people):
	with open('../people.md', 'w') as file:
		file.write("""---
layout: page
title: People
---
""")
		for person in people:
			print("Adding", person.name, person.surname, "to the People page")
			file.write(person.dump())
		file.write('## Past members\n')
		for person in past_people:
			print("Adding", person.name, person.surname, "to the People page")
			file.write(person.dump())

def process_user_and_add(user, people_list, publications_list):
	person = parse_user(access_token, user)
	if person.has_necessary_fields():
		people_list += [person]
	else:
		print('\tUser discarded due to missing fields')

	min_date = user['from']
	max_date = date.today() if user['to'] == 'today' else user['to']
	for work in person.raw_works:
		publication = parse_work(access_token, min_date, max_date, work)
		if publication.is_out_of_date_period():
			print('\tPublication discarded since it is outside of the specified date range')
			continue
		elif not publication.has_necessary_fields():
			print('\tPublication discarded due to missing fields')
			continue
		elif publication.doi is None or any(publication.doi == pub.doi for pub in publications_list):
			print('\tPublication discarded due to missing or duplicate doi')
			continue
		else:
			publications_list += [publication]

def sort_by_date(publication):
	return publication.pub_date

if __name__ == '__main__':
	with open('users.yaml', 'r') as yamlfile:
		data = yaml.load(yamlfile, Loader=yaml.FullLoader)
	print('Configuration read successfully')

	access_token = sys.argv[1]
	people = list()
	past_people = list()
	publications = list()

	for user in data['users']:
		process_user_and_add(user, people, publications)

	for user in data['past_users']:
		process_user_and_add(user, past_people, publications)

	publications = sorted(publications, key=sort_by_date)
	populate_people_page(people, past_people)
	populate_publications_page(reversed(publications))
	
	# cleanup news folder
	if os.path.exists('../news/_posts/'):
		shutil.rmtree('../news/_posts/')
	os.makedirs('../news/_posts/')
	
	for publication in reversed(publications):
		add_news(publication)
