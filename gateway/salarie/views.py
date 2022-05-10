import json
from typing import final
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
# Create your views here.

class SalarieApi(APIView):

    def get(self,request):

        try:
            token = self.request.headers.__dict__['_store']['authorization'][1].split(' ')[1]
        except KeyError:
            return JsonResponse({"status":"not_logged"},status=401)

        logged = controller(token)
        test = isinstance(logged, list)
        if not test:
        #if "id" not in logged.keys():
            return JsonResponse({"status":"not_logged"},status=401)
        
        final_=[]
        try:
            salaries = requests.get(URLSALARIE,params=request.query_params,headers={"Authorization":"Token "+token}).json()
            return Response(salaries,status=200) 
        except requests.JSONDecodeError:
            return JsonResponse({"status":"failure"},status=401) 

    def post(self,request):

        try:
            token = self.request.headers.__dict__['_store']['authorization'][1].split(' ')[1]
        except KeyError:
            return JsonResponse({"status":"not_logged"},status=401)

        logged = controller(token)
        test = isinstance(logged, list)
        if not test:
        #if "id" not in logged.keys():
            return JsonResponse({"status":"not_logged"},status=401)

        try:
            salaries = requests.post(URLSALARIE,headers={"Authorization":"Token "+token},data=self.request.data).json() 
            return Response(salaries,status=200) 
        except requests.JSONDecodeError:
            return JsonResponse({"status":"failure"},status=401) 

               
class SalarieDetailsAPI(APIView):

    def get(self,request,id):

        try:
            token = self.request.headers.__dict__['_store']['authorization'][1].split(' ')[1]
        except KeyError:
            return JsonResponse({"status":"not_logged"},status=401)

        logged = controller(token)
        test = isinstance(logged, list)
        if not test:
        #if "id" not in logged.keys():
            return JsonResponse({"status":"not_logged"},status=401)

        url_ = URLSALARIE+str(id)
    
        try:
            salarie = requests.get(url_,headers={"Authorization":"Token "+token}).json() 
            return Response(salarie,status=200)    
        except requests.JSONDecodeError:
            return JsonResponse({"status":"failure"},status=401) 
            
    #edit rdv
    def put(self,request,id):
        try:
            token = self.request.headers.__dict__['_store']['authorization'][1].split(' ')[1]
        except KeyError:
            return JsonResponse({"status":"not_logged"},status=401)

        logged = controller(token)
        test = isinstance(logged, list)
        if not test:
        #if "id" not in logged.keys():
            return JsonResponse({"status":"not_logged"},status=401)

        try:
            salaries = requests.put(URLSALARIE+str(id),headers={"Authorization":"Token "+token},data=self.request.data).json()
            return Response(salaries,status=401) 
        except requests.JSONDecodeError:
            return JsonResponse({"status":"failure"},status=401) 
           
    def delete(self,request,id):
        try:
            token = self.request.headers.__dict__['_store']['authorization'][1].split(' ')[1]
        except KeyError:
            return JsonResponse({"status":"not_logged"},status=401)

        logged = controller(token)
        test = isinstance(logged, list)
        if not test:
        #if "id" not in logged.keys():
            return JsonResponse({"status":"not_logged"},status=401)

        try:
            salaries = requests.delete(URLSALARIE+str(id),headers={"Authorization":"Token "+token}).json()
            return JsonResponse({"status":"done"},status=200)
        except requests.JSONDecodeError:
            return JsonResponse({"status":"failure"},status=401)


         
            


