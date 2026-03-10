from odoo import models, fields, api, _

class DrugMaster(models.Model):
    _name = 'hms.drug'
    _description = 'Drug Master'

    # Mandatory fields
    name = fields.Char(string="Medicine Name", required=True)
    drug_code = fields.Char(string="Drug Code", copy=False, readonly=True, default='New')
    category = fields.Selection(
        [('tablet', 'Tablet'), ('syrup', 'Syrup'), ('injection', 'Injection')],
        string="Category",
        required=True
    )
    dosage = fields.Char(string="Dosage", required=True)
    price = fields.Float(string="Price", required=True)
    stock = fields.Integer(string="Stock Quantity", default=0)
    description = fields.Text(string="Description")

    # One2many relation to follow-ups/prescriptions
    followup_line_ids = fields.One2many(
        'hms.followup.line',
        'medicine_id',
        string="Prescribed In"
    )
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('drug_code', 'New') == 'New':
                vals['drug_code'] = self.env['ir.sequence'].next_by_code(
                    'hms.drug'
                ) or '/'
        return super().create(vals_list)
    # @api.onchange('medicine_id')
    # def _onchange_medicine_id(self):
    #     if self.medicine_id:
    #         self.dosage = self.medicine_id.dosage