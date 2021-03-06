"""Site logic for parsing hpfanficarchive.com
fanfiction stories"""
from ff_scrape.storybase import Chapter
from ff_scrape.errors import URLError
from ff_scrape.sites.base import Site
from ff_scrape.standardization import *
from urllib.parse import urljoin
from datetime import datetime
import re
import time

class HPFanficArchive(Site):
    """Provides the logic to parse fanfics from hpfanficarchive.com"""

    def __init__(self, site_params={}):
        super().__init__(logger_name='ff_scrape.site.HPFanficArchive',
                         site_params=site_params)
        self.chapter_list = []

    def set_domain(self):
        """Sets the domain of the fanfic to Fanfiction.net"""
        self._fanfic.domain = "HP Fanfic Archive"

    def can_handle(self, url: str):
        if 'hpfanficarchive.com/' in url:
            return True
        return False

    def correct_url(self, url: str):
        """Perform the necessary steps to correct the supplied URL so the parser can work with it"""
        # check if url has "http://" prefix
        # check if url has "http://" prefix
        if "http://" not in url:
            if "https://" not in url:
                url = "http://" + url
        url_split = url.split("/")
        # correct URL as needed for script
        if len(url_split) == 5:
            if url_split[4] == '':
                raise URLError('Unknown URL format')
            else:
                # extract the story id for easy access to the index page
                story_split = url_split[4].split('?')
                if len(story_split) == 2:
                    story_data_split = story_split[1].replace('&', '=').split('=')
                    if len(story_data_split) < 2:
                        raise URLError('No Story ID given')
                    sid = story_data_split[1]
                else:
                    raise URLError('Unknown URL format')
        else:
            raise URLError('Unknown URL format')
        url_fixed = '/'.join(url_split)

        # prep url so it is easy to go to the index page
        url = urljoin(url_fixed, 'viewstory.php?sid=' + str(sid))
        return url

    def check_story_exists(self):
        """Verify that the fanfic exists"""
        divs = self._soup.findAll('div', {'class': 'errortext'})
        if len(divs) > 0:
            self.log_warn("Story doesn't exist.")
            return False
        return True

    def cleanup_custom_vars(self):
        self.chapter_list = []

    def record_story_metadata(self):
        """Record the metadata of the fanfic"""
        content_containers = self._soup.find_all(True, {'class': 'content'})
        self._fanfic.raw_index_page = self._soup.prettify()
        # should be length 5
        # 0 => story tags
        # 1 => parent wrapper of story info
        # 2 => child wrapper of story info
        # 3 => story notes
        # 4 => chapter list

        # build chapter list
        chapter_regex = re.compile("^viewstory.php.*")
        for link in content_containers[4].find_all('a'):
            if chapter_regex.match(link.attrs['href']):
                self.chapter_list.append({'name': link.text, 'link': link.attrs['href']})

        # extract metadata
        summary_text = ""
        parsed_key = ""
        pattern = "%B %d, %YT%H:%M:%S"
        loop_list = content_containers[2].find_all(['span','p', 'a'])
        for item in loop_list:
            if item.name == 'span':
                # this is a key in the metadata
                # note which one we saw
                parsed_key = item.text.replace(':', '').lower().strip()
                if parsed_key == 'rated':
                    self._fanfic.rating = standardize_rating(item.next_sibling)
                elif parsed_key == 'published':
                    self._fanfic.published = datetime.strptime(item.next_sibling.next_sibling + "T00:00:00", pattern)
                elif parsed_key == 'updated':
                    self._fanfic.updated = datetime.strptime(
                        item.next_sibling.next_sibling.next_sibling + "T00:00:00", pattern
                    )
                elif parsed_key == 'completed':
                    if item.next_sibling.strip() == 'Yes':
                        self._fanfic.status = standardize_status("Complete")
            else:
                # we have found a value for the current parsed_key
                if parsed_key == 'summary':
                    summary_text += item.text
                elif parsed_key == 'categories':
                    category = standardize_category(item.text)
                    if category is not None:
                        self._fanfic.add_category(category)
                elif parsed_key == 'status':
                    self._fanfic.status = standardize_status(item.text)
                elif parsed_key == 'characters':
                    self._fanfic.add_character(standardize_character(item.text))
                elif parsed_key == 'pairings':
                    self._fanfic.add_pairing(item.text.split("/"))
                elif parsed_key == 'genres':
                    self._fanfic.add_genre(standardize_genre(item.text))
                elif parsed_key == 'warnings':
                    warning = standardize_warning(item.text)
                    if warning is not None:
                        self._fanfic.add_warning(warning)
        self._fanfic.summary = summary_text

        # set author and title
        title_container = self._soup.find(id='pagetitle')
        title_links = title_container.find_all('a')
        self._fanfic.title = title_links[0].text
        author = title_links[1].text
        author_url = urljoin(self._url, title_links[1].attrs['href'])
        self._fanfic.add_author(author, author_url)

        # set universe to hard coded value due to this being a HP only site
        self._fanfic.add_universe("Harry Potter")

    def record_story_chapters(self):
        """Record the chapters of the fanfic"""
        # get the chapters
        for chapter in self.chapter_list:
            time.sleep(self._chapter_sleep_time)
            self.log_debug("Downloading chapter:" + chapter['name'])
            url_fixed = urljoin(self.url, chapter['link'])

            # get page
            self._update_soup(url=url_fixed)
            story = self._soup.find(id='story')

            chapter_object = Chapter()
            chapter_object.processed_body = story.prettify()
            chapter_object.raw_body = self._soup.prettify()
            chapter_object.word_count = len(story.text.split())
            chapter_object.name = chapter['name']
            self._fanfic.add_chapter(chapter_object)
