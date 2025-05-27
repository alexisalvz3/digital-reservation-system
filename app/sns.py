from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
def send_sms(message: str, account_sid: str, auth_token: str):
    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=message,
            from_="+16199410682",
            to="+16198908097",
        )
    except TwilioRestException as e:
        logging.error(f'An error occurred with twilio api: {e}')
    return message.sid
