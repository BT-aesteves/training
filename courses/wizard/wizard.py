from odoo import models, fields, api

class Wizard(models.TransientModel):

    _name = "wizard"

    def _set_default_session(self):
        return [self._context.get("active_id")]

    session_ids = fields.Many2many("session", "wizard_sessions", "session_id", "wizard_id",
                                  "Sessions", default=_set_default_session)
    attendees = fields.Many2many("res.partner", "wizard_attendees", "attendee_id", "wizard_id", string="Attendees")

    def register_attendees(self):
        for session in self.session_ids:
            session.attendees |= self.attendees



