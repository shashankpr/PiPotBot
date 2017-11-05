import logging
import time
import sys
from os import path
import random
import requests

from wit import Wit
from slackclient import SlackClient
import settings

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# API Services
# from services.weather import CallWeather
# from services.worldtime import CallGoogleTime
# from services.currency_conversion import CurrencyRates


class CallWit(object):
    def __init__(self):
        # Wit.ai API parameters
        self.WIT_TOKEN = settings.WIT_TOKEN

        self.BOT_SLACK_NAME = settings.BOT_SLACK_NAME
        self.BOT_SLACK_TOKEN = settings.BOT_SLACK_TOKEN
        self.BOT_SLACK_ID = settings.BOT_SLACK_ID
        self.SLACK_API = settings.SLACK_API
        self.SLACK_VERIFY_TOKEN = settings.SLACK_VERIFY_TOKEN

        # initialize slack client
        self.bot_slack_client = SlackClient(self.BOT_SLACK_TOKEN)
        self.bot_slack_mention = self.get_mention(self.BOT_SLACK_ID)

        self.SOCKET_DELAY = 1

        # Setup Wit Client
        self.client = Wit(access_token=self.WIT_TOKEN)

        self.replies = {}
        self.context_dict = {}

        self.replies['default'] = ["Sorry mate ! I didn't get what you said..."]
        self.replies['welcome'] = ["How can you help you today ? You can ask me anything related to `Sleep`, `Dozee App`"
                                   " & `Dozee device`, or we could just do some chit chatting here !!! "]
        self.replies['great'] = ['Great !! Glad I could help !!!']

    def handle_message(self, user_query, user, channel):
        wit_response = self.client.message(msg=user_query)
        print wit_response
        logging.debug("Response from Wit : {}".format(wit_response))

        user_mention = self.get_mention(user)
        entities = wit_response['entities']
        # context_dict = self.merge(wit_response)

        greetings = self.first_entity_value(entities, 'greetings')
        bye = self.first_entity_value(entities, 'bye')
        user_reply = self.first_entity_value(entities, 'replies')
        intent = self.first_entity_value(entities=entities, entity='intent')
        logging.info("Entities obtained : {}".format(intent, greetings, bye))

        # if intent == 'getWeather':
        #     context = self.getWeather(context_dict)
        #     messenger.fb_message(session_id, self.weather_replies(user_name, context))
        #
        # elif intent == 'getTime':
        #     context = self.getTime(context_dict)
        #     messenger.fb_message(session_id, self.time_replies(user_name, context))
        #
        # elif intent == 'curConvert':
        #     context = self.get_currency_conversion(context_dict)
        #     messenger.fb_message(session_id, self.currency_replies(user_name, context))
        #
        # elif greetings == 'greetings':
        #     messenger.fb_message(session_id, self.welcome_msg)
        #
        # elif greetings == 'end':
        #     messenger.fb_message(session_id, "See you soon then !!!")
        #
        # else:
        #     messenger.fb_message(session_id, self.default_msg)

        if greetings == 'true':
            self.say_hi()
            self.send_message(reply_list=self.replies['greetings'], channel=channel, user_mention=user_mention)
            self.send_message(reply_list=self.replies['welcome'], channel=channel, user_mention=user_mention)

        elif bye == 'true':
            self.say_bye()
            self.send_message(reply_list=self.replies['bye'], channel=channel, user_mention=user_mention)

        elif intent == 'sleepQuery':
            self.context_dict[intent] = True
            issue_type = self.sleepQuery(wit_response, intent, user_mention, channel)

        elif intent == 'appQuery':
            self.context_dict[intent] = True
            self.appQuery(wit_response, intent, user_mention, channel)

        elif intent == 'deviceQuery':
            self.context_dict[intent] = True
            self.deviceQuery(wit_response, intent, user_mention, channel)

        elif user_reply == 'neg':

            contexts = self.context_dict.keys()[self.context_dict.values().index(True)]
            print contexts
            print self.context_dict

            if 'sleepQuery' in contexts:
                if self.context_dict['snore'] == True:
                    issue_type = 'snore'
                    self.send_message(reply_list=self.replies[issue_type + '-' + user_reply], user_mention=user_mention,
                                      channel=channel)

            elif 'appQuery' in contexts:
                if self.context_dict['crash'] == True:
                    issue_type = 'crash'
                    self.send_message(reply_list=self.replies[issue_type + '-' + user_reply], user_mention=user_mention,
                                      channel=channel)
        elif user_reply == 'pos':
            self.send_message(reply_list=self.replies['great'], user_mention=user_mention, channel=channel)

        else:
            self.send_message(reply_list=self.replies['default'], channel=channel, user_mention=user_mention)

    def send_message(self, reply_list, user_mention, channel):

        response_template = random.choice(reply_list).format(mention=user_mention)
        # print response_template
        # response_template.format(mention=user_mention)
        self.bot_slack_client.api_call('chat.postMessage', channel=channel,
                              text=response_template, as_user=True)

    # Sleep Assistance service
    def sleepQuery(self, response, intent, user_mention, channel):
        # issue_list = ['snoring', 'insomnia', 'drowsy']
        self.say_sleep()

        entities = response['entities']
        issue_type = self.first_entity_value(entities, 'issue_type')
        user_reply = self.first_entity_value(entities, 'replies')

        if issue_type:
            self.context_dict[issue_type] = True
            self.send_message(reply_list=self.replies[issue_type], user_mention=user_mention, channel=channel)

        else:
            self.send_message(reply_list=self.replies[intent], user_mention=user_mention, channel=channel)

        return issue_type

    def deviceQuery(self, response, intent, user_mention, channel):

        self.say_device()
        entities = response['entities']
        issue_type = self.first_entity_value(entities, 'issue_type')

        if issue_type:
            self.context_dict[issue_type] = True
            self.send_message(reply_list=self.replies[issue_type], user_mention=user_mention, channel=channel)
        else:
            self.send_message(reply_list=self.replies[intent], user_mention=user_mention, channel=channel)

        return issue_type

    def appQuery(self, response, intent, user_mention, channel):

        self.say_app()
        entities = response['entities']
        issue_type = self.first_entity_value(entities, 'issue_type')

        if issue_type:
            self.context_dict[issue_type] = True
            self.send_message(reply_list=self.replies[issue_type], user_mention=user_mention, channel=channel)
        else:
            self.send_message(reply_list=self.replies[intent], user_mention=user_mention, channel=channel)

        return issue_type

    def miscQuery(self, response):
        return

    # Wit utility functions
    def speech_to_wit(self, audio_url):
        """
        To Handle Audio files in Messenger
        
        :param audio_url: 
        :return: response as per Wit.AI API docs
        """

        # Download the URL

        r = requests.get(audio_url)
        with open('audio.wav', 'wb') as f:
            f.write(r.content)

        logging.debug("Audio file received")

        response = None
        header = {'Content-Type': 'audio/mpeg3'}
        with open('audio.wav', 'rb') as f:
            response = self.client.speech(f, None, header)

        return response

    def first_entity_value(self, entities, entity):
        """
        Returns first entity value
        """
        if entity not in entities:
            return None
        entity_val = entities[entity][0]['value']
        if not entity_val:
            return None
        return entity_val['value'] if isinstance(entity_val, dict) else entity_val

    def merge(self, request):
        try:
            context = request['context']
        except:
            context = {}
        entities = request['entities']

        loc = self.first_entity_value(entities, 'location')

        # Get context for currency conversion
        currency_source = self.first_entity_value(entities, 'source')
        currency_dest = self.first_entity_value(entities, 'destination')
        if currency_source and currency_dest:
            context['currencyNameSource'] = currency_source
            context['currencyNameDest'] = currency_dest

        elif loc:
            context['weatherLocation'] = loc
            context['timeLocation'] = loc

        return context

    # Basic util functions for slack conversation

    def is_private(self, event):
        """Checks if private slack channel"""
        return event.get('channel').startswith('D')

    # how the bot is mentioned on slack
    def get_mention(self, user):
        return '<@{user}>'.format(user=user)

    def is_for_me(self, event):
        """Know if the message is dedicated to me"""
        # check if not my own event
        type = event.get('type')
        if type and type == 'message' and not(event.get('user')==self.BOT_SLACK_ID):
            # in case it is a private message return true
            if self.is_private(event):
                return True
            # in case it is not a private message check mention
            text = event.get('text')
            channel = event.get('channel')
            if self.bot_slack_mention in text.strip().split():
                return True


    # Services and APIs

    """

    def getWeather(self, context):
        # context = request['context']
        # entities = request['entities']
        # loc = first_entity_value(entities, 'loc')
        del context['timeLocation']
        loc = context['weatherLocation']

        # Initialize Weather API class
        weather_obj = CallWeather(location=loc)
        if loc:
            # This is where we use a weather service api to get the weather.
            try:
                context['forecast'] = weather_obj.inWeather()
                if context.get('missingLocation') is not None:
                    del context['missingLocation']
            except:
                context['weather_default'] = True
                del context['weatherLocation']

                # Delete session ID to stop looping
                # del request['session_id']
        else:
            context['missingLocation'] = True
            if context.get('forecast') is not None:
                del context['forecast']
        return context

    def getName(self, session_id):
        # context = request['context']

        # Get user name from the Messenger API
        resp = requests.get("https://graph.facebook.com/v2.8/" + session_id,
                            params={"access_token": self.FB_PAGE_TOKEN})

        print resp
        sender_name = resp.json()['first_name']
        return sender_name

    def getTime(self, context):
        # context = request['context']
        # entities = request['entities']
        del context['weatherLocation']
        loc = context['timeLocation']

        # Initialize Time API class
        world_time_obj = CallGoogleTime(location=loc)
        if loc:
            try:
                context['country_time'] = world_time_obj.world_time()
                if context.get('missingCountry') is not None:
                    del context['missingCountry']
            except:
                context['time_default'] = True
                del context['timeLocation']

                # Delete session ID to stop looping
                # del request['session_id']
        else:
            context['missingCountry'] = True
            if context.get('country_time') is not None:
                del context['country_time']

        return context

    def get_currency_conversion(self, context):

        # context = request['context']

        source_name = context['currencyNameSource']
        dest_name = context['currencyNameDest']

        currency_object = CurrencyRates()
        if source_name and dest_name:
            try:
                context['conversionVal'] = currency_object.get_conversion_rate(source_name, dest_name)
            except:
                context['cur_default'] = True
                del context['currencyNameSource']
                del context['currencyNameDest']
        else:
            context['cur_default'] = True
            del context['currencyNameSource']
            del context['currencyNameDest']
        return context
    
    """
    #  Replies from Wit

    def weather_replies(self, user_name, context):
        response_template = random.choice(
            ['Hey {mention} ! Weather at {location} is {forecast}',
             'Yo {mention}! It is {forecast} at {location}',
             'Hi {mention} ! The weather is {weather} at {location}'
             ])

        return response_template.format(mention=user_name, location=context.get('weatherLocation'),
                                        forecast=context.get('forecast'))

    def time_replies(self, user_name, context):
        response_template = random.choice(
            ['Hey {mention} ! Time at {location} is {time}',
             'Yo {mention}! It is {time} at {location}',
             'The time is {time} at {location}...',
             'Uno momento please {mention} ... The time is {time} at {location} !!'
             ])

        return response_template.format(mention=user_name, location=context.get('timeLocation'),
                                        time=context.get('country_time'))

    def currency_replies(self, user_name, context):
        response_template = random.choice(
            ['Hey {mention} ! 1 {source_currency} is equal to {conversion_val} {dest_currency}',
             'Yo {mention} ! 1 {source_currency} is equal to {conversion_val} {dest_currency}',
             'Just a moment ... Hey {mention} ! 1 {source_currency} is equal to '
             '{conversion_val} {dest_currency}'
             ])

        return response_template.format(mention=user_name, source_currency=context.get('currencyNameSource'),
                                        dest_currency=context.get('currencyNameDest'),
                                        conversion_val=context.get('conversionVal'))

    def say_hi(self):
        """Say Hi to a user by formatting their mention"""
        self.replies['greetings'] = ['Sup, {mention}...',
                                           'Yo!',
                                           'Hola {mention}',
                                           'Bonjour!']
        return

    def say_bye(self):
        """Say Goodbye to a user"""
        self.replies['bye'] = ['see you later, alligator...',
                                           'adios amigo',
                                           'Bye {mention}!',
                                           'Au revoir!']
        return

    def say_sleep(self):
        """Sleep replies"""
        self.replies['sleepQuery'] = ['Sure !! How can I help you ?',
                                           'Hey {mention}, may I know your query about sleep ?',
                                           ]
        self.replies['snore'] = [
            'To help reduce snoring, you could possibly try sleeping on your sides ...Does it help ?',
            'I have couple of links about snoring and sleep-apnea. It might help you.',
            'I am no doctor but I can give you few suggestions. Try not to sleep on your back. Does it help ?'
        ]

        self.replies['snore-neg'] = [
            'Alright ... Sometimes other health factors like cold could cause snoring. Is that the case ?',
            'Please wait. I have notified about your problem to our sleep expert. He will get in touch with you soon.'
        ]

        return

    def say_app(self):
        """App replies"""
        self.replies['appQuery'] = ['Sure !! How can I help you ?',
                                           'Hey {mention}, may I know your query about our app ?',
                                           ]
        self.replies['crash'] = [
            'Alright ! try closing the app and restarting it. Does it work now ?',
            'Let me help you ... Try uninstalling and reinstalling the app. Does it help?',
            'I am no app developer but I can give you few suggestions. Try signing out and sign back in and see ! Does it '
            'solve the problem ? '
        ]

        self.replies['pair'] = [
            'Have you checked if your device is fully charged ?',
            'Alright {mention} ! Make sure that your mobile data is off ...',
            'I am no hardware engineer but I can give you few suggestions. '
            'Have you checked if the device is paired to other id ?'
        ]

        self.replies['crash-neg'] = [
            'Try clearing the cache memory of app and restart the app again. Does it work now ?',
            'I will connect you with your developer. He will help you fix this issue...'
        ]
        return

    def say_device(self):
        """Device replies"""
        self.replies['deviceQuery'] = ['Sure !! How can I help you ?',
                                           'Hey {mention}, may I know your query about the device?',
                                           ]
        self.replies['device'] = [
            '{mention}, did you try charging it atleast 80% and see ?',
            'Have you checked if the device is placed in right position ?'
        ]

        return

    def run(self):
        if self.bot_slack_client.rtm_connect():
            print '[.] PiPotBot is ON...'
            while True:
                event_list = self.bot_slack_client.rtm_read()
                if len(event_list) > 0:
                    for event in event_list:
                        print(event)
                        if self.is_for_me(event):
                            self.handle_message(user_query=event.get('text'), user=event.get('user'),
                                              channel=event.get('channel'))
                time.sleep(self.SOCKET_DELAY)
        else:
            print('[!] Connection to Slack failed.')

    def wit_interactive(self):

        client = Wit(access_token=self.WIT_TOKEN)
        client.interactive()


if __name__ == '__main__':
    c = CallWit()
    c.run()
