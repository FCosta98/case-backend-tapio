from django.db import models

class Report(models.Model): 
    """
        The Report is the sum of all the emissions. It should be done once a year.
        With each report we provide differents reduction strategies
        {
            "name": "report 1",
            "date": 15-02-2020
        }
    """
    name = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return self.name
    
    def get_total_emissions(self, year=None, sources_list=None):
        """
            Get the total emissions for this report.

            If a year is specified, return the total emissions for that year
            (taking into account the lifetimes of sources).
        """
        total_emissions = 0
        for source in sources_list:
            modif_list = Modification.objects.filter(source=source)
            print("Total emission source :", source.description, " : ", source.get_total_emissions(year=year, modif_list=modif_list))
            total_emissions += source.get_total_emissions(year=year, modif_list=modif_list)
        return total_emissions
    
    def get_delta(self, year=None, sources_list=None):
        """
            Get the total delta for this report.
        """
        total_delta = 0
        for source in sources_list:
            modif_list = Modification.objects.filter(source=source)
            print("Delta source :", source.description, " : ", source.get_delta(year=year, modif_list=modif_list))
            total_delta += source.get_delta(year=year, modif_list=modif_list)
        return total_delta

class Source(models.Model): 
    """
        An Emission is every source that generates GreenHouse gases (GHG).
        It could be defined as source x emission_factor = total
        {
            "report":  4,
            "description": "Voiture thermique",
            "value": 1,
            "emission_factor": 8.95,
            "total_emission": 20000,
            "lifetime": 5,
            "acquisition_year": 2020
        }
    """
    report = models.ForeignKey(Report, on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    emission_factor = models.FloatField(blank=True, null=True)
    total_emission = models.FloatField(blank=True, null=True, help_text="Unit in kg")
    lifetime = models.PositiveIntegerField(blank=True, null=True)
    acquisition_year = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.description
    
    def get_total_emissions(self, year=None, modif_list=None):
        """
            Get the total emissions for this source.

            If a year is specified, return the total emissions for that year
            (taking into account the lifetime of the source).
        """
        modif = self.get_updated_usage_emission(year, modif_list)
        updated_usage_emission = (self.emission_factor * self.value) if modif is None else ( modif.emission_factor * modif.value) 
        usage_emission = updated_usage_emission
        modif_amortization_emission = self.get_modif_emission(year, modif_list)

        if year is None:
            return self.total_emission + modif_amortization_emission
        else:
            years_since_acquisition = year - self.acquisition_year
            if years_since_acquisition < 0:
                return 0
            elif years_since_acquisition >= self.lifetime:
                return 0 + usage_emission + modif_amortization_emission
            else:
                return (self.total_emission / self.lifetime) + usage_emission + modif_amortization_emission
    
    def get_modif_emission(self, year=None, modif_list=None):
        """
            Return the total emission coming from the captital goods amortization from the modification of the source.
            The total is calculated for a specific year. 
            If there is no year specified, the function returns the total of emission without amortization.
        """
        if modif_list is None:
            return 0

        total_emissions = 0
        for modif in modif_list:
            print("MODIF EMISSION :", modif.get_total_emissions(year=year))
            total_emissions += modif.get_total_emissions(year=year)
        return total_emissions
    
    def get_updated_usage_emission(self, year=None, modif_list=None):
        """
            Returns the element in `modif_list` whose `acquisition_year` field value is equal to `year`.
            If there is no such element, returns the closest element whose `acquisition_year`
            field value is lower than `year`.
        """
        if year is None or modif_list is None:
            return None
        
        closest_item = None
        closest_year_diff = float('inf')
        for item in modif_list:
            item_year = item.acquisition_year
            if item_year is not None:
                year_diff = year - item_year
                if year_diff == 0:
                    return item
                elif year_diff > 0 and year_diff < closest_year_diff:
                    closest_item = item
                    closest_year_diff = year_diff
        
        return closest_item


    def get_delta(self, year=None,  modif_list=None):
        """
            Returns the difference in emissions between a report's total emissions before and after its last modification for a specific year.
        """
        if year == self.acquisition_year or modif_list is None or len(modif_list)==0 :
            return 0
        
        total_before = self.get_total_emissions(year, modif_list)
        total_after = total_before

        if year is None:
            max_date_item = max(modif_list, key=lambda x: x.acquisition_year)
            new_list = [item for item in modif_list if item != max_date_item]
            total_before = self.get_total_emissions(modif_list=new_list)
            return total_after - total_before
            
        
        while total_before == total_after and year>self.acquisition_year:
            year -=1
            total_before = self.get_total_emissions(year, modif_list)
        
        print("BEFORE :", total_before, "AFTER :", total_after)
        return  total_after - total_before

class Modification(models.Model):
    """
        {
            "description": "voiture electrique",
            "ratio": 1.0,
            "emission_factor": 3.98,
            "total_emission": 20000.0,
            "value": 1.0,
            "acquisition_year": 2020,
            "lifetime": 5,
            "source": 5
        }
    """

    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, blank=True, null=True)
    ratio = models.FloatField(default=1)
    emission_factor = models.FloatField(blank=True, null=True)
    total_emission = models.FloatField(blank=True, null=True, help_text="Unit in kg")
    value = models.FloatField(blank=True, null=True)
    acquisition_year = models.PositiveSmallIntegerField(blank=True, null=True)
    lifetime = models.PositiveIntegerField(blank=True, null=True)

    def get_total_emissions(self, year=None):
        """
            Get the total emissions for this modification.
        """
        if year is None:
            return self.total_emission
        else:
            years_since_acquisition = year - self.acquisition_year
            if years_since_acquisition < 0:
                return 0 
            elif years_since_acquisition >= self.lifetime:
                return 0
            else:
                return (self.total_emission / self.lifetime)