# -*- coding: utf-8 -*-
__author__ = 'Philipp Lang'

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from dingos.models import FactTerm


class FactTermWeight(models.Model):
    fact_term = models.ForeignKey(FactTerm,related_name='factterm_set')
    weight = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        unique_together = ('id', 'fact_term')

class AssignmentName(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return ("%s" % self.name)

class FactTerm2Weight(models.Model):
    fact_term = models.ForeignKey(FactTerm,related_name='factterm_set2')
    assignment_name = models.ForeignKey(AssignmentName, related_name='aname')
    weight = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        unique_together = ('fact_term', 'assignment_name')