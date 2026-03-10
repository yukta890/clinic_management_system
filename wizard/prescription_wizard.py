from odoo import models, fields, api, _


class HMSPrescriptionWizard(models.TransientModel):
    _name = 'hms.prescription.wizard'
    _description = 'Prescription Wizard'

    # -------------------------
    # BASIC FIELDS
    # -------------------------

    appointment_id = fields.Many2one('hms.appointment')
    patient_id = fields.Many2one('hms.patient')

    prescription_note = fields.Text(string="Prescription")

    disease_ids = fields.Many2many(
        'hms.diseases',
        string="Diseases"
    )

    flw_date = fields.Date(
        string="Followup Date",
        default=fields.Date.today
    )

    next_followup_date = fields.Date(
        string="Next Followup Date"
    )

    # -------------------------
    # PRESCRIPTION LINES
    # -------------------------

    line_ids = fields.One2many(
        'hms.prescription.wizard.line',
        'wizard_id',
        string="Prescription Lines"
    )

    # -------------------------
    # DEFAULT DISEASES
    # -------------------------

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        appointment = False
        if self.env.context.get('active_id'):
            appointment = self.env['hms.appointment'].browse(
                self.env.context.get('active_id')
            )

        if appointment:
            res['appointment_id'] = appointment.id
            res['patient_id'] = appointment.patient_id.id
            res['disease_ids'] = [(6, 0, appointment.disease_ids.ids)]

        return res

    # -------------------------
    # DONE ACTION
    # -------------------------

    def action_done(self):
        self.ensure_one()

        # 1️⃣ Create Followup (acts as Prescription)
        followup = self.env['hms.followup'].create({
            'appointment_id': self.appointment_id.id,
            'flw_date': self.flw_date,
            'additional': self.prescription_note,
            'next_followup_date': self.next_followup_date,
        })

        # 2️⃣ Copy Diseases
        followup.disease_ids = [(6, 0, self.disease_ids.ids)]

        # 3️⃣ Create Medicine Lines
        for line in self.line_ids:
            self.env['hms.followup.line'].create({
                'followup_id': followup.id,
                'medicine_id': line.medicine_id.id,
                'dosage': line.dosage,
                'instruction': line.instruction,
            })

        # 4️⃣ Move Appointment to DONE
        done_stage = self.env['hms.stage'].search(
            [('code', '=', 'done')],
            limit=1
        )

        if done_stage:
            self.appointment_id.stage_id = done_stage.id

        # 5️⃣ Open Followup Form
        return {
            'name': 'Followup',
            'type': 'ir.actions.act_window',
            'res_model': 'hms.followup',
            'view_mode': 'form',
            'res_id': followup.id,
            'target': 'current',
        }
        

# ====================================
# WIZARD LINE
# ====================================

class HMSPrescriptionWizardLine(models.TransientModel):
    _name = 'hms.prescription.wizard.line'
    _description = 'Prescription Wizard Line'

    wizard_id = fields.Many2one(
        'hms.prescription.wizard',
        ondelete='cascade'
    )

    medicine_id = fields.Many2one(
        'hms.drug',
        string="Medicine"
    )
    dosage = fields.Char("Dosage")
    instruction = fields.Text("Instruction")
    @api.onchange('medicine_id')
    def _onchange_medicine_id(self):
        if self.medicine_id:
            self.dosage = self.medicine_id.dosage