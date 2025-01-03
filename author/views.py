from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import RegistrationSerializer,AuthorLoginSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from rest_framework.authtoken.models import Token
from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from match.models import Match
from match.serializers import MatchSerializer
from author.models import Author
import environ
env = environ.Env()
environ.Env.read_env()


class RegistrationView(APIView):
    serializer_class = RegistrationSerializer
    def post(self,request,format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirmation_link = f"{env('CONFIRMATION_URL')}author/active/{uid}/{token}"
            email_subject = "Email Confirmation Link"
            email_body = render_to_string('email_confirmation.html',{'confirmation_link':confirmation_link,"user":user})
            email = EmailMultiAlternatives(email_subject,'',to=[user.email])
            email.attach_alternative(email_body,"text/html")
            email.send()
            return Response({"Success":"Please check your mail for confirmation"})
        return Response(serializer.errors,status=404)
def activate(request,uid64,token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        return redirect(f"{env('REDIRECT_FROM_REGISTER')}login")
    else:
        return redirect(f"{env('REDIRECT_FROM_REGISTER')}register")

class AuthorLoginApiView(APIView):
    serializer_class = AuthorLoginSerializer

    def post(self,request,*args,**kwargs):
        serializer = AuthorLoginSerializer(data=self.request.data)
        if serializer.is_valid():
            username=serializer.validated_data['username']
            password=serializer.validated_data['password']

            user = authenticate(username=username,password=password)
            if user:
                token,_ = Token.objects.get_or_create(user=user)
                login(request,user)
                return Response({'Token':token.key,'user_id':user.id,'author_id':user.author.id})
            else:
                return Response({"Error":"Invalid Credential!"})
        return Response(serializer.errors)
    
class AuthorLogoutApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user
        if isinstance(user,AnonymousUser):
            return Response({"error":"User is not logged in."},status=400)
        if hasattr(user,'auth_token'):
            user.auth_token.delete()
        logout(request)
        return Response({"Success":"Logout Success"})
    

class GoogleLogin(APIView):
       def post(self, request):
        token = request.data.get('access_token', None)
        if not token:
            return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            request_obj = Request()
            idinfo = id_token.verify_oauth2_token(
                token,
                request_obj,
                env("CLIENT_ID")
            )
            email = idinfo.get('email')
            first_name = idinfo.get('given_name')
            last_name = idinfo.get('family_name')
            username = email.split('@')[0]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
            if user is not None:
                token,_ = Token.objects.get_or_create(user=user)
                login(request,user)
                return Response({'Token':token.key,'user_id':user.id,'author_id':user.author.id}) 
            else:
                new_user = User.objects.create(username=username,email=email,first_name=first_name,last_name=last_name)
                new_author = Author.objects.create(user=new_user)
                token,_ = Token.objects.get_or_create(user=new_user)
                login(request,new_user)
                return Response({'Token':token.key,'user_id':new_user.id,'author_id':new_user.author.id})
        except ValueError as e:
            return Response({'error': 'Invalid token', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class GetAllMatchs(APIView):
    serializer_class = MatchSerializer
    def get(self,request,author_id,*args,**kwargs):
        all_matches = Match.objects.filter(author__id=author_id)
        serializer = self.serializer_class(all_matches,many=True)
        return Response({"all_matches":serializer.data})