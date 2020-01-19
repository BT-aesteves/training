from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class Session(models.Model):

    _name = "session"
    name = fields.Char(string="name")

    def _select_instructor(self):
        return ["|", ("instructor", "=", True), ("category_id.parent_id", "=", self.env.ref("openacademy.teacher_tag").id)]

    start_date = fields.Datetime(string="Start date", default=fields.Date.today)
    end_date = fields.Datetime(string="End date", store=True, compute="_compute_end_date", inverse="_inverse_duration")
    duration = fields.Integer("Duration")
    number_of_seats = fields.Integer("Number of seats")
    course_description = fields.Char(related="session_id.description")
    session_id = fields.Many2one("course", "Course")
    color = fields.Integer(string="Color")
    attendees = fields.Many2many("res.partner", "session_attendees", "attendee_id", "session_id", string="Attendees")
    taken_seats_percentage = fields.Float("Percentage of seats", compute="_compute_percentage_taken")
    instructor = fields.Many2one("res.partner",  "Instructor", domain=_select_instructor)
    status = fields.Selection([
                ("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done")],
                string="Status", default="draft", readonly=True)

    @api.depends("duration", "number_of_seats")
    def _compute_end_date(self):
        for record in self:
            record.end_date = record.start_date + relativedelta(days=record.duration)

    @api.onchange("number_of_seats")
    def _onchange_seats(self):
        for record in self:
            if len(record.attendees) > record.number_of_seats:
                return {
                    "warning": {
                        "title": _("Number of seats exceeded"),
                        "message": _("There cant be more than %s attendees" % len(record.attendees)),
                    }
            }

    @api.onchange("number_of_seats")
    def _onchange_seats_negative(self):
        for record in self:
            if record.number_of_seats < 0:
                return {
                    "warning": {
                        "title": _("Number of seats format error"),
                        "message": _("The number of seats cant be negative"),
                    }
                }

    @api.constrains("attendees","instructor")
    def _check_subtask_level(self):
        if self.instructor in self.attendees:
            raise ValidationError(_("The instructor cannot be present in the  attendees list"))

    def _compute_percentage_taken(self):
        for record in self:
            record.taken_seats_percentage = 100 * record.number_of_seats/100

    def _inverse_duration(self):
        for record in self:
            if not record.end_date or record.end_date == record.start_date:
                continue
            result_date = record.end_date - record.start_date
            record.duration = result_date.days

    def confirm_session(self):
        self.status = "confirmed"
        
    def update_duration_session(self):
        for session in self.env["session"].search([]):
            if session.status == "confirmed" and session.start_date == session.end_date:
                session.status = "done"

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
