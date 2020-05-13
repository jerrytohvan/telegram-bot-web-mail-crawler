#!/usr/bin/env python
# -*- coding: utf-8 -*-


#from os import environ
from flask import Flask, request

#sys.setdefaultencoding("utf-8")


app = Flask(__name__)

@app.route('/')
def index():
	return 'Subscribe to Telegram Bot: @Telegram_bot_username'


if __name__ == '__main__':
	app.run()

