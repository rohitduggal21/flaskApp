### OBJECTIVE
	- Create a Flask Web-API (ProcessPayment) that receives a request as below:
		{
			"CreditCardNumber":(mandatory, string, it should be a valid credit card number with 16 digits),
			"CardHolder":(mandatory, string),
			"ExpirationDate": (mandatory, DateTime, it cannot be in the past),
			"SecurityCode": (optional, string, 3 digits),
			"Amount": (mandatoy decimal, positive amount)
	     	}
	- Next step is to process the payment based on the amount entered.

### PRE-REQUISITES
	- flask: pip3 install flask
	- pymongo: pip3 install pymongo

### INSTRUCTIONS
	- Get inside the repo flaskApp
	- Execute command: python3 flask_API.py
	- Flask test server is now running, a request can be made with python's requests module:
	```
		import requests
		import json
		from bson import json_util

		data={
			"CreditCardNumber":"1234567891234567",
			"CardHolder":"Rohit Duggal",
			"ExpirationDate":datetime.datetime(2025,12,31),
			"SecurityCode":"123",
			"Amount":1.24
	     	     }

		requests.post(
				url="http://127.0.0.1:5000/processPayment",
				json=json.dumps(data,default=json_util.default),
				headers={"Content-type":"application/json"}
		     	     )
	```
