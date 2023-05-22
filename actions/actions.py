# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from rasa_sdk.events import SlotSet
from actions.sendMailFunction import sendMail
from datetime import datetime
import time
import requests
import re
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker

from pymongo import MongoClient

DB_URL = "mongodb://localhost:27017"

client = MongoClient(DB_URL)

db = client["rasa"]
appointment = db["appointment"]


# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class ActionSendOtp(Action):

    def name(self) -> Text:
        return "action_send_otp"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_send_otp")
        email = tracker.get_slot("email")
        AID = tracker.get_slot("AID")
        if AID is not None:
            dt = appointment.find_one({"_id": AID})
            email = dt["email"]
        otp = sendMail(email)
        # otp = "154622"
        dispatcher.utter_message(text="otp sent to "+email+", type 6 digit otp here to verify your email !")

        return [SlotSet("sentOTP", otp)]


def extract_appointment_number(input_string):
    pattern = r"(\w+_\w+_\d+)"
    match = re.search(pattern, input_string)
    if match:
        appointment_number = match.group(1)
        return appointment_number
    else:
        return None


class ActionCancelAppointment(Action):

    def name(self) -> Text:
        return "action_cancel_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("cancel")

        AID = tracker.get_slot("AID")
        otp = tracker.get_slot("otp")
        sentOTP = tracker.get_slot("sentOTP")
        print(sentOTP,otp)
        # AID = extract_appointment_number(tracker.latest_message.get('text'))
        if AID is not None:
            if otp == sentOTP:
                appointment.update_one({"_id":AID},{"$set":{"status":"cancelled"}})
                data = "Your Appointment has been cancelled for AID : " + AID
            else:
                data = "Wrong OTP ! " 

        else:
            data = "Please Enter AID"
        dispatcher.utter_message(text=data)

        return []


# class ActionCheckSatusAppointment(Action):

#     def name(self) -> Text:
#         return "action_check_status_appointment"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         print("check_status")
#         AID = tracker.get_slot("AID")
#         # AID = extract_appointment_number(tracker.latest_message.get('text'))
#         if AID is not None:
#             res = requests.get(
#                 SERVER+"/appointment/getsinglebookeddata/"+AID).json()["data"]
#             if str(res) == "Error":
#                 data = "No Appointment Found!"
#             else:
#                 data = self.makeDataInStrFromJson(res)
#             # data = AID
#         else:
#             data = "Please Enter AID"
#         dispatcher.utter_message(text=data)

#         return []

#     def makeDataInStrFromJson(self, jsn):
#         ans = ""

#         def fun(x, ans):
#             for i in x:
#                 if type(x[i]) == dict:
#                     ans = fun(x[i], ans)
#                 else:
#                     ans += i.upper()+" : "+str(x[i])+"\n\n"
#             return ans
#         return fun(jsn, ans)


class ActionBookAppointment(Action):

    def name(self) -> Text:
        return "action_book_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("book")
        name = tracker.get_slot("name")
        age = tracker.get_slot("age")
        email = tracker.get_slot("email")
        city = tracker.get_slot("city")
        otp = tracker.get_slot("otp")
        sentOTP = tracker.get_slot("sentOTP")
        print(name, age, email, city, otp, sentOTP)

        doc = {
            "_id": "aid_"+str(int(round(time.time() * 10))),
            "name": name,
            "age": age,
            "email": email,
            "city": city,
            "status": "pending",
            "bookedOn": str(datetime.today())
        }
        appointment.insert_one(doc)
        if (sentOTP == otp):
            dispatcher.utter_message(text="Appointment booked !")
        else:
            dispatcher.utter_message(text="Wrong OTP !")

        return []
