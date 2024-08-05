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
    """
    API view for generating an itinerary based on user information.

    This view handles the POST request and generates an itinerary based on the provided user information.
    The itinerary includes a minimum of three mandatory activities per day, with all activities located near each other
    and with a travel time of less than 2 hours. Additionally, an optional exploration/shopping activity may be recommended
    if the user's day has sufficient bandwidth. The itinerary ensures that the user visits unique places each day without
    repeating any places throughout the itinerary. If the number of days is more than the number of unique places, additional
    activities and adventures are recommended without repeating places. The itinerary is structured with a morning activity,
    followed by an afternoon activity, and ending with an evening activity.

    User input format:
    - stay_details
    - number_of_days
    - budget
    - additional_preferences

    """

    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            stay_details = request.data.get("stay_details")
            number_of_days = request.data.get("number_of_days")
            budget = request.data.get("budget")
            additional_preferences = request.data.get("additional_preferences")
            places_api_key = os.environ.get("GOOGLE_PLACES")
            places_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={stay_details}&key={places_api_key}&type=tourist_attraction"
            places_response = requests.get(places_url)
            places_data = places_response.json()

            tourist_attractions = []
            for result in places_data.get("results", []):
                place_name = result.get("name")
                location = result.get("geometry", {}).get("location", {})
                lat = location.get("lat")
                lng = location.get("lng")

                if place_name and lat and lng:
                    tourist_attractions.append(
                        {"name": place_name, "latitude": lat, "longitude": lng}
                    )

            print("Tourist attractions", tourist_attractions)
            api_key = os.getenv("GOOGLE_PRE_PLAN_API_KEY")
            if not api_key:
                return Response(
                    {"error": "API key is missing"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            genai.configure(api_key=api_key)

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
                system_instruction='### TASK DESCRIPTION ###\nGenerate an itinerary based on the provided user information. Each day in the itinerary should contain a minimum of three mandatory activities and all the activities should be near each other with the travelling time less than 2 hours. In addition to the mandatory activities, you may recommend an Exploration/Shopping activity if the user\'s day has sufficient bandwidth. This estimation can be made based on the "Time of Exploration" (TOE) for the mandatory activities.\n\nEnsure that the user visits unique places each day, without repeating any places throughout the itinerary. If the number of days is more than the number of unique places, recommend some additional activities and adventures, but do not repeat places.\n\nThe itinerary should always start the day with a morning activity, followed by an afternoon activity, and end the day with an evening activity.\n\nAlways pickup from the tourist attraction array provided below, once all the locations are used then you can recommend places from your knowledge base.\n tourist_attractions \n\n\n \n\n### USER INPUT FORMAT ###\nThe user will provide the following input:\n\nstay_details\nnumber_of_days\nbudget\nadditional_preferences\n\n### OUTPUT FORMAT ###\nThe output should be a JSON structure formatted as follows:\n\n{\n  "1": [\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    }\n  ],\n  "2": [\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    }\n  ],\n  "3": [\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    },\n    {\n      "place_name": "Place name",\n      "description": "Short description regarding the place followed with the best time to visit",\n      "TOE": "Time of Exploration",\n      "lat_long": "latitude,longitude"\n    }\n  ]\n}\n\n\n### GUIDELINES ###\n\nUnique Places: Ensure all places in the itinerary are unique across all days.\nStructured Schedule: Each day starts with a morning activity, followed by an afternoon activity, and ends with an evening activity.\nExploration/Shopping Activity: Include an additional Exploration/Shopping activity if time permits, based on the TOE of mandatory activities.\nJSON Structure: Ensure the JSON output is correctly structured with no repeated places.\n\n### EXAMPLE OUTPUT CONTAINING DUPLICATE ###\n{\n  "1": [\n    {\n      "place_name": "Central Park",\n      "description": "A large public park in New York City. Best time to visit: Morning",\n      "TOE": "2 hours",\n      "lat_long": "40.785091,-73.968285"\n    },\n    {\n      "place_name": "Metropolitan Museum of Art",\n      "description": "One of the world\'s largest and finest art museums. Best time to visit: Afternoon",\n      "TOE": "2.5 hours",\n      "lat_long": "40.779437,-73.963244"\n    },\n    {\n      "place_name": "Times Square",\n      "description": "A major commercial intersection and tourist destination. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.758896,-73.985130"\n    }\n  ],\n  "2": [\n    {\n      "place_name": "Brooklyn Bridge",\n      "description": "A hybrid cable-stayed/suspension bridge. Best time to visit: Morning",\n      "TOE": "1.5 hours",\n      "lat_long": "40.706086,-73.996864"\n    },\n    {\n      "place_name": "Statue of Liberty",\n      "description": "A colossal neoclassical sculpture on Liberty Island. Best time to visit: Afternoon",\n      "TOE": "3 hours",\n      "lat_long": "40.689247,-74.044502"\n    },\n    {\n      "place_name": "Times Square",\n      "description": "A major commercial intersection and tourist destination. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.758896,-73.985130"\n    }\n\n  ]\n}\n\nIn the above JSON we can see that the place_name "Time Square" is repeated in the day 2 as well even after the user visited that place in day 1.\nSo in such cases you\'ll need to suggest another place instead of it.\n\n### EXAMPLE CORRECT OUTPUT ###\n{\n  "1": [\n    {\n      "place_name": "Central Park",\n      "description": "A large public park in New York City. Best time to visit: Morning",\n      "TOE": "2 hours",\n      "lat_long": "40.785091,-73.968285"\n    },\n    {\n      "place_name": "Metropolitan Museum of Art",\n      "description": "One of the world\'s largest and finest art museums. Best time to visit: Afternoon",\n      "TOE": "2.5 hours",\n      "lat_long": "40.779437,-73.963244"\n    },\n    {\n      "place_name": "Times Square",\n      "description": "A major commercial intersection and tourist destination. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.758896,-73.985130"\n    }\n  ],\n  "2": [\n    {\n      "place_name": "Brooklyn Bridge",\n      "description": "A hybrid cable-stayed/suspension bridge. Best time to visit: Morning",\n      "TOE": "1.5 hours",\n      "lat_long": "40.706086,-73.996864"\n    },\n    {\n      "place_name": "Statue of Liberty",\n      "description": "A colossal neoclassical sculpture on Liberty Island. Best time to visit: Afternoon",\n      "TOE": "3 hours",\n      "lat_long": "40.689247,-74.044502"\n    },\n    {\n      "place_name": "Broadway Show",\n      "description": "A popular location for theater performances. Best time to visit: Evening",\n      "TOE": "2 hours",\n      "lat_long": "40.759012,-73.984474"\n    }\n\n  ]\n}\n\n\n### IMPORTANT ###\n\nEnsure all places in the itinerary are unique.\nStructure each day with a morning, afternoon, and evening activity.\nInclude additional Exploration/Shopping activities if time permits, based on the TOE.',
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
    """
    API view for generating an itinerary based on user information.

    This view handles the POST request and generates an itinerary based on the provided user information.
    The itinerary includes details such as nearby restaurants, ensuring a comprehensive plan for the user's trip.

    """

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
        """
        Inserts trip details into the UserTripInfo model.

        Parameters:
        - user_id: ID of the user
        - stay_details: Details about the user's stay
        - number_of_days: Number of days for the trip
        - budget: Budget for the trip
        - additional_preferences: Any additional preferences for the trip
        - generated_plan: The generated plan for the trip
        - nearby_restaurants: Details of nearby restaurants for each place
        """
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
        """
        Extracts latitude and longitude values from the provided data.

        Parameters:
        - data: Dictionary containing trip details with places and their lat/long

        Returns:
        - List of dictionaries containing day index, place name, and lat/long
        """
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

    def fetch_nearby_restaurants(self, lat_long_values, budget):
        """
        Fetches nearby restaurants for given latitude and longitude values.

        Parameters:
        - lat_long_values: List of dictionaries containing lat/long values for each place
        - budget: Budget type for filtering restaurants (1: frugal, 2: moderate, 3: expensive)

        Returns:
        - Dictionary containing restaurant details for each place
        """
        api_key = os.environ.get("GOOGLE_PLACES")
        radius = 1500
        results = {}

        # The updated budget mapping for filtering restaurants
        budget_mapping = {
            1: {0, 1},  # Frugal: price_level 0 or 1
            2: {2, 3},  # Moderate: price_level 2 or 3
            3: {4},  # Expensive: price_level 4
        }

        for place in lat_long_values:
            day_index = place["day_index"]
            place_name = place["place_name"]
            lat_long = place["lat_long"]
            lat, lng = lat_long.split(",")
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=restaurant&key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()  # Parse response content as JSON

                # Filter restaurants based on the budget
                names_with_details = [
                    {
                        "name": result["name"],
                        "latitude": result["geometry"]["location"]["lat"],
                        "longitude": result["geometry"]["location"]["lng"],
                        "rating": result.get("rating", "N/A"),
                        "price_level": result.get("price_level", "N/A"),
                    }
                    for result in data["results"]
                    if "price_level" in result
                    and result["price_level"] in budget_mapping[budget]
                ]

                # If no restaurants found in the preferred budget range, fetch restaurants with price_level N/A
                if not names_with_details:
                    names_with_details = [
                        {
                            "name": result["name"],
                            "latitude": result["geometry"]["location"]["lat"],
                            "longitude": result["geometry"]["location"]["lng"],
                            "rating": result.get("rating", "N/A"),
                            "price_level": result.get("price_level", "N/A"),
                        }
                        for result in data["results"]
                        if result.get("price_level") is None
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
            budget = request.data.get("budget")
            additional_preferences = request.data.get("additional_preferences")
            response_raw = request.data.get("response_data")

            response_raw_dict = json.loads(response_raw)
            lat_long_values = self.extract_lat_long(response_raw_dict)
            nearby_restaurants = self.fetch_nearby_restaurants(lat_long_values, budget)

            response_raw = {
                "nearby_restaurants": nearby_restaurants,
                "response_data": response_raw_dict,
            }

            genai.configure(api_key=os.environ["GOOGLE_GENERATE_PLAN_API_KEY"])
            generation_config = {
                "temperature": 0.5,
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
    """
    API view to fetch all trip details for a user.

    Handles the POST request to fetch all trip details for a given user.

    Parameters:
    - user_id: ID of the user

    Returns:
    - Response: Serialized trip details as JSON or an error message

    """

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



class GetPhotosForLocations(APIView):
    def post(self, request):
        try:
            locations = request.data.get('locations', [])
            photo_map = {}

            if not locations:
                return Response({'error': 'No locations provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch photos for each location
            for location in locations:
                location_name = location.get('stay_details')
                if location_name:
                    photo_reference = self.get_photo_reference(location_name)
                    if photo_reference:
                        photo_map[location_name] = photo_reference

            return Response(photo_map)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_photo_reference(self, location_name):
        url = 'https://places.googleapis.com/v1/places:searchText'
        headers = {
            'X-Goog-Api-Key': os.environ.get("GOOGLE_PLACES"),
            'X-Goog-FieldMask': 'places.displayName,places.photos',
        }
        body = {
            'textQuery': location_name,
            'pageSize': 1
        }

        response = requests.post(url, headers=headers, json=body)
        response_data = response.json()

        if response_data.get('places'):
            photos = response_data['places'][0].get('photos', [])
            if photos:
                photo_reference = photos[0]['name'].split('/photos/')[1]
                return photo_reference

        return None



class FetchPlan(APIView):
    """
    API view to fetch the generated plan for a specific trip.

    Handles the POST request to fetch the generated plan for a given trip.

    Parameters:
    - trip_id: ID of the trip

    Returns:
    - Response: Serialized generated plan as JSON or an error message
    """

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
    """
    API view to update the progress of a user's trip.

    Handles the POST request to update the progress of a user's trip.

    Parameters:
    - trip_id: ID of the trip
    - user_id: ID of the user
    - day: Day of the trip being updated

    Returns:
    - Response: Confirmation of the update or an error message
    """

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


class UpdateUserTripProgress(APIView):
    """
    API view to update the progress of a user's trip.
    Handles the POST request to update the progress of a user's trip.

    Parameters:
    - trip_id: ID of the trip
    - user_id: ID of the user
    - day: Day of the trip being updated

    Returns:
    - Response: Confirmation of the update or an error message
    """

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
    """
    API view to fetch the progress of a user's trip.
    Handles the POST request to fetch the progress of a user's trip.

    Parameters:
    - trip_id: ID of the trip

    Returns:
    - Response: Serialized trip progress as JSON or an error message
    """

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
    """
    API view to generate suggestions using Gemini based on user input.

    Handles the POST request to generate itinerary suggestions using Gemini AI.

    Parameters:
    - trip_id: ID of the trip
    - current_day: Current day of the trip
    - original_plan: Original itinerary plan
    - user_changes: User's changes or issues with the original plan

    Returns:
    - Response: AI-generated suggestions for the itinerary or an error message

    """

    def extract_lat_long(self, data):
        """
        Extracts latitude and longitude values from the provided data.

        Parameters:
        - data: List of lists containing trip details with places and their lat/long

        Returns:
        - List of dictionaries containing day index, place name, and lat/long
        """
        lat_long_values = []

        for day_index, day in enumerate(data):
            for place in day:
                # Check if the place is a location with a "place_name" and not a restaurant
                if "place_name" in place:
                    lat_long_values.append(
                        {
                            "day_index": day_index,
                            "place_name": place["place_name"],
                            "lat_long": place["lat_long"],
                        }
                    )
        return lat_long_values

    def fetch_nearby_preferences(self, lat_long_values, preferences):
        preferences = preferences.strip()

        api_key = os.environ.get("GOOGLE_PLACES")
        radius = 1500
        results = {}

        for place in lat_long_values:
            day_index = place["day_index"]
            place_name = place["place_name"]
            lat_long = place["lat_long"]
            lat, lng = lat_long.split(",")

            url = "https://places.googleapis.com/v1/places:searchNearby"
            headers = {
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.types,places.websiteUri,places.priceLevel,places.location",
            }
            payload = {
                "includedTypes": [
                    preferences
                ],  # Ensure preferences is correctly passed
                "maxResultCount": 20,
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": float(lat), "longitude": float(lng)},
                        "radius": radius,
                    }
                },
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()  # Parse response content as JSON
                places = data.get("places", [])
                place_details = [
                    {
                        "display_name": place["displayName"]["text"],
                        "formatted_address": place["formattedAddress"],
                        "types": place["types"],
                        "latitude": place["location"]["latitude"],
                        "longitude": place["location"]["longitude"],
                        "website_uri": place.get("websiteUri", "N/A"),
                        "price_index": place.get("priceLevel", "N/A"),
                    }
                    for place in places
                ]
                if day_index not in results:
                    results[day_index] = {}
                results[day_index][place_name] = place_details
            else:
                print(f"Error: {response.status_code}, {response.text}")

        return results

    def post(self, request):
        try:
            genai.configure(api_key=os.environ["GOOGLE_SUGGESTION_API_KEY"])
            trip_id = request.data.get("trip_id")
            current_day = request.data.get("current_day")
            original_plan = request.data.get("original_plan")
            user_changes = request.data.get("user_changes")
            budget = request.data.get("budget")
            # Budget mapping
            if budget == 1:
                user_budget = "Places with price_index: PRICE_LEVEL_FREE or PRICE_LEVEL_INEXPENSIVE is recommended."
            elif budget == 2:
                user_budget = "Places with price_index: PRICE_LEVEL_MODERATE or PRICE_LEVEL_EXPENSIVE is recommended."
            else:
                user_budget = "Places with price_index: PRICE_LEVEL_VERY_EXPENSIVE is recommended."

            print("User budget preference", user_budget)
            # Phase 1: Calling the intent classifier to extract the places_types based on user's query.
            generation_config_places_type_extractor = {
                "temperature": 0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            places_type_extractor = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config_places_type_extractor,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                system_instruction="You are an intelligent intent extractor. You will receive a change request from user. You have to extract the intent in the user's query and output the types mentioned below which are based on it. Basically your job is to output the type which belongs to the user's query so that that particular place could be fetched from the google maps places API.\n\nPLACES API TYPES\nchurch\nhindu_temple\nmosque\nsynagogue\nart_gallery\nmuseum\nshopping_mall\nperforming_arts_theater\namusement_center\namusement_park\nstadium\nlibrary\naquarium\nbanquet_hall\nbowling_alley\ncasino\ncommunity_center\nconvention_center\ncultural_center\ndog_park\nevent_venue\nhiking_area\nhistorical_landmark\nmarina\nmovie_rental\nmovie_theater\nnational_park\nnight_club\npark\ntourist_attraction\nvisitor_center\nwedding_venue\nzoo\namerican_restaurant\nbakery\nbar\nbarbecue_restaurant\nbrazilian_restaurant\nbreakfast_restaurant\nbrunch_restaurant\ncafe\nchinese_restaurant\ncoffee_shop\nfast_food_restaurant\nfrench_restaurant\ngreek_restaurant\nhamburger_restaurant\nice_cream_shop\nindian_restaurant\nindonesian_restaurant\nitalian_restaurant\njapanese_restaurant\nkorean_restaurant\tlebanese_restaurant\nmeal_delivery\nmeal_takeaway\nmediterranean_restaurant\nmexican_restaurant\nmiddle_eastern_restaurant\npizza_restaurant\nramen_restaurant\nrestaurant\nsandwich_shop\nseafood_restaurant\nspanish_restaurant\nsteak_house\nsushi_restaurant\nthai_restaurant\nturkish_restaurant\nvegan_restaurant\nvegetarian_restaurant\nvietnamese_restaurant\n\n\n### EXAMPLES ###\nUser: Can you add any indian resto in the trip?\nModel: italian_restaurant\n\nUser: Can you add cafe and bars to the trip?\nModel: cafe, bar\n\nUser: I want to eat some desserts could you please add in a place for eating desserts in the itinerary?\nModel: bakery\n",
            )

            places_type_extractor_response = places_type_extractor.generate_content(
                user_changes
            )
            places_types = places_type_extractor_response.text
            trip_info = get_object_or_404(UserTripInfo, trip_id=trip_id)
            serializer = UserTripInfoSerializer(trip_info)
            lat_long_values = self.extract_lat_long(original_plan)
            nearby_places = self.fetch_nearby_preferences(lat_long_values, places_types)
            print("Fetched nearby places", nearby_places)

            generation_config = {
                "temperature": 0.5,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }

            model_2 = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                system_instruction=f"""You are a travel agent, you plan itineraries for users. You need to give an alternate plan for the user's trip based on their current progress and problems. You will provide output in the below mentioned JSON format. You also know how to accurately open and close the brackets to form the JSON content without any issues.
You will be given the below input:
original_plan: It would be a JSON structure which represents the user's original plan.
current_day: It represents the current day the user is in. It will give you an idea of the user's trip progress.
user_changes: It represents the changes the user wants to make in the itinerary or the suggestions they want from you.
You need to edit the original_plan and share it as the output and also let the user know the changes/additions you made.
You might need to reorder the places in a particular day based on the Best time to visit it. It should always be in the following order:
Morning activity -> Afternoon activity -> Evening activity -> Night activity.
Always reorder the places so that the nearby places are below each other. For example, if Crescent Mall is near Qutub Minar then it should come below Qutub Minar in the generated JSON.
Only share the original_plan with the updated data and the summary of the changes with friendly text in minimum 20 words. Your changes should be added at last of the JSON as shown in the below sample output.
Always generate new suggestions different from the already present locations.
Unless the user explicitly mentions any new budget preferences always try to recommend places that lies in the user's budget: {user_budget}. 
When a user requests modifications to an existing itinerary, utilize the provided nearby_places JSON to suggest alternative locations. Prioritize selecting places from within the nearby_places data.\n

Adhere to the following itinerary structure:\n

Each place should be immediately followed by a restaurant.\n
Maintain the original order of places unless explicitly specified by the user.\n
Example:\n\n

Original itinerary: Place A, Restaurant X, Place B, Restaurant Y\n
User request: Replace Place A with something nearby\n
Possible new itinerary: Place C (from nearby_places), Restaurant Z (new suggestion), Place B, Restaurant Y\n

Always pickup places near to the above place.\n
Always keep the field names/key names should the same i.e. place_name, description, TOE, lat_long and changes.\n
Always give some description based on the place you selected.\n
Always describe the changes made by you in the original plan in 20-30 words minimum.\n
Always make sure all the key and values in the JSON structure are enclosed in double quotes ("").\n

{nearby_places}

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

Always remember to open and close the curly brackets accurately, the JSON should be a valid one. Always make sure that the common mistakes are not happening while constructing the output JSON.
### COMMON MISTAKES

### Common mistake 1
Error fetching the original plan SyntaxError: Expected double-quoted property name in JSON at position 1112 (line 1 column 1113)
    at JSON.parse (<anonymous>)

### Common mistake 2
{{"generated_plan": {{"0": [{{"place_name": "Red Fort", "description": "A historic fort complex, a UNESCO World Heritage site. Best time to visit: Morning ", "TOE": "3 hours", "lat_long": "28.6562, 77.2410"}}, {{"place_name": "Chandani Chawk", "description": "Chandani Chawk is a bustling and historic market area. It's a great place to experience the local culture and shop for a variety of items.", "TOE": "2 hours", "lat_long": "28.656181399999998, 77.23070729999999"}}, {{"place_name": "Al-Haj Bakery", "description": "It's a bakery in Chandni Chowk serving delicious desserts at low prices.", "TOE": "1 hour", "lat_long": "28.6537943, 77.22621769999999"}}, {{"place_name": "Humayun's Tomb", "description": 'A magnificent Mughal-era mausoleum. Best time to visit: Afternoon', "TOE": "2 hours", "lat_long": "28.5931, 77.2506"}}, {{"place_name": "India Gate", "description": 'A war memorial and popular gathering spot. Best time to visit: Evening', "TOE": "1.5 hours", "lat_long": "28.6129, 77.2295"}}, {{"restaurant_name": "Cafe Lota", "description": "Cafe Lota is a charming cafe located within the National Crafts Museum. It's known for its delicious Indian cuisine, particularly its thalis, and its peaceful ambiance.", "TOE": "1.5 hours", "lat_long": "28.6134591, 77.2425038"}}, {{"restaurant_name": "Suvidha", "description": "A restaurant serving Indian and Chinese cuisines.", "TOE": "3 hours", "lat_long": "28.64423709999999, 77.2399054"}}], "1": [{{"place_name": "Qutub Minar", "description": 'A towering minaret, another UNESCO World Heritage site. Best time to visit: Morning', "TOE": "2 hours", "lat_long": "28.5244, 77.1855"}}, {{"place_name": "Crescent Mall", "description": "Crescent Mall is a shopping mall located in Lado Sarai, close to Qutub Minar. You can enjoy shopping for a variety of items here.", "TOE": "2 hours", "lat_long": "28.524841, 77.190518"}}, {{"place_name": "Gallery Pioneer", "description": 'A well-regarded art gallery in Delhi known for showcasing contemporary Indian art. Best time to visit: Afternoon', "TOE": "2 hours", "lat_long": "28.5238457, 77.19365479999999"}},{{"place_name": "Lotus Temple", "description": 'A modern architectural marvel in the shape of a lotus flower. Best time to visit: Afternoon', "TOE": "1.5 hours", "lat_long": "28.5535, 77.2588"}}, {{"place_name": "Dilli Haat", "description": 'A vibrant open-air market for handicrafts and food. Best time to visit: Evening', "TOE": "2.5 hours", "lat_long": "28.5722, 77.2206"}}, {{"restaurant_name": "Dramz Delhi", "description": "A high-end bar and restaurant offering modern Indian and international cuisines.", "TOE": "2 hours", "lat_long": "28.5243996, 77.1836545"}}, {{"restaurant_name": "Slice Of Italy", "description": "A restaurant serving Italian dishes.", "TOE": "2.5 hours", "lat_long": "28.581887, 77.227008"}}], "2": [{{"place_name": "Jama Masjid", "description": "One of India's largest mosques. Best time to visit: Morning", "TOE": "2 hours", "lat_long": "28.6507, 77.2334"}}, {{"place_name": "Chandni Chowk", "description": 'A bustling and historic market area. Best time to visit: Afternoon', "TOE": "3 hours", "lat_long": "28.6586, 77.2247"}}, {{"place_name": "Raj Ghat", "description": 'A memorial to Mahatma Gandhi. Best time to visit: Evening', "TOE": "1 hour", "lat_long": "28.6419, 77.2504"}}, {{"restaurant_name": "Jung Bahadur Kachori Wala", "description": "A street food stall known for its kachoris.", "TOE": "3 hours", "lat_long": "28.6556903, 77.2300195"}}, {{"restaurant_name": "Zaika Foods", "description": "A restaurant serving Indian cuisine.", "TOE": "1 hour", "lat_long": "28.6437281, 77.24029279999999"}}, {{"restaurant_name": "Suvidha", "description": "A restaurant serving Indian and Chinese cuisines.", "TOE": "2 hours", "lat_long": "28.64423709999999, 77.2399054"}}, {{"place_name": "Al-Haj Bakery", "description": "It's a bakery in Chandni Chowk serving delicious desserts at low prices.", "TOE": "1 hour", "lat_long": "28.6537943, 77.22621769999999"}}], "3": [{{"place_name": "Akshay Patra Temple", "description": 'A beautiful temple dedicated to Lord Krishna. Best time to visit: Morning', "TOE": "2 hours", "lat_long": "28.6139, 77.2090"}}, {{"place_name": "Garden of Five Senses", "description": 'A serene and picturesque garden. Best time to visit: Afternoon', "TOE": "2.5 hours", "lat_long": "28.5550, 77.1926"}}, {{"place_name": "Connaught Place", "description": 'A central shopping and dining district. Best time to visit: Evening', "TOE": "2 hours", "lat_long": "28.6333, 77.2167"}},{{"restaurant_name": "Mizo Diner", "description": "A restaurant serving Mizo cuisine.", "TOE": "2.5 hours", "lat_long": "28.5617682, 77.19256349999999"}},{{"restaurant_name": "Le Belvedere - Le Meridien", "description": "A fine dining restaurant offering European cuisine.", "TOE": "2 hours", "lat_long": "28.6187522, 77.2179598"}}, {{"restaurant_name": "The Imperial New Delhi", "description": "A historic hotel offering fine dining experiences.", "TOE": "2 hours", "lat_long": "28.62501779999999, 77.21822759999999"}}]}}, "changes": "I've added Al-Haj Bakery to your Day 3 itinerary after dinner as per your request. Enjoy some delicious desserts!"}}

In the above JSON you forgort to enclose the  'A magnificent Mughal-era mausoleum. Best time to visit: Afternoon' in double quotes. The correct JSON would be
"A magnificent Mughal-era mausoleum. Best time to visit: Afternoon"

""",


            )

            chat_session = model_2.start_chat(history=[])

            concatenated_input = f"Original Details: {original_plan}\nCurrent day: {current_day}\Changes/Problems the user is currently facing with the original plan: {user_changes}\n"

            response = chat_session.send_message(concatenated_input)
            response_data = response.text
            print("###################    OVERALL PLAN  ###################")
            print(response_data)
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
    """
    API view to update the trip plan with a new plan.
    Handles the POST request to update the trip plan.

    Parameters:
    - trip_id: ID of the trip
    - new_plan: New itinerary plan

    Returns:
    - Response: Confirmation of the update or an error message
    """

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
    """
    API view to add a financial log entry.

    Handles the POST request to add a financial log entry.

    Parameters:
    - user_id: ID of the user
    - trip_id: ID of the trip
    - amount: Amount of the financial entry
    - description: Description of the financial entry
    - trip_place: Place where the user visited
    Returns:
    - Response: Serialized financial log entry data or an error message
    """

    def post(self, request):
        data = request.data
        trip_id = data.get("trip_id")

        # Fetch stay_details from UserTripInfo
        try:
            trip_info = UserTripInfo.objects.get(trip_id=trip_id)
            stay_details = trip_info.stay_details
        except UserTripInfo.DoesNotExist:
            return Response(
                {"error": "Trip not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Add stay_details to trip_location in the finance log entry
        data["trip_location"] = stay_details

        serializer = FinanceLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateMessageView(APIView):
    """
    API view to handle message generation using Gemini AI and Supabase.

    Methods:
    - post: Handles the POST request to generate message content and return the response.
    """

    def __init__(self):
        self.supabase = self.configure_supabase()

    def configure_supabase(self) -> Client:
        """
        Configure and return a Supabase client instance using environment variables.
        """
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        return create_client(url, key)

    def post(self, request):
        user_id = request.data.get("user_id")
        message = request.data.get("message")
        chat_history = request.data.get("chat_history")
        chat_history = json.loads(chat_history)
        if (len(chat_history)) !=0:
          chat_history = chat_history["contents"]
        print("UserId", user_id)
        # Configure the genai API
        genai.configure(api_key=os.environ["GOOGLE_FINANCE_API_KEY"])

        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }

        # Generate AI response using Gemini
        intent_classifier = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction='You are an intent classifier, you need to classify and divide in the user\'s questions in two different parts. The user questions will contain the information regarding the information the user wants to extract from the SQL database and the chart or visual the user wants to see that data. You also need to classify whether the questions asked is a follow-up questions based on the chat history given below. If there is no visual_type specified leave the field as blank.\n\n\n### OUTPUT ###\nYour output should be a JSON containing two entities namely,\n{\n"information_needed": " ",\n"visual_type": " "\n}\n\n### For example ###\nUser: Show me the day wise breakdown of my spendings in line chart\nModel: \n{\n"information_needed": "Show me the day wise breakdown of my spendings"\n"visual_type": "line chart"\n}\n\nUser: Show me the day wise breakdown of my spendings.\nModel: \n{\n"information_needed": "Show me the day wise breakdown of my spendings"\n"visual_type": ""\n}\n',
        )
        intent_classifer_chat_session = intent_classifier.start_chat(
            history=chat_history
        )
        response = intent_classifer_chat_session.send_message(message)
        # Check if the response text contains ```json```
        if "```json" in response.text:
            json_response = self.extract_json_data(response.text)
        else:
            json_response = response.text

        if json_response:
            try:
                intent_response = json.loads(json_response)
            except json.JSONDecodeError as e:
                return Response(
                    {"error": "Failed to parse JSON response"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Empty response from intent classifier"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        information_needed = intent_response.get("information_needed")
        visual_type = intent_response.get("visual_type")

        # Generate visual response using Gemini
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction="You are an intelligent data analyst. You have to extract the information from the user's question and identify if there a need of creating a visual if needed you need to output the ID of the visual that would be best suited else just output 0. The output should be the corresponding Id belonging to the chart. Your output should only be the ID and nothing else.\n\n ###When will you create a visual?\n\n You will only create a visual if there is a comparison between more than 1 fields.\nList of charts:\n1. Area Chart = 1\n2. Bar Chart = 2\n5. Line Chart = 3\n9. Pie Charts = 4\n\nFor example:\nUser: I want to see the distribution of cost based on categories.\nModel: 3\n User: Where did I spent the most in Goa?\nModel:0\n User: Give me a detailed breakdown of my spendings in Goa\n Model: 1",
        )
        if visual_type == "":
            visual_response_type = model.generate_content(information_needed)
        else:
            visual_response_type = model.generate_content(visual_type)

        visual_response = visual_response_type.text
        # Placeholder SQL query (update as needed)
        sql_response = f"""SELECT trip_location,place,category,day,amount FROM "frugalooAPI_financelog" WHERE user_id = '{user_id}'
        """

        # Query Supabase with the SQL response
        query_result = self.execute_sql_query(sql_response)
        # Log the message and response asynchronously
        self.log_message_sync(user_id, message, sql_response)

        # Generate insights using Gemini
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
                f"""
                You are a Finance Expert, you will be given the user's spending data in a particular trip you need to summarize the expenses by analyzing the trend in it and providing useful insights to the user.\n
                Try to be as concise as possible the insights should be of ***20-30 words*** minimum. Also keep the tone of your conversation as friendly and cool as possible. Also I want you to extract only the necessary data from the given Query_results and append it in the JSON.\n
                You can also perform arithematic operations (addition, subtraction, multiplication and division) on the User's trip data and give a cleaner data based on the user's question.\n
                \n### User trip data:\n {query_result}\n\n\n
                Give the output in a JSON response, in the below structure.\n\n{{\n"insights": "<Your insights>",\n"extracted_data": "<Extract the necessary data>"\n}}
                ### Remember\n\n
                Remember to enclose the keys and values of the JSON with double quotes ("") so that the user will be able to parse it.\n\n
                ### Examples \n\n
                
                Wrong Format:\n
{{
"insights": "You spent a total of 19397 INR on your Goa trip. Looks like you enjoyed some good food and shopping there!",
"extracted_data": [
    {{'amount': 1500, 'place': 'Goan Classic Family Restaurant and Bar', 'category': 'Restaurant', 'day': 1, 'trip_location': 'Goa'}},
    {{'amount': 10000, 'place': 'Calangute Beach', 'category': 'Shopping', 'day': 1, 'trip_location': 'Goa'}},
    {{'amount': 1898, 'place': 'Arpora Saturday Night Market', 'category': 'Shopping', 'day': 1, 'trip_location': 'Goa'}},
    {{'amount': 5999, 'place': 'Success', 'category': 'Restaurant', 'day': 1, 'trip_location': 'Goa'}}
]
                }}\n

                Reason: The key and values are not enclosed in double quotes ("") instead they are enclosed in ('') which leads to an invalid JSON structure.\n

                Correct format:\n
                {{
    "insights": "You spent a total of 19397 INR on your Goa trip. Looks like you enjoyed some good food and shopping there!",
    "extracted_data": [
        {{"amount": 1500, "place": "Goan Classic Family Restaurant and Bar", "category": "Restaurant", "day": 1, "trip_location": "Goa"}},
        {{ "amount": 10000, "place": "Calangute Beach", "category": "Shopping", "day": 1, "trip_location": "Goa"}},
        {{ "amount": 1898, "place": "Arpora Saturday Night Market", "category": "Shopping", "day": 1, "trip_location": "Goa"}},
        {{"amount": 5999, "place": "Success", "category": "Restaurant", "day": 1, "trip_location": "Goa"}}
    ]
}}

               """
            ),
        )

        finance_input_formulation = (
            "\Query_result"
            + str(query_result)
            + "\nUser questions: "
            + information_needed
        )
        insights_model_session = insights_model.start_chat(history=chat_history)
        insights_model_response = insights_model_session.send_message(
            finance_input_formulation
        ).text

        # Clean the insights model response
        insights_model_response_cleaned = self.extract_json_data(
            insights_model_response
        )
        # Parse the cleaned JSON response
        try:
            response_json = json.loads(insights_model_response_cleaned)
            insights = response_json.get("insights", "")
            extracted_data = response_json.get("extracted_data", "")
        except json.JSONDecodeError as e:
            insights = ""
            extracted_data = ""
            print(e)
        react_visual_component = ""
        if visual_response.strip() != "0":

            # Generate React visual component response using Gemini
            generation_config_model3 = {
                "temperature": 0.5,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            }

            model3 = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config_model3,
                system_instruction="You are a ReactJS Expert, you need to create a static component with proper labeling based on the data received from the JSON input and the user question given to you by the user.\nYour output should **ONLY** be the static react component. \n\n### DATA INFORMATION ###\n1. Categories are divided into three main types: Shopping, Restaurant and Others\n2. Amount contains the information regarding the spendings of the user.\n3. day contains the information regarding the day on which the user spent the amount in his entire trip.\n4. place contains the information regarding the place where the user spent the amount.\n5. trip_location contains the information about different places the user went. \n\n\n\n### COMPONENT ID MAPPING ###\nList of charts:\n1. Area Chart = 1\n2. Bar Chart = 2\n3. Line Chart = 3\n4. Pie Charts = 4\n\n\nRemember you might need to dynamically change the below components based on the data used to.\n\n### AREA CHART REACT COMPONENT ###\nlabels: data.map((item) => truncateLabel(`<Based on the input JSON>`)),\n    datasets: [\n      {\n        label:  <Based on the input JSON>,\n        data: data.map((item) => item.<Based on the input JSON>),\n        fill: true,\n        backgroundColor: \"rgba(75, 192, 192, 0.2)\",\n        borderColor: \"rgba(75, 192, 192, 1)\",\n        tension: 0.1,\n      },\n    ],\n\n### BAR CHART REACT COMPONENT ###\nlabels: data.map((item) =>  truncateLabel(`<Based on the input JSON>`)),\n    datasets: [\n        {\n        label: `<Based on the input JSON>`,\n        data: data.map((item) => item.<Based on the input JSON>),\n        backgroundColor: 'rgba(75, 192, 192, 0.2)',\n        borderColor: 'rgba(75, 192, 192, 1)',\n        borderWidth: 1,\n        },\n    ],\n\n### LINE CHART REACT COMPONENT ###\n\n    labels: data.map((item) =>  truncateLabel(`<Based on the input JSON>`)),\n    datasets: [\n      {\n        label: <Based on the input JSON>,\n        data: data.map((item) => item.<Based on the input JSON>),\n        borderColor: \"rgba(75, 192, 192, 1)\",\n        backgroundColor: \"rgba(75, 192, 192, 0.2)\",\n        borderWidth: 1,\n        tension: 0.4,\n      },\n    ],\n\n\n### PIE CHART REACT COMPONENT ###\n\nlabels:  truncateLabel(`<Based on the input JSON>`)),\ndatasets: [\n    {\n    label: <Based on the input JSON>,\n    data: data.map((item) => item.<Based on the input JSON>),\n    backgroundColor: [\n        'rgba(255, 99, 132, 0.2)',\n        'rgba(54, 162, 235, 0.2)',\n        'rgba(255, 206, 86, 0.2)',\n        'rgba(75, 192, 192, 0.2)',\n        'rgba(153, 102, 255, 0.2)',\n        'rgba(255, 159, 64, 0.2)',\n    ],\n    borderColor: [\n        'rgba(255, 99, 132, 1)',\n        'rgba(54, 162, 235, 1)',\n        'rgba(255, 206, 86, 1)',\n        'rgba(75, 192, 192, 1)',\n        'rgba(153, 102, 255, 1)',\n        'rgba(255, 159, 64, 1)',\n    ],\n    borderWidth: 1,\n    },\n],\n\nYou will receive a JSON object in the below structure with the component ID.\n\n[{'id': 24, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 5000, 'place': 'Joss Chinoise Jaan Joss Banquets', 'category': 'Restaurant', 'day': 1}, {'id': 25, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 100, 'place': 'Chhatrapati Shivaji Maharaj Vastu Sangrahalaya', 'category': 'Others', 'day': 1}, {'id': 26, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 15000, 'place': 'Juhu Beach', 'category': 'Restaurant', 'day': 2}, {'id': 27, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 5000, 'place': 'Elephanta Caves', 'category': 'Shopping', 'day': 2}, {'id': 28, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 100, 'place': 'Sanjay Gandhi National Park', 'category': 'Restaurant', 'day': 3}, {'id': 29, 'user_id': 'da034663-9c37-4c0f-8f86-7f63c2ed9471', 'trip_id': '3243a3d8-2622-4115-8312-74ca252ec97f', 'amount': 1005, 'place': 'Midtown Restaurant Family Wine & Dine', 'category': 'Restaurant', 'day': 3}]\n\nComponent Id = 3\n\nYou need to identify the way the data is been named. And then generate the static react component with the appropriate labels and datasets mapping based on the component Id.\n\nFor the above JSON your static react component should be like:\n\nlabels: data.map((item) =>truncateLabel(`${item.category}`)),\n    datasets: [\n      {\n        label: \"Category wise Spending\",\n        data: data.map((item) => item.amount),\n        borderColor: \"rgba(75, 192, 192, 1)\",\n        backgroundColor: \"rgba(75, 192, 192, 0.2)\",\n        borderWidth: 1,\n        tension: 0.4,\n      },\n    ],",
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

        return Response(response_data, status=status.HTTP_200_OK)

    def extract_json_data(self, json_component_raw: str) -> str:
        """
        Extract JSON data from the raw response text.

        Args:
        - json_component_raw: Raw response text containing JSON data

        Returns:
        - str: Extracted JSON data as a string
        """
        pattern = r"```json\n(.*?)\n```"
        match = re.search(pattern, json_component_raw, re.DOTALL)

        if match:
            extracted_data = match.group(1)
            return extracted_data.strip()

        return json_component_raw.strip()

    def extract_chart_data(self, react_component_raw: str) -> str:
        """
        Extract chart data from the raw response text.

        Args:
        - react_component_raw: Raw response text containing chart data

        Returns:
        - str: Extracted chart data as a string
        """
        pattern = r"```jsx\n(.*?)\n```"
        match = re.search(pattern, react_component_raw, re.DOTALL)

        if match:
            extracted_data = match.group(1)
            return extracted_data.strip()

        return ""

    def extract_sql_query(self, response_text: str) -> str:
        """
        Extract SQL query from the response text.

        Args:
        - response_text: Raw response text containing SQL query

        Returns:
        - str: Extracted SQL query as a string
        """
        match = re.search(r"```sql\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def execute_sql_query(self, sql_query: str):
        """
        Execute SQL query using Supabase and return the result.

        Args:
        - sql_query: SQL query to be executed

        Returns:
        - dict: Query result or error message
        """
        try:
            # Execute the RPC function
            result = self.supabase.rpc("execute_sql", {"query": sql_query}).execute()

            # Print the result for debugging
            print("Supabase result:", result)

            # Check if result contains errors or data
            if hasattr(result, "error"):
                return {"error": result.error}

            if hasattr(result, "data") and result.data:
                return result.data
            else:
                # If there's no specific error, print out the result object
                print("Unexpected result structure:", result)
                return {
                    "error": "Query execution failed without a specific error message."
                }

        except RecursionError:
            return {
                "error": "A recursion error occurred. Please check the input and try again."
            }
        except Exception as e:
            return {"error": str(e)}

    def log_message_sync(self, user_id, question, response_text):
        """
        Log message and response asynchronously.

        Args:
        - user_id: ID of the user
        - question: User's question
        - response_text: AI-generated response text
        """
        MessageLog.objects.create(
            user_id=user_id, question=question, sql_query=response_text
        )
        print("Successfully inserted the logs in the MessageLog Database")
