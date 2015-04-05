import arrow
from bs4 import BeautifulSoup
import configparser
import json
import requests
import sys
import urllib
import pprint
from time import sleep

class AmazonManager():

    def __init__(self, email, password):

        self.email = email
        self.password = password
        self.session = requests.Session()

        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.13) '\
                + 'Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13',
            'Charset': 'utf-8',
            'Origin': 'http://echo.amazon.com',
            'Referer': 'http://echo.amazon.com/spa/index.html',
        }

        self.session.headers.update(self.default_headers)
        self.login()

    def __del__(self):
        self.logout()

    
    def find_csrf_cookie(self):
        for cookie in self.session.cookies:
            if cookie.name == "csrf":
                return cookie.value
        return None

    def delete_items(self, items):

        # This PUT request needs special headers
        headers = {
            'Content-type': 'application/json',
            'csrf': self.find_csrf_cookie(),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        }

        # Loop through the items and delete each one
        for item in items:
            id = urllib.parse.quote_plus(item['itemId'])
            item['deleted'] = True
            url = 'https://pitangui.amazon.com/api/todos/%s' % id
            delete_request = self.session.put(url, data=json.dumps(item), headers=headers)

            if not delete_request.status_code == 200:
                print("Error deleting item")

    def fetch_items(self, type="SHOPPING_ITEM"):

        # Request the shopping list todo API
        url = 'https://pitangui.amazon.com/api/todos?type=%s&size=100&completed=false' % type
        shopping_request = self.session.get(url)

        data = shopping_request.json()
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(data)
        # Find all the items
        items = []
        if 'values' in data:
            for value in data['values']:
                items.append(value)

        # Return our list of item objects
            return items


    def logout(self):
        self.session.headers.update({ 'Referer': 'http://echo.amazon.com/spa/index.html' })
        url = 'https://pitangui.amazon.com/logout'
        self.session.get(url)


    def login(self):

        # Request the login page
        login_url = 'https://pitangui.amazon.com'
        login_request = self.session.get(login_url)

        # Turn the login page into a soup object
        login_soup = BeautifulSoup(login_request.text)

        # Find the <form> tag and the action from the login page
        form_el = login_soup.find('form')
        action_attr = form_el.get('action')

        # Set up the parameters we will pass to the signin
        parameters = {
            'email': self.email,
            'password': self.password,
            'create': 0,
        }

        # Find all the hidden form elements and stick them in the params
        for hidden_el in form_el.findAll(type="hidden"):
            parameters[hidden_el['name']] = hidden_el['value']

        # Update the session with the new referer
        self.session.headers.update({ 'Referer': login_url })

        # Post to the login page
        login_request = self.session.post(action_attr, data=parameters)

        # Make sure it was successful
        if login_request.status_code != 200:
            sys.exit("Error logging in! Got status %d" % login.status_code)


class TrelloManager():

    def __init__(self, app_key, secret, token):
        self.app_key = app_key
        self.secret = secret
        self.token = token

    def fetch_json(self, uri_path, http_method='GET', post_args=None, query_params=None):
    
        headers = {}
        data = json.dumps(post_args)
    
        if http_method in ("POST", "PUT", "DELETE"):
            headers['Content-Type'] = 'application/json; charset=utf-8'
            headers['Accept'] = 'application/json'
    
        url = 'https://api.trello.com/1/%s' % uri_path
        print("url: " + url)
    
        # perform the HTTP requests, if possible uses OAuth authentication
        response = requests.request(http_method, url, params=query_params, headers=headers, data=data)

        #print(response.status_code)
        #print(response.text)

        return response.json()

    def create_card(self, name, idList, desc = None):
        json_obj = self.fetch_json('lists/' + idList + '/cards',
                http_method='POST',
                post_args={'name': name, 'idList': idList, 'desc': desc}, 
                query_params={'key': self.app_key, 'token' : self.token},)
    

def process_list(type, trello_list_id):
            # Get all the items on your shopping list
        items = manager.fetch_items(type)

        for item in items:
            name = item['text']
            print("creating card for " + name)
            trello.create_card(name, trello_list_id)
            
        # Delete from the Echo
        manager.delete_items(items)

if __name__ == "__main__":

    # Load the config info from the config.txt file
    config = configparser.ConfigParser()
    config.read("config.txt")

    # Make sure we have the items in the config
    try:
        email = config.get('Amazon', 'email')
        password = config.get('Amazon', 'password')
        app_key = config.get('Trello', 'app_key')
        secret = config.get('Trello', 'secret')
        token = config.get('Trello', 'token')
        todo_list_id = config.get('Trello', 'todo_list_id')
        buy_list_id = config.get('Trello', 'buy_list_id')
        poll_time_in_seconds = int(config.get('Trello', 'poll_time_in_seconds'))

    except Exception:
        sys.exit("Invalid or missing config.txt file.")

    # Instantiate the Amazon & Trello wrappers
    manager = AmazonManager(email, password) 
    trello = TrelloManager(app_key, secret, token)

    while True:
        print(".")
        process_list("TASK", todo_list_id)
        process_list("SHOPPING_ITEM", buy_list_id)
        sleep(poll_time_in_seconds)

        #TASK
