import fitbit_keys
import urllib2
import urllib
import base64
import json


class fitbit_api:
	def __init__(self):
		self.read_data()


	def _prepare_strava_packet(self, response):		
		response = json.loads(response)
		packet_for_strava = []
		
		for r in response['activities']:
			activity = {}
			if 'bike' in r.get('activityName').lower():
				activityType = 'ride'
			elif 'walk' in r.get('activityName').lower():
			 	activityType = 'walk'
		 	else:
		 		activityType = 'workout'

			elapsed_time = r.get('activeDuration')/1000
			calories = r.get('calories')
			start_date_local = r.get('originalStartTime')
			import dateutil.parser
			date = dateutil.parser.parse(start_date_local)
			name = activityType + ' ' + str(date)

			activity['type'] = activityType
			activity['elapsed_time'] = elapsed_time
			activity['start_date_local'] = start_date_local
			activity['name'] = name

			packet_for_strava.append(activity)


		print packet_for_strava
		return packet_for_strava


	def create_strava_activity(self, response):	
		packet = self._prepare_strava_packet(response)
		for p in packet:
			BodyURLEncoded = urllib.urlencode(p)	

			#Start the request
			request = urllib2.Request('https://www.strava.com/api/v3/activities', BodyURLEncoded)
		
			request.add_header('Authorization', 'Bearer ' + self.strava_codes.get('access_token'))

			#Fire off the request
			try:
				response = urllib2.urlopen(request).read()
				print response
			except urllib2.URLError as e:
				print e.code
				print e.read()

	def get_new_access_token(self):
		requestBody = {
			'grant_type' : 'refresh_token',
			'refresh_token' : self.fitbit_codes.get('refresh_token')
		}

		try:
			encodedRequestBody = urllib.urlencode(requestBody)
			request = urllib2.Request('https://api.fitbit.com/oauth2/token', encodedRequestBody)

			request.add_header('Authorization', 'Basic ' + base64.b64encode(self.fitbit_codes.get('client_id')  +  ":" + self.fitbit_codes.get('client_secret')))
			request.add_header('Content-Type', 'application/x-www-form-urlencoded')

			response = urllib2.urlopen(request).read()      			
			json_output = json.loads(response)
			self.update_tokens(json_output)
			response = self.doApiCall()
			print response
		except urllib2.URLError as e:
			print '-----Refresh token invalid----\n'
			if e.code == 400:
				print '-----Refresh token invalid----\n'

	def update_tokens(self, response):	
		self.fitbit_codes['access_token'] = response.get('access_token')
		self.fitbit_codes['refresh_token'] = response.get('refresh_token')
		self.all_codes.get('fitbit_codes').update(self.fitbit_codes)

		fitbit_data_write = open('fitbit_keys.json', 'w+')
		fitbit_data_write.write(json.dumps(self.all_codes))
		fitbit_data_write.close()


	def doApiCall(self):
		# import pdb;pdb.set_trace()
		try:
			request = urllib2.Request("https://api.fitbit.com/1/user/-/activities/list.json?afterDate=today&offset=0&limit=20&sort=desc")
			request.add_header('Authorization', 'Bearer ' +  self.fitbit_codes.get('access_token'))
			response = urllib2.urlopen(request).read()          
			return response
		except urllib2.URLError as e:
			if e.code == 401:
				self.get_new_access_token()

	def read_data(self):
		tokens = open('fitbit_keys.json', 'r')	
		tokens_json = json.load(tokens)
		self.all_codes = tokens_json
		self.fitbit_codes = tokens_json.get('fitbit_codes')
		self.strava_codes = tokens_json.get('strava_codes')
		tokens.close()


if __name__ == '__main__':
	
	obj = fitbit_api()	
	obj.read_data()

	#get all activities		
	response = obj.doApiCall()

	obj.create_strava_activity(response)


