from .models import *
from .serializers import *
from .views import *
from rest_framework.authtoken.models import Token
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import pyotp


# Signals
@receiver(pre_save, sender=Account)
def model_pre_save(sender, **kwargs):
	print("Account Signal for saving Avatar")
	if kwargs['instance'].avatar and not "cloudinary" in kwargs['instance'].avatar.name:
		upresult_image = upload(kwargs['instance'].avatar)
		kwargs['instance'].avatar = upresult_image['secure_url']
	totp=pyotp.TOTP("JBSWY3DPEHPK3PXP")
	onetimepassword = totp.now()
	kwargs['instance'].otp = onetimepassword
	kwargs['instance'].otp_active = True
