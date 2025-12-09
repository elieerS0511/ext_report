from odoo import models, fields, api

# Clase que hereda el modelo de órdenes de compra para añadir campos y métodos
# relacionados con el estado de las facturas asociadas a la orden.
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Campos adicionales (computados) añadidos:
    # - invoice_status_info: texto resumen del estado de las facturas (ej. Pagado, Parcial)
    # - invoice_payment_info: texto breve sobre el pago, usado para mostrar enlaces o notas
    # - invoice_count: cuenta de facturas relacionadas (almacenado en la BD)
    # Los campos son computed; algunos no se almacenan para evitar sincronización
    # innecesaria con la base de datos cuando solo se usan en reportes.
    invoice_status_info = fields.Char(
        string='Estado Factura',
        compute='_compute_invoice_status_info',
        store=False,
        help='Muestra el estado de las facturas relacionadas'
    )

    invoice_payment_info = fields.Char(
        string='Información de Pago',
        compute='_compute_invoice_payment_info',
        store=False
    )

    invoice_count = fields.Integer(
        string='Número de Facturas',
        compute='_compute_invoice_count',
        store=True
    )

    # Método computado: actualiza `invoice_count` dependiendo de `invoice_ids`.
    # Se marca con @api.depends para que Odoo recalcule automáticamente cuando
    # cambien las facturas relacionadas.
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for order in self:
            # Asigna la longitud de la relación one2many `invoice_ids`.
            order.invoice_count = len(order.invoice_ids)

    # Método auxiliar (no expuesto directamente como campo) que construye
    # un resumen legible del estado de las facturas asociadas a la orden.
    # - Si no existen facturas devuelve una nota indicando que no se generó.
    # - Recorre las facturas y mapea estados técnicos a textos legibles.
    def _get_invoice_status_info(self):
        self.ensure_one()
        if not self.invoice_ids:
            return 'La factura todavía no se ha generado'

        estados = []
        for inv in self.invoice_ids:
            # Mapear estados y estados de pago a textos amigables.
            if inv.state == 'cancel':
                estados.append('Cancelada')
            elif inv.state == 'posted':
                if inv.payment_state == 'paid':
                    estados.append('Pagado Totalmente')
                elif inv.payment_state == 'partial':
                    # `amount_residual` contiene la cantidad pendiente; aquí se
                    # incluye en texto simple. En vistas se podría formatear
                    # con la moneda utilizando utilidades de Odoo.
                    estados.append(f'Pagado en cuotas (Resta: {inv.amount_residual})')
                elif inv.payment_state == 'not_paid':
                    estados.append('Factura generada - Sin pagar')
            elif inv.state == 'draft':
                estados.append('Borrador')

        # Unir los estados distintos en una cadena separada por '; '. Usamos
        # `set` para evitar duplicados si varias facturas comparten estado.
        if estados:
            return '; '.join(set(estados))
        return 'La factura todavía no se ha generado'

    # Método computado para rellenar `invoice_status_info` usando el método
    # auxiliar `_get_invoice_status_info`.
    def _compute_invoice_status_info(self):
        for order in self:
            order.invoice_status_info = order._get_invoice_status_info()

    # Método computado simplificado para `invoice_payment_info`. Actualmente
    # devuelve textos generales; la lógica detallada de presentación puede
    # implementarse en vistas/XML o extenderse aquí si se requiere.
    def _compute_invoice_payment_info(self):
        for order in self:
            if order.invoice_ids:
                order.invoice_payment_info = "Ver detalles en tabla"
            else:
                order.invoice_payment_info = "No aplica"