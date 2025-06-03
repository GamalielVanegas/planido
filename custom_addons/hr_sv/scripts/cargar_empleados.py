import openpyxl
from odoo import api, SUPERUSER_ID

ruta = '/home/gamaliel/odoo-dev/custom_addons/hr_sv/data/empleados_demo.xlsx'
wb = openpyxl.load_workbook(ruta)
ws = wb.active

# Iniciar entorno Odoo con privilegios de superusuario
env = api.Environment(env.cr, SUPERUSER_ID, {})

creados = 0

for fila in ws.iter_rows(min_row=2, values_only=True):
    nombre, apellido, dui, nup, puesto, salario, fecha_inicio = fila
    nombre_completo = f"{nombre} {apellido}"

    # Verificar si ya existe por DUI
    existe = env['hr.employee'].search([('dui', '=', dui)], limit=1)
    if existe:
        continue  # evitar duplicados

    empleado = env['hr.employee'].create({
        'name': nombre_completo,
        'dui': str(dui),
        'nup': str(nup).zfill(12),
        'job_title': puesto,
    })

    env['hr.contract'].create({
        'name': f'Contrato de {nombre_completo}',
        'employee_id': empleado.id,
        'wage': float(salario),
        'state': 'open',
        'date_start': fecha_inicio.strftime('%Y-%m-%d'),
    })

    creados += 1

print(f"✅ {creados} empleados importados correctamente.")
