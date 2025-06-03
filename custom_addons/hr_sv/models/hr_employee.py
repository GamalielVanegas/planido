from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    dui = fields.Char(string='DUI', size=10)
    nup = fields.Char(string='NUP', size=12)
