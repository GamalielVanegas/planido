import os
import openpyxl
from odoo import api, SUPERUSER_ID

def importar_empleados_excel(cr, registry):
    ruta_excel = os.path.join(os.path.dirname(__file__), 'empleados_demo.xlsx')
    wb = openpyxl.load_workbook(ruta_excel)
    ws = wb.active

    env = api.Environment(cr, SUPERUSER_ID, {})

    for i, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        nombre, apellido, dui, nup, puesto, salario, fecha_inicio = fila
        nombre_completo = f"{nombre} {apellido}".strip()
        salario = float(salario)

        empleado = env['hr.employee'].create({
            'name': nombre_completo,
            'dui': dui,
            'nup': nup,
            'job_title': puesto,
        })

        env['hr.contract'].create({
            'name': f'Contrato de {nombre_completo}',
            'employee_id': empleado.id,
            'wage': salario,
            'state': 'open',
            'date_start': str(fecha_inicio),
        })

    print(f"✔ Empleados importados desde: {ruta_excel}")

