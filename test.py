from restclient import RestClient

def test_odl():
  client = RestClient(base_url='http://192.168.201.43:8181', path='', username='admin', password='admin')
  print client.get().text

def test_url():
  client = RestClient(url='https://api.github.com/users/thuydang')
  client = RestClient(base_url='https://api.github.com', path='/users/thuydang')
  print client.get().text


def main():
  #test_odl()

  #client = RestClient(base_url='http://192.168.201.43:8181', path='/apidoc/explorer/index.html', username='admin', password='admin')
  client = RestClient(base_url='http://192.168.201.43:8181', path='/operational/network-topology:network-topology', username='admin', password='admin')
  print client.get().text

if __name__ == '__main__':
   main()
