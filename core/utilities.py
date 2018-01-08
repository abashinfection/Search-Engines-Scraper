import requests
import csv
import io
from . import config


class Http: 
	'''Preforms HTTP requests.'''
	uastring = config.user_agent
	
	def __init__(self, timeout=config.timeout, proxy=config.proxy):
		self.http = requests.session()
		self.http.headers['User-Agent'] = self.uastring
		self.timeout = timeout
		self.http.proxies = self._set_proxy(proxy)
	
	def get(self, page, ref=None): 
		'''GET request.'''
		headers = {'Referer':(ref if ref else page)}
		try: 
			req = self.http.get(page, headers=headers, timeout=self.timeout)
		except Exception as e: 
			return {'http':0, 'html':str(e)}
		return {'http':req.status_code, 'html':req.text}
	
	def post(self, page, data, ref=None): 
		'''POST request.'''
		headers = {'Referer':(ref if ref else page)}
		try : 
			req = self.http.post(page, data=data, headers=headers, timeout=self.timeout)
		except Exception as e: 
			return {'http':0, 'html':str(e)}
		return {'http':req.status_code, 'html':req.text}
	
	def _set_proxy(self, proxy):
		'''Sets HTTP, HTTPS proxy.'''
		if proxy:
			if proxy is True:
				proxy = {'http':config.tor, 'https':config.tor}
			elif '://' not in str(proxy) or len(str(proxy).split(':')) != 3: 
				print('Invalid proxy format: {}'.format(proxy))
			else: 
				proxy = {'http':proxy, 'https':proxy}
		return proxy


def unquote(url):
	'''decodes urls.'''
	return requests.utils.unquote(url)

def _is_url(link): 
	'''Checks if link is URL'''
	parts = link.split('/')
	return len(parts) > 2 and link.split('://')[0].lower() in ('http', 'https') and '.' in parts[2]
	
def _domain(url): 
	'''Returns domain form URL'''
	if _is_url(url): 
		return url.split('/')[2].replace('www.', '') 


class Html: 
	'''HTML template.'''
	
	html = u'''
	<html>
	<meta charset="UTF-8">
	<head>
	<title>Search Report</title>
	<style>
	body {{ background-color:#f5f5f5; }} 
	a {{ font-size:14px; }} 
	a:link {{ color: #262626; }} 
	a:visited {{ color: #808080; }} 
	th {{ font-size:14px; text-align:left; padding:1px; }} 
	td {{ font-size:14px; text-align:left; padding:1px; }} 
	</style>
	</head>
	<body>
	<table>
	<tr><th>Query: {query}</th></tr>
	<tr><td> </td></tr>
	</table>
	{table}
	</body>
	</html>
	'''
	
	table = u'''
	<table>
	<tr><th>{engine} search results: </th></tr>
	</table>
	<table>
	{rows}
	</table>
	<br>
	'''
	
	row = u'''
	<tr>
	<td>{number})</td>
	<td><a href="{link}" target="_blank">{link}</a></td>
	{data}
	</tr>
	'''
	
	data = u'''<tr><td></td><td>{}</td></tr>\n'''


def _encode(s, errors='replace'):
	'''Encodes unicode to str - str to bytes.'''
	return s if type(s) is bytes else s.encode('utf-8', errors=errors)
	
def _decode(s, errors='replace'):
	'''Decodes bytes to str, str to unicode.'''
	return s.decode('utf-8', errors=errors) if type(s) is bytes else s

def _write(data, path):
	'''
	Creates report files.
	:param data str or list
	:param fname str
	''' 
	try: 
		if config.python_version == 2 and type(data) is list:
			f = io.open(path, 'wb') 
		else: 
			f = io.open(path, 'w', encoding='utf-8', newline='')
		if type(data) is list: 
			writer = csv.writer(f)
			writer.writerows(data)
		else:
			f.write(data)
		f.close()
		print('Report file: ' + path)
	except Exception as e: 
		print(e)
