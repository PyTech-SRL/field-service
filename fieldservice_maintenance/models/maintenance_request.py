# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    fsm_order_id = fields.Many2one("fsm.order", "Field Service Order")

    @api.model
    def create(self, vals):
        # create FSM order with type maintenance if selected equipment is
        # enabled with boolean is_fsm_equipment
        request = super(MaintenanceRequest, self).create(vals)
        ctx = dict(self._context)
        if request.equipment_id.is_fsm_equipment and "fsm_order" not in ctx:
            # Get the fsm equipment
            fsm_equipment = self.env["fsm.equipment"].search(
                [("maintenance_equipment_id", "=", request.equipment_id.id)], limit=1
            )
            fsm_order_type = self.env["fsm.order.type"].search(
                [("internal_type", "=", "maintenance")], order="id desc", limit=1
            )
            if fsm_equipment.current_location_id.id:
                fsm_order_id = self.env["fsm.order"].create(
                    {
                        "type": fsm_order_type.id,
                        "equipment_id": fsm_equipment.id,
                        "location_id": fsm_equipment.current_location_id.id,
                        "request_id": request.id,
                        "description": request.description,
                        "request_early": request.schedule_date,
                        "scheduled_date_start": request.schedule_date,
                        "priority": request.priority,
                    }
                )

                request.fsm_order_id = fsm_order_id
            else:
                _logger.info(
                    _(
                        "Missing location on fsm_equipment %s. fsm_order was not created"
                        % fsm_equipment.id
                    )
                )
        return request
