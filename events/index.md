---
layout: page
title: Events
---

{% assign first_event = site.categories.events | first %}
{% assign year = first_event.date | date: "%Y" %}

<h3>{{ year }}</h3>
<ul>
{% for post in site.categories.events %}
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
