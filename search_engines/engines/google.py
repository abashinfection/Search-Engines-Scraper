from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..utils import unquote_url


class DateSearchToolValueError(Exception):
    pass


class DateSearchToolNotConfigured(Exception):
    pass


class Google(SearchEngine):
    '''Searches google.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT, timeframe=None):
        super(Google, self).__init__(proxy, timeout)
        self._base_url = 'https://www.google.com'
        self._delay = (2, 6)
        self._current_page = 1
        self.set_headers({'User-Agent': FAKE_USER_AGENT})
        self._set_search_tools({
            'date': {
                '1h': 'qdr:h',
                '1d': 'qdr:d',
                '1w': 'qdr:w',
                '1m': 'qdr:m',
                '1y': 'qdr:y'
            }
        })

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[href]',
            'title': 'a',
            'text': 'span > span',
            'links': 'div#search div[class=g]',
            'next': 'a[href][aria-label="Page {page}"]'
        }
        return selectors[element]

    def _first_page(self):
        '''Returns the initial page and query.'''
        date_q_param = ''

        if self._timeframe:
            if 'date' in self._search_tools:
                q_param = self._search_tools['date'].get(self._timeframe, None)
                if not q_param:
                    msg = f"Unsupported value for Date Search Tool: {self._timeframe}"
                    raise DateSearchToolValueError(msg)
                else:
                    date_q_param = f"&{q_param}"
            else:
                msg = "Date Search Tool not configured"
                raise DateSearchToolNotConfigured(msg)

        url = u'{}/search?q={}{}'.format(
            self._base_url,
            self._query,
            date_q_param
        )
        return {'url': url, 'data': None}

    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        self._current_page += 1
        selector = self._selectors('next').format(page=self._current_page)
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = None
        if next_page:
            url = self._base_url + next_page
        return {'url': url, 'data': None}

    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results item.'''
        selector = self._selectors('url')
        url = self._get_tag_item(tag.select_one(selector), item)

        if url.startswith(u'/url?q='):
            url = url.replace(u'/url?q=', u'').split(u'&sa=')[0]
        return unquote_url(url)

    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        selector = self._selectors('text')
        tag = tag.select(selector) or [None]
        return self._get_tag_item(tag[-1], item)
