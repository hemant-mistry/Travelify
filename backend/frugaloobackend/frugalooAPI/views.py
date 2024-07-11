from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
from .models import UserTripInfo
from .serializers import UserTripInfoSerializer, GeneratedPlanSerializer

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
                system_instruction="Generate an itinerary based on the information received from the user.\n\n### INFORMATION ###\nThe user will provide you with the input in the below format:\n- stay_details\n- number_of_days\n- budget\n- additional_preferences\n\nThe output should be a JSON structure as shown below:\n{\n\"day\": <the day of the trip starting from 1 to number_of_days>,\n\"place_name\":<the name of the place>,\n\"description\":<A short description on what to look for in the place>,\n\"cost\":<The approximate cost that will be spent in the place>,\n\"latitude_and_longitude\":<Provide with the lat, long of the place>\n}",
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
