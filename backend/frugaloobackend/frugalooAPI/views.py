from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
from .models import UserTripInfo, UserTripProgressInfo
from .serializers import UserTripInfoSerializer, GeneratedPlanSerializer, UserTripProgressSerializer
import json

class SaveTripDetails(APIView):
    
    def insert_trip_details(self,user_id,stay_details, number_of_days, budget, additional_preferences, generated_plan):
        UserTripInfo.objects.create(
            user_id = user_id,
            stay_details = stay_details,
            number_of_days = number_of_days,
            budget = budget,
            additional_preferences = additional_preferences,
            generated_plan = generated_plan
        )

        print(f"Inserted trip details into DB {user_id}, {stay_details},{number_of_days},{budget},{additional_preferences}, {generated_plan}")


    def post(self,request):
        try:
            user_id = request.data.get('user_id')
            stay_details = request.data.get('stay_details')
            number_of_days = request.data.get('number_of_days')
            budget = request.data.get('budget')
            additional_preferences = request.data.get('additional_preferences')
            
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
                system_instruction="Generate an itinerary based on the information received from the user. Each day in the itinerary should contain minimum 5 activities. \nIn those 5 activities, breakfast, lunch and dinner is included as well. And always recommend the eating places near to the place the user is going to visit.\n### INFORMATION ###\nThe user will provide you with the input in the below format:\n- stay_details\n- number_of_days\n- budget\n- additional_preferences\nThe output should be a JSON structure as shown below:\n\nTOE: It indicates the approx time for exploring that particular activity.\n<OUTPUT FORMAT>\n{  \"1\":[{\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"},{\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"}],\n  \"2\":[{\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"},{\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"}],\n  \"3\":[{\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"},{\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"}, {\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"}],\n  \"4\":[{\"place_name\":\"val1\",\"description\":\"val2\",\"TOE\":\"val3\"}],\n}\n<OUTPUT FORMAT/>\n",
            )

            chat_session = model.start_chat(
                history=[
                ]
            )

            concatenated_input = f"Stay Details: {stay_details}\nNumber of Days: {number_of_days}\nBudget: {budget}\nAdditional Preferences: {additional_preferences}"

            response = chat_session.send_message(concatenated_input)
            response_data = response.text



            self.insert_trip_details(user_id,stay_details,number_of_days,budget,additional_preferences, response_data)

            response = {
                "user_id":user_id,
                "stay_details":stay_details,
                "number_of_days":number_of_days,
                "budget":budget,
                "additional_preferences":additional_preferences,
                "generated_plan":response_data
            }

            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class FetchTripDetails(APIView):
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            # Fetch all records where user_id matches
            trip_details = UserTripInfo.objects.filter(user_id=user_id)
            
            # Serialize the queryset
            serializer = UserTripInfoSerializer(trip_details, many=True)
            serialized_data = serializer.data
            
            # Return the serialized data as JSON response
            return Response(serialized_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FetchPlan(APIView):
    def post(self, request):
        try:
            trip_id = request.data.get('trip_id')

            trip_details = UserTripInfo.objects.filter(trip_id=trip_id).first()  # Assuming trip_id is unique

            if not trip_details:
                return Response({"error": "Trip details not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = GeneratedPlanSerializer(trip_details)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserTripProgress(APIView):
    def post(self,request):
        try:
            trip_id = request.data.get('trip_id')
            user_id = request.data.get('user_id')
            day = request.data.get('day')

            UserTripProgressInfo.objects.create(
            user_id = user_id,
            trip_id = trip_id,
            day = day
            )

            response = {
                "user_id":user_id,
                "trip_id":trip_id,
                "day":day
            }

            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FetchUserTripProgress(APIView):
    def post(self,request):
        try:
            trip_id = request.data.get('trip_id')
            trip_details = UserTripProgressInfo.objects.filter(trip_id=trip_id)
            serializer = UserTripProgressSerializer(trip_details, many=True)
            serialized_data = serializer.data
            
            # Return the serialized data as JSON response
            return Response(serialized_data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GeminiSuggestions(APIView):
    def post(self,request):
        try:
            
            current_day = request.data.get('current_day')
            original_plan = request.data.get('original_plan')
            user_changes = request.data.get('user_changes')

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
                system_instruction="You are a travel agent, you plan itinearies for user. You need to give alternate plan for user's trip based on their current progress and problems.\n\nYou will be given the below input:\noriginal_plan: It would be a JSON structure which represents the user's original plan.\ncurrent_day: It represents the current day the user is in. It will give you an idea of the user's trip progress.\nuser_changes: It represents the changes the user wants to make in the itinerary or the suggestions they want from you.\n\nYou need to edit the the original_plan and share it as the output and also let the user know the changes/additions you made. \n\nSAMPLE_OUTPUT:\n[\n{\n\"day\": 1,\n\"place_name\": \"Red Fort\",\n\"description\": \"A UNESCO World Heritage Site, the Red Fort is a magnificent Mughal-era fort that offers a glimpse into the history and grandeur of the Mughal Empire. Explore its intricate architecture, visit the Diwan-i-Am and Diwan-i-Khas halls, and enjoy the spectacular sound and light show in the evening.\",\n\"cost\": 500,\n\"latitude_and_longitude\": \"28.6560,77.2311\"\n},\n{\n\"day\": 2,\n\"place_name\": \"India Gate\",\n\"description\": \"A war memorial dedicated to the Indian soldiers who died in World War I, India Gate is an iconic landmark in New Delhi. Climb to the top of the arch for stunning views of the city, admire the eternal flame, and soak in the historical significance of this monument.\",\n\"cost\": 300,\n\"latitude_and_longitude\": \"28.6130,77.2296\"\n},\n{\n\"day\": 3,\n\"place_name\": \"National Museum\",\n\"description\": \"One of the largest museums in India, the National Museum houses a vast collection of artifacts from various periods of Indian history and culture. Explore the galleries showcasing ancient sculptures, paintings, textiles, and more.\",\n\"cost\": 200,\n\"latitude_and_longitude\": \"28.6139,77.2286\"\n},\n{\n\"day\": 4,\n\"place_name\": \"Chandni Chowk\",\n\"description\": \"A bustling and vibrant marketplace, Chandni Chowk is a feast for the senses. Stroll through the narrow alleys, shop for traditional Indian clothing, jewelry, and spices, and savor the delicious street food. Don't miss the famous Paranthe wali gali for mouthwatering parathas.\",\n\"cost\": 400,\n\"latitude_and_longitude\": \"28.6512,77.2315\"\n},\n{\n\"day\": 5,\n\"place_name\": \"Humayun's Tomb\",\n\"description\": \"A UNESCO World Heritage Site, Humayun's Tomb is a beautiful Mughal garden tomb that served as the inspiration for the Taj Mahal. Admire the intricate architecture, explore the gardens, and learn about the history of the Mughal dynasty.\",\n\"cost\": 250,\n\"latitude_and_longitude\": \"28.6104,77.2295\"\n},\n{\n\"changes\": \"Hello, I've added day 5 for you to visit Humayun's Tomb. It is a UNESCO World Heritage Site, Humayun's Tomb is a beautiful Mughal garden tomb that served as the inspiration for the Taj Mahal. Admire the intricate architecture, explore the gardens, and learn about the history of the Mughal dynasty.\n}\n]",
            )

            chat_session = model.start_chat(
                history=[
                ]
            )

            concatenated_input = f"Original Details: {original_plan}\nCurrent day: {current_day}\Changes/Problems the user is currently facing with the original plan: {user_changes}\n"

            response = chat_session.send_message(concatenated_input)
            response_data = response.text
            

            response = {
                "user_changes":user_changes,
                "current_day":current_day,
                "response_data": response_data
            }

            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UpdateTrip(APIView):
    def post(self,request):
        try:
            trip_id = request.data.get('trip_id')
            new_plan = request.data.get('new_plan')

            restructured_plan_str = json.dumps(new_plan)

            

            print(restructured_plan_str)
            # Fetch the trip details using the trip_id
            trip_details = UserTripInfo.objects.filter(trip_id=trip_id).first()
            
            
            if not trip_details:
                return Response({"error": "Trip details not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Update the generated_plan with the new_plan
            trip_details.generated_plan = restructured_plan_str
            trip_details.save()

            return Response({"message": "Trip details updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)