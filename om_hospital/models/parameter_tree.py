from odoo import fields,models,api



class ParaTree(models.Model):
    _name = 'para.tree'

    _sql_constraints = [
        ('para_val_unique', 'unique(para_val)', 'This Value already exists!')
    ]

    parameter = fields.Selection([
        ('Technical_parameter', 'Technical Parameter'),
        ('Other_parameter ', 'Other Parameter '),
        ('Requirement_area ', 'Other Requirement Area '),
    ], string='Parameters')

    para_val = fields.Char(string="Value")


