from email import header
from http import client
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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from logger.tools import envoyerEmail
# Create your views here.

def controller(token):
    rdvs = requests.get(URLMANAGER+token,headers={"Authorization":"Bearer "+token}).json()
    return rdvs

def checkRole(token):
    try:
        user = requests.get("http://127.0.0.1:8050/manager_app/viewset/role/?token="+token,headers={"Authorization":"Bearer "+token}).json()[0]
    except KeyError:
        return -1
    return user

class RdvApi(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param])
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
        
        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Administrateur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier" and role['user']['group'] != "Salarie" and role['user']['group'] != "Audit planneur":
            return JsonResponse({"status":"insufficient privileges"},status=401)

        url_ = URLRDV

        if role['user']['group'] == "Client particulier" or role['user']['group'] == "Client pro":
            url_ = url_+"?user="+str(role['user']['id'])
        
        if role['user']['group'] == "Agent secteur":
            url_ = url_+"?agent="+str(role['user']['id'])
        
        if role['user']['group'] == "Agent constat":
            url_ = url_+"?constat="+str(role['user']['id'])

        if role['user']['group'] == "Audit planneur":
            url_ = url_+"?planneur="+str(role['user']['id'])
        
        if role['user']['group'] == "Salarie":
            url_ = url_+"?passeur="+str(role['user']['id'])

        finaly_ ={}
        """if(request.GET.get("value",None) is not None):
            url_ = URLUSERS
            val_ = request.GET.get("value",None)
            users = requests.get(url_,params=request.query_params,headers={"Authorization":"Bearer "+token}).json()
            for user in users:
                rdvs = requests.get(URLRDV,params={"user":user.client}).json()
                for rdv in rdvs:
                   finaly_.append(rdv)
            return Response(finaly_,status=status.HTTP_200_OK)"""

        final_ = []
        rdvs = requests.get(url_,params=request.query_params)
        finaly_ ={}
        test = isinstance(rdvs.json(), list)
        if test:
            r = rdvs.json()
        else:
            r = rdvs.json()['results']
            finaly_['count'] = rdvs.json()['count']
            finaly_['next'] = rdvs.json()['next']
            finaly_['previous'] = rdvs.json()['previous']

        for rdv in r:
            try:
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client'])+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent'] is not None:
                    id_f = str(rdv['agent']).split(".")[0]
                    rdv['agent'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent_constat'] is not None:
                    id_f = str(rdv['agent_constat']).split(".")[0]
                    rdv['agent_constat'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['audit_planneur'] is not None:
                    id_f = str(rdv['audit_planneur']).split(".")[0]
                    rdv['audit_planneur'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['passeur'] is not None:
                    id_f = str(rdv['passeur']).split(".")[0]
                    rdv['passeur'] = requests.get(URLSALARIE+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()
            except ValueError:
                return JsonResponse({"status":"failure"}) 
            final_.append(rdv)
        finaly_['results'] = final_
        return Response(finaly_,status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['data'],
            properties={
                'nom_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'prenom_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'email_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'reference_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'nom_locataire': openapi.Schema(type=openapi.TYPE_STRING),
                'prenom_locataire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'email_locataire': openapi.Schema(type=openapi.TYPE_STRING),
                'telephone_locataire': openapi.Schema(type=openapi.TYPE_STRING),
                'surface_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_parking_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'adresse_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'code_postal_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'ville_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'adresse_complementaire_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_cave_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_sol_propriete' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'ref_lot' : openapi.Schema(type=openapi.TYPE_STRING),
                'ref_edl' : openapi.Schema(type=openapi.TYPE_STRING),
                'intervention' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'client' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'statut' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'date' : openapi.Schema(type=openapi.TYPE_STRING),
                'passeur' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'agent': openapi.Schema(type=openapi.TYPE_INTEGER),
                'longitude':openapi.Schema(type=openapi.TYPE_STRING),
                'latitude':openapi.Schema(type=openapi.TYPE_STRING),
                'type_propriete': openapi.Schema(type=openapi.TYPE_INTEGER),
                'type': openapi.Schema(type=openapi.TYPE_STRING),
                'consignes_part': openapi.Schema(type=openapi.TYPE_STRING),
                'list_documents': openapi.Schema(type=openapi.TYPE_STRING),
                'info_diverses': openapi.Schema(type=openapi.TYPE_STRING),
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

        #contrôle des roles
        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Audit planneur" and  role['user']['group'] != "Administrateur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier" and role['user']['group'] != "Salarie":
            return JsonResponse({"status":"insufficient privileges"},status=401)

        final_=[]
        try:
            rdvs = requests.post(URLRDV,data=self.request.data).json()[0]
        except KeyError:
            return JsonResponse({"status":"failure to post data"}) 

        rdvs = requests.get(URLRDV+str(rdvs['id']))
        for rdv in rdvs.json():
            try:
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client'])+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent'] is not None:
                    id_f = str(rdv['agent']).split(".")[0]
                    rdv['agent'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent_constat'] is not None:
                    id_f = str(rdv['agent_constat']).split(".")[0]
                    rdv['agent_constat'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['audit_planneur'] is not None:
                    id_f = str(rdv['audit_planneur']).split(".")[0]
                    rdv['audit_planneur'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['passeur'] is not None:
                    rdv['passeur'] = requests.get(URLSALARIE+"?specific=t"+str(rdv['passeur']),headers={"Authorization":"Bearer "+token}).json()
            except KeyError:
                return JsonResponse({"status":"failure to get response"})
                
            yourdate_ = datetime.strptime(rdv['date'],"%Y-%m-%dT%H:%M:%SZ")
            mail = {
                "client": rdv['client']['user']['nom']+" "+rdv['client']['user']['prenom'],
                "status":"CREATION COMMANDE",
                "intervention":rdv["intervention"]["type"],
                "jour":str(yourdate_.day)+"/"+str(yourdate_.month)+"/"+str(yourdate_.year),
                "users":[rdv['client']['user']['email'],rdv['agent']['user']['email'].split('/')[0]]
            }
            #contenu = "Votre commande est enregistrée."
            #envoyerEmail("Création de commande",contenu,[rdv['client']['user']['email']],contenu) 
            final_.append(rdv)
            requests.post(URLEMAIL,json=mail,params=self.request.query_params)
        return Response(final_,status=status.HTTP_201_CREATED)

               
class RdvApiDetails(APIView):
    
    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)

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
        
        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if  role['user']['group'] != "Audit planneur" and  role['user']['group'] != "Administrateur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier" and role['user']['group'] != "Salarie":
            return JsonResponse({"status":"insufficient privileges"},status=401)

        url_ = URLRDV

        final_ = []
        url_ = URLRDV+str(id)
        rdvs = requests.get(url_,params=self.request.query_params)

        try:
            for rdv in rdvs.json():
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client'])+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent'] is not None:
                    id_f = str(rdv['agent']).split(".")[0]
                    rdv['agent'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent_constat'] is not None:
                    id_f = str(rdv['agent_constat']).split(".")[0]
                    rdv['agent_constat'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['audit_planneur'] is not None:
                    id_f = str(rdv['audit_planneur']).split(".")[0]
                    rdv['audit_planneur'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['passeur'] is not None:
                    id_f = str(rdv['passeur']).split(".")[0]
                    rdv['passeur'] = requests.get(URLSALARIE+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()
                final_.append(rdv)
        except ValueError:
                return JsonResponse({"status":"failure"},status=401) 
            
        return Response(final_,status=status.HTTP_200_OK)

    #edit rdv

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['data'],
            properties={
                'nom_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'prenom_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'email_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'reference_bailleur': openapi.Schema(type=openapi.TYPE_STRING),
                'nom_locataire': openapi.Schema(type=openapi.TYPE_STRING),
                'prenom_locataire': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'email_locataire': openapi.Schema(type=openapi.TYPE_STRING),
                'telephone_locataire': openapi.Schema(type=openapi.TYPE_STRING),
                'surface_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_parking_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'adresse_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'code_postal_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'ville_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'adresse_complementaire_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_cave_propriete' : openapi.Schema(type=openapi.TYPE_STRING),
                'numero_sol_propriete' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'ref_lot' : openapi.Schema(type=openapi.TYPE_STRING),
                'ref_edl' : openapi.Schema(type=openapi.TYPE_STRING),
                'intervention' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'client' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'date' : openapi.Schema(type=openapi.TYPE_STRING),
                'statut' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'passeur' : openapi.Schema(type=openapi.TYPE_INTEGER),
                'agent': openapi.Schema(type=openapi.TYPE_INTEGER),
                'longitude':openapi.Schema(type=openapi.TYPE_STRING),
                'latitude':openapi.Schema(type=openapi.TYPE_STRING),
                'type_propriete': openapi.Schema(type=openapi.TYPE_INTEGER),
                'type': openapi.Schema(type=openapi.TYPE_STRING),
                'consignes_part': openapi.Schema(type=openapi.TYPE_STRING),
                'list_documents': openapi.Schema(type=openapi.TYPE_STRING),
                'info_diverses': openapi.Schema(type=openapi.TYPE_STRING),
            },
         ),
        manual_parameters=[token_param])
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

        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Audit planneur" and  role['user']['group'] != "Administrateur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier" and role['user']['group'] != "Salarie":
            return JsonResponse({"status":"insufficient privileges"},status=401)

        url_ = URLRDV

        final_=[]
        try:
            rdvs = requests.put(URLRDV+str(id),data=self.request.data).json()[0]
        except ValueError:
            return JsonResponse({"status":"failure to update data"},status=401) 

        rdvs = requests.get(URLRDV+str(rdvs['id']))
        data = request.data
        try:
            for rdv in rdvs.json():
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client'])+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent'] is not None:
                    id_f = str(rdv['agent']).split(".")[0]
                    rdv['agent'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent_constat'] is not None:
                    id_f = str(rdv['agent_constat']).split(".")[0]
                    rdv['agent_constat'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['audit_planneur'] is not None:
                    id_f = str(rdv['audit_planneur']).split(".")[0]
                    rdv['audit_planneur'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['passeur'] is not None:
                    rdv['passeur'] = requests.get(URLSALARIE+"?specific=t"+str(rdv['passeur']),headers={"Authorization":"Bearer "+token}).json()
                final_.append(rdv)
        except ValueError:
                return JsonResponse({"status":"failure to get data"},status=401)
        mail = {}
        #Gestion des mails
        yourdate_ = datetime.strptime(rdv['date'],"%Y-%m-%dT%H:%M:%SZ")
        if request.POST.get("status",None) is not None:
            if data['status'] == "CHANGEMENT DE STATUT":
                mail['client'] = rdv['client']['user']['nom']+" "+rdv['client']['user']['prenom']
                mail['status'] = data['status']
                mail['intervention'] = rdv["intervention"]["type"]
                mail['new'] = int(rdv["statut"])
                mail['date'] = str(yourdate_.day)+"/"+str(yourdate_.month)+"/"+str(yourdate_.year)
                mail['users'] = [rdv['client']['user']['email'].split('/')[0],rdv['agent']['user']['email'].split('/')[0]]

            if data['status'] == "CONFIRMATION HORAIRES":
                mail['client'] = rdv['client']['user']['nom']+" "+rdv['client']['user']['prenom']
                mail['status'] = data['status']
                mail['intervention'] = rdv["intervention"]["type"]
                mail['date'] = str(yourdate_.day)+"/"+str(yourdate_.month)+"/"+str(yourdate_.year)
                mail['heure'] = str(yourdate_.hour)+"H"+str(yourdate_.min)
                mail['users'] = [rdv['client']['user']['email'],rdv['agent']['user']['email'].split('/')[0]]

            if data['status'] == "AFFECTATION AGENT SECTEUR":
                mail['client'] = rdv['client']['user']['nom']+" "+rdv['client']['user']['prenom']
                mail['status'] = data['status']
                mail['intervention'] = rdv["intervention"]["type"]
                mail['date'] = str(yourdate_.day)+"/"+str(yourdate_.month)+"/"+str(yourdate_.year)
                mail['agent1'] = rdv['agent_constat']['user']['nom']+" "+rdv['agent_constat']['user']['prenom'] 
                mail['agent2'] = rdv['audit_planneur']['user']['nom']+" "+rdv['audit_planneur']['user']['prenom']  
                mail['users'] = [rdv['audit_planneur']['user']['email'].split('/')[0],rdv['agent_constat']['user']['email'].split('/')[0],rdv['client']['user']['email'],rdv['agent']['user']['email'].split('/')[0]]

        else:
            liste_gar = [rdv['client']['user']['email'],rdv['agent']['user']['email'].split('/')[0],]
            mail['client'] = rdv['client']['user']['nom']+" "+rdv['client']['user']['prenom']
            mail['status'] = "MODIFICATION"
            mail['intervention'] = rdv["intervention"]["type"]
            mail['ref'] = rdv["ref_rdv_edl"]
            mail['AS'] = rdv["agent"]["user"]['nom']+' '+rdv["agent"]["user"]['prenom']
            mail['date'] = str(yourdate_.day)+"/"+str(yourdate_.month)+"/"+str(yourdate_.year)
            if rdv['audit_planneur'] is not None:
                mail['AP'] = rdv["audit_planneur"]["user"]['nom']+' '+rdv["audit_planneur"]["user"]['prenom']
                liste_gar.append(rdv['audit_planneur']['user']['email'].split('/')[0]) 
            else:
                mail['AP'] = None
            if rdv['agent_constat'] is not None:
                mail['AC'] = rdv["agent_constat"]["user"]['nom']+' '+rdv["agent_constat"]["user"]['prenom']
                liste_gar.append(rdv['agent_constat']['user']['email'].split('/')[0]) 
            else:
                mail['AC'] = None
            mail['users'] = liste_gar

        requests.post(URLEMAIL,json=mail,params=self.request.query_params).json()
        return Response(final_,status=status.HTTP_201_CREATED)

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

        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Administrateur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier":
            return JsonResponse({"status":"insufficient privileges"},status=401)

        url_ = URLRDV

        try:
            rdvs = requests.delete(URLRDV+str(id)).json()
            return JsonResponse({"status":"done"},status=200)
        except ValueError:
            return JsonResponse({"status":"failure"},status=401)


class importRdvApi(APIView):
    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param])
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

        #contrôle des roles
        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Administrateur" :
            return JsonResponse({"status":"insufficient privileges"},status=401)
            
        """final_=[]
        tmp={} 
        try:
            agents = requests.get(URLAGENT+"?paginated=t",headers={"Authorization":"Bearer "+token}).json()
        except:
            pass
        for ag in agents:
            tmp={
                "user": ag['user']['id'],
                "agent": ag['id']
            }
            final_.append(tmp)
        #return JsonResponse({"ag":final_},status=200)"""

        try:
            #data = request.data
            file = {'fichier': request.FILES["fichier"]}
            rdvs = requests.post(URLRDVIMPORT,files=file,data={"cible":3}).json() 
        except KeyError:
            return JsonResponse({"status":"failure to post data"}) 
        return Response(rdvs,status=status.HTTP_201_CREATED)

class commentaireApi(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)
    rdv = openapi.Parameter('rdv', in_=openapi.IN_QUERY ,description="Commentaires des RDV" ,type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[token_param,rdv])
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

        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Salarie" and   role['user']['group'] != "Administrateur" and role['user']['group'] != "Audit planneur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier":
            return JsonResponse({"status":"insufficient privileges"},status=401)

        final_=[]
        data = request.data
        try:
            comments = requests.get(URLALLCOMMENT,params=request.query_params).json()
            for com in comments['comment']:
                com['user'] = requests.get(URLUSERS+str(com["user_id"]),params=request.query_params).json()[0]
                final_.append(com)
            return Response(final_,status=status.HTTP_201_CREATED)  
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

        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Audit planneur" and  role['user']['group'] != "Salarie" and  role['user']['group'] != "Administrateur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier":
            return JsonResponse({"status":"insufficient privileges"},status=401)
        #final_=[]
        data=request.data
        try:
            #var = 10
            #pass
            comments = requests.post(URLADDCOMMENT,json=self.request.data,params=request.query_params,headers={"Authorization":"Bearer "+token}).json()
            #return Response(comments,status=status.HTTP_201_CREATED)
        except ValueError:
            #pass
            return JsonResponse({"status":"failure"},status=401)
        url_ = URLRDV
        url_ = URLRDV+str(data['rdv'])
        rdvs = requests.get(url_,params=self.request.query_params)

        try:
            for rdv in rdvs.json():
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client'])+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent'] is not None:
                    id_f = str(rdv['agent']).split(".")[0]
                    rdv['agent'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent_constat'] is not None:
                    id_f = str(rdv['agent_constat']).split(".")[0]
                    rdv['agent_constat'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['audit_planneur'] is not None:
                    id_f = str(rdv['audit_planneur']).split(".")[0]
                    rdv['audit_planneur'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['passeur'] is not None:
                    id_f = str(rdv['passeur']).split(".")[0]
                    rdv['passeur'] = requests.get(URLSALARIE+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()
            
            yourdate_ = datetime.strptime(rdv['date'],"%Y-%m-%dT%H:%M:%SZ")
            liste_gar = [rdv['client']['user']['email'],rdv['agent']['user']['email'].split('/')[0],]
            mail = {
                "client": rdv['client']['user']['nom']+" "+rdv['client']['user']['prenom'],
                "status":"COMMENT",
                "type":rdv["intervention"]["type"],
                "date":str(yourdate_.day)+"/"+str(yourdate_.month)+"/"+str(yourdate_.year),
            }
            if rdv["agent_constat"] is not None:
                liste_gar.append(rdv['agent_constat']['user']['email'].split('/')[0]) 
            
            if rdv["audit_planneur"] is not None:
                liste_gar.append(rdv['audit_planneur']['user']['email'].split('/')[0]) 
            mail['users'] = liste_gar
            
            requests.post(URLEMAIL,json=mail,params=self.request.query_params).json()
        except ValueError:
                return JsonResponse({"status":"failure"},status=401) 
        return Response(mail,status=status.HTTP_201_CREATED)

            
class documentAPI(APIView):

    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)
    rdv = openapi.Parameter('rdv', in_=openapi.IN_QUERY ,description="Commentaires des RDV" ,type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[token_param,rdv])
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

        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if  role['user']['group'] != "Salarie" and role['user']['group'] != "Administrateur" and role['user']['group'] != "Audit planneur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier":
            return JsonResponse({"status":"insufficient privileges"},status=401)
        final_=[]
        try:
            
            docs = requests.get(URLALLFILES,params=request.query_params).json()
            for com in docs['document']:
                com['user'] = requests.get(URLUSERS+str(com["user_id"]),params=request.query_params).json()[0]
                final_.append(com)
            return Response(docs,status=status.HTTP_201_CREATED)
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

        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if role['user']['group'] != "Audit planneur" and  role['user']['group'] != "Salarie" and role['user']['group'] != "Administrateur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier":
            return JsonResponse({"status":"insufficient privileges"},status=401)
        #final_=[]
        data = request.data
        #try:
        file = {'fichier': request.FILES["fichier"]}
        comments = requests.post(URLADDFILE,files=file,data={'user':data['user'],'type':data['type'],'rdv':data['rdv'],'comment':data['comment']},headers={"Authorization":"Bearer "+token}).json()
            #return Response(comments,status=status.HTTP_201_CREATED)
        #except ValueError:
            #return JsonResponse({"status":"failure"},status=401)

        url_ = URLRDV
        url_ = URLRDV+str(data['rdv'])
        rdvs = requests.get(url_,params=self.request.query_params)

        try:
            for rdv in rdvs.json():
                rdv['client'] = requests.get(URLCLIENT+str(rdv['client'])+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent'] is not None:
                    id_f = str(rdv['agent']).split(".")[0]
                    rdv['agent'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['agent_constat'] is not None:
                    id_f = str(rdv['agent_constat']).split(".")[0]
                    rdv['agent_constat'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['audit_planneur'] is not None:
                    id_f = str(rdv['audit_planneur']).split(".")[0]
                    rdv['audit_planneur'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                if rdv['passeur'] is not None:
                    id_f = str(rdv['passeur']).split(".")[0]
                    rdv['passeur'] = requests.get(URLSALARIE+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()
            
            yourdate_ = datetime.strptime(rdv['date'],"%Y-%m-%dT%H:%M:%SZ")
            liste_gar = [rdv['client']['user']['email'],rdv['agent']['user']['email'].split('/')[0],]
            mail = {
                "client": rdv['client']['user']['nom']+" "+rdv['client']['user']['prenom'],
                "status":"DOCUMENT",
                "type":rdv["intervention"]["type"],
                "date":str(yourdate_.day)+"/"+str(yourdate_.month)+"/"+str(yourdate_.year),
            }
            if rdv["agent_constat"] is not None:
                liste_gar.append(rdv['agent_constat']['user']['email'].split('/')[0]) 
            
            if rdv["audit_planneur"] is not None:
                liste_gar.append(rdv['audit_planneur']['user']['email'].split('/')[0]) 
            mail['users'] = liste_gar

            requests.post(URLEMAIL,json=mail,params=self.request.query_params).json()
        except ValueError:
                return JsonResponse({"status":"failure"},status=401) 
        return Response(mail,status=status.HTTP_201_CREATED)

class TriRdvApi(APIView):
    token_param = openapi.Parameter('Authorization', in_=openapi.IN_HEADER ,description="Token for Auth" ,type=openapi.TYPE_STRING)
    rdv = openapi.Parameter('rdv', in_=openapi.IN_QUERY ,description="Commentaires des RDV" ,type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[token_param,rdv])
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

        role = checkRole(token)
        if role == -1:
            return JsonResponse({"status":"No roles"},status=401) 

        if  role['user']['group'] != "Salarie" and role['user']['group'] != "Administrateur" and role['user']['group'] != "Audit planneur" and role['user']['group'] != "Agent constat" and role['user']['group'] != "Agent secteur" and role['user']['group'] != "Client pro" and role['user']['group'] != "Client particulier":
            return JsonResponse({"status":"insufficient privileges"},status=401)
        final_=[]
        finaly_={}
        try:
            rdvs = requests.get(URLTRIAPP,data=request.data,params=request.query_params)
            for rdv in rdvs.json()['results']:
                try:
                    rdv['client'] = requests.get(URLCLIENT+str(rdv['client'])+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                    if rdv['agent'] is not None:
                        id_f = str(rdv['agent']).split(".")[0]
                        rdv['agent'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                    if rdv['agent_constat'] is not None:
                        id_f = str(rdv['agent_constat']).split(".")[0]
                        rdv['agent_constat'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                    if rdv['audit_planneur'] is not None:
                        id_f = str(rdv['audit_planneur']).split(".")[0]
                        rdv['audit_planneur'] = requests.get(URLAGENT+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()[0]
                    if rdv['passeur'] is not None:
                        id_f = str(rdv['passeur']).split(".")[0]
                        rdv['passeur'] = requests.get(URLSALARIE+str(id_f)+"?specific=t",headers={"Authorization":"Bearer "+token}).json()
                except ValueError:
                    return JsonResponse({"status":"failure"}) 
                final_.append(rdv)
            finaly_['count'] = rdvs.json()['count']
            finaly_['next'] = rdvs.json()['next']
            finaly_['previous'] = rdvs.json()['previous']
            finaly_['results'] = final_
            return Response(finaly_,status=status.HTTP_200_OK)
        except ValueError:
            return JsonResponse({"status":"failure"},status=401)



