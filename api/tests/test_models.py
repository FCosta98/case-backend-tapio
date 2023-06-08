from django.test import TestCase
from api.models import Report, Source, Modification
from datetime import datetime

class TestModels(TestCase):

    def setUp(self):
        report1 = Report.objects.create(
            name='Report 1',
            date='2020-02-23'
        )
        self.report1 = Report.objects.get()
        self.source_list = []
        source1 = Source.objects.create(
            report = self.report1,
            description = 'Source 1',
            value = 10,
            emission_factor = 2.0,
            total_emission = 1000,
            lifetime = 5,
            acquisition_year = 2020
        )
        self.source1 = Source.objects.get()
        self.source_list = [Source.objects.get()]


    
    def test_source_total_emission_without_modif(self):
        self.assertEquals(self.source1.get_total_emissions(), 1000)
        self.assertEquals(self.source1.get_total_emissions(2021), 220)
        self.assertEquals(self.source1.get_total_emissions(2025), 20)
        self.assertEquals(self.source1.get_total_emissions(2019), 0)
    
    def test_source_total_emission_with_modif_EF(self):
        modif_list = []
        modif1 = Modification.objects.create(
            source = self.source1,
            description = 'modif 1',
            emission_factor = 1,
            total_emission = 60,
            acquisition_year = '2023-02-23',
            lifetime = 3,
        )
        modif_list = [Modification.objects.get()]
        
        self.assertEquals(self.source1.get_total_emissions(2021, modif_list=modif_list), 220)   # source_amo + modif_amo + usage_emission = 200 + 0 + 20
        self.assertEquals(self.source1.get_total_emissions(2023, modif_list=modif_list), 230)   # 200 + 20 + 10
        self.assertEquals(self.source1.get_total_emissions(2025, modif_list=modif_list), 30)    # 0 + 20 + 10
        self.assertEquals(self.source1.get_total_emissions(2026, modif_list=modif_list), 10)    # 0 + 0 + 10

        modif2 = Modification.objects.create(
            source = self.source1,
            description = 'modif 2',
            emission_factor = 3,
            total_emission = 150,
            acquisition_year = '2024-02-23',
            lifetime = 3,
        )
        modif_list.append(Modification.objects.get(description = 'modif 2'))

        self.assertEquals(self.source1.get_total_emissions(2023, modif_list=modif_list), 230)   # 200 + 20 + 10
        self.assertEquals(self.source1.get_total_emissions(2024, modif_list=modif_list), 300)    # 200 + 20 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2026, modif_list=modif_list), 80)    # 0 + 0 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2027, modif_list=modif_list), 30)    # 0 + 0 + 0 + 30
    
    def test_source_total_emission_with_modif_same_year(self):
        modif_list = []
        modif1 = Modification.objects.create(
            source = self.source1,
            description = 'modif 1',
            emission_factor = 1,
            total_emission = 60,
            acquisition_year = '2023-02-23',
            lifetime = 3,
        )
        modif_list = [Modification.objects.get()]

        self.assertEquals(self.source1.get_total_emissions(2021, modif_list=modif_list), 220)   # source_amo + modif_amo + usage_emission = 200 + 0 + 20
        self.assertEquals(self.source1.get_total_emissions(2023, modif_list=modif_list), 230)   # 200 + 20 + 10
        self.assertEquals(self.source1.get_total_emissions(2025, modif_list=modif_list), 30)    # 0 + 20 + 10
        self.assertEquals(self.source1.get_total_emissions(2026, modif_list=modif_list), 10)    # 0 + 0 + 10

        modif2 = Modification.objects.create(
            source = self.source1,
            description = 'modif 2',
            emission_factor = 3,
            total_emission = 150,
            acquisition_year = '2023-02-26',
            lifetime = 3,
        )
        modif_list.append(Modification.objects.get(description = 'modif 2'))
        
        self.assertEquals(self.source1.get_total_emissions(2023, modif_list=modif_list), 300)   # 200 + 20 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2024, modif_list=modif_list), 300)   # 200 + 20 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2025, modif_list=modif_list), 100)   # 0 + 20 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2027, modif_list=modif_list), 30)    # 0 + 0 + 0 + 30

        modif3 = Modification.objects.create(
            source = self.source1,
            description = 'modif 3',
            emission_factor = 3,
            total_emission = 150,
            acquisition_year = '2023-01-26',
            lifetime = 3,
        )
        modif_list.append(Modification.objects.get(description = 'modif 3'))

        self.assertEquals(self.source1.get_total_emissions(2023, modif_list=modif_list), 350)   # 200 + 20 + 50 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2024, modif_list=modif_list), 350)   # 200 + 20 + 50 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2025, modif_list=modif_list), 150)   # 0 + 20 + 50 + 50 + 30
        self.assertEquals(self.source1.get_total_emissions(2027, modif_list=modif_list), 30)    # 0 + 0 + 0 + 30


    def test_source_total_emission_with_modif_ratio(self):
        modif_list = []
        modif1 = Modification.objects.create(
            source = self.source1,
            description = 'modif 1',
            emission_factor = 2.0,
            ratio = 2,
            total_emission = 60,
            acquisition_year = '2023-02-23',
            lifetime = 3,
        )
        modif_list = [Modification.objects.get()]
        
        self.assertEquals(self.source1.get_total_emissions(2021, modif_list=modif_list), 220)   # source_amo + modif_amo + usage_emission = 200 + 0 + 20
        self.assertEquals(self.source1.get_total_emissions(2023, modif_list=modif_list), 260)   # 200 + 20 + 40
        self.assertEquals(self.source1.get_total_emissions(2025, modif_list=modif_list), 60)    # 0 + 20 + 40
        self.assertEquals(self.source1.get_total_emissions(2026, modif_list=modif_list), 40)    # 0 + 0 + 40

    def test_report_total_emission_with_1_source(self):
        self.assertEquals(self.report1.get_total_emissions(sources_list=self.source_list), 1000)
        self.assertEquals(self.report1.get_total_emissions(year=2019, sources_list=self.source_list), 0)
        self.assertEquals(self.report1.get_total_emissions(year=2020, sources_list=self.source_list), 220)
        self.assertEquals(self.report1.get_total_emissions(year=2025, sources_list=self.source_list), 20)


    def test_report_total_emission_with_2_sources(self):
        source2 = Source.objects.create(
            report = self.report1,
            description = 'Source 2',
            value = 30,
            emission_factor = 2.0,
            total_emission = 1000,
            lifetime = 5,
            acquisition_year = 2022
        )
        self.source_list.append(Source.objects.get(description = 'Source 2'))

        self.assertEquals(self.report1.get_total_emissions(sources_list=self.source_list), 2000)
        self.assertEquals(self.report1.get_total_emissions(year=2019, sources_list=self.source_list), 0)
        self.assertEquals(self.report1.get_total_emissions(year=2020, sources_list=self.source_list), 220)  # 200 + 20
        self.assertEquals(self.report1.get_total_emissions(year=2022, sources_list=self.source_list), 480)  # 200 + 200 + 20 + 60
        self.assertEquals(self.report1.get_total_emissions(year=2025, sources_list=self.source_list), 280)  # 0 + 200 + 20 + 60
        self.assertEquals(self.report1.get_total_emissions(year=2027, sources_list=self.source_list), 80)   # 0 + 0 + 20 + 60
    
    def test_source_delta(self):
        modif_list = []
        self.assertEquals(self.source1.get_delta(modif_list=modif_list), 0)
        
        modif1 = Modification.objects.create(
            source = self.source1,
            description = 'modif 1',
            emission_factor = 1,
            total_emission = 60,
            acquisition_year = '2023-02-23',
            lifetime = 3,
        )
        modif_list = [Modification.objects.get()]

        self.assertEquals(self.source1.get_delta(year=2020, modif_list=modif_list), 0)
        self.assertEquals(self.source1.get_delta(modif_list=modif_list), 10)                # amo_modif + (usage_post - usage_prev) = 20 + (10-20)
        self.assertEquals(self.source1.get_delta(year=2024, modif_list=modif_list), 10)     # 20 + (10-20)
        self.assertEquals(self.source1.get_delta(year=2026, modif_list=modif_list), -10)     # 0 + (10-20)

        modif2 = Modification.objects.create(
            source = self.source1,
            description = 'modif 2',
            emission_factor = 3,
            total_emission = 150,
            acquisition_year = '2024-02-26',
            lifetime = 3,
        )
        modif_list.append(Modification.objects.get(description = 'modif 2'))
        
        self.assertEquals(self.source1.get_delta(modif_list=modif_list), 70)            # 50 + (30-10)
        self.assertEquals(self.source1.get_delta(year=2023, modif_list=modif_list), 10) # 20 + (10-20)
        self.assertEquals(self.source1.get_delta(year=2024, modif_list=modif_list), 70) # 50 + (30-10)
        self.assertEquals(self.source1.get_delta(year=2027, modif_list=modif_list), 20) # 0 + (30-10)

    def test_report_delta(self):
        source2 = Source.objects.create(
            report = self.report1,
            description = 'Source 2',
            value = 30,
            emission_factor = 2.0,
            total_emission = 1000,
            lifetime = 5,
            acquisition_year = 2022
        )
        self.source_list.append(Source.objects.get(description = 'Source 2'))

        modif_list = []
        
        modif1 = Modification.objects.create(
            source = self.source1,
            description = 'modif 1',
            emission_factor = 1,
            total_emission = 60,
            acquisition_year = '2023-02-23',
            lifetime = 3,
        )

        modif2 = Modification.objects.create(
            source = source2,
            description = 'modif 2',
            emission_factor = 1,
            total_emission = 60,
            acquisition_year = '2023-04-23',
            lifetime = 3,
        )

        self.assertEquals(self.report1.get_delta(year=2020, sources_list=self.source_list), 0)
        self.assertEquals(self.report1.get_delta(sources_list=self.source_list), 0)                # 20 + (10-20) + 20 + (30-60) 
        self.assertEquals(self.report1.get_delta(year=2024, sources_list=self.source_list), 0)     # 20 + (10-20) + 20 + (30-60) 
        self.assertEquals(self.report1.get_delta(year=2026, sources_list=self.source_list), -40)   # 0 + (10-20) + 0 + (30-60)