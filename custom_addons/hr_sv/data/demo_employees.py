from odoo import api, SUPERUSER_ID

def crear_empleados_demo(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    cargos = ['Analista', 'Desarrollador', 'Gerente', 'Asistente', 'Supervisor']
    for i in range(1, 21):
        nombre = f'Empleado {i}'
        dui = f'0{i:07d}-X'
        nup = f'{i:012d}'
        salario = 500 + (i * 25)  # Sueldos entre 525 y 1000

        empleado = env['hr.employee'].create({
            'name': nombre,
            'dui': dui,
            'nup': nup,
            'job_title': cargos[i % len(cargos)],
        })

        env['hr.contract'].create({
            'name': f'Contrato {nombre}',
            'employee_id': empleado.id,
            'wage': salario,
            'state': 'open',
            'date_start': '2024-01-01',
        })
