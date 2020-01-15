from odoo import models, fields

class Courses(models.Model):

    _name = "courses"
    name = fields.Char(string='Name')
    description = fields.Char(string="Description")
    course_id = fields.One2many(comodel_name='sessions', inverse_name='session_id')
    responsible = fields.Many2one(comodel_name="res.users", string="Responsible")