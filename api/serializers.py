from rest_framework import serializers
from .models import*
from cloudinary.uploader import upload
from rest_framework.serializers import SerializerMethodField
from django.contrib.auth import get_user_model

class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.
    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268
    Updated for Django REST framework 3.
    """
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')
            else:
                return data
            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr
        extension = imghdr.what(file_name, decoded_file)
        extension = "png" if extension == "jpg" else extension
        return extension


class AccountSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=8, max_length=16,error_messages={"blank": "Password cannot be empty", "min_length": "Password is too short","max_length": "Password is too long"})
    avatar = Base64ImageField(use_url=True, default="", required=False)

    correct_image = SerializerMethodField()
    def get_correct_image(self, obj):
        return obj.avatar.name

    class Meta:
        """Doc string for class Meta"""
        model = get_user_model()
        exclude = ('password','date_created','date_modified','is_active','is_admin','last_login','is_superuser','otp', 'otp_active', 'is_staff', 'groups', 'user_permissions')
        # fields = ('first_name','last_name','email','dob','gender','uuid','transport_mode')

    def create(self, validated_data):
        print(validated_data)
        user = Account.objects.create(email=validated_data['email'], first_name=validated_data['first_name'], last_name=validated_data['last_name'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing `User` instance, given the validated data.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        if validated_data.get('avatar'):
            instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
