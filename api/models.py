from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
import datetime
import uuid
from django.utils import timezone
from django.conf import settings
# Create your models here.

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = False
        user.is_staff = True
        user.save(using=self._db)
        try:
            Token.objects.create(user=user)
        except Exception as e:
            print("Error in creating User---------",e)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email,password=password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.role = 0
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser, PermissionsMixin):
    avatar = models.ImageField(null=True, blank=True)
    first_name = models.CharField(('First Name'), max_length=30, blank=False)
    last_name = models.CharField(('Last Name'), max_length=30, blank=False)
    email = models.EmailField(('Email address'), max_length=30, unique=True)
    email_verified = models.BooleanField(_('Email Verification'), default=False, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    otp = models.CharField(('OTP '), max_length=6, blank=True,null=True,default='000000')
    otp_active = models.BooleanField(_('OTP Active'), default=True)
    is_active = models.BooleanField(_('Active'), default=False)
    is_admin = models.BooleanField(_('Admin'), default=False)
    is_staff = models.BooleanField(_('Staff'), default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)



    objects = AccountManager()

    USERNAME_FIELD = 'email'
    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name+" "+self.last_name
    def __str__(self):
        return self.first_name+" "+self.last_name

    class Meta:
        """
        Meta Class to show Desired name of Table in Admin.py
        """
        verbose_name = 'Api_Test User'
        verbose_name_plural = 'Api_Test Users'
