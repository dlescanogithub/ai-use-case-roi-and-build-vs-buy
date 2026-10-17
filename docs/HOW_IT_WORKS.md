# Cómo funciona (en criollo)

Esto es un calculador. No es un agente que habla con clientes y no llama a ningún modelo pago. Sirve para sentarte en una entrevista y explicar, sin humo, cómo se mira el ROI de un caso de uso de IA.

## Analogía

Pensalo como arreglar una canilla que gotea.

- La implementación es la plata y las horas que ponés el primer día (el plomero, las piezas).
- El ahorro mensual es el agua que dejás de tirar, menos lo que te cuesta el repuesto que se gasta.
- El recupero (payback) es cuántos meses tardás en juntar de nuevo lo que gastaste al principio.
- El volumen de equilibrio es cuántos baldes tenés que ahorrar por mes para que el arreglo no te deje pérdida, sin contar todavía el gasto del primer día.
- La sensibilidad es mover una perilla: ¿y si la canilla gotea menos de lo que creías? ¿y si el plomero sale el doble? El gráfico tornado muestra qué perilla mueve más el resultado.
- El Monte Carlo es tirar los dados muchas veces, con un rango para cada perilla, y mirar el percentil 10, el 50 y el 90. No es una promesa. Es un barrido.

Fijate: si la revisión humana se come casi todo el tiempo que “ahorrabas”, la canilla sigue goteando. El modelo mete ese tiempo adentro, no en una nota al pie.

## Paso a paso

1. Abrís un YAML de supuestos. Cada número tiene una razón y tiene que decir `[EST]`, porque es una estimación, no una medición.
2. El cargador rechaza tasas fuera de 0 a 1, costos negativos y un archivo que no es claramente ficticio (`fictional: true`).
3. Por cada ítem calcula:
   - costo manual = minutos de trabajo × costo horario / 60 + errores manuales × costo de un error
   - costo del agente = tokens × precio ilustrativo (o un costo medido si pasás un archivo) + minutos de revisión × tasa de revisión
   - ahorro ajustado por calidad = costo manual − costo del agente − costo del error que igual queda
4. El volumen del mes es ítems por día × días hábiles, o ítems por mes si el caso está escrito así.
5. El ahorro neto del mes, en régimen, es volumen × ahorro por ítem − costo fijo mensual. El costo fijo se paga entero desde el mes 1, aunque la adopción vaya a mitad.
6. La adopción sube en línea durante los meses de rampa y después se queda en 1.
7. El payback mira el acumulado. Si en régimen el mes no suma plata y hubo costo de implementación, dice **nunca**, con una frase, no un número mágico.
8. El VPN a 3 años descuenta esos flujos. La implementación está en el mes 0.
9. El tornado mueve un supuesto a la vez a su piso y a su techo. Los escenarios pesimista / base / optimista cambian varios juntos. El Monte Carlo usa una semilla, así que la misma semilla da los mismos percentiles.
10. Escribe Markdown, HTML, un SVG, un CSV con valores y un XLSX con fórmulas. No manda mails ni aprueba nada.

## Glosario

| Palabra | Qué quiere decir acá |
| --- | --- |
| [EST] | Supuesto. No salió de un sistema real |
| Simulado | Lo calculó este programa a partir de esos supuestos |
| Ahorro ajustado por calidad | El ahorro después de restar el costo de los errores que el agente todavía comete |
| Costo por ítem terminado | Corrida del agente + tiempo de quien revisa. Sin el error residual, que va en el ajuste de calidad |
| Volumen de equilibrio | Ítems por mes donde el ahorro neto del mes es cero. No incluye la implementación |
| Payback | Meses hasta recuperar la implementación. Puede ser “nunca” |
| VPN | Valor presente neto de los flujos del horizonte, menos la implementación |
| Tornado | Qué supuesto, movido solo, cambia más el VPN |
| Casete | Respuesta grabada. Si no está el id, falla. No hay llamada en vivo |
| Ranura de costo medido | Un archivo aparte puede reemplazar tokens × precio. Un stub no se aplica |

## Límites honestos

- Mirá los supuestos antes de repetir el número. El VPN base del escritorio de reembolsos salió **USD 180,923.12** el 2026-10-17 con el comando de `docs/results/refund_desk.json`, y el escenario pesimista **no se paga nunca**. Los dos salen del mismo programa.
- No hay datos de un cliente. Puerto Gris Parcel Co. está inventada.
- El precio por token del YAML es ilustrativo. No es una lista de un proveedor.
- El Excel tiene fórmulas vivas, pero este repo no las ejecuta. Las chequea un humano abriendo el archivo.
- No predice la cola, ni el SLA, ni si la gente va a usar la herramienta. La rampa es un supuesto.
- No decide. Vos decidís.

## Qué no hace

La lista larga está en el README, sección “What this does NOT do”. En corto: no llama a un proveedor, no se conecta a datos vivos, no aprueba un gasto y no muestra un tablero.
