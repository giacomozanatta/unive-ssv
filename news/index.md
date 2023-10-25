---
layout: page
title: News
---

{% assign first_news = site.categories.news | first %}
{% assign year = first_news.date | date: "%Y" %}

<h2>{{ year }}</h2>
<ul class="list-page">
{% for post in site.categories.news %}
	{% assign cur_year = post.date | date: "%Y" %}
	{% if cur_year != year %}
</ul>
		{% assign year = cur_year %} 
<h2>{{ year }}</h2>
<ul class="list-page">
	{% endif %}
	<li>
      <a href="{{ post.url }}">{{ post.title }}</a><br/>
      <small>{{ post.date | date: "%-d %B %Y" }}</small>
    </li>
{% endfor %}
</ul>
