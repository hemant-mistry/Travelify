from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os


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
        "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="You are a travel assistant. ",
        )

        chat_session = model.start_chat(
        history=[
        ]
        )

        response = chat_session.send_message(message)

        print(response.text)

        # Respond with a confirmation message
        response_data = {
            'response': response.text
        }
        return Response(response_data, status=status.HTTP_200_OK)
