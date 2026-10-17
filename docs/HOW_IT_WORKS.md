# Cómo funciona (en criollo)

Esto es un calculador con dos módulos. No es un agente que habla con clientes y no llama a ningún modelo pago. Sirve para sentarte en una entrevista y explicar, sin humo, el camino completo: primero decidís si construís o comprás, después mirás si el caso cierra en plata, y recién ahí hablás de un rollout por fases. El rollout de este repo se queda en sombra: escribe archivos, no toca un proceso real.

El código está en inglés. El paquete se llama `roi_and_build_vs_buy`, versión 0.2.0. El comando es `python -m roi_and_build_vs_buy` con dos subcomandos: `decide` y `roi`.

## Dos analogías, en orden

### 1. Alquilar o construir

Imaginate que necesitás un lugar para vivir.

- **Construir (build)** tarda más y ponés mucha plata al principio. Después la casa es tuya. El mantenimiento queda en vos.
- **Alquilar (buy)** te mudás más rápido. Pagás todos los meses. El dueño puede subir el alquiler. Irte tiene mudanza y a veces una cláusula.

Un agente interno es parecido. Construirlo es un equipo, un set de pruebas y un costo chico por cada corrida. Comprarlo es asientos, un precio de uso y una salida que duele si el formato es cerrado.

Este módulo no elige la casa. Arma la planilla: puntajes, pesos, plata a 3 años, y la pregunta "¿cuánto tendría que moverse un peso para que gane el otro?".

### 2. La canilla que gotea

Cuando ya te inclinaste por una opción, mirá si el ahorro mensual alcanza.

- La implementación es la plata y las horas del primer día.
- El ahorro mensual es el agua que dejás de tirar, menos lo que te cuesta el repuesto que se gasta.
- El recupero (payback) es cuántos meses tardás en juntar de nuevo lo que gastaste al principio.
- El volumen de equilibrio es cuántos baldes tenés que ahorrar por mes para que el arreglo no te deje pérdida, sin contar todavía el gasto del primer día.
- La sensibilidad es mover una perilla. El gráfico tornado muestra cuál mueve más el resultado.
- El Monte Carlo es tirar los dados muchas veces y mirar el percentil 10, el 50 y el 90. No es una promesa.

Fijate: si la revisión humana se come casi todo el tiempo que “ahorrabas”, la canilla sigue goteando. El modelo mete ese tiempo adentro, no en una nota al pie.

## Paso a paso

1. Abrís una carpeta de caso de `decide`. Adentro hay tres YAML: `weights.yaml`, `scores.yaml`, `tco.yaml`. Los dos ejemplos son **Bruma Freight** (mesa de excepciones de carga, empresa inventada) y **Cedro Records** (archivo cooperativo inventado).
2. Los pesos son ocho criterios y tienen que sumar 1: control, tiempo hasta ver valor, TCO a 3 años, riesgo de proveedor, seguridad y cumplimiento, mantenibilidad, extensibilidad, costo de salida.
3. Cada opción tiene un puntaje de 1 a 5 por criterio, con una frase que explica por qué. **Más alto es mejor**, también en costo y en riesgo. Un número ilustrativo va con `[EST]`.
4. `decide score` multiplica peso por puntaje y ordena. Si hay empate, desempatan por el id.
5. La sensibilidad mueve un peso por vez (−0.10, −0.05, +0.05, +0.10), tira los movimientos que dejarían un peso fuera de 0.01–0.90, reescala el resto, y vuelve a rankear. En Bruma, con estos puntajes ilustrativos, son 19 de 28, o sea 67.86%. Después busca, de a 0.001, el cambio más chico que da vuelta al ganador.
6. `decide tco` proyecta la plata a 3 años. El costo de salida no entra en el total operativo: se suma en el último año, en la columna "con salida".
7. El reporte junta las dos historias. Si el ganador de la matriz y el más barato en caja son distintos, lo dice. En los dos ejemplos pasa eso: gana `build` en puntaje y `vendor_b` es más barato en costo operativo.
8. El ADR queda en `proposed`. Una persona lo acepta. El comando no compra nada.
9. Si la opción sigue en pie, abrís un YAML de ROI. Cada número tiene una razón y tiene que decir `[EST]`. Los ejemplos son el escritorio de reembolsos de Puerto Gris Parcel Co. (inventada) y un reporte semanal personal.
10. Por cada ítem el ROI calcula el costo manual, el costo del agente (tokens por un precio ilustrativo, o un costo medido si pasás un archivo distinto), y el ahorro ajustado por calidad.
11. El ahorro neto del mes, en régimen, es volumen × ahorro por ítem − costo fijo mensual. El costo fijo se paga entero desde el mes 1. La adopción sube en línea durante la rampa.
12. El payback puede decir **nunca**. El VPN a 3 años descuenta los flujos. El tornado mueve un supuesto a la vez. El Monte Carlo usa una semilla.
13. Escribe Markdown, HTML, un SVG, un CSV y un XLSX con fórmulas. No manda mails ni aprueba nada.
14. `python -m roi_and_build_vs_buy.evalkit` corre las dos compuertas. La de ROI rechequea la identidad del ahorro. La de `decide` chequea que los pesos suman 1, que el ganador coincide con `evals/golden/decisions.json`, que el TCO no baja cuando subís volumen u horas, que el cassette cuesta 0, y que el trace no registra una acción externa. No evalúa un asistente.
15. Hay dos regresiones que **tienen que fallar**. `evalkit.roi_regression` mete una fórmula de ahorro mala a propósito. `evalkit.decide_regression` cambia los pesos de Bruma: el ganador pasa a `vendor_b` y la estabilidad queda en 59.09%, debajo del piso de 67.86%. El CI chequea que las dos fallen. El 67.86% no es una probabilidad ni una tasa de éxito en un escritorio real.

