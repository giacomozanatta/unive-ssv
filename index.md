---
layout: home
---

<center>
	<img src="{{ site.baseurl }}/images/ssv.png" alt="{{ site.title | escape }}" style="max-height: 200px; margin-bottom: 20px;"/>
</center>

The Software and System Verification group @ Ca’ Foscari University of Venice is a research team focused on static analysis and its applications.

<style>
.column {
	float: left;
	width: 50%;
}

/* Clear floats after the columns */
.row:after {
	content: "";
	display: table;
	clear: both;
}
</style>

<div class="row">
	<div class="column">
		<h2>Latest news</h2>
		<ul class="list-page">
{% for post in site.categories.news limit: 2 %}
			<li>
				<a href="{{ post.url }}">{{ post.title }}</a><br/>
				<small>{{ post.date | date: "%-d %B %Y" }}</small>
			</li>
{% endfor %}
		</ul>
		<a href="{{ site.baseurl }}/news/">All news ({{ site.categories.news.size }}) »</a><br><br>
	</div>
  	<div class="column">
  		<h2>Latest events</h2>
		<ul class="list-page">
{% for post in site.categories.events limit: 2 %}
			<li>
				<a href="{{ post.url }}">{{ post.title }}</a><br/>
				<small>{{ post.date | date: "%-d %B %Y" }}</small>
			</li>
{% endfor %}
		</ul>
		<a href="{{ site.baseurl }}/events/">All events ({{ site.categories.events.size }}) »</a><br><br>
	</div>
</div> 

<div class="div-img-table">
<div class="div-img-table-row">
  <img class="div-img-table-col" src="{{ site.baseurl }}/images/home-1.jpg"/>
  <img class="div-img-table-col" src="{{ site.baseurl }}/images/home-2.jpg"/>
  <img class="div-img-table-col" src="{{ site.baseurl }}/images/home-3.jpg"/> 
</div>
<div class="div-img-table-row">
  <img class="div-img-table-col" src="{{ site.baseurl }}/images/home-4.jpg"/>
  <img class="div-img-table-col" src="{{ site.baseurl }}/images/home-5.jpg"/>
  <img class="div-img-table-col" src="{{ site.baseurl }}/images/home-6.jpg"/>
</div>
<div class="div-img-table-row">
  <img class="div-img-table-multicol" src="{{ site.baseurl }}/images/home-big.jpg"/>
</div>
</div>
