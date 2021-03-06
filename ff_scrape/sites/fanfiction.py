from ff_scrape.storybase import Chapter
from ff_scrape.errors import URLError
from ff_scrape.sites.base import Site
from ff_scrape.standardization import *
from urllib.parse import urljoin
from datetime import datetime
import re
import time


class Fanfiction(Site):
    """Provides the logic to parse fanfics from fanfiction.net"""

    def __init__(self, site_params={}):
        super().__init__(logger_name='ff_scrape.site.Fanfiction',
                         site_params=site_params)
        self.chapter_list = []

    def set_domain(self) -> None:
        """Sets the domain of the fanfic to Fanfiction.net"""
        self._fanfic.domain = "Fanfiction.net"

    def can_handle(self, url: str) -> bool:
        if 'fanfiction.net/' in url:
            return True
        return False

    def cleanup_custom_vars(self):
        self.chapter_list = []

    def correct_url(self, url: str) -> str:
        """Perform the necessary steps to correct the supplied _url so the parser can work with it"""
        # check if _url has "https://" or "http://" prefix
        if "http://" not in url:
            if "https://" not in url:
                url = "http://%s" % url
        _url_split = url.split("/")
        if len(_url_split) < 5:
            raise URLError('Unknown URL format')
        # correct for https
        if _url_split[0] == 'http:':
            _url_split[0] = "https:"
        # correct for mobile _url
        if _url_split[2] == "m.fanfiction.net":
            _url_split[2] = "www.fanfiction.net"
        # correct _url as needed for script
        if _url_split[4] == '':
            raise URLError('No Story ID given')
        # adds chapter id is 1 and trailing /
        if len(_url_split) == 5:
            _url_split.append('1')
            _url_split.append('')
        # sets chapter id to 1 and trailing /
        elif len(_url_split) == 6:
            _url_split[5] = '1'
            _url_split.append('')
        # sets chapter id to 1 and removes chapter title
        elif len(_url_split) == 7:
            _url_split[5] = '1'
            _url_split[6] = ''
        else:
            raise URLError('Unknown URL format')
        url = '/'.join(_url_split)
        tmp = urljoin(url, ' ')[0:-2]
        return tmp

    def check_story_exists(self) -> bool:
        """Verify that the fanfic exists"""
        warning = self._soup.findAll("div", {"class": "panel_warning"})
        if len(warning) == 1:
            return False
        return True

    def record_story_metadata(self) -> None:
        """Record the metadata of the fanfic"""

        # get section of code where the universe is listed
        universe_tags = self._soup.find('div', {'id': 'pre_story_links'}).find_all('a', href=True)
        # check if it is a crossover type
        universe_str = universe_tags[-1].string.replace(" Crossover", "")
        for universe in universe_str.split(" + "):
            self._fanfic.add_universe(universe)

        top_profile = self._soup.find(id="profile_top")
        self._fanfic.raw_index_page = self._soup.prettify()

        # record title and author
        self._fanfic.title = top_profile.b.string
        author = top_profile.a.string
        author_url = "https://www.fanfiction.net/" + top_profile.a.attrs['href']
        # need to remove author name from url in case author changes their name in the future
        author_url = urljoin(author_url, ' ').strip()
        self._fanfic.add_author(author, author_url)

        # record summary
        self._fanfic.summary = top_profile.find('div', attrs={'class': 'xcontrast_txt'}).string

        # record published and updated timestamps
        times = top_profile.find_all(attrs={'data-xutime': True})
        timestamps = []
        timestamps.append(datetime.fromtimestamp(int(times[0]['data-xutime'])))

        if len(times) == 2:
            timestamps.append(datetime.fromtimestamp(int(times[1]['data-xutime'])))
        self._fanfic.published = min(timestamps)
        self._fanfic.updated = max(timestamps)

        # record rating
        rating_tag = top_profile.find('a', {'target': 'rating'})
        rating_split = rating_tag.string.split(" ")
        self._fanfic.rating = standardize_rating(rating_split[-1])

        # the remaining attributes need to be positionally extracted from story meta
        metadata_tags = self._soup.find('span', {'class': 'xgray xcontrast_txt'})
        metadata = [s.strip() for s in metadata_tags.text.split('-')]
        genres = metadata[2].split('/')
        for genre in genres:
            self._fanfic.add_genre(standardize_genre(genre))
        if 'Complete' in metadata:
            self._fanfic.status = 'Complete'
        else:
            self._fanfic.status = 'WIP'

        # extract people and pairings
        people_str = metadata[3]
        pairing_match = re.compile(r'(\[.*?\])')
        for pairing in pairing_match.findall(people_str):
            pairing = pairing.replace('[', '').replace(']', '')
            pairing_arr = pairing.split(', ')
            for person in pairing_arr:
                person = standardize_character(person)
                if person is not None:
                    self._fanfic.add_character(standardize_character(person))
            self._fanfic.add_pairing(pairing_arr)
        non_pairing = pairing_match.sub('', people_str)
        non_pairing = non_pairing.strip()
        for person in non_pairing.split(', '):
            person = standardize_character(person)
            if person is not None:
                self._fanfic.add_character(standardize_character(person))
        chap_select = self._soup.find(id='chap_select')
        if chap_select is not None:
            for entry in chap_select.contents:
                self.chapter_list.append({'name': entry.text, 'link': entry.attrs['value']})
        else:
            self.chapter_list.append({'name': self._fanfic.title, 'link': '1'})

    def record_story_chapters(self) -> None:
        """Record the chapters of the fanfic"""
        # get the chapters
        for chapter in self.chapter_list:
            time.sleep(self._chapter_sleep_time)
            chapter_object = Chapter()
            self.log_debug("Downloading chapter: " + chapter['link'])
            self._update_soup(url=self._url[0:-1]+chapter['link'])
            chapter_text = ""
            chapter_count = 0
            story_tag = self._soup.find(id="storytextp")
            for content in story_tag.find_all(['p', 'hr']):
                chapter_text += content.prettify()
                chapter_count += len(content.text.split())
            chapter_object.processed_body = chapter_text
            chapter_object.raw_body = self._soup.prettify()
            chapter_object.word_count = chapter_count
            chapter_object.name = chapter['name']
            self._fanfic.add_chapter(chapter_object)
