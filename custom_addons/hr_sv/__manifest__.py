{
    'name': 'Planilla El Salvador',
    'version': '16.0.1.0.0',
    'summary': 'Gestión de planilla con leyes salvadoreñas (ISSS, AFP, Renta)',
    'description': 'Extiende empleados y genera planillas mensuales/quincenales con deducciones legales de El Salvador.',
    'category': 'Human Resources',
    'author': 'Tu Nombre o Empresa',
    'depends': ['hr', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_payslip_sv_views.xml',
    ],
    'installable': True,
    'application': True,
    'post_init_hook': 'importar_empleados_excel',
}
