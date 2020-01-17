from odoo import models, fields, api

class Wizard(models.TransientModel):

    _name = "wizard"

    def _set_default_session(self):
        return self._context.get('active_id')

    session_id = fields.Many2one('sessions', 'Sessions', default=_set_default_session)
    attendees = fields.Many2many('res.partner', 'wizard_attendees', 'attendee_id', 'wizard_id', string='Attendees')

    def register_attendees(self):
        self.session_id.attendees |= self.attendees



