from odoo import models, fields, api

class HrPayslipSVLine(models.Model):
    _name = 'hr.payslip.sv.line'
    _description = 'Línea de Planilla SV'

    payslip_id = fields.Many2one('hr.payslip.sv', string='Planilla', required=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)

    wage = fields.Float(string='Sueldo Base', required=True)

    isss = fields.Float(string='ISSS', compute='_compute_descuentos', store=True)
    afp = fields.Float(string='AFP', compute='_compute_descuentos', store=True)
    renta = fields.Float(string='Renta', compute='_compute_descuentos', store=True)

    total_descuentos = fields.Float(string='Total Descuentos', compute='_compute_descuentos', store=True)
    neto_pagar = fields.Float(string='Neto a Pagar', compute='_compute_descuentos', store=True)

    @api.depends('wage')
    def _compute_descuentos(self):
        for rec in self:
            # ISSS: 3% del empleado, hasta $1,000
            isss_base = min(rec.wage, 1000.00)
            rec.isss = isss_base * 0.03

            # AFP: 7.25%
            rec.afp = rec.wage * 0.0725

            # Cálculo de Renta
            if rec.wage <= 472.00:
                rec.renta = 0.0
            elif rec.wage <= 895.24:
                rec.renta = (rec.wage - 472.00) * 0.10 + 17.67
            elif rec.wage <= 2038.10:
                rec.renta = (rec.wage - 895.24) * 0.20 + 60.00
            else:
                rec.renta = (rec.wage - 2038.10) * 0.30 + 288.57

            rec.total_descuentos = rec.isss + rec.afp + rec.renta
            rec.neto_pagar = rec.wage - rec.total_descuentos

