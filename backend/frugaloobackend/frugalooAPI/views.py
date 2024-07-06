from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
from .models import UserTripInfo


class GenerateMessageView(APIView):
    def post(self, request):
        user_name = request.data.get('user_name')
        message = request.data.get('message')
        
        # Add any processing logic here if needed
        genai.configure(api_key=os.environ["GOOGLE_GEMINI_API_KEY"])

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }


        model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        

        )


        chat_session = model.start_chat(
        history=[
        ]
        )

        response = chat_session.send_message(
            "You are a travel assistant. Your job is to suggest good itineraries to users."+
            message
            
            )

   

        print(response.text)

        # Respond with a confirmation message
        response_data = {
            'response': response.text
        }
        return Response(response_data, status=status.HTTP_200_OK)


class SaveTripDetails(APIView):
    
    def insert_trip_details(self,user_id,stay_details, number_of_days, budget, additional_preferences):
        UserTripInfo.objects.create(
            user_id = user_id,
            stay_details = stay_details,
            number_of_days = number_of_days,
            budget = budget,
            additional_preferences = additional_preferences
        )

        print(f"Inserted trip details into DB {user_id}, {stay_details},{number_of_days},{budget},{additional_preferences}")


    def post(self,request):
        try:
            user_id = request.data.get('user_id')
            stay_details = request.data.get('stay_details')
            number_of_days = request.data.get('number_of_days')
            budget = request.data.get('budget')
            additional_preferences = request.data.get('additional_preferences')

            self.insert_trip_details(user_id,stay_details,number_of_days,budget,additional_preferences)

            response = {
                "user_id":user_id,
                "stay_details":stay_details,
                "number_of_days":number_of_days,
                "budget":budget,
                "additional_preferences":additional_preferences
            }

            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

