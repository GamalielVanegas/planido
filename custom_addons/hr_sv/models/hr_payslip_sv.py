from odoo import models, fields, api

class HrPayslipSV(models.Model):
    _name = 'hr.payslip.sv'
    _description = 'Planilla SV'
    _order = 'date_start desc'

    name = fields.Char(string='Nombre', compute='_compute_name', store=True)
    date_start = fields.Date(string='Fecha Inicio', required=True, default=fields.Date.today)
    date_end = fields.Date(string='Fecha Fin', required=True)
    period_type = fields.Selection([
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual')
    ], string='Tipo de Periodo', required=True)

    line_ids = fields.One2many('hr.payslip.sv.line', 'payslip_id', string='Líneas de Planilla')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Finalizado'),
    ], string='Estado', default='draft')

    @api.depends('date_start', 'date_end')
    def _compute_name(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                rec.name = f"Planilla {rec.date_start.strftime('%d/%m/%Y')} - {rec.date_end.strftime('%d/%m/%Y')}"
            else:
                rec.name = 'Nueva Planilla'

    def action_calcular_planilla(self):
        self.ensure_one()

        # Borrar líneas existentes para no duplicar
        self.line_ids.unlink()

        empleados = self.env['hr.employee'].search([
            ('contract_id.state', '=', 'open')
        ])

        for emp in empleados:
            contrato = emp.contract_id
            if contrato and contrato.wage:
                self.env['hr.payslip.sv.line'].create({
                    'payslip_id': self.id,
                    'employee_id': emp.id,
                    'wage': contrato.wage,
                    # Puedes inicializar adelantos, prestamos, horas extras, etc. en 0
                })

