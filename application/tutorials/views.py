from rest_framework import permissions, viewsets
from rest_framework.response import Response

from tutorials.models import TutorialGroup, Tutorial
from tutorials.permissions import IsAdmin
from tutorials.serializers import TutorialGroupSerializer, TutorialSerializer

class TutorialGroupViewSet(viewsets.ModelViewSet):
    queryset = TutorialGroup.objects.all()
    serializer_class = TutorialGroupSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsAdmin(),)

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        return super(TutorialGroupViewSet, self).perform_create(serializer)

class TutorialViewSet(viewsets.ModelViewSet):
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsAdmin(),)

    def list(self, request, tutorialgroup_pk=None):
        queryset = self.queryset.filter(t_group__id=tutorialgroup_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        return super(TutorialViewSet, self).perform_create(serializer)
