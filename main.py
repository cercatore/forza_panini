from flask import Flask,request

app = Flask(__name__)
# START APP

import logging
import json
import duckduckgo
from bs4 import BeautifulSoup as bs
from player import PlayerProfile
#,methods = ['POST', 'GET'])
#PLAYER_PHOTO.RESPONSE_VALUES.SUCCESS = 1
#PLAYER_PHOTO.RESPONSE_VALUES.ERROR = 2

@app.route('/server')
def server():
   if request.method == 'GET':
     user = request.args['name']
     if len(user) == 0:
       return serveError(2)
     else:
       if user.find('trans') == -1 :
         user = 'transfermarkt ' + user
         logging.info('***** sanitizing \''+ user + '\'')
       return serveSuccess( user)
   else:
     return "<h1>Ritenta e non uomo in apnea</h1>"
@app.route('/')
def serve_soccer():
    return "ciao google"

def serveSuccess( name):
  for link in duckduckgo.search( name , 10):
    url = link
    break
  player = PlayerProfile(url, bs)

  data = {}
  data['query'] = name
  data['duck_source'] = url
  data['tranfermarkt_image_figurina'] = player.PlayerData.img

  json_data = json.dumps(data)
  return json_data

@app.errorhandler(500)
def server_error(e):
# Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
def serveError(code):
    logging.error('request input: user is null or blank')
    data = {}
    data['error_code'] = code
    data['message'] = 'user is null or blank'
    return json.dumps(data)

if __name__ == '__main__':
    app.debug = True
    app.run()
