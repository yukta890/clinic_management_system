{
    'name': 'Clinic Management System',
    'version': '17.0.1.0',
    'category': 'Management',
    'description': """
        A comprehensive Clinic Management System to manage patients, appointments, prescriptions, and follow-ups efficiently.
        """,
    'category': 'Management',
    
    'author': 'Laxicon Solution Pvt Ltd.',
    'website': 'https://www.laxicon.in',
    'support': 'info@laxicon.in',
    'license': 'OPL-1',
 
    'depends': ['base','mail'],
 
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/stage_data.xml',
        'wizard/prescription_wizard_view.xml',
        'views/patient_view.xml',
        'views/occupation_view.xml',
        'views/followup_view.xml',
        'views/stage_view.xml', 
        'views/appointment_view.xml',
        'views/doctor_view.xml',
        'views/drug_view.xml',
        # 'views/opd_view.xml',
        'views/menu.xml',
        
    ],
 
    
    'installable': True,
    'application': True,
    'auto_install': False
}