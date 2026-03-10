import string

from odoo import models, fields, api, _

class HMSDoctor(models.Model):
    _name = 'hms.doctor'
    _description = 'Doctor Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name", required=True, tracking=True)
    specialization = fields.Char(string="Specialization", tracking=True)
    phone = fields.Char(string="Phone", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    experience = fields.Integer(string="Experience (Years)")
    consultation_fees = fields.Float(string="Consultation Fees")
    active = fields.Boolean(string="Active", default=True)