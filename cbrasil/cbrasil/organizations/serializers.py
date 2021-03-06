from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.contrib.auth.models import User as DjangoUser

from rest_framework import serializers

from cbrasil.organizations.models import Sectors, Organizations
from cbrasil.places.serializers import NestedCitiesSerializer, NestedRegionsSerializer
from cbrasil.news.models import Events
from cbrasil.news.serializers import NestedNewsSerializer


class OrganizationsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Organizations
        fields = '__all__'

class SectorsSerializer(serializers.ModelSerializer):
    total_estimated_impact = serializers.IntegerField(read_only=True)
    events_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sectors
        fields = ['id', 'total_estimated_impact', 'name', 'events_count']

class NestedOrganizationsSerializer(OrganizationsSerializer):
    
    def get_field_names(self, declared_fields, info):
        return ['name']


class AuthorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = DjangoUser
        fields = ['name']

    def get_name(self, obj):
        if obj.first_name != '' and obj.last_name != '':
            return "{} {}".format(obj.first_name, obj.last_name)
        elif obj.first_name != '':
            return obj.first_name
        else:
            return None

class EventsSerializer(serializers.ModelSerializer):

    source = NestedNewsSerializer()
    region = NestedRegionsSerializer()
    city = NestedCitiesSerializer()
    organization = NestedOrganizationsSerializer()
    author = AuthorSerializer()
    
    class Meta:
        model = Events
        fields = '__all__'

class SectorEventsSerializer(SectorsSerializer):
    events = serializers.SerializerMethodField()

    def get_field_names(self, declared_fields, info):
        return ['id', 'name', 'events']

    def to_representation(self, instance):
        fields = super().to_representation(instance)
        return fields

    def get_events(self, obj):
        region__initial = self.context.get('request').query_params.get('region__initial', None)
        events = obj.events.filter(Q(Q(region__initial=region__initial) | Q(city__region__initial=region__initial))) if region__initial else obj.events.all()
        serializer = EventsSerializer(instance=events[:5], many=True)

        return serializer.data






