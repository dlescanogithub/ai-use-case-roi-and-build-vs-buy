# Refund desk agent

Generado el 2026-10-17T15:17:20.092837+00:00 con `python -m roi_model.cli publish-docs` (paquete 0.1.0, git 345f7dd).
Simulado. Cada insumo es [EST]. Esto no es un resultado medido de un negocio real.

Mirá: el número de abajo sale de supuestos, no de una factura.
Fijate que el tiempo de revisión y el error que queda están adentro del cálculo.

Puerto Gris Parcel Co. es una empresa de paquetes inventada. Un agente de back-office redactaría la decisión de un reembolso. Una persona sigue aprobando los casos que la política manda a revisión. Ninguna de estas cifras es una medición.

## Qué dice el modelo

- Ahorro mensual neto en régimen: USD 12,775.15.
- Recupero de la inversión: 17.08 meses.
- Volumen de equilibrio: 412.43 ítems por mes (ahorro mensual neto en cero; la implementación no entra en este volumen).
- VPN a 3 años: USD 180,923.12.
- Costo por ítem terminado, con el tiempo de quien revisa: USD 1.34.
- Ahorro por ítem ajustado por calidad (después del error residual): USD 6.06.
- Los supuestos que más mueven la VPN: volume_per_day, manual_minutes_per_item, loaded_cost_per_hour.

## Lo que una persona tiene que hacer

El modelo no aprueba una compra, un proveedor ni un despliegue.
Tenés que cambiar los [EST] por mediciones antes de tratar la VPN como un plan.

## Lugar para un dato medido

Slot de costo medido por corrida: podés enchufar un número medido en agent-runtime-evals (privado) solo con un archivo en status measured. Los stubs no son precios de proveedor y no se aplican si el status no es measured.
Aplicado en esta corrida: no.
