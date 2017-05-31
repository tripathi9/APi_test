from django.contrib.auth import update_session_auth_hash
from .serializers import*
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework_jwt.utils import jwt_payload_handler
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import jwt
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import AllowAny
from .models import*
from rest_framework.decorators import api_view, permission_classes
from cloudinary.utils import cloudinary_url
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.dispatch import receiver
import simplejson as json
from .signals import *

# Create your views here.


def Serializererror(serializer):
	message = serializer.errors[list(serializer.errors)[0]][0]
	error_keys = list(serializer.errors.keys())
	message = message.replace("this field",error_keys[0])
	print("Error------",serializer.errors)
	return message


def otp(uuid,type):
	print("Mobile OTP User Detail",uuid)
	try:
		user = Account.objects.get(uuid=uuid,is_active=False,otp_active=True)
		if type=='signup':
			send_mail('verify your Account', user.otp, settings.EMAIL_HOST_USER, ['tripathi.ankur9@gmail.com'], fail_silently=False)
		else:
			send_mail('verify your Account', user.otp, settings.EMAIL_HOST_USER, ['tripathi.ankur9@gmail.com'], fail_silently=False)
	except Exception as e :
		print("Error in OTP",e)


@api_view(['POST','PUT'])
@permission_classes((AllowAny,))
def SignupView(request,format='json'):
	"""
	Signup ViewSet
	"""
	params = request.data
	params['avatar'] = request.data['avatar']
	print("SignupView Requsted parameters",params)
	serializer = AccountSerializer(data=params)
	# print (serializer)
	print("Validation-----",serializer.is_valid())
	if serializer.is_valid():
		try:
			result = serializer.save()
		except Exception as e:
			print("Error is",e)
		otp(serializer.data['uuid'],"signup")
		return Response({"status":200, "message":"Otp Send to your Email", "uuid":serializer.data['uuid']})
	else:
		message = Serializererror(serializer)
		return Response({"status":500, "message":message, "Error":serializer.errors})



@api_view(['POST'])
@permission_classes((AllowAny,))
def LoginView(request, format='json'):
	"""
	Login ViewSet
	"""
	params = request.data
	print("LoginView Requsted parameters",params)
	try:
		user = get_user_model().objects.get(email=params['email'].lower())
		serializer = AccountSerializer(user)
		user_profile = serializer.data
		pass_valid = user.check_password(params['password'])
		if pass_valid:
			payload = jwt_payload_handler(user)
			token = jwt.encode(payload, settings.SECRET_KEY)
			auth_token = token.decode('unicode_escape')
			if not user.email_verified:
				otp(user.uuid,"signup")
				return Response({"status":300, "message":"Email not Verified.Please verify First.OTP send to your registered Email", "uuid":user.uuid})
			else:
				return Response({"status":200, "message":"Login Successfully", "user_detail":serializer.data, "auth_token":auth_token})
		else:
			return Response({"status":500, "message":"*Email & Password are not Correct"})
	except get_user_model().DoesNotExist:
		return Response({"status":500, "message":"*Email & Password are not Correct"})


@api_view(['POST'])
@permission_classes((AllowAny,))
def OtpVerificationView(request, format='json'):
	"""
	OTP Verification ViewSet
	"""
	params = request.data
	print("OTP Verification Requested Parameters",params)
	try:
		user = Account.objects.get(otp=params['otp'], uuid=params['uuid'], otp_active=True, is_active=False)
		print (user)
		user.otp = '000000'
		user.otp_active = False
		user.email_verified = True
		user.is_active = True
		user.save()
		payload = jwt_payload_handler(user)
		token = jwt.encode(payload, settings.SECRET_KEY)
		auth_token = token.decode('unicode_escape')
		serializer = AccountSerializer(user)
		return Response({"status":200, "message":"OTP Verification Successfully", "user_detail":serializer.data,"auth_token":auth_token})
	except Exception as e:
		print('Error in OTP Verification View----',e)
		return Response({"status":500, "message":"Invalid OTP or OTP get Expired.Request for the new one"})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def GetProfileView(request,format='json'):
	"""
	GetProfile ViewSet
	"""
	params = request.data
	user = request.user
	print("Get Profile Requsted parameters",params)
	try:
		serializer = AccountSerializer(user)
		return Response({"status":200, "message":"User Profile", "user_detail":serializer.data})
	except Exception as e:
		print("Error in Get Profile View",e)
		return Response({"status":500, "message":"Requested User does not Exist"})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def EditProfileView(request, format='json'):
	"""
	Edit Profile ViewSet
	"""
	params = request.data
	user = request.user
	print("EditProfileView Requested Parameters",params)
	serializer = AccountSerializer(user,data=params)
	if serializer.is_valid():
		serializer.save()
		return Response({"status":200, "message":"Profile Updated Successfully.", "user_detail":serializer.data})
	else:
		message = Serializererror(serializer)
		return Response({"status":500, "message":message, "Error":serializer.errors})


@api_view(['POST'])
@permission_classes((AllowAny,))
def ForgotPasswordView(request, format='json'):
	"""
	Forgot Password ViewSet
	"""
	params = request.data
	print("Forgot Password Requested Parameters",params)
	try:
		user = Account.objects.get(email=params['email'])
		current_date = datetime.now().strftime('%d %b %Y')
		totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
		otp=totp.now()
		user.otp=otp
		user.otp_active=True
		user.save()
		send_mail('verify your Account', user.otp, settings.EMAIL_HOST_USER, ['tripathi.ankur9@gmail.com'], fail_silently=False)
		return Response({"status":200, "message":"OTP send on your registered email"})
	except Exception as e:
		print('Error in forgot Password View----',e)
		return Response({"status":500, "message":"Entered email/mobile is not in our Records"})


@api_view(['POST'])
@permission_classes((AllowAny,))
def ForgotOTPVerify(request, format='json'):
	"""
	RequestToCancel ViewSet
	"""
	params = request.data
	print("ForgotOTPVerify Requsted parameters",params)
	try:
		user = Account.objects.get(email=params['email'].lower(), otp=params['otp'])
		return Response({"status":200, "message":"Your OTP is verified", 'uuid':user.uuid})
	except Exception as e:
		print("Error in ForgotOTPVerify view",e)
		return Response({"status":500, "message":"OTP not verified"})
