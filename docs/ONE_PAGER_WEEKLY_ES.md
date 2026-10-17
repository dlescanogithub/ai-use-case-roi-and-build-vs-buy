# Weekly report automation

Generado el 2026-10-17T15:16:12.798911+00:00 con `python -m roi_model.cli publish-docs` (paquete 0.1.0, git 130b921).
Simulado. Cada insumo es [EST]. Esto no es un resultado medido de un negocio real.

Mirá: el número de abajo sale de supuestos, no de una factura.
Fijate que el tiempo de revisión y el error que queda están adentro del cálculo.

Ejemplo personal, nada más. Cuatro reportes por mes, hoy escritos a mano. Igual leés cada borrador. El valor de la hora es lo que vos suponés que vale tu tiempo. No es un sueldo y no es un dato de un empleador.

## Qué dice el modelo

- Ahorro mensual neto en régimen: USD 168.96.
- Recupero de la inversión: 1.78 meses.
- Volumen de equilibrio: 0.42 ítems por mes (ahorro mensual neto en cero; la implementación no entra en este volumen).
- VPN a 3 años: USD 5,114.00.
- Costo por ítem terminado, con el tiempo de quien revisa: USD 13.36.
- Ahorro por ítem ajustado por calidad (después del error residual): USD 47.24.
- Los supuestos que más mueven la VPN: loaded_cost_per_hour, volume_per_month, manual_minutes_per_item.

## Lo que una persona tiene que hacer

El modelo no aprueba una compra, un proveedor ni un despliegue.
Tenés que cambiar los [EST] por mediciones antes de tratar la VPN como un plan.

## Lugar para un dato medido

Slot de costo medido por corrida: podés enchufar un número medido en agent-runtime-evals (privado) solo con un archivo en status measured. Los stubs no son precios de proveedor y no se aplican si el status no es measured.
Aplicado en esta corrida: no.
