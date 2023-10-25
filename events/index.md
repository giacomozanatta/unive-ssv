---
layout: page
title: Events
---

{% assign first_event = site.categories.events | first %}
{% assign year = first_event.date | date: "%Y" %}

<h2>{{ year }}</h2>
<ul class="list-page">
{% for post in site.categories.events %}
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
