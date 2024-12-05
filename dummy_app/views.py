from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class DummyView(APIView):
    def get(self, request):
        return Response({}, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        return Response({}, status=status.HTTP_201_CREATED)