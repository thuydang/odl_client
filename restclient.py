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

  def get(self):
    return self.session.get(self.url)
