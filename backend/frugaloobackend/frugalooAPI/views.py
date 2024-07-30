from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
import requests
import re
from supabase import create_client, Client  # type: ignore
from .models import UserTripInfo, UserTripProgressInfo, MessageLog
from .serializers import (
    UserTripInfoSerializer,
    GeneratedPlanSerializer,
    UserTripProgressSerializer,
    FinanceLogSerializer,
)
from asgiref.sync import sync_to_async
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
                model_name="gemini-1.5-pro",
                generation_config=generation_config,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                system_instruction='### TASK DESCRIPTION ###\nGenerate an itinerary based on the provided user information. Each day in the itinerary should contain a minimum of three mandatory activities and all the activities should be near each other with the travelling time less than 2 hours. In addition to the mandatory activities, you may recommend an Exploration/Shopping activity if the user\'s day has sufficient bandwidth. This estimation can be made based on the "Time of Exploration" (TOE) for the mandatory activities.\n\nEnsure that the user visits unique places each day, without repeating any places throughout the itinerary. If the number of days is more than the number of unique places, recommend some additional activities and adventures, but do not repeat places.\n\nThe itinerary should always start the day with a morning activity, followed by an afternoon activity, and end the day with an evening activity.\n\n### USER INPUT FORMAT ###\nThe user will provide the following input:\n\nstay_details\nnumber_of_days\nbudget\nadditional_preferences\n\n### OUTPUT FORMAT ###\nThe output should be a JSON structure formatted as follows:\n\n{\n  "1": [\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    }\n  ],\n  "2": [\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    }\n  ],\n  "3": [\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    }\n  ]\n}\n\n\n### GUIDELINES ###\n\nUnique Places: Ensure all places in the itinerary are unique across all days.\nStructured Schedule: Each day starts with a morning activity, followed by an afternoon activity, and ends with an evening activity.\nExploration/Shopping Activity: Include an additional Exploration/Shopping activity if time permits, based on the TOE of mandatory activities.\nJSON Structure: Ensure the JSON output is correctly structured with no repeated places.\n\n### EXAMPLE OUTPUT CONTAINING DUPLICATE ###\n{\n  "1": [\n    {\n      "place_name": "Central Park",\n      "description": "A large public park in New York City. Best time to visit: Morning",\n      "TOE": "2 hours",\n      "lat_long": "40.785091,-73.968285"\n    },\n    {\n      "place_name": "Metropolitan Museum of Art",\n      "description": "One of the world\'s largest and finest art museums. Best time to visit: Afternoon",\n      "TOE": "2.5 hours",\n      "lat_long": "40.779437,-73.963244"\n    },\n    {\n      "place_name": "Times Square",\n      "description": "A major commercial intersection and tourist destination. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.758896,-73.985130"\n    }\n  ],\n  "2": [\n    {\n      "place_name": "Brooklyn Bridge",\n      "description": "A hybrid cable-stayed/suspension bridge. Best time to visit: Morning",\n      "TOE": "1.5 hours",\n      "lat_long": "40.706086,-73.996864"\n    },\n    {\n      "place_name": "Statue of Liberty",\n      "description": "A colossal neoclassical sculpture on Liberty Island. Best time to visit: Afternoon",\n      "TOE": "3 hours",\n      "lat_long": "40.689247,-74.044502"\n    },\n    {\n      "place_name": "Times Square",\n      "description": "A major commercial intersection and tourist destination. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.758896,-73.985130"\n    }\n\n  ]\n}\n\nIn the above JSON we can see that the place_name "Time Square" is repeated in the day 2 as well even after the user visited that place in day 1.\nSo in such cases you\'ll need to suggest another place instead of it.\n\n### EXAMPLE CORRECT OUTPUT ###\n{\n  "1": [\n    {\n      "place_name": "Central Park",\n      "description": "A large public park in New York City. Best time to visit: Morning",\n      "TOE": "2 hours",\n      "lat_long": "40.785091,-73.968285"\n    },\n    {\n      "place_name": "Metropolitan Museum of Art",\n      "description": "One of the world\'s largest and finest art museums. Best time to visit: Afternoon",\n      "TOE": "2.5 hours",\n      "lat_long": "40.779437,-73.963244"\n    },\n    {\n      "place_name": "Times Square",\n      "description": "A major commercial intersection and tourist destination. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.758896,-73.985130"\n    }\n  ],\n  "2": [\n    {\n      "place_name": "Brooklyn Bridge",\n      "description": "A hybrid cable-stayed/suspension bridge. Best time to visit: Morning",\n      "TOE": "1.5 hours",\n      "lat_long": "40.706086,-73.996864"\n    },\n    {\n      "place_name": "Statue of Liberty",\n      "description": "A colossal neoclassical sculpture on Liberty Island. Best time to visit: Afternoon",\n      "TOE": "3 hours",\n      "lat_long": "40.689247,-74.044502"\n    },\n    {\n      "place_name": "Broadway Show",\n      "description": "A popular location for theater performances. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.759012,-73.984474"\n    }\n\n  ]\n}\n\n\n### IMPORTANT ###\n\nEnsure all places in the itinerary are unique.\nStructure each day with a morning, afternoon, and evening activity.\nInclude additional Exploration/Shopping activities if time permits, based on the TOE.',
            )

            chat_session = model.start_chat(history=[])

            concatenated_input = f"Stay Details: {stay_details}\nNumber of Days: {number_of_days}\nBudget: {budget}\nAdditional Preferences: {additional_preferences}"

            response = chat_session.send_message(concatenated_input)
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
        nearby_restaurants,
    ):
        UserTripInfo.objects.create(
            user_id=user_id,
            stay_details=stay_details,
            number_of_days=number_of_days,
            budget=budget,
            additional_preferences=additional_preferences,
            generated_plan=generated_plan,
            nearby_restaurants=nearby_restaurants,
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
                names_with_details = [
                    {
                        "name": result["name"],
                        "latitude": result["geometry"]["location"]["lat"],
                        "longitude": result["geometry"]["location"]["lng"],
                        "rating": result.get("rating", "N/A"),
                        "price_level": result.get("price_level", "N/A"),
                    }
                    for result in data["results"]
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
                "temperature": 1,
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
                system_instruction='Role: You are an intelligent travel planner.\n\nObjective: Integrate the best matching restaurants from a provided list of nearby options into an existing itinerary based on user preferences. You will receive two JSON objects: "nearby_restaurants" and "response_data". Always suggest unique restaurants only.\n\n### Input Details: ###\n\n1. nearby_restaurants: A JSON object containing lists of restaurants near each place the user is visiting. Each restaurant has a description, TOE (Time of Exploration), and latitude and longitude information.\n\n2. response_data: A JSON object representing the user\'s itinerary, where you will integrate the best matching restaurants.\n\n### Task: ###\n\n1. Select Restaurants:\nBy default, recommend the best-rated and cheapest restaurant.\nIntegrate the selected restaurants into the appropriate places in the "response_data".\n\n\nOutput: Provide only the updated "response_data" JSON. Ensure that the JSON is correctly structured without any bad escaped characters.\n\n### GENERAL STRUCTURE ###\n\n{\n  "response_data": {\n    "1": [\n      {\n        "place_name": <Place_one>,\n        "description": "val1",\n        "TOE": "val2",\n        "lat_long": "lat,long"\n      },\n      {\n        "restaurant_name": <Restaurant near to the Place_one>,\n        "description": "<A short description related to the restaurant>",\n        "TOE": "val2",\n        "lat_long": "lat,long"\n      },\n      {\n        "place_name": <Place_two>,\n        "description": "val1",\n        "TOE": "val2",\n        "lat_long": "lat,long"\n      },\n{\n        "place_name": <Place_three>,\n        "description": "val1",\n        "TOE": "val2",\n        "lat_long": "lat,long"\n      },\n{\n        "restaurant_name": <Restaurant near to the Place_three>,\n        "description": "<A short description related to the restaurant",\n        "TOE": "val2",\n        "lat_long": "lat,long"\n      },\n\n    ],\n    "day_2": [\n      ...\n    ]\n  }\n}\n\n\n### Guidelines: ###\n\n1. Ensure the selected restaurants are close to the places in the itinerary.\n2. Maintain the correct structure and format of the JSON.\n3. Avoid any bad escaped characters.\n\n### EXAMPLE INPUT ###\n\n{\n"nearby_restaurants": {\n"1": {\n"Gateway of India": [\n{\n"name": "Shamiana",\n"latitude": 18.9220554,\n"longitude": 72.8330387,\n"rating": 4.7,\n"price_level": 3\n},\n{\n"name": "Golden Dragon",\n"latitude": 18.9218167,\n"longitude": 72.8334331,\n"rating": 4.6,\n"price_level": 4\n},\n{\n"name": "Wasabi by Morimoto",\n"latitude": 18.9225215,\n"longitude": 72.83322919999999,\n"rating": 4.6,\n"price_level": 4\n},\n{\n"name": "Souk",\n"latitude": 18.9220554,\n"longitude": 72.8330387,\n"rating": 4.6,\n"price_level": 4\n},\n{\n"name": "Sea Lounge",\n"latitude": 18.921611,\n"longitude": 72.83330509999999,\n"rating": 4.5,\n"price_level": 4\n}\n],\n"Elephanta Caves": [],\n"Dhobi Ghat": [\n{\n"name": "Saikrupa Hotel",\n"latitude": 18.9618653,\n"longitude": 72.8350256,\n"rating": 5,\n"price_level": "N/A"\n},\n{\n"name": "ZAS Kitchen",\n"latitude": 18.95548879999999,\n"longitude": 72.83328929999999,\n"rating": 4.6,\n"price_level": "N/A"\n},\n{\n"name": "Bon Appetit",\n"latitude": 18.9545604,\n"longitude": 72.8332453,\n"rating": 4.5,\n"price_level": "N/A"\n},\n{\n"name": "Arrakis Cafe",\n"latitude": 18.9583136,\n"longitude": 72.83748969999999,\n"rating": 4.4,\n"price_level": 1\n},\n{\n"name": "Cafe Shaheen",\n"latitude": 18.9576754,\n"longitude": 72.83133800000002,\n"rating": 4.2,\n"price_level": "N/A"\n}\n]\n},\n"2": {\n"Chhatrapati Shivaji Maharaj Terminus": [\n{\n"name": "Super Taste",\n"latitude": 18.9533807,\n"longitude": 72.8348168,\n"rating": 5,\n"price_level": "N/A"\n},\n{\n"name": "Hotel Grant House",\n"latitude": 18.945688,\n"longitude": 72.8350631,\n"rating": 4.6,\n"price_level": 2\n},\n{\n"name": "Bon Appetit",\n"latitude": 18.9545604,\n"longitude": 72.8332453,\n"rating": 4.5,\n"price_level": "N/A"\n},\n{\n"name": "Royal China",\n"latitude": 18.9384896,\n"longitude": 72.8328156,\n"rating": 4.4,\n"price_level": 3\n},\n{\n"name": "Ustaadi",\n"latitude": 18.9456713,\n"longitude": 72.8341837,\n"rating": 4.3,\n"price_level": 3\n}\n],\n"Kanheri Caves": [\n{\n"name": "Famous Chinese",\n"latitude": 19.1353643,\n"longitude": 72.8995789,\n"rating": 5,\n"price_level": "N/A"\n},\n{\n"name": "Mumbai Vadapav - मुंबई वडापाव",\n"latitude": 19.1358904,\n"longitude": 72.90076499999999,\n"rating": 4.9,\n"price_level": "N/A"\n},\n{\n"name": "Anna\'s Kitchen",\n"latitude": 19.1351649,\n"longitude": 72.89989829999999,\n"rating": 4.8,\n"price_level": "N/A"\n},\n{\n"name": "chandshah wali garib nawaz hotel",\n"latitude": 19.1393675,\n"longitude": 72.9046766,\n"rating": 4.5,\n"price_level": 1\n},\n{\n"name": "Skky - Ramada",\n"latitude": 19.1358383,\n"longitude": 72.8985196,\n"rating": 4.3,\n"price_level": "N/A"\n}\n],\n"Marine Drive": [\n{\n"name": "All Seasons Banquets",\n"latitude": 18.938381,\n"longitude": 72.824679,\n"rating": 4.9,\n"price_level": "N/A"\n},\n{\n"name": "The Gourmet Restaurant",\n"latitude": 18.9389568,\n"longitude": 72.8287517,\n"rating": 4.7,\n"price_level": "N/A"\n},\n{\n"name": "Joss Chinoise Jaan Joss Banquets",\n"latitude": 18.93289,\n"longitude": 72.83127999999999,\n"rating": 4.7,\n"price_level": "N/A"\n},\n{\n"name": "Royal China",\n"latitude": 18.9384896,\n"longitude": 72.8328156,\n"rating": 4.4,\n"price_level": 3\n},\n{\n"name": "Castle Hotel",\n"latitude": 18.9447236,\n"longitude": 72.8289277,\n"rating": 4.3,\n"price_level": "N/A"\n}\n]\n},\n"3": {\n"Juhu Beach": [\n{\n"name": "Hakkasan Mumbai",\n"latitude": 19.0608636,\n"longitude": 72.834589,\n"rating": 4.7,\n"price_level": 4\n},\n{\n"name": "Bonobo",\n"latitude": 19.0655221,\n"longitude": 72.8340542,\n"rating": 4.3,\n"price_level": 3\n},\n{\n"name": "Candies",\n"latitude": 19.0610866,\n"longitude": 72.8266907,\n"rating": 4.3,\n"price_level": 2\n},\n{\n"name": "Escobar",\n"latitude": 19.0600351,\n"longitude": 72.8363962,\n"rating": 4.2,\n"price_level": 3\n},\n{\n"name": "Joseph’s Tandoori Kitchen",\n"latitude": 19.0617858,\n"longitude": 72.8303955,\n"rating": 4.2,\n"price_level": 2\n}\n],\n"Mani Bhavan": [\n{\n"name": "MAYUR HOSPITALITY",\n"latitude": 18.9552008,\n"longitude": 72.8281485,\n"rating": 4.8,\n"price_level": "N/A"\n},\n{\n"name": "Bon Appetit",\n"latitude": 18.9545604,\n"longitude": 72.8332453,\n"rating": 4.5,\n"price_level": "N/A"\n},\n{\n"name": "Haji Tikka - The Kabab Corner",\n"latitude": 18.9599894,\n"longitude": 72.8306206,\n"rating": 4.3,\n"price_level": 2\n},\n{\n"name": "Kings Shawarma",\n"latitude": 18.9617761,\n"longitude": 72.82895789999999,\n"rating": 4.3,\n"price_level": 2\n},\n{\n"name": "Cafe Shaheen",\n"latitude": 18.9576754,\n"longitude": 72.83133800000002,\n"rating": 4.2,\n"price_level": "N/A"\n}\n],\n"Siddhivinayak Temple": [\n{\n"name": "Food Corp",\n"latitude": 18.969915,\n"longitude": 72.82032509999999,\n"rating": 5,\n"price_level": "N/A"\n},\n{\n"name": "Food Box",\n"latitude": 18.9752524,\n"longitude": 72.82382179999999,\n"rating": 4.4,\n"price_level": "N/A"\n},\n{\n"name": "Natural Ice Cream",\n"latitude": 18.9677866,\n"longitude": 72.82051009999999,\n"rating": 4.4,\n"price_level": 2\n},\n{\n"name": "Sarvi Restaurant",\n"latitude": 18.9668207,\n"longitude": 72.8291165,\n"rating": 4.2,\n"price_level": 2\n},\n{\n"name": "Grills & Wok",\n"latitude": 18.9707473,\n"longitude": 72.8323569,\n"rating": 4.2,\n"price_level": 2\n}\n]\n}\n},\n"response_data": {\n"1": [\n{\n"place_name": "Gateway of India",\n"description": "The Gateway of India is an arch monument built in 1924. It is a popular tourist destination, especially during the evening.",\n"TOE": "1.5 hours",\n"lat_long": "18.9220, 72.8347"\n},\n{\n"place_name": "Elephanta Caves",\n"description": "The Elephanta Caves are a UNESCO World Heritage Site located on an island near Mumbai. The caves are dedicated to the Hindu god Shiva and are known for their intricate carvings. It is recommended to visit in the morning or afternoon.",\n"TOE": "2.5 hours",\n"lat_long": "18.9843, 72.8777"\n},\n{\n"place_name": "Dhobi Ghat",\n"description": "Dhobi Ghat is an open-air laundry in Mumbai. It is a unique and fascinating place to visit. It is recommended to visit in the morning or afternoon.",\n"TOE": "1 hour",\n"lat_long": "18.9583, 72.8343"\n}\n],\n"2": [\n{\n"place_name": "Chhatrapati Shivaji Maharaj Terminus",\n"description": "Chhatrapati Shivaji Maharaj Terminus is a UNESCO World Heritage Site located in Mumbai. It is a beautiful example of Victorian Gothic Revival architecture. It is recommended to visit in the morning or afternoon.",\n"TOE": "2 hours",\n"lat_long": "18.9491, 72.8335"\n},\n{\n"place_name": "Kanheri Caves",\n"description": "The Kanheri Caves are a group of ancient Buddhist cave temples located in the Sanjay Gandhi National Park. It is recommended to visit in the morning or afternoon.",\n"TOE": "3 hours",\n"lat_long": "19.1426, 72.9018"\n},\n{\n"place_name": "Marine Drive",\n"description": "Marine Drive is a beautiful promenade located along the coast of Mumbai. It is a popular spot for evening walks and strolls.",\n"TOE": "1 hour",\n"lat_long": "18.9392, 72.8247"\n}\n],\n"3": [\n{\n"place_name": "Juhu Beach",\n"description": "Juhu Beach is a popular beach in Mumbai. It is a great place to relax and enjoy the sunset. It is recommended to visit in the evening.",\n"TOE": "2 hours",\n"lat_long": "19.0646, 72.8379"\n},\n{\n"place_name": "Mani Bhavan",\n"description": "Mani Bhavan is a historic building in Mumbai that was once the home of Mahatma Gandhi. It is a popular destination for history buffs. It is recommended to visit in the morning or afternoon.",\n"TOE": "1.5 hours",\n"lat_long": "18.9582, 72.8291"\n},\n{\n"place_name": "Siddhivinayak Temple",\n"description": "Siddhivinayak Temple is a popular Hindu temple dedicated to Lord Ganesha. It is a popular destination for devotees and tourists alike. It is recommended to visit in the morning or afternoon.",\n"TOE": "1 hour",\n"lat_long": "18.9727, 72.8252"\n}\n]\n}\n}\n\n\n\n### EXAMPLE OUTPUT ###\n{\n    "1": [\n      {\n        "place_name": "Gateway of India",\n        "description": "The Gateway of India is an arch monument built in 1924. It is a popular tourist destination, especially during the evening.",\n        "TOE": "1.5 hours",\n        "lat_long": "18.9220, 72.8347"\n      },\n      {\n        "restaurant_name": "Shamiana",\n        "description": "A fine dining restaurant serving Indian, Asian, and Continental cuisines.",\n        "TOE": "1.5 hours",\n        "lat_long": "18.9220554, 72.8330387"\n      },\n      {\n        "place_name": "Elephanta Caves",\n        "description": "The Elephanta Caves are a UNESCO World Heritage Site located on an island near Mumbai. The caves are dedicated to the Hindu god Shiva and are known for their intricate carvings. It is recommended to visit in the morning or afternoon.",\n        "TOE": "2.5 hours",\n        "lat_long": "18.9843, 72.8777"\n      },\n      {\n        "place_name": "Dhobi Ghat",\n        "description": "Dhobi Ghat is an open-air laundry in Mumbai. It is a unique and fascinating place to visit. It is recommended to visit in the morning or afternoon.",\n        "TOE": "1 hour",\n        "lat_long": "18.9583, 72.8343"\n      },\n      {\n        "restaurant_name": "Arrakis Cafe",\n        "description": "A cafe offering a casual dining experience with a variety of options.",\n        "TOE": "1 hour",\n        "lat_long": "18.9583136, 72.83748969999999"\n      }\n    ],\n    "2": [\n      {\n        "place_name": "Chhatrapati Shivaji Maharaj Terminus",\n        "description": "Chhatrapati Shivaji Maharaj Terminus is a UNESCO World Heritage Site located in Mumbai. It is a beautiful example of Victorian Gothic Revival architecture. It is recommended to visit in the morning or afternoon.",\n        "TOE": "2 hours",\n        "lat_long": "18.9491, 72.8335"\n      },\n      {\n        "restaurant_name": "Super Taste",\n        "description": "A local restaurant known for its delicious and affordable food.",\n        "TOE": "2 hours",\n        "lat_long": "18.9533807, 72.8348168"\n      },\n      {\n        "place_name": "Kanheri Caves",\n        "description": "The Kanheri Caves are a group of ancient Buddhist cave temples located in the Sanjay Gandhi National Park. It is recommended to visit in the morning or afternoon.",\n        "TOE": "3 hours",\n        "lat_long": "19.1426, 72.9018"\n      },\n      {\n        "restaurant_name": "Famous Chinese",\n        "description": "A local restaurant serving authentic Chinese dishes.",\n        "TOE": "3 hours",\n        "lat_long": "19.1353643, 72.8995789"\n      },\n      {\n        "place_name": "Marine Drive",\n        "description": "Marine Drive is a beautiful promenade located along the coast of Mumbai. It is a popular spot for evening walks and strolls.",\n        "TOE": "1 hour",\n        "lat_long": "18.9392, 72.8247"\n      },\n      {\n        "restaurant_name": "All Seasons Banquets",\n        "description": "A banquet hall offering a wide selection of cuisines.",\n        "TOE": "1 hour",\n        "lat_long": "18.938381, 72.824679"\n      }\n    ],\n    "3": [\n      {\n        "place_name": "Juhu Beach",\n        "description": "Juhu Beach is a popular beach in Mumbai. It is a great place to relax and enjoy the sunset. It is recommended to visit in the evening.",\n        "TOE": "2 hours",\n        "lat_long": "19.0646, 72.8379"\n      },\n      {\n        "restaurant_name": "Hakkasan Mumbai",\n        "description": "A fine dining restaurant offering modern Cantonese cuisine.",\n        "TOE": "2 hours",\n        "lat_long": "19.0608636, 72.834589"\n      },\n      {\n        "place_name": "Mani Bhavan",\n        "description": "Mani Bhavan is a historic building in Mumbai that was once the home of Mahatma Gandhi. It is a popular destination for history buffs. It is recommended to visit in the morning or afternoon.",\n        "TOE": "1.5 hours",\n        "lat_long": "18.9582, 72.8291"\n      },\n      {\n        "restaurant_name": "MAYUR HOSPITALITY",\n        "description": "A restaurant offering a variety of cuisines and a casual dining experience.",\n        "TOE": "1.5 hours",\n        "lat_long": "18.9552008, 72.8281485"\n      },\n      {\n        "place_name": "Siddhivinayak Temple",\n        "description": "Siddhivinayak Temple is a popular Hindu temple dedicated to Lord Ganesha. It is a popular destination for devotees and tourists alike. It is recommended to visit in the morning or afternoon.",\n        "TOE": "1 hour",\n        "lat_long": "18.9727, 72.8252"\n      },\n      {\n        "restaurant_name": "Food Corp",\n        "description": "A restaurant known for its quick and affordable food.",\n        "TOE": "1 hour",\n        "lat_long": "18.969915, 72.82032509999999"\n      }\n    ]\n}',
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
                nearby_restaurants,
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

### General Structure of JSON output ###

{{
  "generated_plan":{{
        "day_number":[
          {{
          "place_name": <place_name_1>,
          "description":<place_description_1>
          "TOE": "2 hours",
          "lat_long": "13.0546, 80.2717"
          }}
        ],
  }},
   "changes": <summary_of_the_change_with_positive_message>
}}

### EXAMPLES ###
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

SAMPLE_OUTPUT 2:

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

""",
            )

            chat_session = model.start_chat(history=[])

            concatenated_input = f"Original Details: {original_plan}\nCurrent day: {current_day}\Changes/Problems the user is currently facing with the original plan: {user_changes}\n"

            response = chat_session.send_message(concatenated_input)
            response_data = response.text

            response = {
                "user_changes": user_changes,
                "current_day": current_day,
                "response_data": response_data,
            }

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


class AddFinanceLog(APIView):
    def post(self, request):
        serializer = FinanceLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateMessageView(APIView):
    def __init__(self):
        self.supabase = self.configure_supabase()

    def configure_supabase(self) -> Client:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        return create_client(url, key)

    def post(self, request):
        user_id = request.data.get("user_id")
        message = request.data.get("message")

        # Configure the genai API
        genai.configure(api_key=os.environ["GOOGLE_FINANCE_API_KEY"])

        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }

        # Generate SQL response
        intentclassifier = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction='You are an intent classifier, you need to classify and divide in the user\'s questions in two different parts. The user questions will contain the information regarding the information the user wants to extract from the SQL database and the chart or visual the user wants to see that data. You also need to classify whether the questions asked is a follow-up questions based on the chat history given below. If there is no visual_type specified leave the field as blank.\n\n\n### OUTPUT ###\nYour output should be a JSON containing two entities namely,\n{\n"information_needed": " ",\n"visual_type": " "\n}\n\n### For example ###\nUser: Show me the day wise breakdown of my spendings in line chart\nModel: \n{\n"information_needed": "Show me the day wise breakdown of my spendings"\n"visual_type": "line chart"\n}\n\nUser: Show me the day wise breakdown of my spendings.\nModel: \n{\n"information_needed": "Show me the day wise breakdown of my spendings"\n"visual_type": ""\n}\n',
        )

        
        response = intentclassifier.generate_content(message)
        # Check if the response text contains ```json```
        if "```json" in response.text:
            json_response = self.extract_json_data(response.text)
        else:
            json_response = response.text

        print("RESPONSE TEXT FROM INTENT CLASSIFIER", response.text)
        if json_response:
            print("Response text:", json_response)
            try:
                intent_response = json.loads(json_response)
            except json.JSONDecodeError as e:
                print("JSON decode error:", str(e))
                return Response(
                    {"error": "Failed to parse JSON response"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            print("Empty response text")
            return Response(
                {"error": "Empty response from intent classifier"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print("Response from intent_classifier", intent_response)
        information_needed = intent_response.get("information_needed")
        visual_type = intent_response.get("visual_type")
        # Generate visual response
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction="You are an intelligent data analyst. You have to extract the information from the user's question and identify if there is any mention of charts. Otherwise you need to use your knowledge of data visualization and recommend any of the below charts based on the user's scenario. The output should be the corresponding Id belonging to the chart. Your output should only be the ID and nothing else.\n\nList of charts:\n1. Area Chart = 1\n2. Bar Chart = 2\n5. Line Chart = 3\n9. Pie Charts = 4\n\nFor example:\nUser: I want to see the distribution of cost based on categories.\nModel: 3",
        )
        if visual_type == "":
            visual_response_type = model.generate_content(information_needed)
        else:
            visual_response_type = model.generate_content(visual_type)

        visual_response = visual_response_type.text

       
        sql_response = """ SELECT * FROM "frugalooAPI_financelog" WHERE user_id = 'da034663-9c37-4c0f-8f86-7f63c2ed9471'"""
        # Query Supabase with the SQL response
        query_result = self.execute_sql_query(sql_response)
        # Log the message and response asynchronously
        self.log_message_sync(user_id, message, sql_response)
        insights_model_generation_config = {
            "temperature": 0.6,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        insights_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=insights_model_generation_config,
            # safety_settings = Adjust safety settings
            # See https://ai.google.dev/gemini-api/docs/safety-settings
            system_instruction=(
                "You are a Finance Expert, you will be given the user's spending data in a particular trip you need to summarize the expenses by analyzing the trend in it and providing useful insights to the user. "
                "Try to be as concise as possible the insights should be short. Also keep the tone of your conversation as friendly and cool as possible. Also I want you to extract only the necessary data from the given Query_results and append it in the JSON. "
                'Give the output in a JSON response, in the below structure.\n\n{\n"insights": <Your insights>,\n"extracted_data": <Extract the necessary data>\n}'
            ),
        )

        finance_input_formulation = (
            "\Query_result"
            + str(query_result)
            + "\nUser questions: "
            + information_needed
        )

        insights_model_response = insights_model.generate_content(
            finance_input_formulation
        ).text

        # Clean the insights model response
        insights_model_response_cleaned = self.extract_json_data(
            insights_model_response
        )
        print("CLEANED INSIGHTS RESPONSE", insights_model_response_cleaned)

        # Parse the cleaned JSON response
        try:
            response_json = json.loads(insights_model_response_cleaned)
            insights = response_json.get("insights", "")
            extracted_data = response_json.get("extracted_data", "")
            print("EXTRACTED DATA", extracted_data)
            print("INSIGHTS", insights)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            insights = ""
            extracted_data = ""


        generation_config_model3 = {
            "temperature": 0.5,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }

        # Generate React Visual Component response
        model3 = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config_model3,
            system_instruction="You are a ReactJS Expert, you need to create a static component with proper labeling based on the data received from the JSON input and the user question given to you by the user.\nYour output should **ONLY** be the static react component. \n\n### DATA INFORMATION ###\n1. Categories are divided into three main types: Shopping, Restaurant and Others\n2. Amount contains the information regarding the spendings of the user.\n3. day contains the information regarding the day on which the user spent the amount in his entire trip.\n4. place contains the information regarding the place where the user spent the amount.\n\n\n\n\n### COMPONENT ID MAPPING ###\nList of charts:\n1. Area Chart = 1\n2. Bar Chart = 2\n3. Line Chart = 3\n4. Pie Charts = 4\n\n\nRemember you might need to dynamically change the below components based on the data used to.\n\n### AREA CHART REACT COMPONENT ###\nlabels: data.map((item) => `<Based on the input JSON>`),\n    datasets: [\n      {\n        label:  <Based on the input JSON>,\n        data: data.map((item) => item.<Based on the input JSON>),\n        fill: true,\n        backgroundColor: \"rgba(75, 192, 192, 0.2)\",\n        borderColor: \"rgba(75, 192, 192, 1)\",\n        tension: 0.1,\n      },\n    ],\n\n### BAR CHART REACT COMPONENT ###\nlabels: data.map((item) => `<Based on the input JSON>`),\n    datasets: [\n        {\n        label: `<Based on the input JSON>`,\n        data: data.map((item) => item.<Based on the input JSON>),\n        backgroundColor: 'rgba(75, 192, 192, 0.2)',\n        borderColor: 'rgba(75, 192, 192, 1)',\n        borderWidth: 1,\n        },\n    ],\n\n### LINE CHART REACT COMPONENT ###\n\n    labels: data.map((item) => `<Based on the input JSON>`),\n    datasets: [\n      {\n        label: <Based on the input JSON>,\n        data: data.map((item) => item.<Based on the input JSON>),\n        borderColor: \"rgba(75, 192, 192, 1)\",\n        backgroundColor: \"rgba(75, 192, 192, 0.2)\",\n        borderWidth: 1,\n        tension: 0.4,\n      },\n    ],\n\n\n### PIE CHART REACT COMPONENT ###\n\nlabels: data.map((item) => `<Based on the input JSON>`),\ndatasets: [\n    {\n    label: <Based on the input JSON>,\n    data: data.map((item) => item.<Based on the input JSON>),\n    backgroundColor: [\n        'rgba(255, 99, 132, 0.2)',\n        'rgba(54, 162, 235, 0.2)',\n        'rgba(255, 206, 86, 0.2)',\n        'rgba(75, 192, 192, 0.2)',\n        'rgba(153, 102, 255, 0.2)',\n        'rgba(255, 159, 64, 0.2)',\n    ],\n    borderColor: [\n        'rgba(255, 99, 132, 1)',\n        'rgba(54, 162, 235, 1)',\n        'rgba(255, 206, 86, 1)',\n        'rgba(75, 192, 192, 1)',\n        'rgba(153, 102, 255, 1)',\n        'rgba(255, 159, 64, 1)',\n    ],\n    borderWidth: 1,\n    },\n],\n\nYou will receive a JSON object in the below structure with the component ID.\n\n[{'id': 24, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 5000, 'place': 'Joss Chinoise Jaan Joss Banquets', 'category': 'Restaurant', 'day': 1}, {'id': 25, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 100, 'place': 'Chhatrapati Shivaji Maharaj Vastu Sangrahalaya', 'category': 'Others', 'day': 1}, {'id': 26, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 15000, 'place': 'Juhu Beach', 'category': 'Restaurant', 'day': 2}, {'id': 27, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 5000, 'place': 'Elephanta Caves', 'category': 'Shopping', 'day': 2}, {'id': 28, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 100, 'place': 'Sanjay Gandhi National Park', 'category': 'Restaurant', 'day': 3}, {'id': 29, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 1005, 'place': 'Midtown Restaurant Family Wine & Dine', 'category': 'Restaurant', 'day': 3}]\n\nComponent Id = 3\n\nYou need to identify the way the data is been named. And then generate the static react component with the appropriate labels and datasets mapping based on the component Id.\n\nFor the above JSON your static react component should be like:\n\nlabels: data.map((item) => `${item.category}`),\n    datasets: [\n      {\n        label: \"Category wise Spending\",\n        data: data.map((item) => item.amount),\n        borderColor: \"rgba(75, 192, 192, 1)\",\n        backgroundColor: \"rgba(75, 192, 192, 0.2)\",\n        borderWidth: 1,\n        tension: 0.4,\n      },\n    ],",
        )
        model3_input_formulation = (
            str(extracted_data)
            + "\nComponent Id: "
            + visual_response
            + "\nUser_question:"
            + information_needed
        )
        react_visual_response = model3.generate_content(model3_input_formulation)
        react_visual_raw = react_visual_response.text
        react_visual_component = self.extract_chart_data(react_visual_raw)

        

        # Respond with the results
        response_data = {
            "visual_response": visual_response,
            "sql_response": sql_response,
            "query_result": extracted_data,
            "react_component": react_visual_component,
            "insights": insights,
        }

        print(response_data)
        return Response(response_data, status=status.HTTP_200_OK)

    def extract_json_data(self, json_component_raw: str) -> str:
        pattern = r"```json\n(.*?)\n```"
        match = re.search(pattern, json_component_raw, re.DOTALL)

        if match:
            extracted_data = match.group(1)
            return extracted_data.strip()

        # If there's no match, return the raw string (assuming it might be a valid JSON)
        return json_component_raw.strip()

    def extract_chart_data(self, react_component_raw: str) -> str:
        # Updated regex pattern to capture the entire content between the backticks ```
        pattern = r"```jsx\n(.*?)\n```"
        match = re.search(pattern, react_component_raw, re.DOTALL)

        if match:
            extracted_data = match.group(1)
            return extracted_data.strip()

        return ""

    def extract_sql_query(self, response_text: str) -> str:
        """Extracts the SQL query from the response text."""
        match = re.search(r"```sql\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def execute_sql_query(self, sql_query: str):
        """Executes the SQL query using Supabase and returns the result."""
        try:
            # Use Supabase client to run the query through the execute_sql function
            result = self.supabase.rpc("execute_sql", {"query": sql_query}).execute()
            if result.data:
                return result.data
            else:
                return {"error": result.error_message}
        except RecursionError as e:
            return {
                "error": "A recursion error occurred. Please check the input and try again."
            }
        except Exception as e:
            return {"error": str(e)}

    def log_message_sync(self, user_id, question, response_text):
        MessageLog.objects.create(
            user_id=user_id, question=question, sql_query=response_text
        )
        print("Successfully inserted the logs in the MessageLog Database")
