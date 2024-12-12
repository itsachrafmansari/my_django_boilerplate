from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Dummy
from .serializers import DummySerializer


class DummyView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):

        if pk:
            try:
                queryset = Dummy.objects.get(id=pk)
                serializer = DummySerializer(queryset)
                return Response(serializer.data)
            except Dummy.DoesNotExist:
                return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            objects = Dummy.objects.all()
            serializer = DummySerializer(objects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if isinstance(request.data, list):
            serializer = DummySerializer(data=request.data, many=True)
        else:
            serializer = DummySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if pk:
            try:
                obj = Dummy.objects.get(id=pk)
                obj.delete()
            except Dummy.DoesNotExist:
                return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Missing 1 expected parameter PK'}, status=status.HTTP_400_BAD_REQUEST)

class DummyViewProtected(DummyView):
    permission_classes = (IsAuthenticated,)
