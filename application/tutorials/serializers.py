from rest_framework import serializers
from tutorials.models import TutorialGroup, Tutorial


class TutorialGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorialGroup

        fields = ('id', 'title', 'info', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(TutorialGroupSerializer, self).get_validation_exclusions()
        return exclusions

class TutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial

        fields = ('id', 't_group', 'title', 'url', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(TutorialSerializer, self).get_validation_exclusions()

        return exclusions + ['t_group']
