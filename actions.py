from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import glob

from zomato_slots import results
from city_check import check_location
import smtplib
import  pandas as pd


class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')

		#global restaurants
		glob.restaurants = pd.DataFrame(results(loc, cuisine, price))

		glob.restaurants = glob.restaurants.drop_duplicates()
		top5 = glob.restaurants.head(5)
		print(top5)
		# top 5 results to display
		if len(top5)>0:
			response = 'Showing you top results:' + "\n"
			for index, row in top5.iterrows():
				response = response + str(row["restaurant_name"]) + ' (rated ' + row['restaurant_rating'] + ') in ' + row['restaurant_address'] + ' and the average budget for two people ' + str(row['budget_for2people'])+"\n"
				# response = response + "\nShould i mail you the details"

		else:
			response = 'No restaurants found' 

		dispatcher.utter_message(str(response))



class SendMail(Action):
	def name(self):
		return 'email_restaurant_details'
		
	def run(self, dispatcher, tracker, domain):
		recipient = tracker.get_slot('email')

		top10 = glob.restaurants[:10]
		print("got this correct email is {}".format(recipient))
		response = 'Showing you top results:' + "\n"
		for idx, row in top10.iterrows():
			response = response + 'Restaurant Name: ' + str(row["restaurant_name"]) + "\n" + 'User Rating: ' + row[
				'restaurant_rating'] + "\n" + 'Address : ' + row[
						   'restaurant_address'] + "\n" + 'Average Budget for two people ' + str(
				row['budget_for2people']) + "\n\n"

		user = "zomatobot.iiitb@gmail.com"
		password = "zomato123"
		sent_from = user
		to = tracker.get_slot('email')
		subject = " Restaurant recommendations in " + tracker.get_slot("location").title()

		email_text = """\  
					From: %s  
					To: %s  
					Subject: %s
					%s
					""" % (sent_from, to, subject, response)
		print(email_text)

		try:
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(user, password)
			server.sendmail(sent_from, to, email_text)
			server.close()
			print(response)
			dispatcher.utter_message("Message sent.Have a great day!")

		except:

			dispatcher.utter_message("Unfortunately I am not able to send email!!!")

		return [SlotSet('email', to)]




class Check_location(Action):
	def name(self):
		return 'action_check_location'
		
	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		check = check_location(loc)
		
		return [SlotSet('location',check['location_new']), SlotSet('location_found',check['location_f'])]
		
		
		
		

