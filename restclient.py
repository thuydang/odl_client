import requests
from requests import Request, Session

from requests.auth import HTTPBasicAuth

class RestClient():
  """All restful client should be
  """

  def __init__(self, **kwargs):
    '''
    '''
    self.protocol = 'http'
    self.host = '127.0.0.1'
    self.port = '8181'
    self.username = 'admin'
    self.password = 'admin'
    # html doc path
    self.path = ''
    # params to the url
    self.params = ''
    self.session = Session()

    if kwargs:
      for k,v in kwargs.iteritems():
        setattr(self, k, v)

    if 'base_url' not in kwargs:
      self.base_url = self.protocol + "://" + self.host + ":" + self.port

    if 'url' not in kwargs:
      self.url = self.base_url + self.path

    if 'username' in kwargs:
      self.session.auth = HTTPBasicAuth(self.username, self.password)

  def get_base_url(self):
    return self.base_url

  def set_path(self, path):
    self.path = path
    self.url = self.base_url + self.path

  def get(self):
    return self.session.get(self.url)

  def send_request(self, request):
    s = self.session
    p_request = s.prepare_request(request)
    return s.send(p_request)

class OdlEndpoint():
  '''*args: will be concatenated to form url. '/' is added b/w arguments.
     **kwargs: will be turned to key/value for specification of node/node:id.
  '''
  def __init__(self, *args, **kwargs):
    self._url = ''
    for arg in args:
      self._url = self._url + arg
      if arg != args[-1]:
        self._url += '/'

    if kwargs:
      for k,v in kwargs.iteritems():
        self._url += '/' + k + '/' + v

  def url(self):
    return self._url


class OdlRequest(requests.Request):
  def __init__(self, *args, **kwargs):
    super(OdlRequest, self).__init__(*args)

    if kwargs:
      for k,v in kwargs.iteritems():
        setattr(self, k, v)


class OdlClient(RestClient):
  '''
  '''
  def __init__(self, **kwargs):
    RestClient.__init__(self, **kwargs)


