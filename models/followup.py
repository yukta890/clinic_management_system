from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HMSFollowup(models.Model):
    _name = 'hms.followup'
    _description = 'Patient Followup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'follow_up_id'

    # =========================
    # BASIC FIELDS
    # =========================

    follow_up_id = fields.Char(string="Followup ID",required=True,copy=False,readonly=True,default="New")
    appointment_id = fields.Many2one('hms.appointment',string="Appointment",required=True)
    patient_id = fields.Many2one('hms.patient',related='appointment_id.patient_id',store=True)
    doctor_id = fields.Many2one('hms.doctor',related='appointment_id.patient_doctor',store=True)
    next_followup_date = fields.Date(string="Next Follow-up Date")
    flw_date = fields.Date(default=fields.Date.today,tracking=True)
    disease_ids = fields.Many2many('hms.diseases',string="Diseases")
    charge = fields.Float(related="doctor_id.consultation_fees",store=True,readonly=True)
    paid = fields.Boolean()
    additional = fields.Html()

    # =========================
    # STAGE (USING SAME hms.stage)
    # =========================
    stage_id = fields.Many2one('hms.stage',string="Stage",tracking=True,group_expand='_read_group_stage_ids',default=lambda self: self._default_stage())
    stage_code = fields.Char(related='stage_id.code',store=True)
    
    @api.model
    def _default_stage(self):
        stage = self.env['hms.stage'].search([], order='sequence', limit=1)
        return stage.id if stage else False
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hms.stage'].search(
            [], order='sequence, id'
        )
    @api.onchange('doctor_id')
    def _onchange_doctor(self):
        if self.doctor_id:
            self.charge = self.doctor_id.consultation_fee
    # =========================
    # PRESCRIPTION LINES
    # =========================

    line_ids = fields.One2many('hms.followup.line','followup_id',string="Prescription Lines")
    medicine_ids = fields.Many2many('hms.drug',string="Medicines")
    medicine_html = fields.Html(string="Medicines",compute="_compute_medicine_html",sanitize=False)

    @api.depends('line_ids.medicine_id', 'line_ids.dosage', 'line_ids.instruction')
    def _compute_medicine_html(self):
        for rec in self:
            html = ""

            for line in rec.line_ids:
                med = line.medicine_id.name or ""
                dosage = line.dosage or ""
                instruction = line.instruction or ""

                html += f"""
                <div style="margin-bottom:3px;">
                    <span style="font-weight:600;">{med}</span>
                    <span style="color:#555;"> - ({dosage})</span>
                    <span style="color:#888;"> - {instruction}</span>
                </div>
                """

            rec.medicine_html = html or "No Prescription"
    # =========================
    # BUTTON (MOVE TO DONE)
    # =========================
    def action_set_done(self):
        done_stage = self.env['hms.stage'].search(
            [('code', '=', 'done')],
            limit=1
        )

        if done_stage:
            self.write({'stage_id': done_stage.id})

            # ALSO update appointment stage
            if self.appointment_id:
                self.appointment_id.write({'stage_id': done_stage.id})
    def action_set_cancel(self):
        cancel_stage = self.env['hms.stage'].search(
            [('code', '=', 'cancel')],
            limit=1
        )

        if cancel_stage:
            self.write({'stage_id': cancel_stage.id})

            # ALSO update appointment stage
            if self.appointment_id:
                self.appointment_id.write({'stage_id': cancel_stage.id})

    # =========================
    # SEQUENCE
    # =========================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('follow_up_id', 'New') == 'New':
                vals['follow_up_id'] = (
                    self.env['ir.sequence']
                    .next_by_code('hms.followup.seq')
                    or 'New'
                )
        return super().create(vals_list)

# ======================================
# FOLLOWUP LINE
# ======================================

class HMSFollowupLine(models.Model):
    _name = 'hms.followup.line'
    _description = 'Followup Prescription Line'

    followup_id = fields.Many2one('hms.followup',string="Followup",ondelete="cascade")
    medicine_id = fields.Many2one('hms.drug',string="Medicine")
    dosage = fields.Char("Dosage")
    instruction = fields.Text("Instruction")