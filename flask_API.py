from flask import Flask, render_template, request, Response, jsonify
from pymongo import MongoClient
import datetime
from bson import json_util
import json

app = Flask(__name__)

'''
Represents a cheap payment gateway.
Note: 
	(1) This class acts as a base class for expensive and premium payment gateways
	(2) A Transaction basically means an insertion of records in a local mongo collection
'''
class CheapPaymentGateway:	
	def __init__(self,cred):	
		self.credentials = cred
	def make_transaction(self):	
		try:	
			client = MongoClient()
			db = client['flaskApp']['transactions']
			db.insert_one({"CardHolder":self.credentials["CardHolder"],"Amount":self.credentials["Amount"]})
			client.close()
		except:	
			return False
		return True
	def pay(self):	
		return self.make_transaction()

'''
Represents expensive payment gateway.
'''
class ExpensivePaymentGateway(CheapPaymentGateway):	
	def __init__(self,cred,retries,SecondaryGateway):	
		super().__init__(cred)
		self.retries=retries
		self.SecondaryGateway=SecondaryGateway
	def pay(self):	
		if self.make_transaction():	
			return True
		else:	
			return self.SecondaryGateway(self.credentials).pay()

'''
Represents premium payment gateway.
'''
class PremiumPaymentGateway(CheapPaymentGateway):	
	def __init__(self,cred,retries):	
		super().__init__(cred)
		self.retries=retries
		self.count = 0
	def pay(self):	
		if self.make_transaction():	
			return True
		else:	
			if self.count < self.retries:	
				self.count = self.count + 1
				return self.pay()
			else:	
				return False
		
'''
Verify Credentials
Note:	
	(1) We assume that the structure of JSON to be received is fixed.
	(2) That means, even if the user doesn't enter optional parameters, we still get those keys with NULL/None values
	(3) This function returns False if:
					- Type of credentials received is not of dict type
					- Keys of credentials are not ["CreditCardNumber","CardHolder","ExpirationDate","SecurityCode","Amount"]
					- CreditCardNumber is None/NULL
					- Length(CreditCardNumber) does not equal 16
					- CardHolder is None/NULL
					- Type of ExpirationDate is not datetime
					- Expiration date is in the past
					- Type of Amount is not float
					- Length(SecurityCode) is not 3 (if SecurityCode is entered)
'''
def verifyCredentials(cred):	
	if type(cred) is not dict or list(cred.keys()) != ["CreditCardNumber","CardHolder","ExpirationDate","SecurityCode","Amount"] or cred["CreditCardNumber"] is None or len(cred["CreditCardNumber"])!=16 or cred["CardHolder"] is None or type(cred['ExpirationDate'])!=datetime.datetime or cred['ExpirationDate'].year < datetime.datetime.now().year or (cred['ExpirationDate'].year == datetime.datetime.now().year and cred['ExpirationDate'].month < datetime.datetime.now().month)  or type(cred["Amount"])!=float or (cred["SecurityCode"] is not None and len(cred["SecurityCode"])!=3):	
		return False
	else:	
		return True

@app.route('/')
def index():	
	return render_template('index.html')

'''
This is the end point where credentials will be received.
Example:
	Say, we have the following credentials:
	data={
		"CreditCardNumber":"1234567891234567",
		"CardHolder":"Rohit Duggal",
		"ExpirationDate":datetime.datetime(2025,12,31),
		"SecurityCode":"123",
		"Amount":1.24
	     }

	We can send the above using python's requests module as follows.
	(NOTE: Start this app first using command: python3 flask_API.py)

	import requests
	import json
	from bson import json_util

	requests.post(
			url="http://127.0.0.1:5000/processPayment",
			json=json.dumps(data,default=json_util.default),
			headers={"Content-type":"application/json"}
		     )
'''
@app.route('/processPayment',methods=['POST'])
def ProcessPayment():	
	credentials = json.loads(request.get_json(),object_hook=json_util.object_hook)
	if verifyCredentials(credentials):	
		if credentials["Amount"] < 20:	
			gateway = CheapPaymentGateway(cred=credentials)
		elif credentials["Amount"] > 21 and credentials["Amount"] < 500:	
			gateway = ExpensivePaymentGateway(cred=credentials,retries=1,SecondaryGateway=CheapPaymentGateway)
		else:	
			gateway = PremiumPaymentGateway(cred=credentials,retries=3)
		if not gateway.pay():	
			return jsonify(msg="Internal Server Error"),500
		return jsonify(msg="OK"),200
	return jsonify(msg="Invalid Parameters"),400
	

if __name__ == '__main__': 
	app.run(debug=True)
