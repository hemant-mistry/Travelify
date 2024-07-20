from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
import requests
from .models import UserTripInfo, UserTripProgressInfo
from .serializers import (
    UserTripInfoSerializer,
    GeneratedPlanSerializer,
    UserTripProgressSerializer,
)
import json


class SaveTripDetails(APIView):

    def insert_trip_details(
        self,
        user_id,
        stay_details,
        number_of_days,
        budget,
        additional_preferences,
        generated_plan,
    ):
        UserTripInfo.objects.create(
            user_id=user_id,
            stay_details=stay_details,
            number_of_days=number_of_days,
            budget=budget,
            additional_preferences=additional_preferences,
            generated_plan=generated_plan,
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
                system_instruction='Generate an itinerary based on the information received from the user. Each day in the itinerary should contain minimum 3 mandatory activities. In addition to that you can recommend Exploration/Shopping activity if the user\'s day have bandwidth. You can make that estimate from "Time of Exploration" for all the above three mandatory activities. \n\nTOE: It indicates the approx time for exploring that particular activity.\n\n\n<Mandatory List>\nBelow is the list of mandatory activities: \n###############################################\n1. Morning Activity\n2. Afternoon Activity\n3. Evening Activity\n###############################################\n<Mandatory List/>\n\n\n\n\n### INFORMATION ###\nThe user will provide you with the input in the below format:\n- stay_details\n- number_of_days\n- budget\n- additional_preferences\nThe output should be a JSON structure as shown below:\n\n\n<OUTPUT FORMAT INFORMATION>\n\n9:00 AM - 11:00 AM: Morning Activity\n11:00 AM - 12:30 PM: Exploration/Shopping\n1:30 PM - 4:00 PM: Afternoon Activity\n4:00 PM - 4:30 PM: Break\n4:30 PM - 5:30 PM: Additional Exploration\n7:00 PM - 9:00 PM: Evening Activity\n\nIn the "description" do mention to the user when it is recommeded to visit that location: Morning, Afternoon and Evening. The last activity should always be a night activity.\nMake sure the JSON is correctly structured there should not be any Bad escaped character \n\n\n\n<OUTPUT FORMAT INFORMATION/>\n\n<OUTPUT FORMAT>\n{  "1":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"},{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n  "2":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"},{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n  "3":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"},{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}, {"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n  "4":[{"place_name":"val1","description":"val2","TOE":"val3","lat_long":"val4"}],\n}\n<OUTPUT FORMAT/>\n\n',
            )

            chat_session = model.start_chat(history=[])

            concatenated_input = f"Stay Details: {stay_details}\nNumber of Days: {number_of_days}\nBudget: {budget}\nAdditional Preferences: {additional_preferences}"

            response = chat_session.send_message(concatenated_input)
            response_data = response.text
            response_data_dict = json.loads(response_data)
            print("Response_data_dict",response_data_dict)
            lat_long_values = self.extract_lat_long(response_data_dict)

            # Fetch nearby restaurants for each lat_long value
            nearby_restaurants = self.fetch_nearby_restaurants(lat_long_values)

            response_raw = {
                "nearby_restaurants": nearby_restaurants,
                "response_data": response_data_dict,
            }
            print("Response Raw", response_raw)
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
system_instruction="\n\nYou are an intelligent travel planner that merges the best matching restaurants near to the place the user is visiting. You'll receive two objects \"nearby_restaurants\" and \"response_data\" based on it you need to merge the best restaurants that matches the user preferences. All the nearest restaurants close to the place are clubbed together in a single object which is \"nearby_restaurants\". You need to pickup from that and then recreate the response_data including them with the description, TOE and lat_long. By default recommend the best rated and cheap restaurant. Only provide the response_data JSON as output. \n\nAlso add description, TOE and make up the lat_long from the respective restaurant's latitude, longitude. \nInstead of \"val1\" and \"val2\" you need to add description for that place and estimated time of exploration.\nMake sure the JSON is correctly structured there should not be any Bad escaped character \n\n\n<User Input>\n{\n    \"nearby_restaurants\": {\n        \"1\": {\n            \"Gateway of India\": [\n                {\n                    \"name\": \"Shamiana\",\n                    \"latitude\": 18.9220554,\n                    \"longitude\": 72.8330387,\n                    \"rating\": 4.7,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Golden Dragon\",\n                    \"latitude\": 18.9218167,\n                    \"longitude\": 72.8334331,\n                    \"rating\": 4.6,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Wasabi by Morimoto\",\n                    \"latitude\": 18.9225215,\n                    \"longitude\": 72.83322919999999,\n                    \"rating\": 4.6,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Souk\",\n                    \"latitude\": 18.9220554,\n                    \"longitude\": 72.8330387,\n                    \"rating\": 4.6,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Sea Lounge\",\n                    \"latitude\": 18.921611,\n                    \"longitude\": 72.83330509999999,\n                    \"rating\": 4.5,\n                    \"price_level\": 4\n                }\n            ],\n            \"Elephanta Caves\": [],\n            \"Dhobi Ghat\": [\n                {\n                    \"name\": \"Saikrupa Hotel\",\n                    \"latitude\": 18.9618653,\n                    \"longitude\": 72.8350256,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"ZAS Kitchen\",\n                    \"latitude\": 18.95548879999999,\n                    \"longitude\": 72.83328929999999,\n                    \"rating\": 4.6,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Bon Appetit\",\n                    \"latitude\": 18.9545604,\n                    \"longitude\": 72.8332453,\n                    \"rating\": 4.5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Arrakis Cafe\",\n                    \"latitude\": 18.9583136,\n                    \"longitude\": 72.83748969999999,\n                    \"rating\": 4.4,\n                    \"price_level\": 1\n                },\n                {\n                    \"name\": \"Cafe Shaheen\",\n                    \"latitude\": 18.9576754,\n                    \"longitude\": 72.83133800000002,\n                    \"rating\": 4.2,\n                    \"price_level\": \"N/A\"\n                }\n            ]\n        },\n        \"2\": {\n            \"Chhatrapati Shivaji Maharaj Terminus\": [\n                {\n                    \"name\": \"Super Taste\",\n                    \"latitude\": 18.9533807,\n                    \"longitude\": 72.8348168,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Hotel Grant House\",\n                    \"latitude\": 18.945688,\n                    \"longitude\": 72.8350631,\n                    \"rating\": 4.6,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Bon Appetit\",\n                    \"latitude\": 18.9545604,\n                    \"longitude\": 72.8332453,\n                    \"rating\": 4.5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Royal China\",\n                    \"latitude\": 18.9384896,\n                    \"longitude\": 72.8328156,\n                    \"rating\": 4.4,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Ustaadi\",\n                    \"latitude\": 18.9456713,\n                    \"longitude\": 72.8341837,\n                    \"rating\": 4.3,\n                    \"price_level\": 3\n                }\n            ],\n            \"Kanheri Caves\": [\n                {\n                    \"name\": \"Famous Chinese\",\n                    \"latitude\": 19.1353643,\n                    \"longitude\": 72.8995789,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Mumbai Vadapav - मुंबई वडापाव\",\n                    \"latitude\": 19.1358904,\n                    \"longitude\": 72.90076499999999,\n                    \"rating\": 4.9,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Anna's Kitchen\",\n                    \"latitude\": 19.1351649,\n                    \"longitude\": 72.89989829999999,\n                    \"rating\": 4.8,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"chandshah wali garib nawaz hotel\",\n                    \"latitude\": 19.1393675,\n                    \"longitude\": 72.9046766,\n                    \"rating\": 4.5,\n                    \"price_level\": 1\n                },\n                {\n                    \"name\": \"Skky - Ramada\",\n                    \"latitude\": 19.1358383,\n                    \"longitude\": 72.8985196,\n                    \"rating\": 4.3,\n                    \"price_level\": \"N/A\"\n                }\n            ],\n            \"Marine Drive\": [\n                {\n                    \"name\": \"All Seasons Banquets\",\n                    \"latitude\": 18.938381,\n                    \"longitude\": 72.824679,\n                    \"rating\": 4.9,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"The Gourmet Restaurant\",\n                    \"latitude\": 18.9389568,\n                    \"longitude\": 72.8287517,\n                    \"rating\": 4.7,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Joss Chinoise Jaan Joss Banquets\",\n                    \"latitude\": 18.93289,\n                    \"longitude\": 72.83127999999999,\n                    \"rating\": 4.7,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Royal China\",\n                    \"latitude\": 18.9384896,\n                    \"longitude\": 72.8328156,\n                    \"rating\": 4.4,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Castle Hotel\",\n                    \"latitude\": 18.9447236,\n                    \"longitude\": 72.8289277,\n                    \"rating\": 4.3,\n                    \"price_level\": \"N/A\"\n                }\n            ]\n        },\n        \"3\": {\n            \"Juhu Beach\": [\n                {\n                    \"name\": \"Hakkasan Mumbai\",\n                    \"latitude\": 19.0608636,\n                    \"longitude\": 72.834589,\n                    \"rating\": 4.7,\n                    \"price_level\": 4\n                },\n                {\n                    \"name\": \"Bonobo\",\n                    \"latitude\": 19.0655221,\n                    \"longitude\": 72.8340542,\n                    \"rating\": 4.3,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Candies\",\n                    \"latitude\": 19.0610866,\n                    \"longitude\": 72.8266907,\n                    \"rating\": 4.3,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Escobar\",\n                    \"latitude\": 19.0600351,\n                    \"longitude\": 72.8363962,\n                    \"rating\": 4.2,\n                    \"price_level\": 3\n                },\n                {\n                    \"name\": \"Joseph’s Tandoori Kitchen\",\n                    \"latitude\": 19.0617858,\n                    \"longitude\": 72.8303955,\n                    \"rating\": 4.2,\n                    \"price_level\": 2\n                }\n            ],\n            \"Mani Bhavan\": [\n                {\n                    \"name\": \"MAYUR HOSPITALITY\",\n                    \"latitude\": 18.9552008,\n                    \"longitude\": 72.8281485,\n                    \"rating\": 4.8,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Bon Appetit\",\n                    \"latitude\": 18.9545604,\n                    \"longitude\": 72.8332453,\n                    \"rating\": 4.5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Haji Tikka - The Kabab Corner\",\n                    \"latitude\": 18.9599894,\n                    \"longitude\": 72.8306206,\n                    \"rating\": 4.3,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Kings Shawarma\",\n                    \"latitude\": 18.9617761,\n                    \"longitude\": 72.82895789999999,\n                    \"rating\": 4.3,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Cafe Shaheen\",\n                    \"latitude\": 18.9576754,\n                    \"longitude\": 72.83133800000002,\n                    \"rating\": 4.2,\n                    \"price_level\": \"N/A\"\n                }\n            ],\n            \"Siddhivinayak Temple\": [\n                {\n                    \"name\": \"Food Corp\",\n                    \"latitude\": 18.969915,\n                    \"longitude\": 72.82032509999999,\n                    \"rating\": 5,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Food Box\",\n                    \"latitude\": 18.9752524,\n                    \"longitude\": 72.82382179999999,\n                    \"rating\": 4.4,\n                    \"price_level\": \"N/A\"\n                },\n                {\n                    \"name\": \"Natural Ice Cream\",\n                    \"latitude\": 18.9677866,\n                    \"longitude\": 72.82051009999999,\n                    \"rating\": 4.4,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Sarvi Restaurant\",\n                    \"latitude\": 18.9668207,\n                    \"longitude\": 72.8291165,\n                    \"rating\": 4.2,\n                    \"price_level\": 2\n                },\n                {\n                    \"name\": \"Grills & Wok\",\n                    \"latitude\": 18.9707473,\n                    \"longitude\": 72.8323569,\n                    \"rating\": 4.2,\n                    \"price_level\": 2\n                }\n            ]\n        }\n    },\n    \"response_data\": {\n        \"1\": [\n            {\n                \"place_name\": \"Gateway of India\",\n                \"description\": \"The Gateway of India is an arch monument built in 1924. It is a popular tourist destination, especially during the evening.\",\n                \"TOE\": \"1.5 hours\",\n                \"lat_long\": \"18.9220, 72.8347\"\n            },\n            {\n                \"place_name\": \"Elephanta Caves\",\n                \"description\": \"The Elephanta Caves are a UNESCO World Heritage Site located on an island near Mumbai. The caves are dedicated to the Hindu god Shiva and are known for their intricate carvings. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"2.5 hours\",\n                \"lat_long\": \"18.9843, 72.8777\"\n            },\n            {\n                \"place_name\": \"Dhobi Ghat\",\n                \"description\": \"Dhobi Ghat is an open-air laundry in Mumbai. It is a unique and fascinating place to visit. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9583, 72.8343\"\n            }\n        ],\n        \"2\": [\n            {\n                \"place_name\": \"Chhatrapati Shivaji Maharaj Terminus\",\n                \"description\": \"Chhatrapati Shivaji Maharaj Terminus is a UNESCO World Heritage Site located in Mumbai. It is a beautiful example of Victorian Gothic Revival architecture. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"18.9491, 72.8335\"\n            },\n            {\n                \"place_name\": \"Kanheri Caves\",\n                \"description\": \"The Kanheri Caves are a group of ancient Buddhist cave temples located in the Sanjay Gandhi National Park. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"3 hours\",\n                \"lat_long\": \"19.1426, 72.9018\"\n            },\n            {\n                \"place_name\": \"Marine Drive\",\n                \"description\": \"Marine Drive is a beautiful promenade located along the coast of Mumbai. It is a popular spot for evening walks and strolls.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9392, 72.8247\"\n            }\n        ],\n        \"3\": [\n            {\n                \"place_name\": \"Juhu Beach\",\n                \"description\": \"Juhu Beach is a popular beach in Mumbai. It is a great place to relax and enjoy the sunset. It is recommended to visit in the evening.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"19.0646, 72.8379\"\n            },\n            {\n                \"place_name\": \"Mani Bhavan\",\n                \"description\": \"Mani Bhavan is a historic building in Mumbai that was once the home of Mahatma Gandhi. It is a popular destination for history buffs. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"1.5 hours\",\n                \"lat_long\": \"18.9582, 72.8291\"\n            },\n            {\n                \"place_name\": \"Siddhivinayak Temple\",\n                \"description\": \"Siddhivinayak Temple is a popular Hindu temple dedicated to Lord Ganesha. It is a popular destination for devotees and tourists alike. It is recommended to visit in the morning or afternoon.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9727, 72.8252\"\n            }\n        ]\n    }\n}\n\n<User Input/>\n\n\nIn the output you just need to give the clubbed JSON with the nearby restaurants with respect to the place.\n<Example Output>\n {\n        \"1\": [\n            {\n                \"place_name\": \"Gateway of India\",\n                \"description\": \"The Gateway of India is an arch monument built in the early 20th century. It is a popular tourist destination and a must-visit for any visitor to Mumbai. It is best to visit the Gateway of India in the morning or evening to avoid the midday heat.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"18.9220, 72.8347\"\n            },\n            {\n                \"place_name\":\"New Apollo Restuarant\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9228566,72.8320693\"\n            },\n            {\n                \"place_name\":\"Shamiana\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9220554, 72.8330387\"\n            },\n            {\n                \"place_name\": \"Elephanta Caves\",\n                \"description\": \"The Elephanta Caves are a UNESCO World Heritage Site and are a must-visit for any visitor to Mumbai. The caves are located on an island in the harbor and are home to ancient Hindu sculptures. It is best to visit the Elephanta Caves in the morning or evening to avoid the midday heat.\",\n                \"TOE\": \"3 hours\",\n                \"lat_long\": \"18.9899, 72.8776\"\n            },\n\n            \n        \"2\": [\n            {\n                \"place_name\": \"Chhatrapati Shivaji Maharaj Terminus\",\n                \"description\": \"Chhatrapati Shivaji Maharaj Terminus is a UNESCO World Heritage Site and is a must-visit for any visitor to Mumbai. The station is a beautiful example of Victorian Gothic Revival architecture. It is best to visit the Chhatrapati Shivaji Maharaj Terminus in the morning or evening to avoid the midday heat.\",\n                \"TOE\": \"2 hours\",\n                \"lat_long\": \"18.9482, 72.8341\"\n            },\n            {\n                \"place_name\":\"Royal China\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9384896, 72.8328156\"\n            },\n            {\n                \"place_name\": \"Marine Drive\",\n                \"description\": \"Marine Drive is a scenic promenade that stretches along the Arabian Sea. It is a popular spot for evening walks and is a must-visit for any visitor to Mumbai. It is best to visit Marine Drive in the evening to enjoy the sunset.\",\n                \"TOE\": \"1 hour\",\n                \"lat_long\": \"18.9344, 72.8344\"\n            },\n            {\n                \"place_name\": \"Delhi Darbar\",\n                \"description\":\"val1\",\n                \"TOE\":\"val2\",\n                \"lat_long\":\"18.9238178, 72.8317462\"\n            }\n\n            \n        ],\n       \n        ]\n    }\n}\n<Example Output/>",
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

            current_day = request.data.get("current_day")
            original_plan = request.data.get("original_plan")
            user_changes = request.data.get("user_changes")

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
  system_instruction="You are a travel agent, you plan itinearies for user. You need to give alternate plan for user's trip based on their current progress and problems.\n\nYou will be given the below input:\noriginal_plan: It would be a JSON structure which represents the user's original plan.\n\ncurrent_day: It represents the current day the user is in. It will give you an idea of the user's trip progress.\nuser_changes: It represents the changes the user wants to make in the itinerary or the suggestions they want from you.\nYou need to edit the the original_plan and share it as the output and also let the user know the changes/additions you made.\n\nOnly share the original_plan with the updated data and the summary of the changes with friendly text. Your changes should be added at last of the JSON as shown in the below sample output.\n\n\nSAMPLE_OUTPUT 1:\n{\n\"generated_plan\":{\n \"1\": [\n    {\n      \"place_name\": \"Gateway of India\",\n      \"description\": \"The Gateway of India is an arch monument built in 1924. It is a popular tourist destination in Mumbai, India. It is located in the Colaba area of South Mumbai. The Gateway was built to commemorate the arrival of King George V and Queen Mary in India. It is a popular spot for taking pictures and enjoying the views of the Arabian Sea.\",\n      \"TOE\": \"2 hours\",\n      \"lat_long\": \"18.9220, 72.8347\"\n    },\n    {\n      \"place_name\": \"Shamiana\",\n      \"description\": \"Shamiana is a popular restaurant located near the Gateway of India. It is known for its Indian and Continental cuisine. It is a great place to enjoy a meal with a view of the Arabian Sea.\",\n      \"TOE\": \"1 hour\",\n      \"lat_long\": \"18.9220554, 72.8330387\"\n    },\n    {\n      \"place_name\": \"Elephanta Caves\",\n      \"description\": \"The Elephanta Caves are a UNESCO World Heritage Site located on an island in the harbor of Mumbai, India. The caves are known for their intricate rock-cut Hindu sculptures. The caves are dedicated to the Hindu god Shiva, and they date back to the 5th and 6th centuries AD.\",\n      \"TOE\": \"3 hours\",\n      \"lat_long\": \"18.9814, 72.8762\"\n    },\n    {\n      \"place_name\": \"Marine Drive\",\n      \"description\": \"Marine Drive is a scenic promenade located in South Mumbai, India. It is also known as the Queen's Necklace because of the string of lights that illuminate the road at night. It is a popular spot for taking walks, enjoying the views of the Arabian Sea, and watching the sunset.\",\n      \"TOE\": \"1 hour\",\n      \"lat_long\": \"18.9418, 72.8271\"\n    }\n  ],\n  \"2\": [\n    {\n      \"place_name\": \"Chhatrapati Shivaji Maharaj Terminus\",\n      \"description\": \"Chhatrapati Shivaji Maharaj Terminus is a UNESCO World Heritage Site located in Mumbai, India. The terminus is a beautiful example of Victorian Gothic Revival architecture. It is a major railway station in Mumbai, and it is a popular tourist destination.\",\n      \"TOE\": \"2 hours\",\n      \"lat_long\": \"18.9429, 72.8353\"\n    },\n    {\n      \"place_name\": \"The Gourmet Restaurant\",\n      \"description\": \"The Gourmet Restaurant is a popular restaurant located near Chhatrapati Shivaji Maharaj Terminus. It is known for its fine dining experience. It is a great place to enjoy a meal with a view of the city.\",\n      \"TOE\": \"1.5 hours\",\n      \"lat_long\": \"18.9389568, 72.8287517\"\n    },\n    {\n      \"place_name\": \"Kanheri Caves\",\n      \"description\": \"The Kanheri Caves are a group of Buddhist cave temples located in the Sanjay Gandhi National Park in Mumbai, India. The caves date back to the 1st century BC, and they are known for their intricate carvings and sculptures.\",\n      \"TOE\": \"2 hours\",\n      \"lat_long\": \"19.1839, 72.9080\"\n    },\n    {\n      \"place_name\": \"Juhu Beach\",\n      \"description\": \"Juhu Beach is a popular beach in Mumbai, India. It is a great place to relax, enjoy the beach, and watch the sunset.\",\n      \"TOE\": \"2 hours\",\n      \"lat_long\": \"19.0674, 72.8427\"\n    }\n  ],\n  \"3\": [\n    {\n      \"place_name\": \"Mani Bhavan\",\n      \"description\": \"Mani Bhavan is a historic building in Mumbai, India. It was the residence of Mahatma Gandhi during his time in Mumbai. The building is now a museum that showcases Gandhi's life and work.\",\n      \"TOE\": \"1 hour\",\n      \"lat_long\": \"18.9466, 72.8281\"\n    },\n    {\n      \"place_name\": \"All Seasons Banquets\",\n      \"description\": \"All Seasons Banquets is a popular restaurant located near Mani Bhavan. It is known for its banqueting services. It is a great place to host a special event.\",\n      \"TOE\": \"1.5 hours\",\n      \"lat_long\": \"18.938381, 72.824679\"\n    },\n    {\n      \"place_name\": \"National Gallery of Modern Art\",\n      \"description\": \"The National Gallery of Modern Art is a museum located in Mumbai, India. It houses a collection of modern and contemporary art from India and around the world. It is a great place to learn about Indian art and culture.\",\n      \"TOE\": \"2 hours\",\n      \"lat_long\": \"19.0087, 72.8403\"\n    },\n    {\n      \"place_name\": \"Juhu Beach\",\n      \"description\": \"Juhu Beach is a popular beach in Mumbai, India. It is a great place to relax, enjoy the beach, and watch the sunset.\",\n      \"TOE\": \"2 hours\",\n      \"lat_long\": \"19.0674, 72.8427\"\n    }\n  ],\n},\n \n  \"changes\": \"Removed Dhobi Ghat from Day 2 and added Juhu Beach in its place.\"\n}\n\n\nSAMPLE OUTPUT 2:\n{\n\"generated_plan\":{\n \"1\": [\n    {\"place_name\": \"Eiffel Tower\", \"description\": \"The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed in 1889 as the entrance arch to the 1889 World's Fair, it has become both a global icon of France and one of the most recognizable structures in the world. The tower is 330 meters (1,083 feet) tall and is the tallest structure in Paris. It has three levels for visitors, with restaurants on the first and second levels. The top level offers panoramic views of the city. It is recommended to visit in the morning or evening to avoid the crowds.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8584, 2.2945\"}, {\"place_name\": \"Hôtel San Régis\", \"description\": \"A luxury hotel with a Michelin-starred restaurant, located near the Eiffel Tower.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8665, 2.3085\"}, {\"place_name\": \"Le Cinq\", \"description\": \"A renowned French restaurant with a five-star rating, known for its elegant ambiance and exquisite cuisine.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8688, 2.3007\"}, {\"place_name\": \"Arc de Triomphe\", \"description\": \"The Arc de Triomphe de l'Étoile is one of the most famous monuments in Paris, France, standing at the western end of the Champs-Élysées at the center of Place Charles de Gaulles. It was commissioned by Napoleon in 1806 to commemorate the Grande Armée's victories.  It is recommended to visit in the afternoon.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8738, 2.2950\"}, {\"place_name\": \"Saint James Paris\", \"description\": \"A charming hotel with a Michelin-starred restaurant, offering a luxurious experience in a tranquil setting.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8706, 2.2796\"}, {\"place_name\": \"Le Taillevent\", \"description\": \"A Michelin-starred restaurant known for its refined French cuisine and elegant ambiance.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8741, 2.3025\"}, {\"place_name\": \"Louvre Museum\", \"description\": \"The Louvre Museum is one of the world's largest museums and a historic monument in Paris, France. A central landmark of the city, it is located on the Right Bank of the Seine in the city's 1st arrondissement and home to some of the most canonical works of Western art, including the Mona Lisa and the Venus de Milo. It is recommended to visit in the afternoon.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8606, 2.3376\"}, {\"place_name\": \"Hotel Montalembert\", \"description\": \"A stylish hotel known for its elegant rooms and proximity to the Louvre Museum.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8567, 2.3279\"}, {\"place_name\": \"Pavillon Faubourg Saint-Germain & Spa\", \"description\": \"A luxurious hotel with a Michelin-starred restaurant and a tranquil spa, offering a pampering experience.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8565, 2.3304\"}], \"2\": [{\"place_name\": \"Musée d'Orsay\", \"description\": \"The Musée d'Orsay is a museum in Paris, France, on the Left Bank of the Seine. It is housed in the former Gare d'Orsay, a Beaux-Arts railway station built between 1898 and 1900. The museum holds mainly French art dating from 1848 to 1914, including Impressionist, Post-Impressionist, and Art Nouveau works. It is recommended to visit in the morning.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8582, 2.3299\"}, {\"place_name\": \"Hotel Montalembert\", \"description\": \"A stylish hotel known for its elegant rooms and proximity to the Louvre Museum.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8567, 2.3279\"}, {\"place_name\": \"Pavillon Faubourg Saint-Germain & Spa\", \"description\": \"A luxurious hotel with a Michelin-starred restaurant and a tranquil spa, offering a pampering experience.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8565, 2.3304\"}, {\"place_name\": \"Hotel Crillon, A Rosewood Hotel\", \"description\": \"A historic hotel with a Michelin-starred restaurant, offering a luxurious experience in a prime location.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8680, 2.3221\"}, {\"place_name\": \"Centre Pompidou\", \"description\": \"The Centre Pompidou is a complex that includes a museum of modern art, public library, and music and acoustic research center, located in the Beaubourg area of the 4th arrondissement of Paris, France. The building, designed by architect Renzo Piano and Richard Rogers, was completed in 1977, and its distinctive style makes it one of the most recognizable structures in Paris. It is recommended to visit in the afternoon.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8608, 2.3488\"}, {\"place_name\": \"Pavillon Faubourg Saint-Germain & Spa\", \"description\": \"A luxurious hotel with a Michelin-starred restaurant and a tranquil spa, offering a pampering experience.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8565, 2.3304\"}, {\"place_name\": \"Grand Hôtel du Palais Royal\", \"description\": \"A luxurious hotel with a Michelin-starred restaurant, known for its elegant ambiance and prime location.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8631, 2.3379\"}, {\"place_name\": \"Notre Dame Cathedral\", \"description\": \"Notre-Dame de Paris, referred to simply as Notre-Dame, is a medieval Catholic cathedral on the Île de la Cité. The cathedral is widely considered to be one of the finest examples of French Gothic architecture. It is recommended to visit in the evening.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8534, 2.3497\"}, {\"place_name\": \"Pavillon Faubourg Saint-Germain & Spa\", \"description\": \"A luxurious hotel with a Michelin-starred restaurant and a tranquil spa, offering a pampering experience.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8565, 2.3304\"}, {\"place_name\": \"Shu\", \"description\": \"A popular restaurant known for its delicious Asian cuisine and vibrant atmosphere.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8530, 2.3422\"}], \"3\": [{\"place_name\": \"Sacré-Cœur Basilica\", \"description\": \"The Basilica of the Sacred Heart of Paris, commonly known as Sacré-Cœur Basilica, is a Roman Catholic church and minor basilica, dedicated to the Sacred Heart of Jesus, in the Montmartre district of Paris, France. The basilica is located at the summit of the Butte Montmartre, the highest point in Paris. It is recommended to visit in the morning.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8892, 2.3419\"}, {\"place_name\": \"Crêperie Brocéliande\", \"description\": \"A charming crêperie known for its delicious crêpes and authentic French ambiance.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8844, 2.3411\"}, {\"place_name\": \"Le Supercoin\", \"description\": \"A popular bistro known for its casual atmosphere and delicious French cuisine.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8931, 2.3506\"}, {\"place_name\": \"Bistrot HOTARU\", \"description\": \"A cozy bistro offering a unique blend of French and Japanese cuisine, known for its intimate setting.\", \"TOE\": \"1 hour\", \"lat_long\": \"48.8782, 2.3427\"}, {\"place_name\": \"Montmartre\", \"description\": \"Montmartre is a district of Paris, France, located in the 18th arrondissement. The district is known for its hill, the Butte Montmartre, which is the highest point in Paris. Montmartre is also known for its bohemian history and its association with artists, writers, and musicians. It is recommended to visit in the afternoon.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8864, 2.3429\"}, {\"place_name\": \"Crêperie Brocéliande\", \"description\": \"A charming crêperie known for its delicious crêpes and authentic French ambiance.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8844, 2.3411\"}, {\"place_name\": \"Bistrot HOTARU\", \"description\": \"A cozy bistro offering a unique blend of French and Japanese cuisine, known for its intimate setting.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8782, 2.3427\"}, {\"place_name\": \"Le Supercoin\", \"description\": \"A popular bistro known for its casual atmosphere and delicious French cuisine.\", \"TOE\": \"3 hours\", \"lat_long\": \"48.8931, 2.3506\"}, {\"place_name\": \"Moulin Rouge\", \"description\": \"The Moulin Rouge is a famous cabaret in Paris, France. It is known for its red windmill and its lavish shows featuring can-can dancers. The Moulin Rouge is located in the Montmartre district of Paris. It is recommended to visit in the evening.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8858, 2.3417\"}, {\"place_name\": \"Crêperie Brocéliande\", \"description\": \"A charming crêperie known for its delicious crêpes and authentic French ambiance.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8844, 2.3411\"}, {\"place_name\": \"Bistrot HOTARU\", \"description\": \"A cozy bistro offering a unique blend of French and Japanese cuisine, known for its intimate setting.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8782, 2.3427\"}, {\"place_name\": \"L'Office\", \"description\": \"A popular bistro known for its casual atmosphere and delicious French cuisine.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8740, 2.3474\"}, {\"place_name\": \"Le Supercoin\", \"description\": \"A popular bistro known for its casual atmosphere and delicious French cuisine.\", \"TOE\": \"2 hours\", \"lat_long\": \"48.8931, 2.3506\"}], \"changes\": \"I have shortened your trip to 3 days. I have removed Day 4 and Day 5 from your itinerary.\"}\n",
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
