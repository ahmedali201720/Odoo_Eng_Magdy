# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CarRequest(http.Controller):

    @http.route('/car_request/list', auth='user', type='http', website=True)
    def list_all_requests(self, **kw):
        objects = request.env['car.request'].sudo().search([('employee_id.user_id', '=', request.env.user.id)])
        return http.request.render('car_request.list_requests', {'requests': objects})

    @http.route('/employee/<model("hr.employee"):emp_obj>', auth='public', type='http', website=True)
    def get_employee(self, emp_obj, **kw):
        return request.render('car_request.employee_details', {'employee': emp_obj})

    @http.route(['/car_request', '/api/car_requests'], type='http', auth='public', methods=['GET'], website=True)
    def get_requests_1(self, **kw):
        print(kw)
        requests = request.env['car.request'].sudo().search([('state', '=', 'approved')])
        return http.request.render('car_request.list_requests', {'requests': requests})

    @http.route(['/car_request', '/api/car_requests'], type='json', auth='public', methods=['POST'])
    def get_requests(self, **kw):
        print(kw)
        requests = request.env['car.request'].sudo().search_read([], {'name', 'vehicle_id', 'employee_id'})
        return requests