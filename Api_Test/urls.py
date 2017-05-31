"""Api_Test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from api import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signup$', views.SignupView),
    url(r'^login$', views.LoginView),
    url(r'^otpVerification$', views.OtpVerificationView),
    # url(r'^changePassword$', views.ChangePasswordView),
    url(r'^editProfile$', views.EditProfileView),
    url(r'^forgotPassword$', views.ForgotPasswordView),
    url(r'^forgototpVerify$', views.ForgotOTPVerify),
]
