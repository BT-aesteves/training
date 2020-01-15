from odoo import models, fields

class Partner(models.Model):

    _name = "res.partner"
    _inherit = "res.partner"
    instructor = fields.Boolean(Default=False)
    sessions = fields.Many2many('sessions', 'session_partner', 'session_id', 'partner_id', string='Sessions')