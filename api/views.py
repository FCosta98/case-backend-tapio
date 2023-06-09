from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Report, Source, Modification
from .serializers import ReportSerializer, SourceSerializer, ModificationSerializer

class ReportList(APIView):
    def get(self, request, *args, **kwargs):
        '''
            List all the Report items
        '''
        reports = Report.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response({"Reports : ":serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        '''
            Create the Report with given data
        '''
        data = {
            'name': request.data.get('name'),
            'date': request.data.get('date'),
        }
        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Report created : ": serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"Report error : ": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ReportDetail(APIView):

    def get(self, request, report_id, *args, **kwargs):
        instance = Report.objects.filter(id=report_id).first()
        if instance is None:
            return Response({"Report doesn't exist"})

        sources = Source.objects.filter(report=report_id)
        
        year = int(request.query_params.get('year')) if request.query_params.get('year') is not None else None
        total_emission = instance.get_total_emissions(year, sources)
        delta = instance.get_delta(year, sources)

        list_of_emission = {year: total_emission}
        if year is not None:
            to = int(request.query_params.get('to')) if request.query_params.get('to') is not None else None
            if to is not None and to > year:
                for i in range(year+1, to+1):
                    list_of_emission[i] = instance.get_total_emissions(i, sources)

        serializer = ReportSerializer(instance)
        sources_serializer = SourceSerializer(sources, many=True)

        return Response(
            {
                "Report ": serializer.data, 
                "Sources ": sources_serializer.data, 
                "Total Emission ": total_emission,
                "Delta ": delta,
                "List of emission ": list_of_emission
            }, 
            status=status.HTTP_200_OK
        )
    
    def delete(self, request, report_id, *args, **kwargs):
        '''
            Deletes the report item
        '''
        report_instance = Report.objects.get(id=report_id)
        if not report_instance:
            return Response( {"res": "Object with report id does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        report_instance.delete()
        return Response( {"res": "Report deleted!"}, status=status.HTTP_200_OK )

class SourceList(APIView):

    def get(self, request, *args, **kwargs):
        '''
            List all the Source items
        '''
        report = request.query_params.get('report')
        if report is not None:
            sources = Source.objects.filter(report=report)
        else:
            sources = Source.objects.all()
        serializer = SourceSerializer(sources, many=True)
        return Response({"Sources ":serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        '''
            Create the Source with given data
        '''
        data = {
            "description": request.data.get('description'),
            "value": request.data.get('value'),
            "emission_factor": request.data.get('emission_factor'),
            "total_emission": request.data.get('total_emission'),
            "lifetime": request.data.get('lifetime'),
            "acquisition_year": request.data.get('acquisition_year'),
            "report": request.data.get('report')
        }
        serializer = SourceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Source created ": serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"Error ": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class SourceDetail(APIView):

    def get(self, request, source_id, *args, **kwargs):

        source_instance = Source.objects.filter(id=source_id).first()
        if source_instance is None:
            return Response({"Source doesn't exist"})
        
        modif_list = Modification.objects.filter(source=source_id).order_by("acquisition_year")

        year = int(request.query_params.get('year')) if request.query_params.get('year') is not None else None
        total_emission = source_instance.get_total_emissions(year, modif_list)
        delta = source_instance.get_delta(year, modif_list)

        year2 = year if year is not None else "total"
        list_of_emission = {year2: total_emission}
        if year is not None:
            to = int(request.query_params.get('to')) if request.query_params.get('to') is not None else None
            if to is not None and to > year:
                for i in range(year+1, to+1):
                    list_of_emission[i] = source_instance.get_total_emissions(i, modif_list)


        source_serializer = SourceSerializer(source_instance)
        modif_serializer = ModificationSerializer(modif_list, many=True)
        
        return Response(
            {
                "Source": source_serializer.data, 
                "Modifications": modif_serializer.data,
                "Total Emission": total_emission,
                "Delta": delta,
                "List of emission": list_of_emission
            }, 
            status=status.HTTP_200_OK
        )

    def post(self, request, source_id, *args, **kwargs):
        '''
            Create a Modification with given data
            {
                "description": "test date",
                "ratio": 2.0,
                "emission_factor": 1.234,
                "total_emission": 15.0,
                "acquisition_year": "2023-09-22",
                "lifetime": 1,
                "source": 101
            }
        '''
        source_instance = Source.objects.get(id=source_id)

        acquisition_year = request.data.get('acquisition_year')
        source_acquisition_year = int(acquisition_year[:4]) 
        if source_acquisition_year < source_instance.acquisition_year:
            return Response({"ERROR: the modification acquisition year cannot be lower than its source acquisition year"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "source": source_id,
            "ratio":  request.data.get('ratio') if request.data.get('ratio') is not None else 1,
            "description": request.data.get('description'),
            "emission_factor": request.data.get('emission_factor') if request.data.get('emission_factor') is not None else source_instance.emission_factor,
            "total_emission": request.data.get('total_emission') if request.data.get('total_emission') is not None else 0,
            "lifetime": request.data.get('lifetime') if request.data.get('lifetime') != None else source_instance.lifetime,
            "acquisition_year": request.data.get('acquisition_year')
        }
        
        serializer = ModificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response({"Modification created ": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, source_id, *args, **kwargs):
        '''
            Deletes the report item
        '''
        source_instance = Source.objects.get(id=source_id)
        if not source_instance:
            return Response( {"res": "Object with report id does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        source_instance.delete()
        return Response( {"res": "Object deleted!"}, status=status.HTTP_200_OK )
