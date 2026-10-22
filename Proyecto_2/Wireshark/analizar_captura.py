"""Generate an analysis from fields exported by Tshark from the actual PCAPNG."""
import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
P=Path(__file__).resolve().parent
rows=[r['_source']['layers'] for r in json.loads((P/'paquetes.json').read_text())]
def get(r,k,default=''):
 v=r.get(k,[])
 return v[0] if isinstance(v,list) and v else (v if v else default)
def vals(r,k):return r.get(k,[])
def frame(r):return int(get(r,'frame.number'))
def boolval(r,k):return get(r,k).lower() in ['true','1']
def first(predicate):return next(r for r in rows if predicate(r))
http=first(lambda r:get(r,'http.host')=='example.com' and get(r,'http.request.method')=='GET')
stream=get(http,'tcp.stream')
syn=first(lambda r:get(r,'tcp.stream')==stream and boolval(r,'tcp.flags.syn') and not boolval(r,'tcp.flags.ack'))
synack=first(lambda r:get(r,'tcp.stream')==stream and boolval(r,'tcp.flags.syn') and boolval(r,'tcp.flags.ack'))
ack=first(lambda r:get(r,'tcp.stream')==stream and frame(r)>frame(synack) and not boolval(r,'tcp.flags.syn') and boolval(r,'tcp.flags.ack') and get(r,'tcp.len')=='0')
response=first(lambda r:get(r,'tcp.stream')==stream and get(r,'http.response.code')=='200')
query=first(lambda r:get(r,'ip.dst')=='1.1.1.1' and get(r,'dns.qry.type')=='1' and get(r,'dns.flags.response')=='False')
answer=first(lambda r:get(r,'ip.src')=='1.1.1.1' and get(r,'dns.id')==get(query,'dns.id') and get(r,'dns.flags.response')=='True')
clienthello=first(lambda r:'1' in vals(r,'tls.handshake.type'))
tlsstream=get(clienthello,'tcp.stream')
serverhello=first(lambda r:get(r,'tcp.stream')==tlsstream and '2' in vals(r,'tls.handshake.type'))
certificate=first(lambda r:get(r,'tcp.stream')==tlsstream and '11' in vals(r,'tls.handshake.type'))
application=[r for r in rows if get(r,'tcp.stream')==tlsstream and '23' in vals(r,'tls.record.content_type')]
requests=[r for r in rows if get(r,'ip.dst')=='1.1.1.1' and get(r,'icmp.type')=='8']
replies=[r for r in rows if get(r,'ip.src')=='1.1.1.1' and get(r,'icmp.type')=='0']
assert len(requests)==4 and len(replies)==4
assert application and get(clienthello,'tls.handshake.version')=='0x0303'
assert frame(syn)<frame(synack)<frame(ack)<frame(http)
assert vals(answer,'dns.a')
capture=P/'captura_wireshark_202010298.pcapng'
assert capture.read_bytes()[:4]==b'\x0a\x0d\x0d\x0a'
digest=hashlib.sha256(capture.read_bytes()).hexdigest()
local=datetime.fromtimestamp(float(get(rows[0],'frame.time_epoch')),timezone(timedelta(hours=-6)))
summary=dict(file=capture.name,sha256=digest,packets=len(rows),vm_ip=get(syn,'ip.src'),http_stream=int(stream),tls_stream=int(tlsstream),tcp_handshake=[frame(syn),frame(synack),frame(ack)],dns=[frame(query),frame(answer)],http=[frame(http),frame(response)],tls_clienthello=frame(clienthello),tls_serverhello=frame(serverhello),tls_certificate=frame(certificate),tls_application_frames=[frame(r) for r in application],icmp_requests=[frame(r) for r in requests],icmp_replies=[frame(r) for r in replies])
(P/'resumen_validacion.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

lines=['# Análisis de tráfico real con Wireshark','','Sergio Sandoval · Carné 202010298 · Redes de Computadoras 2 · Proyecto 2','','## Procedencia y validación','',
f'- Archivo: `{capture.name}`. Formato pcapng verificado con Capinfos y mediante su cabecera binaria.',
f'- Contiene **{len(rows)} tramas reales**. Primera trama: **{local.strftime("%Y-%m-%d %H:%M:%S %z")}**, hora de Guatemala.',
f'- SHA-256: `{digest}`.',
'- Captura realizada con Dumpcap/Tshark de Wireshark 4.2.2 dentro de Ubuntu 24.04, ejecutado en VMware Workstation. `systemd-detect-virt` devolvió `vmware`.',
f'- Interfaz capturada: `ens64`, dirección `{get(syn,"ip.src")}`. La VM usa exclusivamente un adaptador NAT, con gateway `192.168.163.2`.',
'- Se limitó la captura a la VM y los destinos de prueba. Se excluyen la administración SSH, las descargas de actualizaciones y las interfaces de Windows. El filtro exacto se conserva en `entorno_vm.txt`.',
'- Los paquetes se generaron durante la captura mediante curl, dig y ping. No se construyeron paquetes artificiales ni se utilizó una captura ajena.',
'- `capinfos.txt`, `paquetes.json` y `escenarios.log` permiten contrastar las cifras y comandos. Las imágenes muestran la interfaz gráfica real de Wireshark ejecutándose en una pantalla virtual dentro de la VM.','','## 1. Three-way handshake TCP','',
f'Flujo `tcp.stream == {stream}`: `{get(syn,"ip.src")}:{get(syn,"tcp.srcport")} → {get(syn,"ip.dst")}:80`. Wireshark muestra números de secuencia relativos:','',
'| Trama | Dirección | Flags | SEQ | ACK |','|---|---|---|---:|---:|']
for r,label,flags in [(syn,'Cliente a servidor','SYN'),(synack,'Servidor a cliente','SYN, ACK'),(ack,'Cliente a servidor','ACK')]:
 lines.append(f'| {frame(r)} | {label} | {flags} | {get(r,"tcp.seq")} | {get(r,"tcp.ack")} |')
lines += ['',
'El SYN anuncia el inicio de la conexión. SYN-ACK reconoce ese inicio y anuncia el del servidor. El ACK final confirma ambos extremos. Un SYN consume una posición de la secuencia, por eso el reconocimiento avanza a 1 aunque todavía no se hayan enviado datos de aplicación.',
f'En capa 2, la trama de salida usa MAC origen `{get(syn,"eth.src")}` y destino `{get(syn,"eth.dst")}`, correspondiente al siguiente salto de la red NAT. En capa 3, IPv4 conserva el destino público `{get(syn,"ip.dst")}`. En capa 4, TCP utiliza un puerto efímero de cliente y el puerto 80 del servicio.',
f'Filtro: `tcp.stream == {stream}`.','','![Three-way handshake TCP](01_tcp_handshake.png)','','## 2. Resolución DNS','',
f'La consulta explícita `dig @1.1.1.1 example.com A` aparece en las tramas **{frame(query)} y {frame(answer)}**. El identificador DNS compartido es `{get(query,"dns.id")}`.',
f'- Consulta: `{get(query,"ip.src")}:{get(query,"udp.srcport")} → 1.1.1.1:53`, transporte UDP.',
f'- Nombre: `{get(query,"dns.qry.name")}`. Tipo de registro: **A (1)**, una dirección IPv4.',
f'- Direcciones de respuesta: **{", ".join(vals(answer,"dns.a"))}**.',
f'- TTL observado de los registros A: **{", ".join(vals(answer,"dns.resp.ttl"))} segundos**. Es tiempo de caché DNS, distinto del TTL de la cabecera IP.',
'UDP no establece un three-way handshake. El cliente utiliza el identificador de la consulta y el par de puertos para relacionar la respuesta. Ethernet e IPv4 transportan el datagrama UDP hasta el servidor DNS.',
f'Filtro: `dns.id == {get(query,"dns.id")}`.','','![Consulta y respuesta DNS](02_dns.png)','','## 3. HTTP frente a HTTPS','',
f'**HTTP:** la trama **{frame(http)}** muestra `GET {get(http,"http.request.uri")}` con Host `{get(http,"http.host")}`. La trama **{frame(response)}** contiene estado **200 OK**. El flujo usa TCP/80 y Wireshark puede interpretar directamente las cabeceras HTTP y el cuerpo sin claves de descifrado.',
f'**HTTPS:** el flujo `tcp.stream == {tlsstream}` usa TCP/443. Se forzó TLS 1.2 con `curl --tls-max 1.2` para poder observar el intercambio de certificado en el handshake. El ClientHello está en la trama **{frame(clienthello)}**, el ServerHello en **{frame(serverhello)}** y el certificado en **{frame(certificate)}**. Algunas de estas estructuras pueden compartir una misma trama.',
f'Wireshark identifica versión de handshake `0x0303`, correspondiente a **TLS 1.2**. Las tramas de Application Data cifrada son **{", ".join(str(frame(r)) for r in application)}**.',
'El servidor presenta su certificado y ambos extremos negocian claves de sesión. A continuación TLS protege los datos HTTP mediante cifrado autenticado. Las direcciones IP, los puertos y parte del handshake siguen visibles. El método, cabeceras y contenido HTTP de la sesión HTTPS no aparecen legibles en la captura sin las claves de sesión. El 200 OK de HTTPS está confirmado por curl en `escenarios.log`; no se inventa una trama HTTP legible dentro del flujo cifrado.',
'La pila en este caso es Ethernet, IPv4, TCP, TLS y HTTP protegido por TLS. TLS se sitúa sobre TCP y protege el protocolo de aplicación.',
f'Filtros: `tcp.stream == {stream}` para HTTP y `tcp.stream == {tlsstream}` para HTTPS.','','![HTTP en texto claro](03_http.png)','','![Handshake TLS y datos cifrados](04_https_tls.png)','','## 4. ICMP Echo Request y Echo Reply','',
'Se ejecutó `ping -c 4 -W 3 1.1.1.1`. La captura contiene cuatro solicitudes y cuatro respuestas, sin pérdida. ICMP pertenece a la capa de red y no utiliza puertos TCP o UDP. Echo Request usa tipo 8/código 0 y Echo Reply tipo 0/código 0.','',
'| Secuencia | Trama Request | Trama Reply | Identificador | RTT observado | TTL del Reply |','|---:|---:|---:|---:|---:|---:|']
for q in requests:
 a=first(lambda r:get(r,'icmp.type')=='0' and get(r,'icmp.ident')==get(q,'icmp.ident') and get(r,'icmp.seq')==get(q,'icmp.seq'))
 rtt=(float(get(a,'frame.time_relative'))-float(get(q,'frame.time_relative')))*1000
 lines.append(f'| {get(q,"icmp.seq")} | {frame(q)} | {frame(a)} | {get(q,"icmp.ident")} | {rtt:.3f} ms | {get(a,"ip.ttl")} |')
lines += ['',
'El identificador y la secuencia permiten emparejar cada respuesta con su solicitud. El RTT se calculó restando las marcas de tiempo de las tramas correspondientes. El TTL observado pertenece a IPv4 y no debe interpretarse como TTL de DNS ni como una medida exacta del número de saltos sin conocer el valor inicial.',
'Filtro: `icmp && ip.addr == 1.1.1.1`.','','![ICMP Request y Reply](05_icmp.png)','','## Guion de demostración','',
'1. Abrir el archivo `.pcapng` en Wireshark y confirmar que Capinfos lo identifica como pcapng/Ethernet.',
f'2. Filtrar `tcp.stream == {stream}` y señalar las tres tramas del handshake y el GET HTTP.',
f'3. Aplicar `dns.id == {get(query,"dns.id")}` y comparar puertos, tipo A y TTL de caché.',
f'4. Filtrar `tcp.stream == {tlsstream}` y distinguir los mensajes de handshake de TLS Application Data.',
'5. Filtrar ICMP y emparejar cada solicitud y respuesta mediante identificador y secuencia.',
'6. Explicar las capas de cada protocolo. La captura de la VM es distinta de la simulación de BGP, OSPF/EIGRP y DHCP de Packet Tracer.','']
(P/'ANALISIS_WIRESHARK.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(summary,indent=2))
