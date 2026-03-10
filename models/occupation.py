from odoo import models, fields, api

class PatientOccupation(models.Model):
    _name = 'hms.occupation'
    _description = 'Patient Occupation'
    _rec_name = 'name'

    name = fields.Char(string="Occupation",required=True)
    active = fields.Boolean(string="Active",default=True)
    note = fields.Text(string="Description")

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Occupation already exists!')
    ]
