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


class RegistrationView(APIView):
    serializer_class = RegistrationSerializer
    def post(self,request,format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirmation_link = f"https://cricketscorer.vercel.app/author/active/{uid}/{token}"
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
        return redirect('https://ph-cricket-scorer.netlify.app/login')
    else:
        return redirect('https://ph-cricket-scorer.netlify.app/register')

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
        print(user)
        if isinstance(user,AnonymousUser):
            return Response({"error":"User is not logged in."},status=400)
        if hasattr(user,'auth_token'):
            print("has_auth")
            user.auth_token.delete()
        logout(request)
        return Response({"Success":"Logout Success"})