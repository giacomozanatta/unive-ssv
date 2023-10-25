# https://github.com/ORCID/ORCID-Source/tree/main/orcid-api-web

# To get access token: 
# curl -i -L -H 'Accept: application/json' -d 'client_id=[APP ID]' -d 'client_secret=[APP SECRET]' -d 'scope=/read-public' -d 'grant_type=client_credentials' 'https://orcid.org/oauth/token'

# To get APP ID and SECRET: https://info.orcid.org/documentation/features/public-api/

import requests
import json
import yaml
import sys
from datetime import *
import hashlib
import os
import shutil

def query_api(access_token, user_id, method):
	return query_path(access_token, '/' + user_id + '/' + method)

def query_path(access_token, path):
	headers_dict = {
		'Accept': 'application/vnd.orcid+json',
		'Authorization':'Bearer ' + access_token
	}
	response = requests.get('https://pub.orcid.org/v2.1' + path, headers=headers_dict) 
	return json.loads(response.text)

def parse_user(access_token, user):
	user_id = user['id']
	print('Processing', user_id)

	record = query_api(access_token, user_id, 'person')
	name = record['name']['given-names']['value']
	surname = record['name']['family-name']['value']
	bio = record['biography']['content']
	mail = record['emails']['email'][0]['email']
	website = record['researcher-urls']['researcher-url'][0]['url']['value']

	try:
		record = query_api(access_token, user_id, 'activities')
		role = record['employments']['employment-summary'][0]['role-title']
		org = record['employments']['employment-summary'][0]['organization']['name']
	except:
		# if no employment, this is a student
		role = 'PhD Student'
		org = 'Università Ca\' Foscari Venezia'

	return (name, surname, user['photo'], mail, website, role, org, bio), record['works']['group']

def parse_work(access_token, min_date, max_date, work):
	year = int(work['work-summary'][0]['publication-date']['year']['value'])
	if work['work-summary'][0]['publication-date']['month'] is not None:
		month = int(work['work-summary'][0]['publication-date']['month']['value'])
	else:
		month = 1
	if work['work-summary'][0]['publication-date']['month'] is not None:
		day = int(work['work-summary'][0]['publication-date']['day']['value'])
	else:
		day = 1
	pub_date = date(year, month, day)
	if pub_date < min_date or pub_date > max_date:
		return None

	workrecord = query_path(access_token, work['work-summary'][0]['path'])
	title = workrecord['title']['title']['value']
	pubtype = workrecord['type']
	where = workrecord['journal-title']['value']
	doi = None
	for extid in workrecord['external-ids']['external-id']:
		#print(extid)
		if extid['external-id-type'] == 'doi':
			doi = extid['external-id-value']
			break
	contribs = list()
	for contributor in workrecord['contributors']['contributor']:
		contribs += [contributor['credit-name']['value']]
	return (title, pub_date, pubtype, where, doi, contribs)

def by_date(publication):
	return publication[1]

def readable(kind):
	r = kind.lower().replace('_', ' ')
	if r == 'book':
		r = 'book chapter'
	elif r == 'other':
		r = 'article'
	return r

def populate_people_page(people):
	with open('../people.md', 'w') as file:
		file.write("""---
layout: page
title: People
---
""")
		for person in people:
			print("Adding", person[0], person[1], "to the People page")
			file.write("""
<div class="div-person-table">
	<div class="div-person-table">
		<img class="div-person-table-col" src="{{{{ site.baseurl }}}}/images/{picture}"/>
		<div class="div-person-table-multicol">
			<h3>{name} {surname}</h3>
			<h5>{position} @ {location}</h5>
			Email: <a href="mailto:{mail}">{mail}</a><br/>
			Website: <a href="{website}">{website}</a>
		</div>
	</div>	
</div>
{bio}
<br/><br/>

""".format(
	name=person[0], 
	surname=person[1], 
	picture=person[2], 
	mail=person[3], 
	website=person[4], 
	position=person[5], 
	location=person[6], 
	bio=person[7]))

def add_news(publication):
	newsname = '{year}-{month}-{day}-paper-{hash}'.format(
		year=publication[1].year, 
		month=publication[1].month, 
		day=publication[1].day, 
		hash=hashlib.md5(publication[0].encode('utf-8')).hexdigest())
	print("Generating news for", publication[0], "(", newsname, ")")		
	with open('../news/_posts/{fname}.md'.format(fname=newsname), 'w') as news:
		news.write("""---
layout: page
title: '{startingkind} published in "{venue}"'
---

<small>{{{{ page.date | date: "%-d %B %Y" }}}}</small>

The {kind} "{title}", by {authors}, has just been published in "{venue}"! Available [here](https://doi.org/{doi}).
""".format(
	authors=', '.join(publication[5]), 
	title=publication[0], 
	venue=publication[3], 
	year=publication[1].year, 
	month=publication[1].month, 
	day=publication[1].day, 
	doi=publication[4], 
	kind=readable(publication[2]),
	startingkind=readable(publication[2]).capitalize()))

def populate_publications_page(publications):
	with open('../publications.md', 'w') as file:
		file.write("""---
layout: page
title: Publications
---
""")
		curryear = None
		for publication in publications:
			year = publication[1].year
			if curryear is None:
				curryear = year
				file.write('## {year}\n\n'.format(year=curryear))
			elif year != curryear:
				curryear = year
				file.write('## {year}\n\n'.format(year=curryear))

			print("Adding", publication[0], "to the Publications page")
			file.write('{authors}: _"{title}"_, in {venue} [[DOI]](https://doi.org/{doi})\n\n'.format(
				authors=', '.join(publication[5]), 
				title=publication[0], 
				venue=publication[3], 
				doi=publication[4]))

if __name__ == '__main__':
	with open('users.yaml', 'r') as yamlfile:
	    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
	print('Configuration read successfully')

	access_token = sys.argv[1]
	people = list()
	publications = list()

	for user in data['users']:
		person, works = parse_user(access_token, user)
		print(person)
		people += [person]

		min_date = user['from']
		max_date = date.today() if user['to'] == 'today' else user['to']
		for work in works:
			publication = parse_work(access_token, min_date, max_date, work)	
			if publication is None:
				continue
			doi = publication[4]
			if doi is not None and not any(doi == pub[4] for pub in publications):
				# avoid duplicates
				print(publication)
				publications += [publication]

	publications = sorted(publications, key=by_date)
	populate_people_page(people)
	populate_publications_page(reversed(publications))
	
	# cleanup news folder
	if os.path.exists('../news/_posts/'):
		shutil.rmtree('../news/_posts/')
	os.makedirs('../news/_posts/')
	
	for publication in reversed(publications):
		add_news(publication)
