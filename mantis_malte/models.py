

# -*- coding: utf-8 -*-

# Copyright (c) Siemens AG, 2015
#
# This file is part of MANTIS.  MANTIS is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#



from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from dingos.models import FactTerm


#class FactTermWeight(models.Model):
#    fact_term = models.ForeignKey(FactTerm,related_name='factterm_set2')
#    weight = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
#
#    class Meta:
#        unique_together = ('id', 'fact_term')

class AssignmentName(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return ("%s" % self.name)

class FactTerm2Weight(models.Model):
    fact_term = models.ForeignKey(FactTerm,related_name='weight_set')
    assignment_name = models.ForeignKey(AssignmentName, related_name='aname')
    weight = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        unique_together = ('fact_term', 'assignment_name')