import json,re
from pathlib import Path
from build_project import OUT

ev=OUT/'evidencias'
hosts=json.loads((ev/'hosts_dhcp.json').read_text())
matrix=json.loads((ev/'matriz_ping.json').read_text(encoding='utf-8'))
web=json.loads((ev/'pruebas_web.json').read_text())
acl=json.loads((ev/'pruebas_acl_web.json').read_text())['tests']
lacp=json.loads((ev/'prueba_lacp.json').read_text())
hsrp=json.loads((ev/'prueba_hsrp.json').read_text())
assert len(hosts)==20 and all(h['dhcp'] and h['ip'] not in ['0.0.0.0',''] and not h['ip'].startswith('169.254') for h in hosts)
assert len(matrix)==30 and all((r['received']==4 if r['expected'] else r['received']==0) for r in matrix)
assert len(web)==14 and all(r['ok'] for r in web)
assert len(acl)==24 and all(r['passed'] for r in acl)
assert len(lacp['pings'])==6 and not lacp['timeouts']
assert all('Received = 4' in p['output'] for p in lacp['pings'])
assert 'Received = 4' in hsrp['ping_after_failover'] and not hsrp.get('error')

lines=['# Resultados verificados en Packet Tracer','','Estas pruebas provienen del simulador. La [captura Wireshark de la VM](../Wireshark/ANALISIS_WIRESHARK.md) está completa y documenta por separado TCP, DNS, HTTP/HTTPS e ICMP con 42 tramas reales.','','| Comprobación | Resultado | Evidencia |','|---|---|---|',
 '| DHCP | 20 de 20 hosts finales con concesión dinámica válida | `hosts_dhcp.json` |',
 '| ACL ICMP | 30 de 30 pares dirigidos coinciden con la política | `matriz_ping.json` |',
 '| Web central | 14 de 14: HTTP y HTTPS desde seis departamentos y la laptop | `pruebas_web.json` |',
 '| ACL TCP | 24 de 24 casos HTTP/HTTPS departamentales coinciden con la política | `pruebas_acl_web.json` |',
 '| HSRP | Apagado real de AC-R4, toma de rol por AC-R5 y ping 4/4 | `prueba_hsrp.json` |',
 '| LACP | Un miembro fuera de servicio en cada uno de seis grupos, seis pings 4/4 | `prueba_lacp.json` |','','## Direcciones realmente concedidas','','| Host | Interfaz | Dirección | Máscara | DHCP |','|---|---|---|---|---|']
for h in hosts:lines.append(f'| {h["name"]} | {h["interface"]} | {h["ip"]} | {h["mask"]} | Sí |')
names=['FG-ADM-PC1','FG-ATC-PC1','AC-VEN-PC1','AC-FAC-PC1','ML-SOP-PC1','ML-SEG-PC1']
short=['ADM','ATC','VEN','FAC','SOP','SEG']
lines+=['','## Matriz final de ping','','Filas: origen. Columnas: destino. `4/4` indica cuatro respuestas; `0/4` es un bloqueo esperado. No se presentan los bloqueos como pérdidas accidentales.','','| Origen | '+' | '.join(short)+' |','|---|'+'---|'*6]
for n,s in zip(names,short):
 cells=[]
 for dest in names:
  r=next((r for r in matrix if r['source']==n and r['destination']==dest),None)
  cells.append('-' if not r else str(r['received'])+'/4')
 lines.append('| '+s+' | '+' | '.join(cells)+' |')
lines+=['','Las repeticiones de las pruebas que presentaron pérdida durante convergencia o resolución ARP se conservan en `previous_attempts`. La tabla muestra la ejecución final después de estabilizar la red.','','## Pruebas HTTP/HTTPS de ACL','','Se crearon temporalmente seis Server-PT departamentales, con DHCP y servicios reales HTTP/HTTPS. Se usó una página distinta por destino para distinguir una respuesta nueva de contenido anterior en el cliente. Tras las pruebas se retiraron esos seis equipos. Los 20 hosts de la entrega no incluyen esos servidores temporales.','','| Origen | Destino | Protocolo | Esperado | Recibió página | Cumple |','|---|---|---|---|---|---|']
for r in acl:lines.append(f'| {r["source"]} | {r["destination"]} | {r["protocol"].upper()} | {"Permitir" if r["expected"] else "Bloquear"} | {"Sí" if r["received"] else "No"} | Sí |')
lines+=['','## Recuperación y persistencia','','Todos los puertos usados para la prueba LACP se restauraron. AC-R4 se volvió a encender después de la prueba HSRP. La configuración efectiva se exportó en `../configs_aplicadas/`; el archivo `.pkt` se guardó después de restaurar los equipos.','','## Ajustes detectados durante la validación','','- Packet Tracer 9.0.1 utiliza el tipo de conexión óptica 8117 para estos módulos. El tipo `fiber` del MCP instalado usa un valor anterior y no creó los enlaces. Se identificó el tipo real mediante una conexión automática y se recrearon los enlaces previstos.','- Se enviaron los comandos mediante `CiscoDevice.enterCommand`, la API de la CLI. Así se evitó el error de análisis del helper que recibe bloques multilínea.','- Se permitieron específicamente los mensajes HSRP entre los dos gateways en las ACL de AndinaCom. Sin esa excepción ambos podían considerarse activos.','- Se asignaron costos OSPF diferentes a los enlaces redundantes de AndinaCom para obtener rutas principales y de respaldo deterministas.','- Se desactivó el DHCP del WRT300N. La laptop usa el SSID de laboratorio `Default`, se colocó dentro de la cobertura física y obtiene su concesión desde AC-R5.','','## Captura real de la topología','','![Topología completa](topologia_completa.png)','']
(ev/'RESULTADOS.md').write_text('\n'.join(lines),encoding='utf-8')
print('Verified all evidence and wrote RESULTADOS.md')
