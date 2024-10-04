from calendar import calendar

from django.conf import settings
from djoser.social.views import ProviderAuthView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
import re
import requests
from bs4 import BeautifulSoup
from users.models import UserAccount
from users.permissions import AdminToStudent
from users.serializers import UserAccountSerializer


class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response


@api_view(['GET'])
@permission_classes([AdminToStudent])
def get_user_by_id(request):
    user_id = request.GET.get('user_id')
    user = UserAccount.objects.get(id=user_id)
    serializer = UserAccountSerializer(user, many=False)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_calendar(req):
    url = 'https://www.uiu.ac.bd/academics/calendar/'
    data = []

    try:
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        print("Successfully fetched the webpage!")

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        calendar_items = soup.find_all('div')

        # Navigate to the relevant section
        cal = calendar_items[0].find_next(class_='calender-table').find_next(class_='calender-table')
        table = cal.find_next('table').find_next('tbody').find_all('tr')

        # Extract data from the table rows
        for row in table:
            date = row.find_all('td')[0].get_text(strip=True)
            day = row.find_all('td')[1].get_text(strip=True)
            details = row.find_all('td')[2].get_text()

            # Replace multiple newlines with a single newline and remove extra spaces
            details = re.sub(r'\s*\n\s*', '\n', details).strip()

            data.append({
                'date': date,
                'day': day,
                'details': details,
            })

    except requests.RequestException as e:
        print(f"HTTP error: {e}")
        return Response({"error": "Failed to retrieve the webpage."}, status=500)
    except IndexError:
        print("Error: Unexpected HTML structure.")
        return Response({"error": "Failed to retrieve the data."}, status=500)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({"error": "An unexpected error occurred."}, status=500)

    return Response({"calendar": data})



@api_view(['GET'])
@permission_classes([AllowAny])
def get_notice(req):
    url = 'https://www.uiu.ac.bd/notice/'
    data = []

    try:
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        print("Successfully fetched the webpage!")

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        notice_grid = soup.find('div', {"id": "notice-container"})
        notices = notice_grid.find_all('div', class_='notice')

        # Extract data from the table rows
        for notice in notices:
            date = notice.find_next('span', class_='date').getText(strip=True)
            a = notice.find_next('a')
            title = a.getText(strip=True)
            link = a.get('href')
            data.append({
                'date': date,
                'title': title,
                'link': link,
            })

    except requests.RequestException as e:
        print(f"HTTP error: {e}")
        return Response({"error": "Failed to retrieve the webpage."}, status=500)
    except IndexError:
        print("Error: Unexpected HTML structure.")
        return Response({"error": "Failed to retrieve the data."}, status=500)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({"error": "An unexpected error occurred."}, status=500)

    return Response({"notices": data})
