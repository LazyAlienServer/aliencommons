from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import ListFrontendLogSerializer


class FrontendLogCreateView(generics.GenericAPIView):
    serializer_class = ListFrontendLogSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logs = serializer.save()
        return Response({"count": len(logs)}, status=status.HTTP_201_CREATED)
