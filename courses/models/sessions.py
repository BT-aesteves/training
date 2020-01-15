from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Sessions(models.Model):

    _name = "sessions"
    name = fields.Char(string='name')
    start_date = fields.Datetime(string='Start date', default=fields.Date.today)
    end_date = fields.Datetime(string='End date', store=True, compute='_compute_end_date', inverse="_inverse_duration")
    duration = fields.Integer("Duration")
    number_of_seats = fields.Integer("Number of seats")
    course_description = fields.Char(related='session_id.description')
    session_id = fields.Many2one(comodel_name="courses", string="Course")
    attendees = fields.Many2many('res.partner', 'session_attendees', 'attendee_id', 'session_id', string='Attendees')
    taken_seats_percentage = fields.Float("Percentage of seats", compute='_compute_percentage_taken')
    instructor = fields.Many2one(comodel_name="res.partner", string="Instructor")

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

