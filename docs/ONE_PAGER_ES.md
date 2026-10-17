Illustrative numbers, replace with your own

# Refund desk agent

Generado el 2026-10-17T15:42:32.584614+00:00 con `python -m roi_model.cli publish-docs` (paquete 0.1.0, git 30a9581).
Simulado. Cada insumo es ilustrativo [EST]. Esto no es un resultado medido de un negocio real.

Mirá: el número de abajo sale de supuestos, no de una factura.
Fijate que el tiempo de revisión y el error que queda están adentro del cálculo.

Puerto Gris Parcel Co. es una empresa de paquetes inventada. Un agente de back-office redactaría la decisión de un reembolso. Una persona sigue aprobando los casos que la política manda a revisión. Ninguna de estas cifras es una medición.

| Input | Value | Label |
| --- | --- | --- |
| volume_per_day | 120.0 items/day | illustrative [EST] |
| working_days_per_month | 21.0 days/month | illustrative [EST] |
| manual_minutes_per_item | 12.0 minutes | illustrative [EST] |
| loaded_cost_per_hour | 32.0 USD/hour | illustrative [EST] |
| manual_error_rate | 0.06 fraction | illustrative [EST] |
| agent_error_rate | 0.02 fraction | illustrative [EST] |
| cost_of_error | 25.0 USD/error | illustrative [EST] |
| input_tokens | 1800.0 tokens | illustrative [EST] |
| output_tokens | 400.0 tokens | illustrative [EST] |
| input_price_per_million | 1.5 USD/1M tokens | illustrative [EST] |
| output_price_per_million | 6.0 USD/1M tokens | illustrative [EST] |
| review_minutes | 5.0 minutes | illustrative [EST] |
| review_rate | 0.5 fraction | illustrative [EST] |
| implementation_cost | 180000.0 USD | illustrative [EST] |
| monthly_run_cost | 2500.0 USD/month | illustrative [EST] |
| adoption_ramp_months | 6.0 months | illustrative [EST] |
| discount_rate_annual | 0.1 fraction | illustrative [EST] |

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

Dato medido, aparte de los insumos inventados. Es la factura de una corrida de evaluación de 23 casos, no el costo de un reembolso de producción. No está aplicado a la VPN de esta página.

Source: agent-runtime-evals commit c1efdfd, measured 2026-10-17, provider xAI. Price page https://docs.x.ai/docs/models fetched 2026-10-17.

| Sample | Billed USD | Tokens | Label |
| --- | --- | --- | --- |
| non-reasoning | US$0.036-0.037 | about 66-70k input / 3-3.4k output tokens | measured |
| grok-4.3 | US$0.072 | 62.7k input / 14.5k output, including about 11.6k reasoning tokens | measured |

[EST] `per_production_item_usd = billed_eval_run_usd / 23`
One production refund costs the same as one case inside this 23-case eval run. The billed dollars, the token counts and the case count are measured. This equality is not. It is not applied to the invented case inputs in refund_desk.yaml or weekly_report.yaml.

[EST] non-reasoning: US$0.036-0.037 / 23 = US$0.001565 to US$0.001609 per case (display rounded to 6 decimal places).
[EST] grok-4.3: US$0.072 / 23 = US$0.003130 per case (display rounded to 6 decimal places).

Short-context list price times the token counts does not equal the billed sample. The measured figure is the billed total. The non-reasoning sample is recorded as non-reasoning; the list-price row used for that reconstruction is grok-4.20-0309-non-reasoning on the price page fetched the same day. This file does not claim a model id for that sample beyond non-reasoning.

List-price reconstruction for non-reasoning using grok-4.20-0309-non-reasoning at US$1.25 input and US$2.50 output per million tokens: US$0.09 to US$0.096. Billed sample: US$0.036-0.037. The reconstruction is not the measured bill.
List-price reconstruction for grok-4.3 using grok-4.3 at US$1.25 input and US$2.50 output per million tokens: US$0.114625. Billed sample: US$0.072. The reconstruction is not the measured bill.

Aplicado como costo del agente en esta corrida: no.
