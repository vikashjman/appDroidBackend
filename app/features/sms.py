import os

from telesign.messaging import MessagingClient
from twilio.rest import Client

def send_sms(phn, msg):
    print("send_sms_reached")

    # Replace the defaults below with your Telesign authentication credentials or pull them from environment variables.
    customer_id = os.getenv('CUSTOMER_ID', '5B3EF05D-AE08-4C59-B1AB-F3B7F150D009')
    api_key = os.getenv('API_KEY', 'OSoqZy62yZgGPgIMZ0TEyY+iNgzwHAU2KMDmuyl5rFC2C+9eXe8VZ473/XYHOJkPx0ehteep4twVNLs6chHoMg==')

    # Set the default below to your test phone number or pull it from an environment variable. 
    # In your production code, update the phone number dynamically for each transaction.
    phone_number = os.getenv('PHONE_NUMBER', '91'+phn)
    print(phone_number)
    # Set the message text and type.
    message = msg
    message_type = "ARN"

    # Instantiate a messaging client object.
    messaging = MessagingClient(customer_id, api_key)

    # Make the request and capture the response.
    response = messaging.message(phone_number, message, message_type)

    # Display the response body in the console for debugging purposes. 
    # In your production code, you would likely remove this.
    print(f"\nResponse:\n{response.body}\n")
    try:
        account_sid = 'ACad11e8d7af05eacceb137e6225a364f7'
        auth_token = '490a68b1e7db59c2c1aba3581e2df288'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='+14787392082',
            body=msg,
            to='+916287388363'
        )

        print(message.sid)
    except Exception as e:
        print(e)