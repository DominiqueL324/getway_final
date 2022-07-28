import json
import string
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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg import generators
# Create your views here.

class AdministrateurApi(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Some description" ,type=openapi.TYPE_STRING)
    pagination_param = openapi.Parameter('paginated', in_=openapi.IN_QUERY ,description="Some description" ,type=openapi.TYPE_STRING,required=False)
    page_param = openapi.Parameter('page', in_=openapi.IN_QUERY ,description="Some description" ,type=openapi.TYPE_INTEGER,required=False)

    @swagger_auto_schema(manual_parameters=[token_param,pagination_param,page_param])
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
            admins = requests.get(URLADMINISTRATEUR,params=request.query_params,headers={"Authorization":"Bearer "+token}).json()
            return Response(admins,status=200) 
        except ValueError:
            return JsonResponse({"status":"failure"},status=401) 

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['data'],
            properties={
                'nom': openapi.Schema(type=openapi.TYPE_STRING),
                'prenom': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'login': openapi.Schema(type=openapi.TYPE_STRING),
                'mdp': openapi.Schema(type=openapi.TYPE_STRING),
                'adresse': openapi.Schema(type=openapi.TYPE_STRING),
                'telephone': openapi.Schema(type=openapi.TYPE_STRING),
            },
         ),
        manual_parameters=[token_param])
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
            #return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
            #return JsonResponse({"status":"No roles"},status=401)

        try:
            administrateurs = requests.post(URLADMINISTRATEUR,headers={"Authorization":"Bearer "+token},data=self.request.data).json() 
            return Response(administrateurs,status=200) 
        except ValueError:
            return JsonResponse({"status":"failure"},status=401) 

               
class AdministrateurDetailsAPI(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Some description" ,type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[token_param])
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

        url_ = URLADMINISTRATEUR+str(id)
    
        try:
            administrateur = requests.get(url_,headers={"Authorization":"Bearer "+token}).json() 
            return Response(administrateur,status=200)    
        except ValueError:
            return JsonResponse({"status":"failure"},status=401) 
            
    #edit rdv
    @swagger_auto_schema(request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['data'],
            properties={
                'nom': openapi.Schema(type=openapi.TYPE_STRING),
                'prenom': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'login': openapi.Schema(type=openapi.TYPE_STRING),
                'mdp': openapi.Schema(type=openapi.TYPE_STRING),
                'adresse': openapi.Schema(type=openapi.TYPE_STRING),
                'telephone': openapi.Schema(type=openapi.TYPE_STRING),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
         ),manual_parameters=[token_param])
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
            #return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
            #return JsonResponse({"status":"No roles"},status=401)

        try:
            administrateurs = requests.put(URLADMINISTRATEUR+str(id),headers={"Authorization":"Bearer "+token},data=self.request.data).json()
            return Response(administrateurs,status=401) 
        except ValueError:
            return JsonResponse({"status":"failure"},status=401) 

    @swagger_auto_schema(manual_parameters=[token_param])      
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
            #return JsonResponse({"status":"insufficient privileges"},status=401)
        #if checkRole(self.request,"administrateur")== -1:
            #return JsonResponse({"status":"No roles"},status=401)

        try:
            administrateurs = requests.delete(URLADMINISTRATEUR+str(id),headers={"Authorization":"Bearer "+token}).json()
            return JsonResponse({"status":"done"},status=200)
        except ValueError:
            return JsonResponse({"status":"failure"},status=401)

class UsersApi(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token pour auth" ,type=openapi.TYPE_STRING)
    pagination_param = openapi.Parameter('paginated', in_=openapi.IN_QUERY ,description="Pagination ou non" ,type=openapi.TYPE_STRING,required=False)
    page_param = openapi.Parameter('page', in_=openapi.IN_QUERY ,description="page de pagination" ,type=openapi.TYPE_INTEGER,required=False)
    search_param = openapi.Parameter('value', in_=openapi.IN_QUERY ,description="Valeur pour la recherche" ,type=openapi.TYPE_STRING,required=False)
    @swagger_auto_schema(manual_parameters=[token_param,pagination_param,page_param,search_param])
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

        url_ = URLUSERS
        try:
            users = requests.get(url_,params=request.query_params,headers={"Authorization":"Bearer "+token}).json() 
            return Response(users,status=200)    
        except ValueError:
            return JsonResponse({"status":"failure"},status=401) 

class userStateApi(APIView):
    
    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Some description" ,type=openapi.TYPE_STRING)
    user_param = openapi.Parameter('id', in_=openapi.IN_QUERY ,description="Some description" ,type=openapi.TYPE_INTEGER,required=True)
    @swagger_auto_schema(manual_parameters=[token_param,user_param])
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

        id = request.GET.get("id",None)
        if id is not None:
            try:
                go = requests.get(URLUSERS +"active/"+str(id),headers={"Authorization":"Bearer "+token}).json()
                return Response({"status":"done"},status=status.HTTP_200_OK)  
            except KeyError:
                return JsonResponse({"status":"failure"},status=401) 
        return Response({"status":"failure"},status=status.HTTP_200_OK) 

         
            


