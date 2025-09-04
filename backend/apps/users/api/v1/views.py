from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from ...models import Customer
from .serializers import RegisterInSerializer, LoginInSerializer, CustomerOutSerializer, UserSerializer
from apps.users.services.jwt_utils import create_jwt_token, decode_jwt_token

User = get_user_model()


@extend_schema(request=RegisterInSerializer, responses={201: CustomerOutSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cust = serializer.create(serializer.validated_data)
    # issue JWT
    token = create_jwt_token(cust.CustomerID)
    out = CustomerOutSerializer(cust).data
    return Response({'user': out, 'token': token}, status=status.HTTP_201_CREATED)


@extend_schema(request=LoginInSerializer, responses={200: OpenApiResponse(response=CustomerOutSerializer)})
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        cust = Customer.objects.get(Email=data['email'])
    except Customer.DoesNotExist:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    pwd_ok = False
    # support both Django hashed passwords and legacy plaintext
    try:
        pwd_ok = check_password(data['password'], cust.PasswordHash)
    except Exception:
        # fallback: direct compare (legacy plaintext)
        if data['password'] == cust.PasswordHash:
            pwd_ok = True

    if not pwd_ok:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    # upgrade legacy plaintext to hashed password if needed
    if not cust.PasswordHash.startswith('pbkdf2_') and not cust.PasswordHash.startswith('argon2$'):
        cust.PasswordHash = make_password(data['password'])
        cust.save()

    # issue JWT
    token = create_jwt_token(cust.CustomerID)

    # set session for backward compatibility
    if not request.session.session_key:
        request.session.create()
    request.session['customer_id'] = cust.CustomerID

    out = CustomerOutSerializer(cust)
    return Response({'user': out.data, 'token': token})


@extend_schema(responses={204: OpenApiResponse(description='No Content')})
@api_view(['POST'])
def logout_view(request):
    try:
        del request.session['customer_id']
    except KeyError:
        pass
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses={200: CustomerOutSerializer, 204: OpenApiResponse(description='No user in session')})
@api_view(['GET'])
def me(request):
    # Try JWT first from Authorization header
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if auth.startswith('Bearer '):
        token = auth.split(' ', 1)[1]
        payload = decode_jwt_token(token)
        if payload and payload.get('sub'):
            cid = payload.get('sub')
            try:
                cust = Customer.objects.get(CustomerID=cid)
            except Customer.DoesNotExist:
                return Response(None, status=status.HTTP_200_OK)
            out = CustomerOutSerializer(cust)
            return Response(out.data)

    # fallback to session
    cid = request.session.get('customer_id')
    if not cid:
        return Response(None, status=status.HTTP_200_OK)
    try:
        cust = Customer.objects.get(CustomerID=cid)
    except Customer.DoesNotExist:
        return Response(None, status=status.HTTP_200_OK)
    out = CustomerOutSerializer(cust)
    return Response(out.data)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
