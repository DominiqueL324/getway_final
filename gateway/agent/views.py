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
from logger.views import checkRole
# Create your views here.

class AgentApi(APIView):

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
        
        #controle des roles 
        #if checkRole(self.request,"administrateur") == 0:
            #return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
            #return JsonResponse({"status":"No roles"},status=401)
        
        try:
            clients = requests.get(URLAGENT,params=request.query_params,headers={"Authorization":"Bearer "+token}).json()
            return Response(clients,status=200) 
        except ValueError:
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
        #controle des roles 
        #if checkRole(self.request,"administrateur") == 0:
        #    return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
        #    return JsonResponse({"status":"No roles"},status=401)
        try:
            agents = requests.post(URLAGENT,headers={"Authorization":"Bearer "+token},data=self.request.data).json() 
            return Response(agents,status=200) 
        except ValueError:
            return JsonResponse({"status":"failure"},status=401) 

               
class AgentDetailsAPI(APIView):

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
        #controle des roles 
        #if checkRole(self.request,"administrateur") == 0:
            #return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
            #return JsonResponse({"status":"No roles"},status=401)

        url_ = URLAGENT+str(id)
    
        try:
            agent = requests.get(url_,headers={"Authorization":"Bearer "+token}).json() 
            return Response(agent,status=200)    
        except ValueError:
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
        
        #controle des roles 
        #if checkRole(self.request,"administrateur") == 0:
         #   return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
            #return JsonResponse({"status":"No roles"},status=401)

        try:
            agents = requests.put(URLAGENT+str(id),headers={"Authorization":"Bearer "+token},data=self.request.data).json()
            return Response(agents,status=401) 
        except ValueError:
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
        #controle des roles 
        #if checkRole(self.request,"administrateur") == 0:
        #   return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
        #    return JsonResponse({"status":"No roles"},status=401)

        try:
            agents = requests.delete(URLAGENT+str(id),headers={"Authorization":"Bearer "+token}).json()
            return JsonResponse({"status":"done"},status=200)
        except ValueError:
            return JsonResponse({"status":"failure"},status=401)


         
            


