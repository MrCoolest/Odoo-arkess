from odoo import models, fields, api


class HospitalLab(models.Model):
    _name = 'hospital.lab'
    _description = 'Hospital Lab'

    name = fields.Char(string="Name",required=True)
    user_id = fields.Many2one('res.users', string='Responsible')