# utils.py
def request_user_info(request):
    return {
        "username": request.user.username,
        "email": request.user.email,
    }


import requests

# Helper function to check internet connectivity
def check_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False