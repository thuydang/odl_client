from tools.xml_parser_tools import XMLtoDictParserTools
import odl_endpoint
from restclient import RestClient, OdlClient, OdlRequest, OdlEndpoint
from requests import Request
from xml.dom.minidom import parse, parseString

import websocket # pip install websocket-client
import threading
from time import sleep
import json

def test_odl():
  client = RestClient(base_url='http://192.168.201.43:8181', path='', username='admin', password='admin')
  print client.get().text

def test_url():
  client = RestClient(url='https://api.github.com/users/thuydang')
  client = RestClient(base_url='https://api.github.com', path='/users/thuydang')
  print client.get().text

def test_session():
  #test_odl()

  #client = RestClient(base_url='http://192.168.201.43:8181', path='/apidoc/explorer/index.html', username='admin', password='admin')
  client = RestClient(base_url='http://192.168.201.43:8181', path='/restconf/operational/network-topology:network-topology', username='admin', password='admin')
  client = RestClient(base_url='http://192.168.201.43:8181', username='admin', password='admin')
  client.set_path('/restconf/operational/network-topology:network-topology/topology/flow:1')

  print client.get().json()
  print client.get().text

def test_get():
  client = OdlClient(base_url='http://192.168.201.43:8181', username='admin', password='admin')

  # test 1
  endpoint = OdlEndpoint(client.get_base_url(),odl_endpoint.RESTCONF, odl_endpoint.OPERATIONAL,
      odl_endpoint.NETWORK_TOPOLOGY)

  endpoint = OdlEndpoint(client.get_base_url(),
      odl_endpoint.RESTCONF,
      odl_endpoint.OPERATIONAL,
      odl_endpoint.NETWORK_TOPOLOGY,
      topology='flow:1')

  request = Request('GET', endpoint.url())

  # test 2

  endpoint = OdlEndpoint(client.get_base_url(), 'restconf/operations/sal-remote:create-data-change-event-subscription')

  #headers = None
  headers = {'Content-type': 'application/xml', 'Accept': 'application/xml'}

  #body = json.dumps()
  body = '<input xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:remote"><path xmlns:a="urn:opendaylight:inventory">/a:nodes</path><datastore xmlns="urn:sal:restconf:event:subscription">CONFIGURATION</datastore><scope xmlns="urn:sal:restconf:event:subscription">BASE</scope></input>'

  request = OdlRequest('POST', endpoint.url(), headers=headers, data = body)

  #
  r = client.send_request(request)
  print '+++ The URL was: %s \n' % r.url
  print r.text

## web socket Thread
def on_message(ws, message):
  print message

def on_error(ws, error):
  print error

def on_close(ws):
  print "### closed ###"

## main
def main():
  #client = RestClient(base_url='http://192.168.201.43:8181', path='/operational/network-topology:network-topology', username='admin', password='admin')

  client = OdlClient(base_url='http://192.168.201.43:8181', username='admin', password='admin')

  endpoint = OdlEndpoint(client.get_base_url(),odl_endpoint.RESTCONF, odl_endpoint.OPERATIONAL,
      odl_endpoint.NETWORK_TOPOLOGY)

  endpoint = OdlEndpoint(client.get_base_url(),
      odl_endpoint.RESTCONF,
      odl_endpoint.OPERATIONAL,
      odl_endpoint.NETWORK_TOPOLOGY,
      topology='flow:1')

  print '++++ Subscribe ------'

  endpoint = OdlEndpoint(client.get_base_url(), 'restconf/operations/sal-remote:create-data-change-event-subscription')

  #headers = None
  headers = {'Content-type': 'application/xml', 'Accept': 'application/xml'}

  #body = json.dumps()
  body_dict = {}
  body_xml = '<input xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:remote"><path xmlns:a="urn:opendaylight:inventory">/a:nodes</path><datastore xmlns="urn:sal:restconf:event:subscription">CONFIGURATION</datastore><scope xmlns="urn:sal:restconf:event:subscription">BASE</scope></input>'

  data = body_xml

  request = OdlRequest('POST', endpoint.url(), headers=headers, data = data)

  r = client.send_request(request)
  print '+++ The URL was: %s \n' % r.url

  # get stream-name with dict.
  # ERROR: CONFIGURATION, BASE must stay capitalized after conversion.
  #output_dict = XMLtoDictParserTools.parseDOM_ToDict( parseString(r.text)._get_documentElement())
  # {'output': {'stream-name': 'opendaylight-inventory:nodes/datastore=configuration/scope=base'}}

  # get stream-name from xml. See example https://docs.python.org/2/library/xml.dom.minidom.html
  stream_name = parseString(r.text).getElementsByTagName("stream-name")[0].childNodes[0].data


  print '++++ Request socket ----------'

  #endpoint = OdlEndpoint(client.get_base_url(), 'restconf/streams/stream', 'opendaylight-inventory:nodes/datastore=CONFIGURATION/scope=BASE')
  #endpoint = OdlEndpoint(client.get_base_url(), 'restconf/streams/stream', output_dict['output']['stream-name'])
  endpoint = OdlEndpoint(client.get_base_url(), 'restconf/streams/stream', stream_name)

  #headers = None
  headers = {'Content-type': 'application/xml', 'Accept': 'application/xml', 'Cache-Control': 'no-cache'}

  request = OdlRequest('GET', endpoint.url(), headers=headers)

  r = client.send_request(request)

  print '+++ The URL was: %s \n' % r.url

  #print r.headers
  # {'content-length': '0', 'location': 'ws://192.168.201.43:8185/opendaylight-inventory:nodes/datastore=CONFIGURATION/scope=BASE', 'server': 'Jetty(8.1.15.v20140411)'}
  ws_location = r.headers['location']


  print '++++ Open socket & wait for notification -----------'

  websocket.enableTrace(True)
  ws = websocket.WebSocketApp(ws_location,
      on_message = on_message,
      on_error = on_error,
      on_close = on_close)

  wst = threading.Thread(target=ws.run_forever)
  #wst.daemon = True
  wst.start()


  print '++++ Create Sample Node -----------'

  endpoint = OdlEndpoint(client.get_base_url(), 'restconf/config')

  headers = {'Content-type': 'application/xml', 'Accept': 'application/xml'}

  body_xml = '<nodes xmlns="urn:opendaylight:inventory"><node><id>166</id></node></nodes>'
  data = body_xml

  request = OdlRequest('POST', endpoint.url(), headers=headers, data = data)

  r = client.send_request(request)
  print '+++ The URL was: %s \n' % r.url

  conn_timeout = 5
  while not ws.sock.connected and conn_timeout:
    sleep(1)
    conn_timeout -= 1

  msg_counter = 0
  #while ws.sock.connected:
  #  ws.send('Hello world %d'%msg_counter)
  #  sleep(1)
  #  msg_counter += 1

if __name__ == '__main__':
  main()
