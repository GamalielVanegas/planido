from odoo import models, fields, api
from datetime import datetime
import io
import base64
import csv

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

    archivo_spu = fields.Binary("Archivo SPU", readonly=True)
    nombre_archivo_spu = fields.Char("Nombre Archivo", readonly=True)

    @api.depends('date_start', 'date_end')
    def _compute_name(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                rec.name = f"Planilla {rec.date_start.strftime('%d/%m/%Y')} - {rec.date_end.strftime('%d/%m/%Y')}"
            else:
                rec.name = 'Nueva Planilla'

    def action_calcular_planilla(self):
        self.ensure_one()
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
                })

    def action_marcar_finalizado(self):
        for rec in self:
            rec.state = 'done'

    def action_exportar_spu(self):
        salida = io.StringIO()
        writer = csv.writer(salida)

        # ENCABEZADOS
        writer.writerow([
            'DUI/NIT del Empleador',
            'Número patronal ISSS',
            'Período Mes-Año',
            'Correlativo Centro de Trabajo ISSS',
            'Número de Documento',
            'Tipo de Documento',
            'Número de Afiliación ISSS',
            'Institución Previsional',
            'Primer Nombre',
            'Segundo Nombre',
            'Primer Apellido',
            'Segundo Apellido',
            'Apellido de Casada',
            'Salario',
            'Pago Adicional',
            'Monto de Vacación',
            'Días',
            'Horas',
            'Días de Vacación',
            'Código de Observación 01',
            'Código de Observación 02'
        ])

        for linea in self.line_ids:
            emp = linea.employee_id
            contrato = emp.contract_id
            if not contrato:
                continue

            nombres = emp.name.split()
            primer_nombre = nombres[0] if len(nombres) > 0 else ''
            segundo_nombre = nombres[1] if len(nombres) > 1 else ''
            apellidos = emp.name.split()
            primer_apellido = apellidos[-1] if len(apellidos) >= 1 else ''
            segundo_apellido = apellidos[-2] if len(apellidos) >= 2 else ''

            writer.writerow([
                '038931211',                             # DUI/NIT del Empleador
                '789897899',                             # Número patronal ISSS
                self.date_end.strftime('%m%Y'),          # Período Mes-Año (MMYYYY)
                '456',                                   # Correlativo Centro Trabajo ISSS
                emp.dui.replace('-', '') if emp.dui else '',  # DUI sin guión
                '01',                                    # Tipo de Documento
                (emp.nup or '').zfill(9),                # Número Afiliación ISSS
                'COF',                                   # Institución Previsional
                primer_nombre,
                segundo_nombre,
                segundo_apellido,                        # Primer Apellido
                primer_apellido,                         # Segundo Apellido
                '',                                      # Apellido de Casada
                f"{linea.wage:.2f}",                     # Salario
                "0.00",                                  # Pago Adicional
                "0.00",                                  # Monto Vacación
                "30",                                    # Días trabajados
                "160",                                   # Horas trabajadas
                "0",                                     # Días de Vacación
                "00",                                    # Código Observación 01
                "00",                                    # Código Observación 02
            ])

        datos_csv = salida.getvalue().encode('utf-8')
        salida.close()

        nombre = f'planilla_spu_{self.date_end.strftime("%Y%m")}.csv'

        self.write({
            'archivo_spu': base64.b64encode(datos_csv),
            'nombre_archivo_spu': nombre,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=hr.payslip.sv&id={self.id}&field=archivo_spu&filename_field=nombre_archivo_spu&download=true',
            'target': 'self',
        }

