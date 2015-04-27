from tools.xml_parser_tools import XMLtoDictParserTools
import odl_endpoint
from restclient import RestClient, OdlClient, OdlRequest, OdlEndpoint
from requests import Request
from xml.dom.minidom import parse, parseString

import websocket # pip install websocket-client
import threading
import thread
from time import sleep
import json

import signal
import sys

def signal_term_handler(signal, frame):
  print 'got SIGTERM'
  ws.close()
  sys.exit(0)

## web socket Thread
def on_message(ws, message):
  print message

def on_error(ws, error):
  print error

def on_close(ws):
  print "### closed ###"

def on_open(ws):
  def run(*args):
    while(True):
      pass
  thread.start_new_thread(run, ())

def odl_subscribe():
  global _stream_name
  global client

  print '++++ Subscribe ------'
  client = OdlClient(base_url='http://192.168.201.43:8181', username='admin', password='admin')
  endpoint = OdlEndpoint(client.get_base_url(), 'restconf/operations/sal-remote:create-data-change-event-subscription')
  headers = {'Content-type': 'application/xml', 'Accept': 'application/xml'}
  body_xml = '<input xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:remote"><path xmlns:a="urn:opendaylight:inventory">/a:nodes</path><datastore xmlns="urn:sal:restconf:event:subscription">CONFIGURATION</datastore><scope xmlns="urn:sal:restconf:event:subscription">BASE</scope></input>'
  #body_xml = '<input xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:remote"><path xmlns:a="urn:opendaylight:inventory">/a:nodes/node/openflow:1</path><datastore xmlns="urn:sal:restconf:event:subscription">CONFIGURATION</datastore><scope xmlns="urn:sal:restconf:event:subscription">BASE</scope></input>'
  data = body_xml
  request = OdlRequest('POST', endpoint.url(), headers=headers, data = data)
  r = client.send_request(request)
  # get stream-name with dict.
  # ERROR: CONFIGURATION, BASE must stay capitalized after conversion.
  #output_dict = XMLtoDictParserTools.parseDOM_ToDict( parseString(r.text)._get_documentElement())
  # {'output': {'stream-name': 'opendaylight-inventory:nodes/datastore=configuration/scope=base'}}
  print r.text
  # get stream-name from xml. See example https://docs.python.org/2/library/xml.dom.minidom.html
  _stream_name = parseString(r.text).getElementsByTagName("stream-name")[0].childNodes[0].data



def odl_get_socket_location():
  global _ws_location 

  print '++++ Request socket ----------'

  endpoint = OdlEndpoint(client.get_base_url(), 'restconf/streams/stream', _stream_name)
  headers = {'Content-type': 'application/xml', 'Accept': 'application/xml', 'Cache-Control': 'no-cache'}
  request = OdlRequest('GET', endpoint.url(), headers=headers)
  r = client.send_request(request)
  print r.headers
  # {'content-length': '0', 'location': 'ws://192.168.201.43:8185/opendaylight-inventory:nodes/datastore=CONFIGURATION/scope=BASE', 'server': 'Jetty(8.1.15.v20140411)'}
  _ws_location = r.headers['location']

def odl_open_websocket():
  global ws
  global wst

  print '++++ Open socket & wait for notification -----------'
  websocket.enableTrace(True)
  ws = websocket.WebSocketApp(_ws_location,
      on_message = on_message,
      on_error = on_error,
      on_close = on_close)

  #ws.on_open = on_open
  #ws.run_forever()

  wst = threading.Thread(target=ws.run_forever)
  #wst.daemon = True
  wst.start()

def odl_add_node():
  print '++++ Create Sample Node -----------'
  endpoint = OdlEndpoint(client.get_base_url(), 'restconf/config')
  headers = {'Content-type': 'application/xml', 'Accept': 'application/xml'}
  body_xml = '<nodes xmlns="urn:opendaylight:inventory"><node><id>66</id></node></nodes>'
  data = body_xml

  request = OdlRequest('DELETE', endpoint.url(), headers=headers, data = data)
  #r = client.send_request(request)

  request = OdlRequest('POST', endpoint.url(), headers=headers, data = data)
  r = client.send_request(request)
  print r.text

  conn_timeout = 5
  while not ws.sock.connected and conn_timeout:
    sleep(1)
    conn_timeout -= 1

  #msg_counter = 0
  #while ws.sock.connected:
  #  ws.send('Hello world %d'%msg_counter)
  #  sleep(1)
  #  msg_counter += 1


## main
def main():
  signal.signal(signal.SIGTERM, signal_term_handler)
  signal.signal(signal.SIGINT, signal_term_handler)

  odl_subscribe()
  sleep(1)
  odl_get_socket_location()
  sleep(1)
  odl_open_websocket()
  sleep(2)
  odl_add_node()

  sleep(5)
  wst.join()

if __name__ == '__main__':
  main()
