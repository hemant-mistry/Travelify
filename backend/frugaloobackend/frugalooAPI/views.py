from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
import requests
import asyncio
import aiohttp
from .models import UserTripInfo, UserTripProgressInfo
from .serializers import (
    UserTripInfoSerializer,
    GeneratedPlanSerializer,
    UserTripProgressSerializer,
)
import json


class Preplan(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            stay_details = request.data.get("stay_details")
            number_of_days = request.data.get("number_of_days")
            budget = 1000
            additional_preferences = request.data.get("additional_preferences")

            genai.configure(api_key=os.environ["GOOGLE_GEMINI_API_KEY"])

            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                system_instruction='Generate an itinerary based on the information received from the user. Each day in the itinerary should contain minimum 3 mandatory activities. In addition to that you can recommend Exploration/Shopping activity if the user\'s day have bandwidth. You can make that estimate from "Time of Exploration" for all the above three mandatory activities. \n\nTOE: It indicates the approx time for exploring that particular activity.\n\n\n<Mandatory List>\nBelow is the list of mandatory activities: \n###############################################\n1. Morning Activity\n2. Afternoon Activity\n3. Evening Activity\n###############################################\n<Mandatory List/>\n\n\n\n\n### INFORMATION ###\nThe user will provide you with the input in the below format:\n- stay_details\n- number_of_days\n- budget\n- additional_preferences\nThe output should be a JSON structure as shown below:\n\n\n<OUTPUT FORMAT INFORMATION>\n\n9:00 AM - 11:00 AM: Morning Activity\n11:00 AM - 12:30 PM: Exploration/Shopping\n1:30 PM - 4:00 PM: Afternoon Activity\n4:00 PM - 4:30 PM: Break\n4:30 PM - 5:30 PM: Additional Exploration\n7:00 PM - 9:00 PM: Evening Activity\n\nIn the "description" do mention to the user when it is recommeded to visit that location: Morning, Afternoon and Evening. The last activity should always be a night activity.\nMake sure the JSON is correctly structured there should not be any Bad escaped character \n\n\n\n<OUTPUT FORMAT INFORMATION/>\n\n<OUTPUT FORMAT>\n{  "1":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"},{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n  "2":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"},{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n  "3":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"},{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}, {"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n  "4":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n}\n<OUTPUT FORMAT/>\n\n',            )

            chat_session = model.start_chat(history=[])

            concatenated_input = f"Stay Details: {stay_details}\nNumber of Days: {number_of_days}\nBudget: {budget}\nAdditional Preferences: {additional_preferences}"

            response = chat_session.send_message(concatenated_input)
            print("PHASE 1 GEMINI API RESPONSE", response)
            response_data = response.text
            response = {
                "user_id": user_id,
                "stay_details": stay_details,
                "number_of_days": number_of_days,
                "budget": budget,
                "additional_preferences": additional_preferences,
                "response_data": response_data,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GenerateFinalPlan(APIView):

    def insert_trip_details(
        self,
        user_id,
        stay_details,
        number_of_days,
        budget,
        additional_preferences,
        generated_plan,
        nearby_restaurants
    ):
        UserTripInfo.objects.create(
            user_id=user_id,
            stay_details=stay_details,
            number_of_days=number_of_days,
            budget=budget,
            additional_preferences=additional_preferences,
            generated_plan=generated_plan,
            nearby_restaurants = nearby_restaurants
        )

        

    def extract_lat_long(self, data):
        lat_long_values = []

        for day_index, day in data.items():
            for place in day:
                lat_long_values.append(
                    {
                        "day_index": day_index,
                        "place_name": place["place_name"],
                        "lat_long": place["lat_long"],
                    }
                )
        return lat_long_values

    def fetch_nearby_restaurants(self, lat_long_values):
        api_key = os.environ.get("GOOGLE_PLACES")
        radius = 1500
        results = {}

        for place in lat_long_values:
            day_index = place["day_index"]
            place_name = place["place_name"]
            lat_long = place["lat_long"]
            lat, lng = lat_long.split(",")
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=restaurant&key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()  # Parse response content as JSON
                # Sort results by rating descending and take top 5
                sorted_results = sorted(
                    data["results"], key=lambda x: x.get("rating", 0), reverse=True
                )[:5]
                names_with_details = [
                    {
                        "name": result["name"],
                        "latitude": result["geometry"]["location"]["lat"],
                        "longitude": result["geometry"]["location"]["lng"],
                        "rating": result.get("rating", "N/A"),
                        "price_level": result.get("price_level", "N/A"),
                    }
                    for result in sorted_results
                ]
                if day_index not in results:
                    results[day_index] = {}
                results[day_index][place_name] = names_with_details
            else:
                if day_index not in results:
                    results[day_index] = {}
                results[day_index][place_name] = {"error": response.status_code}

        return results

    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            stay_details = request.data.get("stay_details")
            number_of_days = request.data.get("number_of_days")
            budget = 1000
            additional_preferences = request.data.get("additional_preferences")
            response_raw = request.data.get("response_data")

            response_raw_dict = json.loads(response_raw)
            lat_long_values = self.extract_lat_long(response_raw_dict)
            nearby_restaurants = self.fetch_nearby_restaurants(lat_long_values)
            
            response_raw = {
                "nearby_restaurants": nearby_restaurants,
                "response_data": response_raw_dict,
            }

            genai.configure(api_key=os.environ["GOOGLE_GEMINI_API_KEY"])
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                system_instruction="You are an intelligent travel planner that merges the best matching restaurants near to the place the user is visiting. You'll receive two objects \"nearby_restaurants\" and \"response_data\" based on it you need to merge the best restaurants that matches the user preferences. All the nearest restaurants close to the place are clubbed together in a single object which is \"nearby_restaurants\". You need to pickup from that and then recreate the response_data including them with the description, TOE and lat_long. By default recommend the best rated and cheap restaurant. Only provide the response_data JSON as output. \n\nAlso add description, TOE and make up the lat_long from the respective restaurant's latitude, longitude. \nInstead of \"val1\" and \"val2\" you need to add description for that place and estimated time of exploration.\nDo not use single quotes or double quotes anywhere inside the place_name, description.\n\n<EXAMPLES>\n\n### EXAMPLE 1 ###\n<User Input>\n{\n    \"nearby_restaurants\": {\n        \"1\": {\n            \"Gateway of India\": [\n                {\n                    \"name\": \"Shamiana\",\n                    \"latitude\": 18.9220554,\n                    \"longitude\": 72.8330387,\n                    \"rating\": 4.7,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Golden Dragon\",\n                    \"latitude\": 18.9218167,\n                    \"longitude\": 72.8334331,\n                    \"rating\": 4.6,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Wasabi by Morimoto\",\n                    \"latitude\": 18.9225215,\n                    \"longitude\": 72.83322919999999,\n                    \"rating\": 4.6,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Souk\",\n                    \"latitude\": 18.9220554,\n                    \"longitude\": 72.8330387,\n                    \"rating\": 4.6,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Sea Lounge\",\n                    \"latitude\": 18.921611,\n                    \"longitude\": 72.83330509999999,\n                    \"rating\": 4.5,\n                    \"price_level\": 4\n                }\n            ],\n            \"Elephanta Caves\": [],\n            \"Dhobi Ghat\": [\n                {\n                    \"name\": \"Saikrupa Hotel\",\n                    \"latitude\": 18.9618653,\n                    \"longitude\": 72.8350256,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"ZAS Kitchen\",\n                    \"latitude\": 18.95548879999999,\n                    \"longitude\": 72.83328929999999,\n                    \"rating\": 4.6,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Bon Appetit\",\n                    \"latitude\": 18.9545604,\n                    \"longitude\": 72.8332453,\n                    \"rating\": 4.5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Arrakis Cafe\",\n                    \"latitude\": 18.9583136,\n                    \"longitude\": 72.83748969999999,\n                    \"rating\": 4.4,\n                    \"price_level\": 1\n                },\n                {\n                    \"name\": \"Cafe Shaheen\",\n                    \"latitude\": 18.9576754,\n                    \"longitude\": 72.83133800000002,\n                    \"rating\": 4.2,\n                    \"price_level\": \"N/A\"\n                }\n            ]\n        },\n        \"2\": {\n            \"Chhatrapati Shivaji Maharaj Terminus\": [\n                {\n                    \"name\": \"Super Taste\",\n                    \"latitude\": 18.9533807,\n                    \"longitude\": 72.8348168,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Hotel Grant House\",\n                    \"latitude\": 18.945688,\n                    \"longitude\": 72.8350631,\n                    \"rating\": 4.6,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Bon Appetit\",\n                    \"latitude\": 18.9545604,\n                    \"longitude\": 72.8332453,\n                    \"rating\": 4.5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Royal China\",\n                    \"latitude\": 18.9384896,\n                    \"longitude\": 72.8328156,\n                    \"rating\": 4.4,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Ustaadi\",\n                    \"latitude\": 18.9456713,\n                    \"longitude\": 72.8341837,\n                    \"rating\": 4.3,\n                    \"price_level\": 3\n                }\n            ],\n            \"Kanheri Caves\": [\n                {\n                    \"name\": \"Famous Chinese\",\n                    \"latitude\": 19.1353643,\n                    \"longitude\": 72.8995789,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Mumbai Vadapav - मुंबई वडापाव\",\n                    \"latitude\": 19.1358904,\n                    \"longitude\": 72.90076499999999,\n                    \"rating\": 4.9,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Anna's Kitchen\",\n                    \"latitude\": 19.1351649,\n                    \"longitude\": 72.89989829999999,\n                    \"rating\": 4.8,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"chandshah wali garib nawaz hotel\",\n                    \"latitude\": 19.1393675,\n                    \"longitude\": 72.9046766,\n                    \"rating\": 4.5,\n                    \"price_level\": 1\n                },\n                {\n                    \"name\": \"Skky - Ramada\",\n                    \"latitude\": 19.1358383,\n                    \"longitude\": 72.8985196,\n                    \"rating\": 4.3,\n                    \"price_level\": \"N/A\"\n                }\n            ],\n            \"Marine Drive\": [\n                {\n                    \"name\": \"All Seasons Banquets\",\n                    \"latitude\": 18.938381,\n                    \"longitude\": 72.824679,\n                    \"rating\": 4.9,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"The Gourmet Restaurant\",\n                    \"latitude\": 18.9389568,\n                    \"longitude\": 72.8287517,\n                    \"rating\": 4.7,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Joss Chinoise Jaan Joss Banquets\",\n                    \"latitude\": 18.93289,\n                    \"longitude\": 72.83127999999999,\n                    \"rating\": 4.7,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Royal China\",\n                    \"latitude\": 18.9384896,\n                    \"longitude\": 72.8328156,\n                    \"rating\": 4.4,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Castle Hotel\",\n                    \"latitude\": 18.9447236,\n                    \"longitude\": 72.8289277,\n                    \"rating\": 4.3,\n                    \"price_level\": \"N/A\"\n                }\n            ]\n        },\n        \"3\": {\n            \"Juhu Beach\": [\n                {\n                    \"name\": \"Hakkasan Mumbai\",\n                    \"latitude\": 19.0608636,\n                    \"longitude\": 72.834589,\n                    \"rating\": 4.7,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Bonobo\",\n                    \"latitude\": 19.0655221,\n                    \"longitude\": 72.8340542,\n                    \"rating\": 4.3,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Candies\",\n                    \"latitude\": 19.0610866,\n                    \"longitude\": 72.8266907,\n                    \"rating\": 4.3,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Escobar\",\n                    \"latitude\": 19.0600351,\n                    \"longitude\": 72.8363962,\n                    \"rating\": 4.2,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Joseph’s Tandoori Kitchen\",\n                    \"latitude\": 19.0617858,\n                    \"longitude\": 72.8303955,\n                    \"rating\": 4.2,\n                    \"price_level\": 2\n                }\n            ],\n            \"Mani Bhavan\": [\n                {\n                    \"name\": \"MAYUR HOSPITALITY\",\n                    \"latitude\": 18.9552008,\n                    \"longitude\": 72.8281485,\n                    \"rating\": 4.8,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Bon Appetit\",\n                    \"latitude\": 18.9545604,\n                    \"longitude\": 72.8332453,\n                    \"rating\": 4.5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Haji Tikka - The Kabab Corner\",\n                    \"latitude\": 18.9599894,\n                    \"longitude\": 72.8306206,\n                    \"rating\": 4.3,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Kings Shawarma\",\n                    \"latitude\": 18.9617761,\n                    \"longitude\": 72.82895789999999,\n                    \"rating\": 4.3,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Cafe Shaheen\",\n                    \"latitude\": 18.9576754,\n                    \"longitude\": 72.83133800000002,\n                    \"rating\": 4.2,\n                    \"price_level\": \"N/A\"\n                }\n            ],\n            \"Siddhivinayak Temple\": [\n                {\n                    \"name\": \"Food Corp\",\n                    \"latitude\": 18.969915,\n                    \"longitude\": 72.82032509999999,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Food Box\",\n                    \"latitude\": 18.9752524,\n                    \"longitude\": 72.82382179999999,\n                    \"rating\": 4.4,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Natural Ice Cream\",\n                    \"latitude\": 18.9677866,\n                    \"longitude\": 72.82051009999999,\n                    \"rating\": 4.4,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Sarvi Restaurant\",\n                    \"latitude\": 18.9668207,\n                    \"longitude\": 72.8291165,\n                    \"rating\": 4.2,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Grills & Wok\",\n                    \"latitude\": 18.9707473,\n                    \"longitude\": 72.8323569,\n                    \"rating\": 4.2,\n                    \"price_level\": 2\n                }\n            ]\n        }\n    },\n    \"response_data\": {\n        \"1\": [\n            {\n                \"place_name\": \"Gateway of India\",\n                \"description\": \"The Gateway of India is an arch monument built in 1924. It is a popular tourist destination, especially during the evening.\",\n                \"TOE\": \"1.5 hours\",\n                \"lat_long\": \"18.9220, 72.8347\"\n            },\n            {\n                \"place_name\": \"Elephanta Caves\",\n                \"description\": \"The Elephanta Caves are a UNESCO World Heritage Site located on an island near Mumbai. The caves are dedicated to the Hindu god Shiva and are known for their intricate carvings. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"2.5 hours\",\n                \"lat_long\": \"18.9843, 72.8777\"\n            },\n            {\n                \"place_name\": \"Dhobi Ghat\",\n                \"description\": \"Dhobi Ghat is an open-air laundry in Mumbai. It is a unique and fascinating place to visit. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9583, 72.8343\"\n            }\n        ],\n        \"2\": [\n            {\n                \"place_name\": \"Chhatrapati Shivaji Maharaj Terminus\",\n                \"description\": \"Chhatrapati Shivaji Maharaj Terminus is a UNESCO World Heritage Site located in Mumbai. It is a beautiful example of Victorian Gothic Revival architecture. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"18.9491, 72.8335\"\n            },\n            {\n                \"place_name\": \"Kanheri Caves\",\n                \"description\": \"The Kanheri Caves are a group of ancient Buddhist cave temples located in the Sanjay Gandhi National Park. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"3 hours\",\n                \"lat_long\": \"19.1426, 72.9018\"\n            },\n            {\n                \"place_name\": \"Marine Drive\",\n                \"description\": \"Marine Drive is a beautiful promenade located along the coast of Mumbai. It is a popular spot for evening walks and strolls.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9392, 72.8247\"\n            }\n        ],\n        \"3\": [\n            {\n                \"place_name\": \"Juhu Beach\",\n                \"description\": \"Juhu Beach is a popular beach in Mumbai. It is a great place to relax and enjoy the sunset. It is recommended to visit in the evening.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"19.0646, 72.8379\"\n            },\n            {\n                \"place_name\": \"Mani Bhavan\",\n                \"description\": \"Mani Bhavan is a historic building in Mumbai that was once the home of Mahatma Gandhi. It is a popular destination for history buffs. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"1.5 hours\",\n                \"lat_long\": \"18.9582, 72.8291\"\n            },\n            {\n                \"place_name\": \"Siddhivinayak Temple\",\n                \"description\": \"Siddhivinayak Temple is a popular Hindu temple dedicated to Lord Ganesha. It is a popular destination for devotees and tourists alike. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9727, 72.8252\"\n            }\n        ]\n    }\n}\n\n<User Input/>\n\n\nIn the output you just need to give the clubbed JSON with the nearby restaurants with respect to the place.\n<Output>\n {\n        \"1\": [\n            {\n                \"place_name\": \"Gateway of India\",\n                \"description\": \"The Gateway of India is an arch monument built in the early 20th century. It is a popular tourist destination and a must-visit for any visitor to Mumbai. It is best to visit the Gateway of India in the morning or evening to avoid the midday heat.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"18.9220, 72.8347\"\n            },\n            {\n                \"place_name\":\"New Apollo Restuarant\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9228566,72.8320693\"\n            },\n            {\n                \"place_name\":\"Shamiana\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9220554, 72.8330387\"\n            },\n            {\n                \"place_name\": \"Elephanta Caves\",\n                \"description\": \"The Elephanta Caves are a UNESCO World Heritage Site and are a must-visit for any visitor to Mumbai. The caves are located on an island in the harbor and are home to ancient Hindu sculptures. It is best to visit the Elephanta Caves in the morning or evening to avoid the midday heat.\",\n                \"TOE\": \"3 hours\",\n                \"lat_long\": \"18.9899, 72.8776\"\n            },\n\n            \n        \"2\": [\n            {\n                \"place_name\": \"Chhatrapati Shivaji Maharaj Terminus\",\n                \"description\": \"Chhatrapati Shivaji Maharaj Terminus is a UNESCO World Heritage Site and is a must-visit for any visitor to Mumbai. The station is a beautiful example of Victorian Gothic Revival architecture. It is best to visit the Chhatrapati Shivaji Maharaj Terminus in the morning or evening to avoid the midday heat.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"18.9482, 72.8341\"\n            },\n            {\n                \"place_name\":\"Royal China\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9384896, 72.8328156\"\n            },\n            {\n                \"place_name\": \"Marine Drive\",\n                \"description\": \"Marine Drive is a scenic promenade that stretches along the Arabian Sea. It is a popular spot for evening walks and is a must-visit for any visitor to Mumbai. It is best to visit Marine Drive in the evening to enjoy the sunset.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9344, 72.8344\"\n            },\n            {\n                \"place_name\": \"Delhi Darbar\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9238178, 72.8317462\"\n            }\n\n            \n        ],\n       \n        ]\n    }\n}\n<Output/>\n\n\n### EXAMPLE 2 ###\nIn the output you just need to give the clubbed JSON with the nearby restaurants with respect to the place.\n\n<Input>\n{'nearby_restaurants': {'1': {'Eiffel Tower': [{'name': 'Hôtel San Régis', 'latitude': 48.86647959999999, 'longitude': 2.3084964, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Le Cinq', 'latitude': 48.868849, 'longitude': 2.300683, 'rating': 4.6, 'price_level': 4}, {'name': 'De la Tour', 'latitude': 48.8544716, 'longitude': 2.2949214, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Hotel De Sers', 'latitude': 48.8682311, 'longitude': 2.300383999999999, 'rating': 4.5, 'price_level': 'N/A'}, {'name': 'Astrance', 'latitude': 48.8650824, 'longitude': 2.2898578, 'rating': 4.5, 'price_level': 4}], 'Louvre Museum': [{'name': 'Hotel Montalembert', 'latitude': 48.8567203, 'longitude': 2.3278538, 'rating': 4.7, 'price_level': 'N/A'}, {'name': 'Pavillon Faubourg Saint-Germain & Spa', 'latitude': 48.8564689, 'longitude': 2.3303746, 'rating': 4.7, 'price_level': 'N/A'}, {'name': 'Grand Hôtel du Palais Royal', 'latitude': 48.8631306, 'longitude': 2.3379051, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Hotel Edouard VII', 'latitude': 48.8683206, 'longitude': 2.333098, 'rating': 4.5, 'price_level': 'N/A'}, {'name': 'Castille Paris', 'latitude': 48.8683896, 'longitude': 2.326849, 'rating': 4.4, 'price_level': 'N/A'}], 'Arc de Triomphe': [{'name': 'Saint James Paris', 'latitude': 48.8706168, 'longitude': 2.2796401, 'rating': 4.7, 'price_level': 'N/A'}, {'name': 'Le Taillevent', 'latitude': 48.874097, 'longitude': 2.302475, 'rating': 4.7, 'price_level': 4}, {'name': 'Hôtel San Régis', 'latitude': 48.86647959999999, 'longitude': 2.3084964, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Le Cinq', 'latitude': 48.868849, 'longitude': 2.300683, 'rating': 4.6, 'price_level': 4}, {'name': 'Hotel Vernet, Champs - Élysées', 'latitude': 48.8719682, 'longitude': 2.2978942, 'rating': 4.5, 'price_level': 'N/A'}]}, '2': {'Notre Dame Cathedral': [{'name': 'Pavillon Faubourg Saint-Germain & Spa', 'latitude': 48.8564689, 'longitude': 2.3303746, 'rating': 4.7, 'price_level': 'N/A'}, {'name': 'Shu', 'latitude': 48.85304559999999, 'longitude': 2.3422136, 'rating': 4.7, 'price_level': 3}, {'name': 'Le Pavillon de la Reine', 'latitude': 48.85627299999999, 'longitude': 2.366041, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Grand Hôtel du Palais Royal', 'latitude': 48.8631306, 'longitude': 2.3379051, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Le Monteverdi', 'latitude': 48.8518912, 'longitude': 2.334929499999999, 'rating': 4.5, 'price_level': 2}], 'Île de la Cité': [{'name': 'Shu', 'latitude': 48.85304559999999, 'longitude': 2.3422136, 'rating': 4.7, 'price_level': 3}, {'name': 'Le Pavillon de la Reine', 'latitude': 48.85627299999999, 'longitude': 2.366041, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Grand Hôtel du Palais Royal', 'latitude': 48.8631306, 'longitude': 2.3379051, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Auberge Nicolas Flamel', 'latitude': 48.8635423, 'longitude': 2.3531534, 'rating': 4.6, 'price_level': 2}, {'name': 'Les Enfants Rouges', 'latitude': 48.863083, 'longitude': 2.3612283, 'rating': 4.5, 'price_level': 2}], \"Musée d'Orsay\": [{'name': 'Hotel Montalembert', 'latitude': 48.8567203, 'longitude': 2.3278538, 'rating': 4.7, 'price_level': 'N/A'}, {'name': 'Pavillon Faubourg Saint-Germain & Spa', 'latitude': 48.8564689, 'longitude': 2.3303746, 'rating': 4.7, 'price_level': 'N/A'}, {'name': 'Hotel Crillon, A Rosewood Hotel', 'latitude': 48.86797199999999, 'longitude': 2.3221172, 'rating': 4.7, 'price_level': 4}, {'name': 'Grand Hôtel du Palais Royal', 'latitude': 48.8631306, 'longitude': 2.3379051, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Hotel Edouard VII', 'latitude': 48.8683206, 'longitude': 2.333098, 'rating': 4.5, 'price_level': 'N/A'}]}, '3': {'Montmartre': [{'name': 'Crêperie Brocéliande', 'latitude': 48.88439590000001, 'longitude': 2.341128300000001, 'rating': 4.7, 'price_level': 2}, {'name': 'Bistrot HOTARU', 'latitude': 48.8782147, 'longitude': 2.342739299999999, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Le Supercoin', 'latitude': 48.8930915, 'longitude': 2.3505518, 'rating': 4.6, 'price_level': 1}, {'name': \"L'Office\", 'latitude': 48.8739656, 'longitude': 2.3473865, 'rating': 4.6, 'price_level': 2}, {'name': 'Le Pigalle', 'latitude': 48.8816959, 'longitude': 2.3372647, 'rating': 4.5, 'price_level': 'N/A'}], 'Latin Quarter': [{'name': 'Shu', 'latitude': 48.85304559999999, 'longitude': 2.3422136, 'rating': 4.7, 'price_level': 3}, {'name': 'Latin Quartier', 'latitude': 48.8449552, 'longitude': 2.3493156, 'rating': 4.7, 'price_level': 2}, {'name': 'La Truffière', 'latitude': 48.84456650000001, 'longitude': 2.348884900000001, 'rating': 4.5, 'price_level': 4}, {'name': 'Le Monteverdi', 'latitude': 48.8518912, 'longitude': 2.334929499999999, 'rating': 4.5, 'price_level': 2}, {'name': 'French Theory Hotel & Restaurant', 'latitude': 48.84808210000001, 'longitude': 2.3422372, 'rating': 4.4, 'price_level': 'N/A'}], 'Seine River Cruise': [{'name': 'Shu', 'latitude': 48.85304559999999, 'longitude': 2.3422136, 'rating': 4.7, 'price_level': 3}, {'name': 'Le Pavillon de la Reine', 'latitude': 48.85627299999999, 'longitude': 2.366041, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Grand Hôtel du Palais Royal', 'latitude': 48.8631306, 'longitude': 2.3379051, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Auberge Nicolas Flamel', 'latitude': 48.8635423, 'longitude': 2.3531534, 'rating': 4.6, 'price_level': 2}, {'name': 'Les Enfants Rouges', 'latitude': 48.863083, 'longitude': 2.3612283, 'rating': 4.5, 'price_level': 2}]}}, 'response_data': '{\"1\": [{\"place_name\": \"Eiffel Tower\", \"description\": \"Visit the iconic Eiffel Tower, a must-see landmark in Paris. The tower offers stunning views of the city, especially during the evening when it is illuminated.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8584, 2.2945\"}, {\"place_name\": \"Louvre Museum\", \"description\": \"Explore the world-renowned Louvre Museum, home to masterpieces like the Mona Lisa and Venus de Milo. It's best to visit in the morning to avoid crowds.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8606, 2.3376\"}, {\"place_name\": \"Arc de Triomphe\", \"description\": \"Visit the Arc de Triomphe, a triumphal arch commemorating French military victories. Climb to the top for panoramic views of the Champs-Élysées.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8738, 2.2950\"}], \"2\": [{\"place_name\": \"Notre Dame Cathedral\", \"description\": \"Visit the historic Notre Dame Cathedral, a masterpiece of Gothic architecture. Explore its intricate details and admire its stained glass windows.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8534, 2.3496\"}, {\"place_name\": \"Île de la Cité\", \"description\": \"Take a stroll around Île de la Cité, the historical heart of Paris. Explore the charming streets and discover hidden gems.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8567, 2.3522\"}, {\"place_name\": \"Musée d'Orsay\", \"description\": \"Explore the Musée d'Orsay, a museum dedicated to Impressionist and Post-Impressionist art. It's best to visit in the afternoon.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8582, 2.3294\"}], \"3\": [{\"place_name\": \"Montmartre\", \"description\": \"Visit Montmartre, a bohemian neighborhood known for its artists and the Sacré-Cœur Basilica. Enjoy the vibrant atmosphere and admire the views.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8864, 2.3445\"}, {\"place_name\": \"Latin Quarter\", \"description\": \"Explore the Latin Quarter, a historic neighborhood known for its student population and charming cafes. Visit the Sorbonne University and the Pantheon.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8452, 2.3488\"}, {\"place_name\": \"Seine River Cruise\", \"description\": \"Enjoy a romantic evening cruise along the Seine River. Admire the illuminated landmarks and enjoy the Parisian atmosphere.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8566, 2.3522\"}]}'}\n<Input/>\n\n<Output>\n{'1': [{'place_name': 'Eiffel Tower', 'description': \"Visit the iconic Eiffel Tower, a must-see in Paris! It's best to visit in the evening to see the twinkling lights.\", 'TOE': '2 hours', 'lat_long': '48.8584, 2.2945'}, {'place_name': 'Hôtel San Régis', 'description': 'Experience luxury and fine dining at Hôtel San Régis, a renowned hotel with a Michelin-starred restaurant.', 'TOE': '2 hours', 'lat_long': '48.8665, 2.3085'}, {'place_name': 'Le Cinq', 'description': 'Indulge in a sophisticated culinary experience at Le Cinq, a Michelin-starred restaurant offering exquisite French cuisine.', 'TOE': '2 hours', 'lat_long': '48.8688, 2.3007'}, {'place_name': 'Arc de Triomphe', 'description': 'Explore the Arc de Triomphe, a triumphal arch commemorating French military victories. Visit in the afternoon for a beautiful view of the Champs-Élysées.', 'TOE': '1.5 hours', 'lat_long': '48.8738, 2.2950'}, {'place_name': 'Musée du Louvre', 'description': 'Immerse yourself in art history at the Louvre Museum. Visit in the morning to avoid crowds.', 'TOE': '3 hours', 'lat_long': '48.8606, 2.3376'}], '2': [{'place_name': 'Notre Dame Cathedral', 'description': \"Visit the Notre Dame Cathedral, a masterpiece of Gothic architecture. It's best to visit in the morning or afternoon.\", 'TOE': '2 hours', 'lat_long': '48.8534, 2.3488'}, {'place_name': 'Pavillon Faubourg Saint-Germain & Spa', 'description': 'Enjoy a luxurious stay and pampering at Pavillon Faubourg Saint-Germain & Spa, a chic hotel with a renowned spa.', 'TOE': '2 hours', 'lat_long': '48.8565, 2.3304'}, {'place_name': 'Shu', 'description': 'Indulge in authentic Japanese cuisine at Shu, a popular restaurant offering fresh and flavorful dishes.', 'TOE': '2 hours', 'lat_long': '48.8530, 2.3422'}, {'place_name': 'Sacré-Cœur Basilica', 'description': 'Explore the Sacré-Cœur Basilica, a beautiful white basilica offering panoramic views of Paris. Visit in the afternoon for a stunning sunset.', 'TOE': '1.5 hours', 'lat_long': '48.8892, 2.3419'}, {'place_name': 'Moulin Rouge', 'description': 'Experience the iconic Moulin Rouge, a world-famous cabaret. Visit in the evening for a spectacular show.', 'TOE': '2 hours', 'lat_long': '48.8738, 2.3382'}], '3': [{'place_name': 'Île de la Cité', 'description': 'Explore the Île de la Cité, the historical heart of Paris, and discover charming streets, medieval architecture, and the Conciergerie.', 'TOE': '3 hours', 'lat_long': '48.8566, 2.3484'}, {'place_name': 'Pavillon Faubourg Saint-Germain & Spa', 'description': 'Enjoy a luxurious stay and pampering at Pavillon Faubourg Saint-Germain & Spa, a chic hotel with a renowned spa.', 'TOE': '2 hours', 'lat_long': '48.8565, 2.3304'}, {'place_name': 'Shu', 'description': 'Indulge in authentic Japanese cuisine at Shu, a popular restaurant offering fresh and flavorful dishes.', 'TOE': '2 hours', 'lat_long': '48.8530, 2.3422'}, {'place_name': \"Musée d'Orsay\", 'description': \"Admire Impressionist and Post-Impressionist art at the Musée d'Orsay. Visit in the afternoon to enjoy natural light.\", 'TOE': '2 hours', 'lat_long': '48.8583, 2.3290'}, {'place_name': 'Montmartre', 'description': 'Explore the bohemian neighborhood of Montmartre, known for its artists, charming cafes, and the iconic Sacré-Cœur Basilica. Visit in the evening for a lively atmosphere.', 'TOE': '2 hours', 'lat_long': '48.8867, 2.3429'}]}\n<Output/>\n\n### EXAMPLE 3 ###\nIn the output you just need to give the clubbed JSON with the nearby restaurants with respect to the place.\n<Input>\n{'nearby_restaurants': {'1': {'Red Fort': [{'name': 'Rehmatullah Hotel', 'latitude': 28.6492301, 'longitude': 77.2336187, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Gaurav Enterprises', 'latitude': 28.6525585, 'longitude': 77.2330089, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Asha Ram Food/Resturant', 'latitude': 28.6562084, 'longitude': 77.2277737, 'rating': 4.3, 'price_level': 1}, {'name': 'Babu Bhai Kabab Jama Masjid', 'latitude': 28.6469926, 'longitude': 77.2339477, 'rating': 4.2, 'price_level': 1}, {'name': 'Hotel De Romana', 'latitude': 28.649223, 'longitude': 77.2368465, 'rating': 4.1, 'price_level': 'N/A'}], 'Jama Masjid': [{'name': 'Victoria', 'latitude': 28.646524, 'longitude': 77.24330599999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Rehmatullah Hotel', 'latitude': 28.6492301, 'longitude': 77.2336187, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Gaurav Enterprises', 'latitude': 28.6525585, 'longitude': 77.2330089, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Kallu Nihari', 'latitude': 28.6421631, 'longitude': 77.2373418, 'rating': 4.4, 'price_level': 1}, {'name': 'Babu Bhai Kabab Jama Masjid', 'latitude': 28.6469926, 'longitude': 77.2339477, 'rating': 4.2, 'price_level': 1}], 'Chandni Chowk': [{'name': 'Rehmatullah Hotel', 'latitude': 28.6492301, 'longitude': 77.2336187, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Gaurav Enterprises', 'latitude': 28.6525585, 'longitude': 77.2330089, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Asha Ram Food/Resturant', 'latitude': 28.6562084, 'longitude': 77.2277737, 'rating': 4.3, 'price_level': 1}, {'name': 'Babu Bhai Kabab Jama Masjid', 'latitude': 28.6469926, 'longitude': 77.2339477, 'rating': 4.2, 'price_level': 1}, {'name': 'Suvidha', 'latitude': 28.64423709999999, 'longitude': 77.2399054, 'rating': 4.1, 'price_level': 2}]}, '2': {\"Humayun's Tomb\": [{'name': 'Kings Motels (P) Ltd.', 'latitude': 28.6268393, 'longitude': 77.24202489999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Malhotra Cold Drinks', 'latitude': 28.6324693, 'longitude': 77.2407498, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Alfresco', 'latitude': 28.6311565, 'longitude': 77.227477, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'SM Chinese Food Corner', 'latitude': 28.6324069, 'longitude': 77.24086179999999, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Kaushal Dhaba', 'latitude': 28.641201, 'longitude': 77.2356147, 'rating': 4.5, 'price_level': 'N/A'}], 'Qutub Minar': [{'name': 'Hot Pan Cafe', 'latitude': 28.52448, 'longitude': 77.1855205, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Dairy Craft India Pvt.Ltd', 'latitude': 28.524452, 'longitude': 77.192176, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Olive Bar & Kitchen', 'latitude': 28.5257701, 'longitude': 77.1841311, 'rating': 4.6, 'price_level': 4}, {'name': 'Serai', 'latitude': 28.5257692, 'longitude': 77.1841488, 'rating': 4.5, 'price_level': 'N/A'}, {'name': 'Dramz Delhi', 'latitude': 28.5243996, 'longitude': 77.1836545, 'rating': 4.4, 'price_level': 4}], 'Lotus Temple': [{'name': 'Shiwansh Food Snacks', 'latitude': 28.5850632, 'longitude': 77.2551021, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Gitwako Farms India Private Limited', 'latitude': 28.5836924, 'longitude': 77.24395439999999, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Novelty Dairy and Stores', 'latitude': 28.5837165, 'longitude': 77.2438629, 'rating': 4.4, 'price_level': 2}, {'name': 'Beliram Degchiwala', 'latitude': 28.582806, 'longitude': 77.245153, 'rating': 4.2, 'price_level': 'N/A'}, {'name': 'भगत भोजनालय', 'latitude': 28.5851354, 'longitude': 77.2558177, 'rating': 4, 'price_level': 'N/A'}]}, '3': {'India Gate': [{'name': 'The Chambers - Taj', 'latitude': 28.6047628, 'longitude': 77.2238177, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Varq', 'latitude': 28.6047281, 'longitude': 77.2234955, 'rating': 4.8, 'price_level': 4}, {'name': 'Le Belvedere - Le Meridien', 'latitude': 28.6187522, 'longitude': 77.2179598, 'rating': 4.8, 'price_level': 4}, {'name': 'Emperor Lounge', 'latitude': 28.604906, 'longitude': 77.22340299999999, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Masala Library by Jiggs Kalra, New Delhi', 'latitude': 28.61823729999999, 'longitude': 77.21854410000002, 'rating': 4.6, 'price_level': 4}], 'Raj Ghat': [{'name': 'Kings Motels (P) Ltd.', 'latitude': 28.6268393, 'longitude': 77.24202489999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Nashta Paani', 'latitude': 28.6323447, 'longitude': 77.2415481, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Parantha places', 'latitude': 28.63121, 'longitude': 77.2414308, 'rating': 5, 'price_level': 'N/A'}, {'name': 'SM Chinese Food Corner', 'latitude': 28.6324069, 'longitude': 77.24086179999999, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Kaushal Dhaba', 'latitude': 28.641201, 'longitude': 77.2356147, 'rating': 4.5, 'price_level': 'N/A'}], 'Akshardham Temple': [{'name': 'Kings Motels (P) Ltd.', 'latitude': 28.6268393, 'longitude': 77.24202489999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'THE BURGER HUB- Best Burger Pizza Shop In Delhi', 'latitude': 28.6275752, 'longitude': 77.2460383, 'rating': 5, 'price_level': 'N/A'}, {'name': 'THE BURGER HUB', 'latitude': 28.6265269, 'longitude': 77.244924, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Umesh Rai egg shop', 'latitude': 28.62699529999999, 'longitude': 77.2429542, 'rating': 5, 'price_level': 'N/A'}, {'name': 'PAPPU YADAV CHATT WALA (PAPPU PAHALWAN)', 'latitude': 28.6266251, 'longitude': 77.2450957, 'rating': 4.8, 'price_level': 'N/A'}]}, '4': {'Connaught Place': [{'name': 'The Imperial New Delhi', 'latitude': 28.62501779999999, 'longitude': 77.21822759999999, 'rating': 4.7, 'price_level': 4}, {'name': 'Zaffran', 'latitude': 28.6337062, 'longitude': 77.2212046, 'rating': 4.4, 'price_level': 3}, {'name': 'Veda Restaurant', 'latitude': 28.6352633, 'longitude': 77.2181009, 'rating': 4.3, 'price_level': 3}, {'name': 'Starbucks coffee', 'latitude': 28.6321801, 'longitude': 77.2177729, 'rating': 4.3, 'price_level': 3}, {'name': 'United Coffee House', 'latitude': 28.632377, 'longitude': 77.2213847, 'rating': 4.3, 'price_level': 3}], 'Hauz Khas Village': [{'name': 'Standard Dairy & Paneer Bhandhar | SDP Sweets', 'latitude': 28.5617973, 'longitude': 77.2076135, 'rating': 4.9, 'price_level': 'N/A'}, {'name': 'Just Wok It', 'latitude': 28.5599257, 'longitude': 77.2040641, 'rating': 4.3, 'price_level': 'N/A'}, {'name': 'Rajinder Da Dhaba', 'latitude': 28.5655965, 'longitude': 77.19931869999999, 'rating': 4.2, 'price_level': 2}, {'name': 'Green Chick Chop', 'latitude': 28.5579759, 'longitude': 77.2074375, 'rating': 4.2, 'price_level': 'N/A'}, {'name': 'Pasta La Vista', 'latitude': 28.5577371, 'longitude': 77.20804249999999, 'rating': 4.1, 'price_level': 2}]}}, 'response_data': '{\"1\":[{\"place_name\":\"Red Fort\",\"description\":\"The Red Fort is a historic fort in Delhi, India, that served as the main residence of the Mughal emperors for nearly 200 years, until 1857. It is one of the most popular tourist attractions in Delhi. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.6560,77.2310\"},{\"place_name\":\"Jama Masjid\",\"description\":\"Jama Masjid is a mosque in Old Delhi, India, built by Mughal emperor Shah Jahan between 1644 and 1656. It is the largest mosque in India and can accommodate up to 25,000 worshippers. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1.5 hours\",\"lat_long\":\"28.6525,77.2410\"},{\"place_name\":\"Chandni Chowk\",\"description\":\"Chandni Chowk is a bustling market in Old Delhi, India. It is one of the oldest and busiest markets in Delhi, and is known for its street food, spices, and textiles. It is best to visit in the evening to experience the hustle and bustle of the market.\",\"TOE\":\"3 hours\",\"lat_long\":\"28.6524,77.2310\"}],\"2\":[{\"place_name\":\"Humayun's Tomb\",\"description\":\"Humayun's Tomb is the tomb of the Mughal emperor Humayun in Delhi, India. It was built in 1569-70 by his wife Hamida Banu Begum. It is a UNESCO World Heritage Site and is a popular tourist destination. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.6318,77.2405\"},{\"place_name\":\"Qutub Minar\",\"description\":\"Qutub Minar is a minaret and UNESCO World Heritage Site in Delhi, India. It is the tallest brick minaret in the world and was built in 1193 by Qutub-ud-din Aibak. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.5244,77.1854\"},{\"place_name\":\"Lotus Temple\",\"description\":\"The Lotus Temple is a Baháʼí House of Worship that is located in New Delhi, India. It is a unique and beautiful building that is shaped like a lotus flower. It is a popular tourist destination and is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1.5 hours\",\"lat_long\":\"28.5830,77.2580\"}],\"3\":[{\"place_name\":\"India Gate\",\"description\":\"India Gate is a war memorial located in New Delhi, India. It was built in 1921 to commemorate the 82,000 soldiers of the British Indian Army who died in the First World War. It is a popular tourist destination and is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1.5 hours\",\"lat_long\":\"28.6129,77.2290\"},{\"place_name\":\"Raj Ghat\",\"description\":\"Raj Ghat is a memorial to Mahatma Gandhi in Delhi, India. It is located on the banks of the Yamuna River and is a popular tourist destination. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1 hour\",\"lat_long\":\"28.6326,77.2441\"},{\"place_name\":\"Akshardham Temple\",\"description\":\"Akshardham Temple is a Hindu temple in New Delhi, India. It is a beautiful and intricately carved temple that is dedicated to Swaminarayan. It is a popular tourist destination and is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.6294,77.2490\"}],\"4\":[{\"place_name\":\"Connaught Place\",\"description\":\"Connaught Place is a commercial and shopping district in New Delhi, India. It is a popular destination for shopping, dining, and entertainment. It is best to visit in the evening to experience the nightlife.\",\"TOE\":\"3 hours\",\"lat_long\":\"28.6328,77.2206\"},{\"place_name\":\"Hauz Khas Village\",\"description\":\"Hauz Khas Village is a popular nightlife spot in Delhi, India. It is known for its restaurants, bars, and art galleries. It is best to visit in the evening to experience the nightlife.\",\"TOE\":\"3 hours\",\"lat_long\":\"28.5676,77.2075\"}]}'}\n<Input/>\n<Output>\n{'nearby_restaurants': {'1': {'Red Fort': [{'name': 'Rehmatullah Hotel', 'latitude': 28.6492301, 'longitude': 77.2336187, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Gaurav Enterprises', 'latitude': 28.6525585, 'longitude': 77.2330089, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Asha Ram Food/Resturant', 'latitude': 28.6562084, 'longitude': 77.2277737, 'rating': 4.3, 'price_level': 1}, {'name': 'Babu Bhai Kabab Jama Masjid', 'latitude': 28.6469926, 'longitude': 77.2339477, 'rating': 4.2, 'price_level': 1}, {'name': 'Hotel De Romana', 'latitude': 28.649223, 'longitude': 77.2368465, 'rating': 4.1, 'price_level': 'N/A'}], 'Jama Masjid': [{'name': 'Victoria', 'latitude': 28.646524, 'longitude': 77.24330599999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Rehmatullah Hotel', 'latitude': 28.6492301, 'longitude': 77.2336187, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Gaurav Enterprises', 'latitude': 28.6525585, 'longitude': 77.2330089, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Kallu Nihari', 'latitude': 28.6421631, 'longitude': 77.2373418, 'rating': 4.4, 'price_level': 1}, {'name': 'Babu Bhai Kabab Jama Masjid', 'latitude': 28.6469926, 'longitude': 77.2339477, 'rating': 4.2, 'price_level': 1}], 'Chandni Chowk': [{'name': 'Rehmatullah Hotel', 'latitude': 28.6492301, 'longitude': 77.2336187, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Gaurav Enterprises', 'latitude': 28.6525585, 'longitude': 77.2330089, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Asha Ram Food/Resturant', 'latitude': 28.6562084, 'longitude': 77.2277737, 'rating': 4.3, 'price_level': 1}, {'name': 'Babu Bhai Kabab Jama Masjid', 'latitude': 28.6469926, 'longitude': 77.2339477, 'rating': 4.2, 'price_level': 1}, {'name': 'Suvidha', 'latitude': 28.64423709999999, 'longitude': 77.2399054, 'rating': 4.1, 'price_level': 2}]}, '2': {\"Humayun's Tomb\": [{'name': 'Kings Motels (P) Ltd.', 'latitude': 28.6268393, 'longitude': 77.24202489999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Malhotra Cold Drinks', 'latitude': 28.6324693, 'longitude': 77.2407498, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Alfresco', 'latitude': 28.6311565, 'longitude': 77.227477, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'SM Chinese Food Corner', 'latitude': 28.6324069, 'longitude': 77.24086179999999, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Kaushal Dhaba', 'latitude': 28.641201, 'longitude': 77.2356147, 'rating': 4.5, 'price_level': 'N/A'}], 'Qutub Minar': [{'name': 'Hot Pan Cafe', 'latitude': 28.52448, 'longitude': 77.1855205, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Dairy Craft India Pvt.Ltd', 'latitude': 28.524452, 'longitude': 77.192176, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Olive Bar & Kitchen', 'latitude': 28.5257701, 'longitude': 77.1841311, 'rating': 4.6, 'price_level': 4}, {'name': 'Serai', 'latitude': 28.5257692, 'longitude': 77.1841488, 'rating': 4.5, 'price_level': 'N/A'}, {'name': 'Dramz Delhi', 'latitude': 28.5243996, 'longitude': 77.1836545, 'rating': 4.4, 'price_level': 4}], 'Lotus Temple': [{'name': 'Shiwansh Food Snacks', 'latitude': 28.5850632, 'longitude': 77.2551021, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Gitwako Farms India Private Limited', 'latitude': 28.5836924, 'longitude': 77.24395439999999, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Novelty Dairy and Stores', 'latitude': 28.5837165, 'longitude': 77.2438629, 'rating': 4.4, 'price_level': 2}, {'name': 'Beliram Degchiwala', 'latitude': 28.582806, 'longitude': 77.245153, 'rating': 4.2, 'price_level': 'N/A'}, {'name': 'भगत भोजनालय', 'latitude': 28.5851354, 'longitude': 77.2558177, 'rating': 4, 'price_level': 'N/A'}]}, '3': {'India Gate': [{'name': 'The Chambers - Taj', 'latitude': 28.6047628, 'longitude': 77.2238177, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Varq', 'latitude': 28.6047281, 'longitude': 77.2234955, 'rating': 4.8, 'price_level': 4}, {'name': 'Le Belvedere - Le Meridien', 'latitude': 28.6187522, 'longitude': 77.2179598, 'rating': 4.8, 'price_level': 4}, {'name': 'Emperor Lounge', 'latitude': 28.604906, 'longitude': 77.22340299999999, 'rating': 4.6, 'price_level': 'N/A'}, {'name': 'Masala Library by Jiggs Kalra, New Delhi', 'latitude': 28.61823729999999, 'longitude': 77.21854410000002, 'rating': 4.6, 'price_level': 4}], 'Raj Ghat': [{'name': 'Kings Motels (P) Ltd.', 'latitude': 28.6268393, 'longitude': 77.24202489999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Nashta Paani', 'latitude': 28.6323447, 'longitude': 77.2415481, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Parantha places', 'latitude': 28.63121, 'longitude': 77.2414308, 'rating': 5, 'price_level': 'N/A'}, {'name': 'SM Chinese Food Corner', 'latitude': 28.6324069, 'longitude': 77.24086179999999, 'rating': 4.8, 'price_level': 'N/A'}, {'name': 'Kaushal Dhaba', 'latitude': 28.641201, 'longitude': 77.2356147, 'rating': 4.5, 'price_level': 'N/A'}], 'Akshardham Temple': [{'name': 'Kings Motels (P) Ltd.', 'latitude': 28.6268393, 'longitude': 77.24202489999999, 'rating': 5, 'price_level': 'N/A'}, {'name': 'THE BURGER HUB- Best Burger Pizza Shop In Delhi', 'latitude': 28.6275752, 'longitude': 77.2460383, 'rating': 5, 'price_level': 'N/A'}, {'name': 'THE BURGER HUB', 'latitude': 28.6265269, 'longitude': 77.244924, 'rating': 5, 'price_level': 'N/A'}, {'name': 'Umesh Rai egg shop', 'latitude': 28.62699529999999, 'longitude': 77.2429542, 'rating': 5, 'price_level': 'N/A'}, {'name': 'PAPPU YADAV CHATT WALA (PAPPU PAHALWAN)', 'latitude': 28.6266251, 'longitude': 77.2450957, 'rating': 4.8, 'price_level': 'N/A'}]}, '4': {'Connaught Place': [{'name': 'The Imperial New Delhi', 'latitude': 28.62501779999999, 'longitude': 77.21822759999999, 'rating': 4.7, 'price_level': 4}, {'name': 'Zaffran', 'latitude': 28.6337062, 'longitude': 77.2212046, 'rating': 4.4, 'price_level': 3}, {'name': 'Veda Restaurant', 'latitude': 28.6352633, 'longitude': 77.2181009, 'rating': 4.3, 'price_level': 3}, {'name': 'Starbucks coffee', 'latitude': 28.6321801, 'longitude': 77.2177729, 'rating': 4.3, 'price_level': 3}, {'name': 'United Coffee House', 'latitude': 28.632377, 'longitude': 77.2213847, 'rating': 4.3, 'price_level': 3}], 'Hauz Khas Village': [{'name': 'Standard Dairy & Paneer Bhandhar | SDP Sweets', 'latitude': 28.5617973, 'longitude': 77.2076135, 'rating': 4.9, 'price_level': 'N/A'}, {'name': 'Just Wok It', 'latitude': 28.5599257, 'longitude': 77.2040641, 'rating': 4.3, 'price_level': 'N/A'}, {'name': 'Rajinder Da Dhaba', 'latitude': 28.5655965, 'longitude': 77.19931869999999, 'rating': 4.2, 'price_level': 2}, {'name': 'Green Chick Chop', 'latitude': 28.5579759, 'longitude': 77.2074375, 'rating': 4.2, 'price_level': 'N/A'}, {'name': 'Pasta La Vista', 'latitude': 28.5577371, 'longitude': 77.20804249999999, 'rating': 4.1, 'price_level': 2}]}}, 'response_data': '{\"1\":[{\"place_name\":\"Red Fort\",\"description\":\"The Red Fort is a historic fort in Delhi, India, that served as the main residence of the Mughal emperors for nearly 200 years, until 1857. It is one of the most popular tourist attractions in Delhi. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.6560,77.2310\"},{\"place_name\":\"Jama Masjid\",\"description\":\"Jama Masjid is a mosque in Old Delhi, India, built by Mughal emperor Shah Jahan between 1644 and 1656. It is the largest mosque in India and can accommodate up to 25,000 worshippers. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1.5 hours\",\"lat_long\":\"28.6525,77.2410\"},{\"place_name\":\"Chandni Chowk\",\"description\":\"Chandni Chowk is a bustling market in Old Delhi, India. It is one of the oldest and busiest markets in Delhi, and is known for its street food, spices, and textiles. It is best to visit in the evening to experience the hustle and bustle of the market.\",\"TOE\":\"3 hours\",\"lat_long\":\"28.6524,77.2310\"}],\"2\":[{\"place_name\":\"Humayun's Tomb\",\"description\":\"Humayun's Tomb is the tomb of the Mughal emperor Humayun in Delhi, India. It was built in 1569-70 by his wife Hamida Banu Begum. It is a UNESCO World Heritage Site and is a popular tourist destination. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.6318,77.2405\"},{\"place_name\":\"Qutub Minar\",\"description\":\"Qutub Minar is a minaret and UNESCO World Heritage Site in Delhi, India. It is the tallest brick minaret in the world and was built in 1193 by Qutub-ud-din Aibak. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.5244,77.1854\"},{\"place_name\":\"Lotus Temple\",\"description\":\"The Lotus Temple is a Baháʼí House of Worship that is located in New Delhi, India. It is a unique and beautiful building that is shaped like a lotus flower. It is a popular tourist destination and is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1.5 hours\",\"lat_long\":\"28.5830,77.2580\"}],\"3\":[{\"place_name\":\"India Gate\",\"description\":\"India Gate is a war memorial located in New Delhi, India. It was built in 1921 to commemorate the 82,000 soldiers of the British Indian Army who died in the First World War. It is a popular tourist destination and is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1.5 hours\",\"lat_long\":\"28.6129,77.2290\"},{\"place_name\":\"Raj Ghat\",\"description\":\"Raj Ghat is a memorial to Mahatma Gandhi in Delhi, India. It is located on the banks of the Yamuna River and is a popular tourist destination. It is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"1 hour\",\"lat_long\":\"28.6326,77.2441\"},{\"place_name\":\"Akshardham Temple\",\"description\":\"Akshardham Temple is a Hindu temple in New Delhi, India. It is a beautiful and intricately carved temple that is dedicated to Swaminarayan. It is a popular tourist destination and is best to visit in the morning or evening to avoid the heat.\",\"TOE\":\"2 hours\",\"lat_long\":\"28.6294,77.2490\"}],\"4\":[{\"place_name\":\"Connaught Place\",\"description\":\"Connaught Place is a commercial and shopping district in New Delhi, India. It is a popular destination for shopping, dining, and entertainment. It is best to visit in the evening to experience the nightlife.\",\"TOE\":\"3 hours\",\"lat_long\":\"28.6328,77.2206\"},{\"place_name\":\"Hauz Khas Village\",\"description\":\"Hauz Khas Village is a popular nightlife spot in Delhi, India. It is known for its restaurants, bars, and art galleries. It is best to visit in the evening to experience the nightlife.\",\"TOE\":\"3 hours\",\"lat_long\":\"28.5676,77.2075\"}]}'}\n<Output/>\n\n<Output/>\n<EXAMPLES/>\n\n",
            
            )

            chat_session = model.start_chat(history=[])
            response_merged = chat_session.send_message(str(response_raw))

            response_data_unmerged = response_merged.text
            self.insert_trip_details(
                user_id,
                stay_details,
                number_of_days,
                budget,
                additional_preferences,
                response_data_unmerged,
                nearby_restaurants
            )

            return Response(response_data_unmerged, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FetchTripDetails(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            # Fetch all records where user_id matches
            trip_details = UserTripInfo.objects.filter(user_id=user_id)

            # Serialize the queryset
            serializer = UserTripInfoSerializer(trip_details, many=True)
            serialized_data = serializer.data

            # Return the serialized data as JSON response
            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FetchPlan(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get("trip_id")

            trip_details = UserTripInfo.objects.filter(
                trip_id=trip_id
            ).first()  # Assuming trip_id is unique

            if not trip_details:
                return Response(
                    {"error": "Trip details not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = GeneratedPlanSerializer(trip_details)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUserTripProgress(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get("trip_id")
            user_id = request.data.get("user_id")
            day = request.data.get("day")

            UserTripProgressInfo.objects.create(
                user_id=user_id, trip_id=trip_id, day=day
            )

            response = {"user_id": user_id, "trip_id": trip_id, "day": day}

            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FetchTripDetails(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            # Fetch all records where user_id matches
            trip_details = UserTripInfo.objects.filter(user_id=user_id)

            # Serialize the queryset
            serializer = UserTripInfoSerializer(trip_details, many=True)
            serialized_data = serializer.data
            # Return the serialized data as JSON response
            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FetchPlan(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get("trip_id")
            trip_details = UserTripInfo.objects.filter(trip_id=trip_id).first()

            if not trip_details:
                return Response(
                    {"error": "Trip details not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = GeneratedPlanSerializer(trip_details)
            response_data = json.dumps(serializer.data)
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUserTripProgress(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get("trip_id")
            user_id = request.data.get("user_id")
            day = request.data.get("day")

            UserTripProgressInfo.objects.create(
                user_id=user_id, trip_id=trip_id, day=day
            )

            response = {"user_id": user_id, "trip_id": trip_id, "day": day}

            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FetchUserTripProgress(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get("trip_id")
            trip_details = UserTripProgressInfo.objects.filter(trip_id=trip_id)
            serializer = UserTripProgressSerializer(trip_details, many=True)
            serialized_data = serializer.data

            # Return the serialized data as JSON response
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeminiSuggestions(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get("trip_id")
            current_day = request.data.get("current_day")
            original_plan = request.data.get("original_plan")
            user_changes = request.data.get("user_changes")
            
            trip_info = get_object_or_404(UserTripInfo, trip_id=trip_id)

            serializer = UserTripInfoSerializer(trip_info)
            nearby_restaurants = serializer.data.get("nearby_restaurants")

            print("Nearby_Restaurants", nearby_restaurants)

            genai.configure(api_key=os.environ["GOOGLE_GEMINI_API_KEY"])

            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                  system_instruction=f"""You are a travel agent, you plan itineraries for users. You need to give an alternate plan for the user's trip based on their current progress and problems. 
You will be given the below input:
original_plan: It would be a JSON structure which represents the user's original plan.
current_day: It represents the current day the user is in. It will give you an idea of the user's trip progress.
user_changes: It represents the changes the user wants to make in the itinerary or the suggestions they want from you.
You need to edit the original_plan and share it as the output and also let the user know the changes/additions you made.
Only share the original_plan with the updated data and the summary of the changes with friendly text. Your changes should be added at last of the JSON as shown in the below sample output.
Always generate new suggestions different from the already present locations.

If the user wants to change any restaurants in the original itinerary always pick up restaurants from the nearby_restaurants JSON given below. It contains all the nearby places based on the places. 

If the user wants you to add entire days always pickup restaurants from the below nearby_restaurants data only. Suggest restaurants for breakfast, lunch and dinner you should only add 3 restaurants per day.

{nearby_restaurants}

SAMPLE_OUTPUT 1:
{{
  "generated_plan": {{
    "1": [
      {{
        "place_name": "Marina Beach",
        "description": "Marina Beach is a must-visit in Chennai, especially in the evening. Enjoy the cool sea breeze and watch the sunset.",
        "TOE": "2 hours",
        "lat_long": "13.0546, 80.2717"
      }},
      {{
        "place_name": "Bismillah Briyani",
        "description": "Enjoy a delicious and affordable biryani at Bismillah Briyani, a popular spot for local flavors.",
        "TOE": "1 hour",
        "lat_long": "13.0598, 80.2746"
      }},
      {{
        "place_name": "Beyond Indus",
        "description": "Indulge in authentic North Indian cuisine at Beyond Indus, known for its flavorful dishes and warm ambiance.",
        "TOE": "1.5 hours",
        "lat_long": "13.0614, 80.2639"
      }},
      {{
        "place_name": "Kapaleeshwarar Temple",
        "description": "This ancient Hindu temple is known for its intricate architecture. Visit in the morning or afternoon to avoid the crowds.",
        "TOE": "1.5 hours",
        "lat_long": "13.0502, 80.2691"
      }},
      {{
        "place_name": "The Madras Crocodile Bank",
        "description": "Visit this unique reptile park in the afternoon or evening. Learn about crocodiles and other reptiles.",
        "TOE": "2 hours",
        "lat_long": "12.9841, 80.2153"
      }}
    ],
    "2": [
      {{
        "place_name": "Fort St. George",
        "description": "Explore this historic fort in the morning to learn about its rich history.",
        "TOE": "2 hours",
        "lat_long": "13.0824, 80.2728"
      }},
      {{
        "place_name": "The Tandoori Kitchen",
        "description": "Enjoy traditional Indian flavors at The Tandoori Kitchen, known for its succulent tandoori dishes.",
        "TOE": "1.5 hours",
        "lat_long": "13.0809, 80.2699"
      }},
      {{
        "place_name": "Government Museum",
        "description": "Visit this museum to see a collection of artifacts from Tamil Nadu's history and culture. This is best visited in the afternoon.",
        "TOE": "2 hours",
        "lat_long": "13.0530, 80.2704"
      }},
      {{
        "place_name": "Parthasarathy Temple",
        "description": "This temple is dedicated to Lord Krishna and is a popular pilgrimage site. It is best visited in the evening.",
        "TOE": "1.5 hours",
        "lat_long": "13.0554, 80.2656"
      }},
      {{
        "place_name": "Beyond Indus",
        "description": "Indulge in authentic North Indian cuisine at Beyond Indus, known for its flavorful dishes and warm ambiance.",
        "TOE": "1.5 hours",
        "lat_long": "13.0614, 80.2639"
      }}
    ],
    "3": [
      {{
        "place_name": "Anna Salai",
        "description": "Explore the bustling Anna Salai for shopping and dining. It's best to visit in the afternoon or evening.",
        "TOE": "3 hours",
        "lat_long": "13.0680, 80.2562"
      }},
      {{
        "place_name": "Dahlia Restaurant",
        "description": "Enjoy a fine dining experience at Dahlia Restaurant, known for its elegant ambiance and delicious cuisine.",
        "TOE": "2 hours",
        "lat_long": "13.0626, 80.2455"
      }},
      {{
        "place_name": "San Thome Basilica",
        "description": "This historic church is a popular pilgrimage site. Visit in the morning or afternoon for a peaceful experience.",
        "TOE": "1.5 hours",
        "lat_long": "13.0645, 80.2689"
      }},
      {{
        "place_name": "VGP Universal Kingdom",
        "description": "Enjoy a day of fun and entertainment at this amusement park. It's best to visit in the afternoon or evening.",
        "TOE": "4 hours",
        "lat_long": "12.9915, 80.2144"
      }},
      {{
        "place_name": "Bismillah Briyani",
        "description": "Enjoy a delicious and affordable biryani at Bismillah Briyani, a popular spot for local flavors.",
        "TOE": "1 hour",
        "lat_long": "13.0598, 80.2746"
      }}
    ],
    "4": [
      {{
        "place_name": "Marina Beach",
        "description": "Marina Beach is a must-visit in Chennai, especially in the evening. Enjoy the cool sea breeze and watch the sunset.",
        "TOE": "2 hours",
        "lat_long": "13.0546, 80.2717"
      }},
      {{
        "place_name": "The Madras Crocodile Bank",
        "description": "Visit this unique reptile park in the afternoon or evening. Learn about crocodiles and other reptiles.",
        "TOE": "2 hours",
        "lat_long": "12.9841, 80.2153"
      }},
      {{
        "place_name": "Kapaleeshwarar Temple",
        "description": "This ancient Hindu temple is known for its intricate architecture. Visit in the morning or afternoon to avoid the crowds.",
        "TOE": "1.5 hours",
        "lat_long": "13.0502, 80.2691"
      }},
      {{
        "place_name": "Government Museum",
        "description": "Visit this museum to see a collection of artifacts from Tamil Nadu's history and culture. This is best visited in the afternoon.",
        "TOE": "2 hours",
        "lat_long": "13.0530, 80.2704"
      }},
      {{
        "place_name": "Fort St. George",
        "description": "Explore this historic fort in the morning to learn about its rich history.",
        "TOE": "2 hours",
        "lat_long": "13.0824, 80.2728"
      }}
    ],
    "5": [
      {{
        "place_name": "MGM Dizzee World",
        "description": "Enjoy a thrilling day at MGM Dizzee World, a popular amusement park in Chennai.",
        "TOE": "4 hours",
        "lat_long": "13.0028, 80.1836"
      }},
      {{
        "place_name": "Qutab Shahi Tombs",
        "description": "Explore the magnificent Qutab Shahi Tombs, a UNESCO World Heritage Site in Hyderabad.",
        "TOE": "2 hours",
        "lat_long": "17.3851, 78.4867"
      }},
      {{
        "place_name": "Birla Mandir",
        "description": "Visit the serene Birla Mandir, a beautiful Hindu temple dedicated to Lord Venkateswara.",
        "TOE": "1.5 hours",
        "lat_long": "17.3839, 78.4741"
      }},
      {{
        "place_name": "Charminar",
        "description": "Admire the iconic Charminar, a historic mosque and a symbol of Hyderabad.",
        "TOE": "1.5 hours",
        "lat_long": "17.3609, 78.4740"
      }},
      {{
        "place_name": "Salar Jung Museum",
        "description": "Explore the rich collection of art and artifacts at the Salar Jung Museum.",
        "TOE": "2 hours",
        "lat_long": "17.3638, 78.4712"
      }}
    ]
  }},
    "changes": "I have added two more days to your trip. Day 4 will be a repeat of Day 1 to allow you to explore more of the city. Day 5 will take you to Hyderabad to experience its rich culture and history. I added MGM Dizzee World in Day 4 to give you a fun day. In Day 5 I added Qutab Shahi Tombs, Birla Mandir, Charminar, and Salar Jung Museum. Enjoy your extended trip!"
}}

{{
  "generated_plan": {{
    "1": [
      {{
        "place_name": "Marina Beach",
        "description": "Marina Beach is a must-visit in Chennai, especially in the evening. Enjoy the cool sea breeze and watch the sunset.",
        "TOE": "2 hours",
        "lat_long": "13.0546, 80.2717"
      }},
      {{
        "place_name": "Bismillah Briyani",
        "description": "Enjoy a delicious and affordable biryani at Bismillah Briyani, a popular spot for local flavors.",
        "TOE": "1 hour",
        "lat_long": "13.0598, 80.2746"
      }},
      {{
        "place_name": "Beyond Indus",
        "description": "Indulge in authentic North Indian cuisine at Beyond Indus, known for its flavorful dishes and warm ambiance.",
        "TOE": "1.5 hours",
        "lat_long": "13.0614, 80.2639"
      }},
      {{
        "place_name": "Kapaleeshwarar Temple",
        "description": "This ancient Hindu temple is known for its intricate architecture. Visit in the morning or afternoon to avoid the crowds.",
        "TOE": "1.5 hours",
        "lat_long": "13.0502, 80.2691"
      }},
      {{
        "place_name": "The Madras Crocodile Bank",
        "description": "Visit this unique reptile park in the afternoon or evening. Learn about crocodiles and other reptiles.",
        "TOE": "2 hours",
        "lat_long": "12.9841, 80.2153"
      }}
    ],
    "2": [
      {{
        "place_name": "Elliot's Beach",
        "description": "Elliot's Beach, also known as Besant Nagar Beach, is a popular beach in Chennai known for its calm waters and beautiful sunset views. It's a great place to relax, enjoy the beach, and watch the sunset.",
        "TOE": "2 hours",
        "lat_long": "13.0232, 80.2565"
      }},
      {{
        "place_name": "The Tandoori Kitchen",
        "description": "Enjoy traditional Indian flavors at The Tandoori Kitchen, known for its succulent tandoori dishes.",
        "TOE": "1.5 hours",
        "lat_long": "13.0809, 80.2699"
      }},
      {{
        "place_name": "Government Museum",
        "description": "Visit this museum to see a collection of artifacts from Tamil Nadu's history and culture. This is best visited in the afternoon.",
        "TOE": "2 hours",
        "lat_long": "13.0530, 80.2704"
      }},
      {{
        "place_name": "Parthasarathy Temple",
        "description": "This temple is dedicated to Lord Krishna and is a popular pilgrimage site. It is best visited in the evening.",
        "TOE": "1.5 hours",
        "lat_long": "13.0554, 80.2656"
      }},
      {{
        "place_name": "Beyond Indus",
        "description": "Indulge in authentic North Indian cuisine at Beyond Indus, known for its flavorful dishes and warm ambiance.",
        "TOE": "1.5 hours",
        "lat_long": "13.0614, 80.2639"
      }}
    ],
    "3": [
      {{
        "place_name": "Anna Salai",
        "description": "Explore the bustling Anna Salai for shopping and dining. It's best to visit in the afternoon or evening.",
        "TOE": "3 hours",
        "lat_long": "13.0680, 80.2562"
      }},
      {{
        "place_name": "Dahlia Restaurant",
        "description": "Enjoy a fine dining experience at Dahlia Restaurant, known for its elegant ambiance and delicious cuisine.",
        "TOE": "2 hours",
        "lat_long": "13.0626, 80.2455"
      }},
      {{
        "place_name": "San Thome Basilica",
        "description": "This historic church is a popular pilgrimage site. Visit in the morning or afternoon for a peaceful experience.",
        "TOE": "1.5 hours",
        "lat_long": "13.0645, 80.2689"
      }},
      {{
        "place_name": "VGP Universal Kingdom",
        "description": "Enjoy a day of fun and entertainment at this amusement park. It's best to visit in the afternoon or evening.",
        "TOE": "4 hours",
        "lat_long": "12.9915, 80.2144"
      }},
      {{
        "place_name": "Bismillah Briyani",
        "description": "Enjoy a delicious and affordable biryani at Bismillah Briyani, a popular spot for local flavors.",
        "TOE": "1 hour",
        "lat_long": "13.0598, 80.2746"
      }}
    ],
    "4": [
      {{
        "place_name": "Marina Beach",
        "description": "Marina Beach is a must-visit in Chennai, especially in the evening. Enjoy the cool sea breeze and watch the sunset.",
        "TOE": "2 hours",
        "lat_long": "13.0546, 80.2717"
      }},
      {{
        "place_name": "The Madras Crocodile Bank",
        "description": "Visit this unique reptile park in the afternoon or evening. Learn about crocodiles and other reptiles.",
        "TOE": "2 hours",
        "lat_long": "12.9841, 80.2153"
      }},
      {{
        "place_name": "Kapaleeshwarar Temple",
        "description": "This ancient Hindu temple is known for its intricate architecture. Visit in the morning or afternoon to avoid the crowds.",
        "TOE": "1.5 hours",
        "lat_long": "13.0502, 80.2691"
      }},
      {{
        "place_name": "Government Museum",
        "description": "Visit this museum to see a collection of artifacts from Tamil Nadu's history and culture. This is best visited in the afternoon.",
        "TOE": "2 hours",
        "lat_long": "13.0530, 80.2704"
      }},
      {{
        "place_name": "Fort St. George",
        "description": "Explore this historic fort in the morning to learn about its rich history.",
        "TOE": "2 hours",
        "lat_long": "13.0824, 80.2728"
      }}
    ],
    "5": [
      {{
        "place_name": "MGM Dizzee World",
        "description": "Enjoy a thrilling day at MGM Dizzee World, a popular amusement park in Chennai.",
        "TOE": "4 hours",
        "lat_long": "13.0028, 80.1836"
      }},
      {{
        "place_name": "Qutab Shahi Tombs",
        "description": "Explore the magnificent Qutab Shahi Tombs, a UNESCO World Heritage Site in Hyderabad.",
        "TOE": "2 hours",
        "lat_long": "17.3851, 78.4867"
      }},
      {{
        "place_name": "Birla Mandir",
        "description": "Visit the serene Birla Mandir, a beautiful Hindu temple dedicated to Lord Venkateswara.",
        "TOE": "1.5 hours",
        "lat_long": "17.3839, 78.4741"
      }},
      {{
        "place_name": "Charminar",
        "description": "Admire the iconic Charminar, a historic mosque and a symbol of Hyderabad.",
        "TOE": "1.5 hours",
        "lat_long": "17.3609, 78.4740"
      }},
      {{
        "place_name": "Salar Jung Museum",
        "description": "Explore the rich collection of art and artifacts at the Salar Jung Museum.",
        "TOE": "2 hours",
        "lat_long": "17.3638, 78.4712"
      }}
    ]
  }},
  "changes": "I have replaced Fort St George with Elliot's Beach on Day 2 as it's a nearby beach."
}}

""" )

            chat_session = model.start_chat(history=[])

            concatenated_input = f"Original Details: {original_plan}\nCurrent day: {current_day}\Changes/Problems the user is currently facing with the original plan: {user_changes}\n"

            response = chat_session.send_message(concatenated_input)
            response_data = response.text

            response = {
                "user_changes": user_changes,
                "current_day": current_day,
                "response_data": response_data,
            }

            print("Suggestion response", response_data)
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateTrip(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get("trip_id")
            new_plan = request.data.get("new_plan")

            restructured_plan_str = json.dumps(new_plan)

            # Fetch the trip details using the trip_id
            trip_details = UserTripInfo.objects.filter(trip_id=trip_id).first()

            if not trip_details:
                return Response(
                    {"error": "Trip details not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Update the generated_plan with the new_plan
            trip_details.generated_plan = restructured_plan_str
            trip_details.save()

            return Response(
                {"message": "Trip details updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
