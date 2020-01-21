from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Course(models.Model):

    _name = "course"
    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    course_id = fields.One2many('session', 'session_id')
    responsible = fields.Many2one('res.users', string='Responsible')
    _sql_constraints = [('name_unique', 'unique(name)', 'entered name already exists!')]

    @api.constrains("name", "description")
    def _check_unique_name(self):
        if self.name == self.description:
            raise ValidationError(_("The name cannot be the same as the description"))