El rollout por fases está en `docs/SCOPE.md`. La fase 0 es este calculador. Un conector o un tablero no están hechos.

## Glosario

| Palabra | Qué quiere decir acá |
| --- | --- |
| [EST] | Supuesto ilustrativo. No salió de un sistema real |
| Simulado | Lo calculó este programa a partir de esos supuestos |
| Matriz ponderada | Puntajes multiplicados por pesos que suman 1 |
| TCO | Costo total en el horizonte, acá 3 años |
| Estabilidad del ganador | Porcentaje de la grilla fija donde el primer puesto se mantiene |
| Ahorro ajustado por calidad | El ahorro después de restar el costo de los errores que todavía quedan |
| Volumen de equilibrio | Ítems por mes donde el ahorro neto del mes es cero. No incluye la implementación |
| Payback | Meses hasta recuperar la implementación. Puede ser “nunca” |
| VPN | Valor presente neto de los flujos del horizonte, menos la implementación |
| Tornado | Qué supuesto, movido solo, cambia más el VPN |
| Casete | Archivo grabado. Si no está el id, falla. No hay llamada en vivo |
| Invariante | Una propiedad que tiene que ser verdad, no un guion de llamadas |

## Límites, dichos en serio

- Mirá los YAML antes de mirar el ranking. Si el puntaje está inflado, el ranking también.
- Fijate que Bruma gana por poco: 3.70 contra 3.62. Con subir 0.031 el peso de tiempo-hasta-valor, gana Vendor A.
- El VPN base del escritorio de reembolsos salió **USD 180,923.12** el 2026-10-17 con el comando de `docs/results/refund_desk.json`, y el escenario pesimista **no se paga nunca**.
- No hay datos de un cliente. Puerto Gris, Bruma y Cedro están inventadas.
- El precio por token del YAML de ROI es ilustrativo. No es una lista de un proveedor.
- Un puntaje de seguridad registra lo que dicen las notas ficticias del caso. No es una certificación.
- El Excel tiene fórmulas vivas, pero este repo no las ejecuta.
- No predice la cola, ni el SLA, ni si la gente va a usar la herramienta.
- No decide. Vos decidís.

## Cómo mostrarlo en cinco minutos

1. Corré `python -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/bruma.md`.
2. Mostrá el ranking y la frase de desacuerdo entre matriz y caja.
3. Mostrá el flip de time-to-value (+0.031).
4. Corré `python -m roi_and_build_vs_buy roi demo` y mostrá el payback del escritorio de reembolsos al lado del escenario que no se paga.
5. Corré `python -m roi_and_build_vs_buy.evalkit.decide_regression` y mostrá que sale con error `golden_winner`. Ese rojo es la prueba de que la regresión puede fallar.
