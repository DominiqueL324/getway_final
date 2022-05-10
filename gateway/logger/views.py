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

class LoginApi(APIView):

    def post(self,request):
        try:
            token = requests.post("http://127.0.0.1:8050/manager_app/login/",data=self.request.data).json()
        except requests.JSONDecodeError:
            return JsonResponse({"status":"Faillure"},status=401)

        if "token" not in token.keys():
            return JsonResponse({"status":"Bad credentials"},status=401)

        token = token['token']
        try:
            user = requests.get("http://127.0.0.1:8050/manager_app/viewset/role/?token="+token,headers={"Authorization":"Token "+token}).json()[0]
            user['token']=token
        except requests.JSONDecodeError:
            return JsonResponse({"status":"Faillure"},status=401)
        return Response(user,status=status.HTTP_200_OK)

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
            user = requests.get("http://127.0.0.1:8050/manager_app/logout/?token="+token,headers={"Authorization":"Token "+token}).json()
        except requests.JSONDecodeError:
            return JsonResponse({"status":"Faillure"},status=401)
        return Response(user,status=status.HTTP_200_OK)

class checkExistingMails(APIView):

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
            resp = requests.get("http://127.0.0.1:8050/manager_app/viewset/checker/",headers={"Authorization":"Token "+token},params=request.query_params).json()
        except requests.JSONDecodeError:
            return JsonResponse({"status":"Faillure"},status=401)
        return Response(resp,status=status.HTTP_200_OK)
        



