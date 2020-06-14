from odoo import api, fields, models
from odoo.exceptions import UserError

class CarRequest(models.Model):
    _name = 'car.request'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = 'Car Request'

    name = fields.Char(string="Description", required=True, )
    comment = fields.Html(string="Comment", )
    info = fields.Text(string="Info", required=False, )
    show_info = fields.Boolean(string="Show", )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, help="The employee created the request", default=lambda s: s.env['hr.employee'].search([('user_id', '=', s.env.user.id)], limit=1) or False)
    email = fields.Char(related="employee_id.work_email")
    other_email = fields.Char(string="Other Email", required=False, )
    date_from = fields.Date(string="Date From", required=True, default=fields.Date.context_today)
    date_to = fields.Date(string="Date To", required=True, default=fields.Date.context_today)
    state = fields.Selection(string="Status", selection=[('new', 'New'), ('approved', 'Approved'), ('reject', 'Reject'), ('cancel', 'Cancel')], default='new', track_visibility="always")
    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehicle", required=True, default=lambda s: s.env.ref('fleet.vehicle_3'))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.other_email = self.employee_id.work_email

    def set_approve(self):
        self.state = 'approved'

    def set_cancel(self):
        self.state = 'cancel'

    def set_reject(self):
        self.state = 'reject'

    @api.constrains("other_email")
    def _check_other_email(self):
        if self.other_email.split('@')[1] in ['gmail.com', 'yahoo.com', 'outlook.com']:
            raise UserError("Invalid Email address!")

    _sql_constraints = [
        ('uniq_car_per_day', 'unique(vehicle_id,date_from)', "You can not create a request for this car!")
    ]

    # I have written this function with the aid of odoo documentation page
    # the function compares the cases for start and end date validity for a specific car
    # a car is retreived and referenced with validation by its ID
    # It ensures that start date and end date are valid (end > start)
    @api.constrains('date_from', 'date_to', 'vehicle_id')
    def _check_dates(self):
        for req in self:
            # retreive start date
            date_from = req.date_from
            # retreive end date
            date_to = req.date_from
            # check input date validity
            if date_to < date_from:
                raise UserError('End date can not be less than start date !')
            # check the dates for a specific car , its 0 if the validation criteria are achieved
            check_domain = [
                ('id', '!=', req.id),
                ('vehicle_id', '=', req.vehicle_id.id), '|', '|',
                '&', ('date_from', '<=', req.date_from), ('date_to', '>=', req.date_to),
                '&', ('date_from', '<=', req.date_from), ('date_to', '>=', req.date_to),
                '&', ('date_from', '>=', req.date_from), ('date_to', '<=', req.date_to)
            ]
            # if condition to check dates validity for the requested car
            if self.search_count(check_domain) > 0:
                raise UserError("The vehicle is not available within this date range( %s ) ." % req.vehicle_id.name)
