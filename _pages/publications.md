---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% include base_path %}

## Full publication list

For the complete, up-to-date list of my publications, see [my INSPIRE-HEP author profile](https://inspirehep.net/literature?sort=mostrecent&size=25&page=1&q=find%20a%20thibeau%20wouters%20and%20not%20fa%20abac%20and%20not%20fa%20abbott%20and%20not%20fa%20acernese).

{% assign arxiv_publications = site.publications | where_exp: "post", "post.paperurl contains 'arxiv.org'" | sort: "inspire_rank" %}
{% for post in arxiv_publications %}
  {% include archive-single.html %}
{% endfor %}
