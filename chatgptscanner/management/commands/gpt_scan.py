from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
import re, json, argparse, random, time, sys, requests
from chatgptscanner.models import Channel
import socket
from chatgpt_wrapper import ChatGPT

class Command(BaseCommand):
    help = 'Runs the chatbot server'
    verbose_on = False

    def add_arguments(self, parser):
    	parser.add_argument('channel', nargs='?', default='mcbanterface', type=str)
    	parser.add_argument('--verbose', action='store_true', help="print debug info to console")

    def verbose_write(self, outputstring):
        if self.verbose_on:
            self.stdout.write(self.style.NOTICE('%s: %s' % (timezone.now(),outputstring)))


    def scan_channels(self):
    	pass

    def extract_message(self, message):
    	msg = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)',message)
    	if msg and msg[0]:
    		return msg[0]
    	return 'none'

    def respond_to_message(self, message):
    	return (
    		re.match('@'+settings.TWITCH_HANDLE, message, re.I) or
    		re.match('!chatgpt', message, re.I)
    	)

    def strip_message(self, message):
    	if re.match('@'+settings.TWITCH_HANDLE, message, re.I):
    		return message[len('@'+settings.TWITCH_HANDLE):].strip()
    	if re.match('!chatgpt', message, re.I):
    		return message[len('!chatgpt'):].strip()
    	return message

    def handle(self, *args, **options):
        self.verbose_on = options['verbose']
        
        self.stdout.write(self.style.SUCCESS('Scanning channel %s' % options['channel']))
        self.stdout.write(self.style.SUCCESS('Started Server'))

        self.verbose_write('Verbose mode activated')
        self.verbose_write('Twitch handle: %s' % settings.TWITCH_HANDLE)
        self.verbose_write('oauth token: %s' % settings.TWITCH_OAUTH_TOKEN)
        self.stdout.write(self.style.SUCCESS('Quit the server with CONTROL-C.'))
        bot = ChatGPT()
        interrupted = False
        while not interrupted:
        	try:
        		print('attempting to connect')
		        try:
		        	sock = socket.socket()
		        	sock.connect((settings.TWITCH_IRC_ADDRESS, settings.TWITCH_IRC_PORT))
		        	sock.send(('CAP REQ :twitch.tv/tags'+'\r\n').encode('utf-8'))
		        	sock.send(('PASS ' + 'oauth:'+str(settings.TWITCH_OAUTH_TOKEN).lstrip('oauth:')+'\r\n').encode('utf-8'))
		        	sock.send(('NICK ' + settings.TWITCH_HANDLE+'\r\n').encode('utf-8'))
		        	sock.send(('JOIN #{}'.format(options['channel'].lower())+'\r\n').encode('utf-8'))

		        	self.verbose_write('established connection')

		        	while True:
		        		resp = sock.recv(2048).decode('utf-8')
		        		message = self.extract_message(resp)
		        		if self.respond_to_message(message):
		        			stripped_message = self.strip_message(message)
		        			response = bot.ask(stripped_message)
		        			print(self.strip_message(message))
		        			print(self.strip_message(response))
		        			sock.send('PRIVMSG #{} :{}'.format(options['channel'].lower(),response[0:350]+'\r\n').encode('utf-8'))
		        except KeyboardInterrupt:
		        	interrupted = True
		        	raise KeyboardInterrupt
		        except Exception as e:
		        	self.stdout.write(self.style.ERROR(str(e)))
	        except KeyboardInterrupt:
	        	interrupted = True
	        	self.stdout.write(self.style.SUCCESS('Stopped server. Keyboard interrupt'))


