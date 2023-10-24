---
layout: page
title: News
---

{% assign first_news = site.categories.news | first %}
{% assign year = first_news.date | date: "%Y" %}

<h3>{{ year }}</h3>
<ul>
{% for post in site.categories.news %}
	{% assign cur_year = post.date | date: "%Y" %}
	{% if cur_year != year %}
</ul>
		{% assign year = cur_year %} 
<h3>{{ year }}</h3>
<ul>
	{% endif %}
	<li>
      <a href="{{ post.url }}">{{ post.title }}</a><br/>
      <small>{{ post.date | date: "%-d %B %Y" }}</small>
    </li>
{% endfor %}
</ul>
