from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HMSAppointment(models.Model):
    _name = 'hms.appointment'
    _description = 'Clinic Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------------
    # BASIC FIELDS
    # -------------------------

    name = fields.Char(string="Appointment No",copy=False,readonly=True,default="New",tracking=True)
    patient_id = fields.Many2one('hms.patient',string="Patient",tracking=True)
    doctor_id = fields.Many2one('hms.doctor',string="Doctor",tracking=True)
    appointment_date = fields.Date(string="Appointment Date",default=fields.Date.today,tracking=True)
    visit_type = fields.Selection([('new', 'New Visit'),('followup', 'Follow-up')],default='new',string="Visit Type")
    notes = fields.Text(string="Notes")

    # -------------------------
    # RELATED FIELDS
    # -------------------------

    patient_age = fields.Integer(string="Age", related="patient_id.age")
    patient_gender = fields.Selection(string="Gender", related="patient_id.sex")
    patient_phone = fields.Char(string="Phone", related="patient_id.phone")
    patient_mobile = fields.Char(string="Mobile", related="patient_id.mobile_no")
    patient_doctor = fields.Many2one(string="Consulting Doctor", related="patient_id.consulting_doctor")
    disease_ids = fields.One2many('hms.diseases','appointment_id',string="Diseases")
    followup_ids = fields.One2many('hms.followup','appointment_id',string="Today's Followups",domain=lambda self: [('flw_date', '=', fields.Date.context_today(self))])

    # -------------------------
    # STAGE (ONLY WORKFLOW FIELD)
    # -------------------------

    stage_id = fields.Many2one('hms.stage',string="Stage",tracking=True,group_expand='_read_group_stage_ids',default=lambda self: self._default_stage())
    stage_code = fields.Char(
    related='stage_id.code',
    store=True
)
    @api.onchange('doctor_id')
    def _onchange_doctor(self):
        if self.doctor_id:
            self.charge = self.doctor_id.consultation_fees
    @api.model
    def _default_stage(self):
        return self.env['hms.stage'].search([], order='sequence', limit=1)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hms.stage'].search([], order='sequence, id')

    # -------------------------
    # FOLLOWUPS HTML
    # -------------------------

    last_three_followup_html = fields.Html(
        compute="_compute_last_three_followups",
        string="Last 3 Follow-ups"
    )
    def _compute_last_three_followups(self):
        for rec in self:
            # today = fields.Date.context_today(self)   # define today

            followups = self.env['hms.followup'].search(
                [
                    ('patient_id', '=', rec.patient_id.id),
                    # ('flw_date', '<', today)   # exclude today's followup
                ],
                order='flw_date desc',
                limit=3
            )

            html = """
            <div style="max-height:220px; overflow:auto;">
            <style>
                .followup_table td {
                    vertical-align: middle;
                }
            </style>

            <table class="table table-sm table-bordered followup_table">
                <thead class="table-light">
                    <tr>
                        <th>Date</th>
                        <th>Diseases</th>
                        <th>Medicine</th>
                        <th>Dosage</th>
                        <th>Instruction</th>
                    </tr>
                </thead>
                <tbody>
            </div>
            """

            if followups:
                for f in followups:

                    diseases = ", ".join(f.disease_ids.mapped('name'))
                    lines = f.line_ids
                    line_count = len(lines) if lines else 1

                    if lines:
                        first = True
                        for line in lines:

                            if first:
                                html += f"""
                                    <tr>
                                        <td rowspan="{line_count}">
                                            {f.flw_date.strftime('%d-%m-%Y') if f.flw_date else ''}
                                        </td>
                                        <td rowspan="{line_count}">
                                            {diseases}
                                        </td>
                                        <td>{line.medicine_id.name or ''}</td>
                                        <td>{line.dosage or ''}</td>
                                        <td>{line.instruction or ''}</td>
                                    </tr>
                                """
                                first = False
                            else:
                                html += f"""
                                    <tr>
                                        <td>{line.medicine_id.name or ''}</td>
                                        <td>{line.dosage or ''}</td>
                                        <td>{line.instruction or ''}</td>
                                    </tr>
                                """
                    else:
                        html += f"""
                            <tr>
                                <td>{f.flw_date.strftime('%d-%m-%Y') if f.flw_date else ''}</td>
                                <td>{diseases}</td>
                                <td colspan="3">No Prescription</td>
                            </tr>
                        """

            else:
                html += """
                    <tr>
                        <td colspan="5" style="text-align:center;">
                            No Follow-ups Found
                        </td>
                    </tr>
                """

            html += """
                </tbody>
            </table>
            """

            rec.last_three_followup_html = html
    def action_copy_last_followup(self):
        self.ensure_one()

        last_followup = self.env['hms.followup'].search(
            [('appointment_id', '=', self.id)],
            order='flw_date desc',
            limit=1
        )

        wizard_lines = []

        if last_followup:
            for line in last_followup.line_ids:
                wizard_lines.append((0, 0, {
                    'medicine_id': line.medicine_id.id,
                    'dosage': line.dosage,
                    'instruction': line.instruction,
                }))

        wiz = self.env['hms.prescription.wizard'].create({
            'appointment_id': self.id,
            'patient_id': self.patient_id.id,
            'line_ids': wizard_lines,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescription',
            'res_model': 'hms.prescription.wizard',
            'res_id': wiz.id,
            'view_mode': 'form',
            'target': 'new',
        }
    # -------------------------
    # CONSTRAINTS
    # -------------------------

    _sql_constraints = [
        ('appointment_unique',
         'unique(patient_id, appointment_date)',
         'This patient already has an appointment at this time!')
    ]

    @api.constrains('doctor_id', 'appointment_date')
    def _check_doctor_double_booking(self):
        for rec in self:
            if rec.doctor_id:
                duplicate = self.search([
                    ('doctor_id', '=', rec.doctor_id.id),
                    ('appointment_date', '=', rec.appointment_date),
                    ('id', '!=', rec.id)
                ])
                if duplicate:
                    raise ValidationError(
                        _("Doctor already has appointment at this time.")
                    )

    # -------------------------
    # BUTTON METHODS (MOVE STAGE)
    # -------------------------

    def _move_stage(self, code):
        stage = self.env['hms.stage'].search([('code', '=', code)], limit=1)
        if stage:
            self.stage_id = stage.id

    def action_set_confirm(self):
        self._move_stage('confirm')

    def action_set_consult(self):
        self._move_stage('consult')

    def action_set_done(self):
        self._move_stage('done')

    def action_set_cancel(self):
        self._move_stage('cancel')
    # -------------------------
    # PRESCRIPTION WIZARD
    # -------------------------

    def action_open_prescription_wizard(self):
        self.ensure_one()
        wiz = self.env['hms.prescription.wizard'].create({
            'appointment_id': self.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescription',
            'res_model': 'hms.prescription.wizard',
            'res_id': wiz.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_id': self.id,
                'default_patient_id': self.patient_id.id,
            }
        }

    # -------------------------
    # AUTO SEQUENCE
    # -------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hms.appointment'
                ) or '/'
        return super().create(vals_list)