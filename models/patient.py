from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
import re


class HMSPatient(models.Model):
    _name = 'hms.patient'
    _description = "Patient Master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    
    # -------------------------------------------------
    # BASIC INFO
    # -------------------------------------------------

    patient_code = fields.Char(string="Patient ID",required=True,copy=False,readonly=True,default="New",tracking=True)
    title = fields.Selection([
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('miss', 'Miss'),
        ('dr', 'Dr.')
    ], string="Title")
    name = fields.Char("First Name", required=True, tracking=True)
    middle_name = fields.Char("Middle Name")
    surname = fields.Char("Surname")
    display_name = fields.Char(compute="_compute_display_name",store=True)
    dob = fields.Date("Date of Birth", tracking=True)
    age = fields.Integer(compute="_compute_age",store=True)
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", tracking=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widow', 'Widow'),
        ('divorced', 'Divorced')
    ], string="Marital Status")
    religion = fields.Char()
    occupation_id = fields.Many2one('hms.occupation')


    
    # -------------------------------------------------
    # CONTACT INFO
    # -------------------------------------------------

    phone = fields.Char(string="Phone", required=True, tracking=True)
    mobile_no = fields.Char(string="Mobile", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City")
    zip = fields.Char(string="Zip")
    state_id = fields.Many2one(string="State", comodel_name='res.country.state')
    country_id = fields.Many2one(string='Country', comodel_name='res.country')

    # -------------------------------------------------
    # DOCTOR & FOLLOW-UP INFO
    # -------------------------------------------------

    consulting_doctor = fields.Many2one('hms.doctor',string="Consulting Doctor")
    followcharge = fields.Float(string="Follow-up Charge")
    date_added = fields.Datetime(string="Created On",default=fields.Datetime.now,readonly=True)         
    appointment_ids = fields.One2many('hms.appointment', 'patient_id')
    followup_ids = fields.One2many('hms.followup', 'patient_id',string="Followups")
    appointment_count = fields.Integer(compute="_compute_counts")
    followup_count = fields.Integer(compute="_compute_counts")
    last_followup_id = fields.Many2one('hms.followup',compute="_compute_last_followup",string="Last Follow-up") 
    # -------------------------------------------------
    # SMART BUTTON ACTIONS
    # -------------------------------------------------

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'res_model': 'hms.appointment',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
    
    def action_view_followups(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Follow-ups',
            'res_model': 'hms.followup',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    def _compute_last_followup(self):
        for rec in self:
            followup = self.env['hms.followup'].search(
                [('patient_id', '=', rec.id)],
                order='flw_date desc',
                limit=1
            )
            rec.last_followup_id = followup
    
    @api.depends('appointment_ids', 'followup_ids')
    def _compute_counts(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)
            # rec.prescription_count = len(rec.prescription_ids)
            rec.followup_count = len(rec.followup_ids)
    
    @api.depends('title', 'name', 'middle_name', 'surname')
    def _compute_display_name(self):
        title_map = dict(self._fields['title'].selection)
        for rec in self:
            parts = []
            if rec.title:
                parts.append(title_map.get(rec.title))
            parts += list(filter(None, [rec.name, rec.middle_name, rec.surname]))
            rec.display_name = " ".join(parts)

    # age compute method
    @api.depends('dob')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.dob:
                rec.age = today.year - rec.dob.year - (
                    (today.month, today.day) < (rec.dob.month, rec.dob.day)
                )
            else:
                rec.age = 0

    

    # -------------------------------------------------
    # SEQUENCE
    # -------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_code', 'New') == 'New':
                vals['patient_code'] = self.env['ir.sequence'].next_by_code('hms.patient') or '/'
        return super().create(vals_list)

    # -------------------------------------------------
    # VALIDATIONS
    # -------------------------------------------------

    @api.constrains('phone')
    def _check_phone(self):
        for rec in self:
            if rec.phone:
                phone = rec.phone.strip()
                if not phone.isdigit() or len(phone) != 10:
                    raise ValidationError(_("Phone number must be exactly 10 digits."))
                
    @api.constrains('mobile_no')
    def _check_mobile_no(self):
        for rec in self:
            if rec.mobile_no:
                mobile = rec.mobile_no.strip()
                if not mobile.isdigit() or len(mobile) != 10:
                    raise ValidationError(_("Mobile number must be exactly 10 digits."))
                
    @api.constrains('email')
    def _check_email(self):
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        for rec in self:
            if rec.email and not re.match(pattern, rec.email.strip()):
                raise ValidationError(_("Invalid email format."))