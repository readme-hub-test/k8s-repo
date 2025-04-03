# Organization Repositories

Here are the README files from all the repositories in the organization:

{% for repo in site.pages %}
## {{ repo.title }}

{% include 'readmes/' + repo.title + '.md' %}
{% endfor %}
