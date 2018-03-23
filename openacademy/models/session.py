from odoo import fields, models, _, api
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError


class OpenacademySession(models.Model):
        _name = 'openacademy.session'

        name = fields.Char(string="Session title", required=True)
        start_date = fields.Datetime(string="Session date", default=fields.Date.today())
        duration = fields.Float(string="Duration time", required=True)
        number_of_seats = fields.Integer(string="Number of seats")
        related_course = fields.Many2one("openacademy.course", string="Course")
        instructor = fields.Many2one("res.partner", domain=[("is_instructor", "=", "True")])
        responsible = fields.Many2one("openacademy.responsible", string="Course's responsible")
        attendees = fields.Many2many("res.partner", "session_partner_rel")
        num_attendees = fields.Integer(compute='_get_number_attendees', store=True)
        remain_seats = fields.Integer(string="Remain seats %", compute='_get_remain_seats')
        end_date = fields.Datetime(string="End date", compute='_get_end_date', inverse='_set_end_date')
        color = fields.Integer(string="Card color", default=0)
        state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                                 string="State of session", default='draft')

        @api.depends('attendees')
        def _get_number_attendees(self):
            for r in self:
                r.num_attendees = len(r.attendees)

        @api.depends('number_of_seats', 'attendees')
        def _get_remain_seats(self):
            for r in self:
                if r.number_of_seats > 0:
                    r.remain_seats = 100 - ((len(r.attendees) * 100) / r.number_of_seats)
                if r.remain_seats <= 0:
                    r.remain_seats = 0

        @api.depends('start_date', 'duration')
        def _get_end_date(self):
            for r in self:
                r.end_date = datetime.strptime(r.start_date, DEFAULT_SERVER_DATETIME_FORMAT)\
                             + timedelta(seconds=(r.duration*3600))

        def _set_end_date(self):
            for r in self:
                if not r.start_date or (r.end_date < r.start_date):
                    continue
                r.duration = (datetime.strptime(r.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                              - datetime.strptime(r.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                              ).total_seconds() / 3600

        @api.onchange('number_of_seats')
        def _onchange_seats(self):
            for r in self:
                if r.number_of_seats < 0:
                    r.number_of_seats = 0
                    return {
                        'warning': {
                            'title': "About number of seats",
                            'message': "Number of seats cannot be negative"
                        }
                    }

        @api.onchange('attendees')
        def _onchange_attendees(self):
            for r in self:
                if len(r.attendees) > r.number_of_seats:
                    return {
                        'warning': {
                            'title': "About attendees",
                            'message': "Number of attendees cannot be more than available seats"
                        }
                    }

        @api.onchange('end_date')
        def _onchange_end_date(self):
            for r in self:
                if r.end_date < r.start_date:
                    r.end_date = r.start_date
                    return {
                        'warning': {
                            'title': "About start_date",
                            'message': "Start date cannot be higher than End date"
                        }
                    }

        @api.constrains('instructor', 'attendees')
        def _constraint_instructor(self):
            for r in self:
                if r.instructor in r.attendees:
                    raise ValidationError(_("Instructor cannot be between attendees"))

        @api.multi
        def open_record(self):
            for r in self:
                form_id = r.env.ref("openacademy.session_form_view").id
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': r._name,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': form_id,
                    'target': 'current',
                    'res_id': r.id,
                    'context': {},
                }

        def move_confirmed(self):
            for r in self:
                r.state = 'confirmed'

        def move_done(self):
            for r in self:
                r.state = 'done'

        def move_draft(self):
            for r in self:
                r.state = 'draft'

        @api.model
        def movedone_cron(self):
            for r in self.search([]):
                if r.state == 'confirmed' and r.end_date < fields.Date.today():
                    r.state = 'done'
