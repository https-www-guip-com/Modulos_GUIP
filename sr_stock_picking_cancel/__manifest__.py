# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': "Stock Picking Cancel",
    'version': "12.0.0.0",
    'summary': "This module used to Cancel Incoming and Outgoing Shipment/picking",
    'category': 'Warehouse',
    'description': """
    cancel stock picking
    cancel incoming shipment
    cancel outgoing shipment
    cancel internal shipment
    cancel stock
    cancel delivery
    cancel shipment
    revert shipment
    revert delivery
    
    
    
    """,
    'author': "Sitaram",
    'website': "http://www.sitaramsolutions.in",
    'depends': ['base','stock'],
    'data': [
        'views/inherited_stock_picking.xml'
    ],
    'live_test_url':'https://youtu.be/LIeYgUzo5DE',
    'images': ['static/description/banner.png'],
    "price": 10,
    "currency": 'EUR',
    'demo': [],
    "license": "AGPL-3",
    'installable': True,
    'auto_install': False,
}
