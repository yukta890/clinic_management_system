from odoo import models, fields, api, _

class HMSDiseases(models.Model):
    _name = 'hms.diseases'
    _description = 'Disease Master'

    name = fields.Char("Disease Name", required=True)
    description = fields.Text("Description")
    appointment_id = fields.Many2one('hms.appointment',string="Appointment")