# -*- coding: utf-8 -*-
__author__ = 'Philipp Lang'

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from dingos.models import FactTerm


class FactTermWeight(models.Model):
    fact_term = models.ForeignKey(FactTerm,related_name='factterm_set')
    weight = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])