from rest_framework.response import Response
from rest_framework import status

def request_key(request, *args, **kwargs):
    if list(request.data.keys()) == args[0]:
        return [True, "ok"]
    else:
        text = f"You need to fill in the fields {args[0]}"
        return [False, Response({ "amount": [text], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)]