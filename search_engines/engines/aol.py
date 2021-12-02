from .yahoo import Yahoo
from ..config import PROXY, TIMEOUT


class Aol(Yahoo):
    '''Seaches aol.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Aol, self).__init__(proxy, timeout)
        self._base_url = u'https://search.aol.com'
        self._set_search_tools({
            'date': {
                '1h': 'tbs=qdr:h',
                '1d': 'tbs=qdr:d',
                '1w': 'tbs=qdr:w',
                '1m': 'tbs=qdr:m',
                '1y': 'tbs=qdr:y'
            }
        })

    def _first_page(self, timeframe=None):  # NOTE: unused timeframe
        '''Returns the initial page and query.'''
        url_str = u'{}/aol/search?q={}&ei=UTF-8&nojs=1'
        url = url_str.format(self._base_url, self._query)
        self._http_client.get(self._base_url)
        return {'url': url, 'data': None}
