from rest_framework import serializers
from .models import Report, Source, Modification

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('__all__')


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('__all__')

class ModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modification
        fields = ('__all__')