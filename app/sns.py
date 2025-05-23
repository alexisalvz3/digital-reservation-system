from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
def send_sms(message: str, account_sid: str, auth_token: str):
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_="+16199410682",
        to="+16198908097",
    )
    print(message.body)
