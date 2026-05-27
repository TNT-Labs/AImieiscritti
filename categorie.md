---
layout: page
title: Categorie
permalink: /categorie/
---

{% for category in site.categories %}
## {{ category[0] | capitalize }}
<ul>
{% for post in category[1] %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <small>— {{ post.date | date: "%-d/%m/%Y" }}</small></li>
{% endfor %}
</ul>
{% endfor %}
