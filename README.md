# echo2trello
Integrates an Amazon Echo with two trello lists - one for todos, and one for shopping.

##config.txt
To use this program you will need to rename config.sample.txt to config.txt, and correct the values it contains.
  - the amazon section contains the username/password that you use to login to echo.amazon.com
  - the trello section comes from trello.
    - getting an app key: https://trello.com/docs/gettingstarted/index.html#getting-an-application-key
    - getting a user token: https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user
  - the schedule

##Usage
You can simply run the program from python3 (i.e. python3 PyEchoTrello.py).  This will cause the program to run every n seconds (the number of seconds is defined in config.txt).

Alternatively, you can tell it to run once.  I use this to run the program as a cron job on a Raspberry Pi.

##Credit
Thanks to Greencoder and his project at https://github.com/greencoder/amazon-echo-cheddar for getting me started on the Amazon Echo side of the integration!
