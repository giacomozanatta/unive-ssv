# SSV's website

The website is fully static. Pages for single events, projects and any additional custom page are manually written.

The `CSV` page displays the content of the event page (i.e., under `events/_posts/`) that has `latest_csv` defined in its frontmatter. When a new edition is being prepared, remove such tag from the previous page and add it to the new one.

The `News` page, the `Events` page, and the `index` contain liquid scripts to update their content whenever the site is generated (i.e., after every commit). The list of events and news will thus automatically refresh.

Finally, the python script `scripts/orcid-crawl.py` will retrieve information from ORCID about the members of SSV, and will fill up the `People` page, the `Publications` page, and will generate a news under `news/_posts` for each publication. Information on how to use the script can be found at the beginning of the script itself. A GitHub action will run the script on every commit or everyday at midnight: updates from ORCID will be automatically reflected on those pages. The action can also be ran manually.

Note that for posts (i.e., `news/_posts` and `events/_posts`), Jekyll uses file names for determining the date of the post. For instance, a file named `events/_posts/2023-06-15-tambre-semestral.md` will generate a page named `events/2023/06/15/tambre-semestral.html`. Use appropriate file names.


## Building locally

[GitHub's guide](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/testing-your-github-pages-site-locally-with-jekyll)

* Download ruby from [here](https://rubyinstaller.org/downloads/) or install via `apt/...`
* Install bundler: **gem install bundler**
* Install jekyll: **gem install jekyll**
* Create Gemfile: 
    * **echo "source 'https://rubygems.org'" > Gemfile**
    * **echo "gem 'github-pages', group: :jekyll_plugins" >> Gemfile**
* Install gems: **bundle install**
    * If some gem fails to install, use this: **gem install gem_name -v 'version' --source 'https://rubygems.org/'**
* Create site: **bundle exec jekyll \_3.3.0\_ new . --force**
    * Revert all changes made to *_config.yml* and *index.md* and other staged files
* Change the Gemfile
    * Find a line similar to this: **gem "minima", "~> 2.0"**
    	* Replace with this: **gem "minima", "~> 2.5.1"**
    * Comment line starting with **gem "jekyll"**
    * Uncomment line starting with **gem "github-pages"**
    * Execute **bundle install**
* Execute Jekyll: **bundle exec jekyll serve**
    * If the port is in use, add **--port port_number**
