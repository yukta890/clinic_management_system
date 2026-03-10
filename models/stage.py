from odoo import models, fields, api


class HMSStage(models.Model):
    _name = 'hms.stage'
    _description = 'Appointment Stage'
    _order = 'sequence, id'

    # -------------------------
    # BASIC FIELDS
    # -------------------------

    name = fields.Char(string='Stage Name',required=True,translate=True)
    code = fields.Char(string='Code',
        # required=True,
        # help="Use: draft, confirm, consult, done, cancel"
    )
    sequence = fields.Integer(string='Sequence',default=1,help="Lower sequence shows first")
    fold = fields.Boolean(string='Folded in Kanban',help='Fold if no appointment is in this stage')
    kanban_color = fields.Integer(string='Kanban Color',default=1)

    # -------------------------
    # RELATION
    # -------------------------

    appointment_ids = fields.One2many('hms.appointment','stage_id',string="Appointments")
    appointment_count = fields.Integer(string="Appointments Count",compute="_compute_appointment_count")

    # -------------------------
    # COMPUTE
    # -------------------------

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for stage in self:
            stage.appointment_count = len(stage.appointment_ids)