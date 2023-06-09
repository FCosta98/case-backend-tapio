from django.db import models
from datetime import datetime

class Report(models.Model): 
    """
        The Report is the sum of all the emissions. It should be done once a year.
        With each report we provide differents reduction strategies
        {
            "name": "report 2",
            "date": "2023-04-19"
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
        source_ids = [source.id for source in sources_list]
        modif_list = Modification.objects.filter(source__in=source_ids).order_by("acquisition_year")
        for source in sources_list:
            #modif_list = Modification.objects.filter(source=source).order_by("acquisition_year")
            total_emissions += source.get_total_emissions(year=year, modif_list=modif_list.filter(source=source))

        return total_emissions
    
    def get_delta(self, year=None, sources_list=None):
        """
            Get the total delta for this report.
        """
        total_delta = 0
        source_ids = [source.id for source in sources_list]
        modif_list = Modification.objects.filter(source__in=source_ids)
        for source in sources_list:
            #modif_list = Modification.objects.filter(source=source)
            filtered_modif_list=modif_list.filter(source=source).order_by("acquisition_year")
            delta = source.get_delta(year=year, modif_list=filtered_modif_list)
            total_delta += delta
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
        modif_amortization_emission = self.get_modif_amortization_emission(year, modif_list)

        if year is None:
            return self.total_emission + modif_amortization_emission
        else:
            modif = self.get_closest_modif(year, modif_list)
            usage_emission = (self.emission_factor * self.value) if modif is None else ( modif.emission_factor * (modif.ratio * self.value))
            years_since_acquisition = year - self.acquisition_year
            if years_since_acquisition < 0:
                return 0
            elif years_since_acquisition >= self.lifetime:
                return 0 + usage_emission + modif_amortization_emission
            else:
                return (self.total_emission / self.lifetime) + usage_emission + modif_amortization_emission
    
    def get_modif_amortization_emission(self, year=None, modif_list=None):
        """
            Return the total emission coming from the captital goods amortization from the modification of the source.
            The total is calculated for a specific year. 
            If there is no year specified, the function returns the total of emission without amortization.
        """
        if modif_list is None:
            return 0

        total_emissions = 0
        for modif in modif_list:
            total_emissions += modif.get_total_emissions(year=year)
        return total_emissions
    
    def get_closest_modif(self, year=None, modif_list=None):
        """
            Returns the element in `modif_list` whose `acquisition_year` field value is equal to `year`.
            If there is no such element, returns the closest element whose `acquisition_year`
            field value is lower than `year`.
        """
    
        if year is None or modif_list is None:
            return None
        
        modifs_with_year = [modif for modif in modif_list if modif.acquisition_year.year <= year]
        if not modifs_with_year:
            return None
        
        closest_modif = max(modifs_with_year, key=lambda modif: modif.acquisition_year)
        return closest_modif


    def get_delta(self, year=None,  modif_list=None):
        """
            Returns the difference in emissions between a source's total emissions before and after its last modification for a specific year.
        """
        if year == self.acquisition_year or modif_list is None or len(modif_list)<=0 :
            return 0

        if year is None:
            last_modif = modif_list[len(modif_list)-1]
            if len(modif_list)>1:
                before_last_modif = modif_list[len(modif_list)-2]
                usage_emission_delta = (last_modif.emission_factor * (last_modif.ratio * self.value)) - (before_last_modif.emission_factor * (before_last_modif.ratio * self.value))
                amortissement_delta = last_modif.total_emission / last_modif.lifetime
                delta = amortissement_delta + usage_emission_delta
                return delta
            else:
                usage_emission_delta = (last_modif.emission_factor * (last_modif.ratio * self.value)) - (self.emission_factor * self.value)
                amortissement_delta = last_modif.total_emission / last_modif.lifetime
                delta = amortissement_delta + usage_emission_delta
                return delta
        else:
            modifs_with_year = [modif for modif in modif_list if modif.acquisition_year.year <= year]
            if len(modifs_with_year)<=0:
                return 0

            last_modif = modifs_with_year[len(modifs_with_year)-1]
            not_amortized = (year - last_modif.acquisition_year.year) < last_modif.lifetime
            if len(modifs_with_year)>1:
                before_last_modif = modifs_with_year[len(modifs_with_year)-2]
                usage_emission_delta = (last_modif.emission_factor * (last_modif.ratio * self.value)) - (before_last_modif.emission_factor * (before_last_modif.ratio * self.value))
                amortissement_delta = last_modif.total_emission / last_modif.lifetime
                delta = amortissement_delta + usage_emission_delta if not_amortized else usage_emission_delta
                return delta
            else:
                usage_emission_delta = (last_modif.emission_factor * (last_modif.ratio * self.value)) - (self.emission_factor * self.value)
                amortissement_delta = last_modif.total_emission / last_modif.lifetime
                delta = amortissement_delta + usage_emission_delta if not_amortized else usage_emission_delta
                return delta

        

class Modification(models.Model):

    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, blank=True, null=True)
    ratio = models.FloatField(default=1)
    emission_factor = models.FloatField(blank=True, null=True)
    total_emission = models.FloatField(blank=True, null=True, help_text="Unit in kg")
    acquisition_year = models.DateField(blank=True, null=True)
    lifetime = models.PositiveIntegerField(blank=True, null=True)

    def get_total_emissions(self, year=None):
        """
            Get the total emissions for this modification.
        """
        if year is None:
            return self.total_emission
        else:
            years_since_acquisition = year - self.acquisition_year.year
            if years_since_acquisition < 0:
                return 0 
            elif years_since_acquisition >= self.lifetime:
                return 0
            else:
                return (self.total_emission / self.lifetime)