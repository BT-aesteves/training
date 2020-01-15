from odoo import models, fields

class courses(models.Model):

    _name = "courses"
    name = fields.Char(string='Name')
    description = fields.Char(string="Description")
    sessions = fields.Many2many('sessions', 'sessions_courses', 'course_id', 'session_id', string='Sessions')
    full_sessions = fields.Many2many('sessions', 'session_course_full_id', 'course_search_id', 'sessions_search_id',
                                     string='Full sessions')