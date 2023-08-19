from rest_framework import generics, status
from django.contrib.auth.models import User
from .serializers import UserSerialize
from .models import *
from .handlers import *
from django.forms import model_to_dict

from rest_framework.response import Response
from rest_framework.views import APIView

import string
import random
import time

class GetUsers(APIView):
    
    def get(self, request):
        user = CustomUser.objects.all().values()
        return Response({"users": list(user)})


class CreateUser(APIView):
    
    def post(self, request):
        req = request_key(request, ['username', 'password', 'email', 'phone_number'])
        if not req[0]:
            return req[1]
        if 'phone_number' in request.data.keys():
            new_user = CustomUser.objects.create(
                username = request.data['username'],
                password = request.data['password'],
                email = request.data['email'],
                phone_number = request.data['phone_number']
            )

            code = ''.join(random.sample(string.digits, 4))
            time.sleep(random.choice([1,2]))

            auth_code = Code.objects.create(
                user = new_user,
                code = code
            )

            return Response({'user': model_to_dict(auth_code)})
        else:
            return Response({ "amount": ["The 'phone_number' field must be filled in."], "description": ["This field cannot be empty"]}, status=status.HTTP_400_BAD_REQUEST)


class AuthorizationUser(APIView):
   
    def post(self, request):
        req = request_key(request, ['user_id', 'code'])
        if not req[0]:
            return req[1]
        if CustomUser.objects.filter(id=request.data['user_id']).exists():
            user = CustomUser.objects.get(id = request.data['user_id'])
            code = Code.objects.filter(user = user)
            uniq_status = True

            if code[0].code == str(request.data['code']):
                while uniq_status == True:
                    self_ref_code = code = ''.join(random.sample(string.digits + string.ascii_uppercase, 6))
                    if not ReferralCode.objects.filter(self_code = str(self_ref_code)).exists():
                        
                        ref_code = ReferralCode.objects.create(
                            user = user,
                            self_code = self_ref_code
                        )
                        update_user = CustomUser.objects.filter(id = request.data['user_id'])
                        update_user.update(status = True)
                        uniq_status = False
                        del_code = Code.objects.get(user = user)
                        del_code.delete()

                return Response(model_to_dict(ref_code))
            else:
                return Response({ "amount": ["Invalid authorization code."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({ "amount": ["The 'user' field should contain the code of a user who has not yet been authorized."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)


class GetProfile(APIView):

    def get(self, request, user_id):
        if CustomUser.objects.filter(id=user_id).exists():
            user = CustomUser.objects.get(id = user_id)

            if user.status != True:
                return Response({ "amount": ["The user is not authorized."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)

            if ReferralCode.objects.filter(user = user).exists():
                ref_code= ReferralCode.objects.get(user = user)
                referral = []
                
                if ref_code.activate_user.all() != []:
                    for item in ref_code.activate_user.all():
                        referral.append(item.phone_number)
                ref_code_dict = {'user': model_to_dict(user), 'self_code': ref_code.self_code, "activate_code": ref_code.activate_code, 'activate_user': referral}
                
                return Response(ref_code_dict)
            return Response({ "amount": ["Invalid authorization code."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({ "amount": ["The 'user' field should contain the code of a user who has not yet been authorized."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)


class ActivateRefCode(APIView):

    def post(self, request):
        req = request_key(request, ['user_id', 'ref_code'])
        if not req[0]:
            return req[1]
        if CustomUser.objects.filter(id=request.data['user_id']).exists():
            user = CustomUser.objects.get(id = request.data['user_id'])
            ref_code = request.data['ref_code']
            
            if ReferralCode.objects.get(user = user).activate_code != "":
                return Response({ "amount": ["Invalid authorization code."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)

            if user.status != True:
                return Response({ "amount": ["The user is not authorized."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)
            
            if ReferralCode.objects.filter(self_code = ref_code).exists():
                referral_code_activate = ReferralCode.objects.filter(user = user)

                if referral_code_activate[0].self_code == ref_code:
                    return Response({ "amount": ["Incorrect referral code."], "description": ["Enter the correct data"]}, status=status.HTTP_400_BAD_REQUEST)

                referral_code_activate.update(activate_code = ref_code)

                referrer = ReferralCode.objects.get(self_code = ref_code)
                referrer.activate_user.add(user)
                return_dict = {"referral": model_to_dict(user), "referrer": referrer.user.username, "referral_code": ref_code}
                return Response(return_dict)
            
            