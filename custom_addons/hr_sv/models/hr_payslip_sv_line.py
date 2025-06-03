from odoo import models, fields, api

class HrPayslipSVLine(models.Model):
    _name = 'hr.payslip.sv.line'
    _description = 'Línea de Planilla SV'
    _order = 'employee_id'

    payslip_id = fields.Many2one('hr.payslip.sv', string='Planilla', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)

    # Salario
    wage = fields.Float(string='Sueldo Base', required=True)
    salario_diario = fields.Float(string='Salario Diario', compute='_compute_salarios', store=True)
    salario_hora = fields.Float(string='Salario Hora', compute='_compute_salarios', store=True)

    # Ingresos del periodo
    dias_laborados = fields.Integer(string='Días Laborados', default=30)
    horas_extras_diurnas = fields.Float(string='Horas Extras Diurnas', default=0.0)
    horas_extras_nocturnas = fields.Float(string='Horas Extras Nocturnas', default=0.0)
    horas_extras_festivos = fields.Float(string='Horas Extras Festivos', default=0.0)
    bonificaciones = fields.Float(string='Bonificaciones', default=0.0)
    comisiones = fields.Float(string='Comisiones', default=0.0)
    viaticos = fields.Float(string='Viáticos', default=0.0)
    otros_ingresos = fields.Float(string='Otros Ingresos', default=0.0)
    total_ingresos = fields.Float(string='Total Ingresos', compute='_compute_total_ingresos', store=True)

    # Deducciones legales y otras
    isss = fields.Float(string='ISSS', compute='_compute_descuentos', store=True)
    afp = fields.Float(string='AFP', compute='_compute_descuentos', store=True)
    renta = fields.Float(string='Renta', compute='_compute_descuentos', store=True)
    embargos = fields.Float(string='Embargos', default=0.0)
    anticipos = fields.Float(string='Anticipos / Préstamos', default=0.0)
    otras_deducciones = fields.Float(string='Otras Deducciones', default=0.0)
    total_descuentos = fields.Float(string='Total Descuentos', compute='_compute_descuentos', store=True)

    # Neto
    neto_pagar = fields.Float(string='Neto a Pagar', compute='_compute_neto_pagar', store=True)

    # Complementos
    horas_trabajadas = fields.Integer(string='Horas Trabajadas', default=160)
    vacaciones_acumuladas = fields.Float(string='Vacaciones Acumuladas', default=0.0)
    aguinaldo_acumulado = fields.Float(string='Aguinaldo Acumulado', default=0.0)
    indemnizacion = fields.Float(string='Indemnización', default=0.0)
    bono_vacacional = fields.Float(string='Bono Vacacional', default=0.0)
    dias_incapacidad = fields.Integer(string='Días de Incapacidad', default=0)
    dias_licencia = fields.Integer(string='Días de Licencia', default=0)

    # Control
    estado_pago = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado')
    ], string='Estado de Pago', default='pendiente')

    forma_pago = fields.Selection([
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
        ('efectivo', 'Efectivo')
    ], string='Forma de Pago')

    observaciones = fields.Text(string='Observaciones')

    # Cálculos
    @api.depends('wage')
    def _compute_salarios(self):
        for rec in self:
            rec.salario_diario = rec.wage / 30.0 if rec.wage else 0.0
            rec.salario_hora = rec.salario_diario / 8.0 if rec.salario_diario else 0.0

    @api.depends(
        'wage',
        'bonificaciones',
        'comisiones',
        'viaticos',
        'otros_ingresos',
        'horas_extras_diurnas',
        'horas_extras_nocturnas',
        'horas_extras_festivos',
        'salario_hora'
    )
    def _compute_total_ingresos(self):
        for rec in self:
            extras = (
                rec.horas_extras_diurnas * rec.salario_hora * 2 +
                rec.horas_extras_nocturnas * rec.salario_hora * 2.25 +
                rec.horas_extras_festivos * rec.salario_hora * 2.0
            )
            rec.total_ingresos = rec.wage + extras + rec.bonificaciones + rec.comisiones + rec.viaticos + rec.otros_ingresos

    @api.depends('wage')
    def _compute_descuentos(self):
        for rec in self:
            isss_base = min(rec.wage, 1000.00)
            rec.isss = isss_base * 0.03
            rec.afp = rec.wage * 0.0725

            if rec.wage <= 472.00:
                rec.renta = 0.0
            elif rec.wage <= 895.24:
                rec.renta = (rec.wage - 472.00) * 0.10 + 17.67
            elif rec.wage <= 2038.10:
                rec.renta = (rec.wage - 895.24) * 0.20 + 60.00
            else:
                rec.renta = (rec.wage - 2038.10) * 0.30 + 288.57

            rec.total_descuentos = rec.isss + rec.afp + rec.renta + rec.embargos + rec.anticipos + rec.otras_deducciones

    @api.depends('total_ingresos', 'total_descuentos')
    def _compute_neto_pagar(self):
        for rec in self:
            rec.neto_pagar = rec.total_ingresos - rec.total_descuentos

