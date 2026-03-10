import string

from odoo import api, fields, models, _

class HMSOPD(models.Model):
    _name = 'hms.opd'
    _description = 'OPD Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="OPD name", required=True, tracking=True)
    patient_id = fields.Many2one(string='hms.patient', string="Patient",tracking=True)
    doctor_id = fields.Many2one(string='hms.doctor', string="Doctor", tracking=True)
    appoinrtment_id = fields.Many2one(string='hms.appointment', string="Appointment", tracking=True)

    symptoms = fields.Text(string="Symptoms", tracking=True)
    diagnosis = fields.Text(string="Diagnosis", tracking=True)

    folloup_date = fields.Date(string="Follow-up Date", tracking=True)
    appointment_date = fields.Date(related="appoinrtment_id.appointment_date", string="Appointment Date", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Completed')
    ], default='draft', tracking=True)