from odoo import models,fields,api
from dateutil.relativedelta import relativedelta

class sessions(models.Model):

    _name = "sessions"
    name = fields.Char(string='name')
    start_date = fields.Datetime(string='Start date', default=fields.Date.today, readonly=False)
    end_date = fields.Datetime(string='End date', store=True, compute='_compute_end_date',
                               readonly=False, inverse="_inverse_duration")
    duration = fields.Integer("Duration")
    number_of_seats = fields.Integer("Number of seats")
    related_course = fields.Many2many('courses', 'course_session_id', 'session_id', 'course_id', string='Related Courses')
    course_description = fields.Char(related='related_course.description', store=True)
    attendees = fields.Many2many('res.partner', 'session_attendees', 'attendee_id', 'session_id', string='Attendees')
    taken_seats_percentage = fields.Integer("Percentage of seats", compute='_compute_percentage_taken')

    @api.depends('duration', 'number_of_seats')
    def _compute_end_date(self):
        for record in self:
            record.end_date = record.start_date + relativedelta(days=record.duration)

    def _compute_percentage_taken(self):
        for record in self:
            record.taken_seats_percentage = 100 * record.number_of_seats/100

    def _inverse_duration(self):
        for record in self:
            if not record.end_date or record.end_date == record.start_date:
                continue
            result_date = record.end_date - record.start_date
            record.duration = result_date.days

