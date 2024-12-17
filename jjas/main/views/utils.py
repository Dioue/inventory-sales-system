# utils.py
def request_user_info(request):
    return {
        "username": request.user.username,
        "email": request.user.email,
    }
