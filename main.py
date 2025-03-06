import google.generativeai as genai
from google.api_core import exceptions  # Import for exception handling
from utils import get_api_key, chat_loop  # Import functions from utils.py (optional)

if __name__ == "__main__":
  api_key = get_api_key()
  try:
    chat_loop(api_key)
  except exceptions.InvalidArgument as e:
    if "API_KEY_INVALID" in str(e):
      print("API Key Expired. Renewing...")
      api_key = get_api_key()
      chat_loop(api_key)  # Retry with the renewed key
    else:
      print(f"An error occurred: {e}")
