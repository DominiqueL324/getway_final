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
from gateway.settings import *
# Create your views here.

class RdvApi(APIView):

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

        final_ = []
        rdvs = requests.get(URLRDV,params=request.query_params)
        finaly_ ={}
        for rdv in rdvs.json()['results']:
            try:
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client']),headers={"Authorization":"Token "+token}).json()[0]
                rdv['agent'] = requests.get(URLAGENT+str(rdv['agent']),headers={"Authorization":"Token "+token}).json()[0]
                #rdv['passeur'] = requests.get(URLAGENT+str(rdv['passeur'])).json()[0]
            except requests.JSONDecodeError:
                return JsonResponse({"status":"failure"}) 
            final_.append(rdv)
        finaly_['count'] = rdvs.json()['count']
        finaly_['next'] = rdvs.json()['next']
        finaly_['previous'] = rdvs.json()['previous']
        finaly_['results'] = final_
        return Response(finaly_,status=status.HTTP_200_OK)

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

        final_=[]
        rdvs = requests.post(URLRDV,data=self.request.data).json()[0]
        rdvs = requests.get(URLRDV+str(rdvs['id']))
        for rdv in rdvs.json():
            try:
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client']),headers={"Authorization":"Token "+token}).json()[0]
                rdv['agent'] = requests.get(URLAGENT+str(rdv['agent']),headers={"Authorization":"Token "+token}).json()[0]
                #rdv['passeur'] = requests.get(URLAGENT+str(rdv['passeur'])).json()[0]
            except requests.JSONDecodeError:
                return JsonResponse({"status":"failure"}) 
            final_.append(rdv)
        return Response(final_,status=status.HTTP_201_CREATED)

               
class RdvApiDetails(APIView):

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

        final_ = []
        url_ = URLRDV+str(id)
        rdvs = requests.get(url_)

        try:
            for rdv in rdvs.json():
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client']),headers={"Authorization":"Token "+token}).json()[0]
                rdv['agent'] = requests.get(URLAGENT+str(rdv['agent']),headers={"Authorization":"Token "+token}).json()[0]
                #rdv['passeur'] = requests.get(URLAGENT+str(rdv['passeur'])).json()[0]
                final_.append(rdv)
        except requests.JSONDecodeError:
                return JsonResponse({"status":"failure"},status=401) 
            
        return Response(final_,status=status.HTTP_200_OK)

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

        final_=[]
        try:
            rdvs = requests.put(URLRDV+str(id),data=self.request.data).json()[0]
        except requests.JSONDecodeError:
            return JsonResponse({"status":"failure"},status=401) 

        rdvs = requests.get(URLRDV+str(rdvs['id']))
        try:
            for rdv in rdvs.json():
                
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client']),headers={"Authorization":"Token "+token}).json()[0]
                rdv['agent'] = requests.get(URLAGENT+str(rdv['agent']),headers={"Authorization":"Token "+token}).json()[0]
                #rdv['passeur'] = requests.get(URLAGENT+str(rdv['passeur'])).json()[0]
                final_.append(rdv)
        except requests.JSONDecodeError:
                return JsonResponse({"status":"failure"},status=401) 
           
        return Response(final_,status=status.HTTP_201_CREATED)

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
            rdvs = requests.delete(URLRDV+str(id)).json()
            return JsonResponse({"status":"done"},status=200)
        except requests.JSONDecodeError:
            return JsonResponse({"status":"failure"},status=401)

def controller(token):
    rdvs = requests.get(URLMANAGER+token,headers={"Authorization":"Token "+token}).json()
    return rdvs
