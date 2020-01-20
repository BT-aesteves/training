from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class Session(models.Model):

    _name = 'session'
    name = fields.Char(string='name')

    def _select_instructor(self):
        return ['|', ('instructor', '=', True), ('category_id', 'child_of', self.env.ref('openacademy.teacher_tag').id)]

    start_date = fields.Datetime(string='Start date', default=fields.Date.today)
    end_date = fields.Datetime(string='End date', store=True, compute='_compute_end_date', inverse='_inverse_duration')
    duration = fields.Integer('Duration')
    number_of_seats = fields.Integer('Number of seats')
    course_description = fields.Char(related='session_id.description')
    session_id = fields.Many2one('course', 'Course')
    color = fields.Integer(string='Color')
    session_ended = fields.Boolean(default=True)
    attendees = fields.Many2many('res.partner', 'session_attendees', 'attendee_id', 'session_id', string='Attendees')
    taken_seats_percentage = fields.Float('Percentage of seats', compute='_compute_percentage_taken')
    instructor = fields.Many2one('res.partner',  'Instructor', domain=_select_instructor)
    state = fields.Selection([
                ('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                string='state', default='draft', readonly=True)
    full_session = fields.Boolean(compute="_compute_full_session", store=True)
    attendees_number = fields.Integer(compute='_compute_attendees_number', store=True)


    @api.depends("duration", "number_of_seats")
    def _compute_end_date(self):
        for record in self:
            record.end_date = record.start_date + relativedelta(days=record.duration)
            if record.duration > 0:
                record.session_ended = False
                return
            record.session_ended = True
            
    @api.depends('attendees')
    def _compute_attendees_number(self):
        for session in self:
            if session.attendees:
                session.attendees_number = len(session.attendees)

    @api.depends('attendees', 'number_of_seats')
    def _compute_full_session(self):
        for session in self:
            if session.number_of_seats == len(session.attendees):
                session.full_session = True
                continue
            session.full_session = False

    @api.onchange("number_of_seats")
    def _onchange_seats(self):
        for record in self:
            if len(record.attendees) > record.number_of_seats:
                return {
                    "warning": {
                        "title": "Number of seats exceeded",
                        "message": "There cant be more than %s attendees" % len(record.attendees),
                    }
            }

    @api.onchange("number_of_seats")
    def _onchange_seats_negative(self):
        for record in self:
            if record.number_of_seats < 0:
                return {
                    "warning": {
                        "title": "Number of seats format error",
                        "message": "The number of seats cant be negative",
                    }
                }

    @api.constrains("attendees","instructor")
    def _check_subtask_level(self):
        if self.instructor in self.attendees:
            raise ValidationError("The instructor cannot be present in the  attendees list")

    def _compute_percentage_taken(self):
        for record in self:
            record.taken_seats_percentage = 100 * record.number_of_seats/100

    def _inverse_duration(self):
        for record in self:
            if not record.end_date or record.session_ended:
                continue
            result_date = record.end_date - record.start_date
            record.duration = result_date.days

    def confirm_session(self):
        for record in self:
            record.state = "confirmed"

    def end_session(self):
        for session in self:
            if session.session_ended:
                session.state = "done"
                return
        raise ValidationError("The session has not ended yet.")

    def update_duration_session(self):
        for session in self.search([('state', '=', 'confirmed'), ('session_ended', '=', True)]):
            session.state = "done"

    def show_form(self):
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "session",
            "views": [(False, "form")],
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "context": dict(self.env.context),
        }
