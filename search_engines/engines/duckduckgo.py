from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT
from ..utils import DateSearchToolValueError
from ..utils import DateSearchToolNotConfigured


class Duckduckgo(SearchEngine):
    '''Searches duckduckgo.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Duckduckgo, self).__init__(proxy, timeout)
        self._base_url = 'https://html.duckduckgo.com/html/'
        self.set_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        self._set_search_tools({
            'date': {
                '1d': 'df=d',
                '1w': 'df=w',
                '1m': 'df=m',
                '1y': 'df=y'
            }
        })

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result__snippet',
            'title': 'h2.result__title a',
            'text': 'a.result__snippet',
            'links': 'div.results div.result.results_links.results_links_deep.web-result',
            'next': {'forms': 'div.nav-link > form', 'inputs': 'input[name]'}
        }
        return selectors[element]

    def _first_page(self, timeframe=None):
        '''Returns the initial page and query.'''
        date_q_param = None

        if timeframe:
            if 'date' in self._search_tools:
                date_q_param = self._search_tools['date'].get(timeframe, None)
                if not date_q_param:
                    msg = f"Unsupported value for Date Search Tool: {timeframe}"
                    raise DateSearchToolValueError(msg)
            else:
                msg = "Date Search Tool not configured"
                raise DateSearchToolNotConfigured(msg)

        data = {'q': self._query, 'b': '', 'kl': 'us-en'}
        if date_q_param:
            date_param_name, date_param_value = date_q_param.split('=')
            data[date_param_name] = date_param_value
        return {'url': self._base_url, 'data': data}

    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        forms = tags.select(selector['forms'])
        url, data = None, None

        if forms:
            form = forms[-1]
            data = {i['name']: i.get('value', '') for i in form.select(selector['inputs'])}
            url = self._base_url
        return {'url': url, 'data': data}
