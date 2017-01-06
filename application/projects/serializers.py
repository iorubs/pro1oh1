from rest_framework import serializers
from authentication.models import Account
from authentication.serializers import AccountSerializer
from projects.models import Project, File


class ProjectSerializer(serializers.ModelSerializer):
    author = AccountSerializer(read_only=True, required=False)

    class Meta:
        model = Project

        fields = ('id', 'author', 'title', 'p_type', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(ProjectSerializer, self).get_validation_exclusions()
        return exclusions + ['author']

class RecursiveFiles(serializers.Serializer):
    def to_native(self, value):
            return self.parent.to_native(value)

class FileSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True, required=False)
    folder = RecursiveFiles(read_only=True, required=False)

    class Meta:
        model = File

        fields = ('id', 'project', 'folder', 'title', 'f_type', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(FileSerializer, self).get_validation_exclusions()

        return exclusions + ['project']
