from ast import Constant
import json
from typing import final
from urllib.request import Request
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import  TokenAuthentication
from rest_framework import generics
from rest_framework import mixins 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User, Group
from datetime import date, datetime,time,timedelta
import requests
from rdv.views import controller
from gateway.settings import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RefreshToken(APIView):

    #refresh token method
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['data'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ))
    def post(self,request):
        try:
            token = requests.post("http://127.0.0.1:8050/manager_app/token/refresh/",data=self.request.data).json()
            return Response(token,status=status.HTTP_200_OK)
        except ValueError:
            return JsonResponse({"status":"Faillure"},status=400)

class LoginApi(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)
    token_black = openapi.Parameter('token', in_=openapi.IN_QUERY ,description="Refresh token for logout" ,type=openapi.TYPE_STRING)

    #login method
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['data'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
         ))
    def post(self,request):
        try:
            token = requests.post("http://127.0.0.1:8050/manager_app/login/",data=self.request.data).json()
        except ValueError:
            return JsonResponse({"status":"Faillure"},status=401)

        if "access" not in token.keys():
            return JsonResponse({"status":"Bad credentials"},status=401)
        
        access_ = token["access"]
        
        try:
            user = requests.get("http://127.0.0.1:8050/manager_app/viewset/role/?token="+access_,headers={"Authorization":"Bearer "+access_}).json()[0]
            user['tokens']=token
        except ValueError:
            return JsonResponse({"status":"Faillure"},status=401)
        return Response(user,status=status.HTTP_200_OK)

    #logout method
    @swagger_auto_schema(manual_parameters=[token_param,token_black])
    def get(self,request):

        try:
            token = self.request.headers.__dict__['_store']['authorization'][1].split(' ')[1]
        except KeyError:
            return JsonResponse({"status":"not_logged"},status=401)

        logged = controller(token)
        test = isinstance(logged, list)
        if not test:
            return JsonResponse({"status":"not_logged"},status=401)

        try:
            user = requests.get("http://127.0.0.1:8050/manager_app/logout/",params=request.query_params,headers={"Authorization":"Bearer "+token}).json()
        except ValueError:
            return JsonResponse({"status":"Faillure"},status=401)
        return Response(user,status=status.HTTP_200_OK)

class checkExistingMails(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)
    login_param = openapi.Parameter('username', in_=openapi.IN_QUERY ,description="Username to check if existing" ,type=openapi.TYPE_STRING)
    id_param = openapi.Parameter('id', in_=openapi.IN_QUERY ,description="Id of the user for check" ,type=openapi.TYPE_STRING)
    email_param = openapi.Parameter('email', in_=openapi.IN_QUERY ,description="Email to check if existing" ,type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param,login_param,email_param,id_param])
    def get(self,request):
        try:
            token = self.request.headers.__dict__['_store']['authorization'][1].split(' ')[1]
        except KeyError:
            return JsonResponse({"status":"not_logged"},status=401)

        logged = controller(token)
        test = isinstance(logged, list)
        if not test:
            return JsonResponse({"status":"not_logged"},status=401)
        try:
            resp = requests.get("http://127.0.0.1:8050/manager_app/viewset/checker/",headers={"Authorization":"Bearer "+token},params=request.query_params).json()
        except ValueError:
            return JsonResponse({"status":"Faillure"},status=401)
        return Response(resp,status=status.HTTP_200_OK)

def checkRole(request,role_):
    try:
        role = request.headers.__dict__['_store']['role'][1]
        if role != role_:
            return 0
        else:
            return 1
    except KeyError:
        return -1
        



