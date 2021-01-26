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

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def picking_cancel(self):
        for move in self.move_ids_without_package :
            move_line = []
            if move.product_id.type == 'product' :
                if move.picking_id.picking_type_id.code == 'outgoing' :
                    for line in move.move_line_ids:
                        move_line += [(0, 0,{
                                    'product_id': line.product_id.id,
                                    'product_uom_id': line.product_uom_id.id, 'location_id': line.location_dest_id.id,
                                    'location_dest_id': line.location_id.id, 'picking_id':False,
                                    'qty_done' : line.qty_done, 'lot_id': False if move.product_id.tracking == 'none' else line.lot_id.id
                                    })]
                    new_move = move.copy({
                            'product_id': move.product_id.id,
                            'product_uom_qty': move.product_uom_qty,
                            'product_uom': move.product_id.uom_id.id,
                            'state': 'draft',
                            'picking_id':False,
                            'location_id': move.location_dest_id.id,
                            'location_dest_id': move.location_id.id ,
                            'date_expected': fields.Datetime.now(),
                            'origin_returned_move_id': False,
                            'picking_type_id': False,
                            'warehouse_id': move.picking_type_id.warehouse_id.id,
                            'move_line_ids':move_line,
                            'procure_method': 'make_to_stock',
                            
                        })
                    new_move._action_confirm()
                    new_move._action_assign()
                    new_move._action_done()
                if move.picking_id.picking_type_id.code == 'incoming' : 
                    if move.product_id.tracking == 'none':
                        quant = self.env['stock.quant'].search([('product_id', '=', move.product_id.id), ('location_id', '=', move.location_dest_id.id)], limit=1)
                        quant._update_available_quantity(move.product_id, move.location_dest_id, -move.quantity_done)
                    else :
                        for line in move.move_line_ids:
                            quant = self.env['stock.quant'].search([('product_id', '=', move.product_id.id), ('location_id', '=', move.location_dest_id.id), ('lot_id', '=', line.lot_id.id)], limit=1)
                            lot_id = line.lot_id
                        quant._update_available_quantity(move.product_id, move.location_dest_id, -move.quantity_done, line.lot_id)
            move.sudo()._action_cancel()
        self.write({'state':'cancel'})
        return

class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_cancel(self):
        if not any(move.picking_id or move.inventory_id for move in self):
            if any(move.state == 'done' for move in self):
                raise UserError(_('No puede cancelar un movimiento de acciones que se haya configurado \'Done\'.'))

        for move in self:
            if move.state == 'cancel':
                continue
            move._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate:
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids.filtered(lambda m: m.state != 'done')._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
        self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        return True

    def _do_unreserve(self):
        moves_to_unreserve = self.env['stock.move']
        for move in self:
            if move.state == 'cancel':
                continue
            if move.state == 'done':
                if move.scrapped:
                    continue
                else:
                    if self.picking_id or self.inventory_id:
                        pass
                    else:
                        raise UserError(_('No puedes anular la reserva de un movimiento de acciones que se haya configurado como \'Done\'.'))
            moves_to_unreserve |= move
        moves_to_unreserve.mapped('move_line_ids').unlink()
        return True

class StockMoveLine(models.Model):
    _inherit= "stock.move.line"
 
    def unlink(self):
        if not any(line.move_id.picking_id or line.move_id.inventory_id for line in self):
            for ml in self:
                if ml.state in ('done', 'cancel'):
                    raise UserError(_('No puede eliminar movimientos de productos si se realiza el picking. Solo puedes corregir las cantidades hechas.'))
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for ml in self:
            if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
                try:
                    self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                except UserError:
                    if ml.lot_id:
                        self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    else:
                        raise
        moves = self.mapped('move_id')
        if not any(line.move_id.picking_id or line.move_id.inventory_id for line in self):
            if moves:
                moves._recompute_state()
            res = super(StockMoveLine, self).unlink()
            return res
        if moves:
            moves._recompute_state()
        return
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: