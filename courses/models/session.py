from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class Session(models.Model):

    def _select_instructor(self):
        return ['|', ('instructor', '=', True), ('category_id', 'child_of', self.env.ref('openacademy.teacher_tag').id)]

    _name = 'session'
    name = fields.Char(string='name')
    start_date = fields.Datetime(string='Start date', default=fields.Date.today)
    end_date = fields.Datetime(string='End date', store=True, compute='_compute_end_date', inverse='_inverse_duration')
    duration = fields.Integer(string='Duration')
    number_of_seats = fields.Integer(string='Number of seats')
    course_description = fields.Char(related='session_id.description')
    session_id = fields.Many2one('course', string='Course')
    color = fields.Integer(string='Color')
    attendees = fields.Many2many('res.partner', 'session_attendees', 'attendee_id', 'session_id', string='Attendees')
    taken_seats_percentage = fields.Float(string='Percentage of seats', compute='_compute_percentage_taken')
    instructor = fields.Many2one('res.partner',  string='Instructor', domain=_select_instructor)
    state = fields.Selection([
                ('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                string='state', default='draft', readonly=True)
    full_session = fields.Boolean(compute="_compute_full_session", store=True)
    attendees_number = fields.Integer(compute='_compute_attendees_number', store=True)


    @api.depends("duration", "start_date")
    def _compute_end_date(self):
        for record in self:
            record.end_date = record.start_date + relativedelta(days=record.duration)
            
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

    def _compute_percentage_taken(self):
        for record in self:
            if record.number_of_seats == 0:
                continue
            record.taken_seats_percentage = 100 * len(record.attendees) / record.number_of_seats

    @api.onchange("number_of_seats")
    def _onchange_seats(self):
        if len(self.attendees) > self.number_of_seats:
            return {
                "warning": {
                    "title": _("Number of seats exceeded"),
                    "message": _("There cant be more than %s attendess" % len(self.attendess)),
                }
        }
        if self.number_of_seats < 0:
            return {
                "warning": {
                    "title": _("Number of seats format error"),
                    "message": _("The number of seats cant be negative"),
                }
            }

    @api.constrains("attendees", "instructor")
    def _check_subtask_level(self):
        for record in self:
            if record.instructor in record.attendees:
                raise ValidationError(_("The instructor cannot be present in the  attendees list"))

    def _inverse_duration(self):
        for record in self:
            if not record.end_date or not record.start_date:
                continue
            if record.start_date == record.end_date:
                record.duration = 0
                continue
            result_date = record.end_date - record.start_date
            record.duration = result_date.days

    def confirm_session(self):
        self.state = "confirmed"

    def end_session(self):
        if self.start_date == self.end_date:
            self.state = 'done'
            return
        raise ValidationError("The session has not ended yet.")

    def update_duration_session(self):
        for session in self.search([('state', '=', 'confirmed')]).filtered(lambda se: se.start_date == se.end_date):
            session.state = "done"

    def show_form(self):
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "session",
            "views": [(False, "form")],
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "context": self.env.context,
        }
