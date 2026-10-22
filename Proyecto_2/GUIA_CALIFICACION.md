# Guía de defensa y demostración

Sergio Sandoval · 202010298. Consultar también `AUDITORIA_ENUNCIADO.md` y `MANUAL_TECNICO.md`.

## Antes de tu turno

1. Abrir `Proyecto2_202010298.pkt` en Packet Tracer 9.0.1 o compatible. El enunciado permite 8.2 o superior, pero un archivo guardado por 9.0.1 puede no abrir en 8.2: usar la versión validada.
2. Esperar convergencia. En la prueba de reapertura corregida, los 20 hosts obtuvieron DHCP automáticamente durante una observación de aproximadamente 2 min 22 s; reservar al menos tres minutos y comprobar el estado, sin asumir un tiempo fijo en otra computadora. Revisar enlaces verdes, BGP Established con prefijos recibidos, vecinos OSPF FULL y vecinos EIGRP presentes. No apagar toda la topología inmediatamente antes de evaluar.
3. Revisar `ipconfig /all` en las PC y laptop: IP dinámica, máscara, gateway y DNS `192.168.98.242`. No reemplazar DHCP por IP estática.
4. Confirmar que AC-R4 y AC-R5 están encendidos, ambos miembros de cada LACP restaurados y el dominio abre por HTTP y HTTPS.
5. Tener abiertos el PDF de presentación, el manual y la captura `.pcapng` en Wireshark. El archivo de Wireshark se abre también desde Windows; la VM acredita su origen y se conserva en el workspace.
6. Ensayar el guion de 7 min 20 s. El tiempo permitido es 5–10 min. Las explicaciones orales dependen de tu preparación.

## Único intento de ping durante la calificación

El enunciado permite un intento para demostrar comunicación entre topologías. Antes del turno, estabilizar ARP y rutas con pruebas de preparación; durante el intento formal, ejecutar solo el ping solicitado por el auxiliar. No prometer que un equipo recién reiniciado nunca perderá el primer paquete por ARP o convergencia.

Si el destino es Seguridad y el origen otro departamento, el bloqueo es el resultado correcto. Seguridad sí puede iniciar hacia los otros cinco. Atención al Cliente y Facturación se bloquean mutuamente. No interpretar un bloqueo esperado como una avería general.

## Recorrido técnico sugerido

| Demostración | Equipo / acción | Qué explicar |
|---|---|---|
| Inter-ISP | FG-R1, AC-R1, ML-R1: `show ip bgp summary`, `show ip bgp` | AS 65001/65002/65003, dos vecinos por borde, prefijos aprendidos y AS_PATH |
| FibraNet | FG-R1: `show ip ospf neighbor` | Árbol de cinco routers, área 0, OSPF y subredes /25 |
| AndinaCom | AC-R1: `show ip ospf neighbor`; AC-R4/R5: `show standby brief` | Jerarquía, rutas de respaldo, gateways virtuales .1 y .65 |
| MoonLink | ML-R1: `show ip eigrp neighbors` | Hub con cuatro spokes, AS EIGRP 100, /26 y WiFi |
| Agregación | AC-SW1 y switches departamentales: `show etherchannel summary` | Dos grupos por ISP, LACP y miembros `(P)`, Port-channel `(SU)` |
| DHCP central | AC-R5: `show ip dhcp pool`, `show ip dhcp binding` | Relay `ip helper-address`, selección del pool por subred, gateway y DNS |
| Sitio | Navegador de una PC: `http://www.proyecto2_202010298.com/` y `https://www.proyecto2_202010298.com/` | DNS primero, luego TCP/80 o TCP/443; datos del estudiante y curso |
| WiFi | ML-SOP-LAP1: Wireless0 e IP dinámica | WRT como puente LAN; DHCP local apagado; concesión de AndinaCom |
| Políticas | `show access-lists` y pruebas permitidas/bloqueadas | ACL extendidas inbound en gateways; precedencia de Seguridad y excepciones de servicios |

## Demostración HSRP controlada

Primero mostrar roles estables: VLAN 30 activa en AC-R4 y VLAN 40 activa en AC-R5. Apagar AC-R4, esperar que AC-R5 sea activo para ambos grupos y demostrar ping al servidor desde Ventas. Volver a encender AC-R4 y esperar preemption. La prueba registrada obtuvo 4/4 después de conmutar; no demuestra cero pérdida durante el intervalo de detección.

HSRP protege el gateway, no sincroniza DHCP. Si falla AC-R5, las concesiones ya vigentes continúan utilizándose mientras haya rutas, pero no se obtienen nuevas concesiones desde ese servidor hasta restaurarlo. El enunciado exige HSRP; no exige un clúster DHCP. No presentar el diseño como tolerante a cualquier falla de cualquier equipo.

## Modo simulación: paquete elegido por el evaluador

Cambiar a Simulation, filtrar el protocolo, generar tráfico y usar Capture/Forward. Abrir el sobre y revisar OSI Model e Inbound/Outbound PDU Details. Volver a Realtime al terminar. Los filtros solo controlan qué eventos se muestran, no son ACL.

| Protocolo | Capas y campos que debes identificar |
|---|---|
| DHCP DORA | Ethernet broadcast del cliente sin IP; IPv4 0.0.0.0→255.255.255.255 al iniciar; UDP 68→67; Discover, Offer, Request, ACK. El relay agrega giaddr y permite que AC-R5 seleccione el pool. El retorno al relay no conserva necesariamente el mismo par de direcciones/puertos del broadcast inicial. |
| DNS | Ethernet hacia el siguiente salto; IPv4 al servidor .242; normalmente UDP con puerto destino 53; identificador de transacción, nombre, registro A y TTL de caché. TCP/53 también está permitido para DNS. |
| HTTP | Ethernet/IPv4/TCP; handshake SYN, SYN-ACK, ACK; puerto 80; GET, Host y respuesta 200. Las cabeceras y el contenido están visibles. |
| HTTPS | Ethernet/IPv4/TCP; puerto 443; TLS negocia la sesión y protege HTTP. No confundir el handshake TCP con el handshake TLS. Packet Tracer simplifica el protocolo; usar la captura real para explicar ClientHello, certificado y datos cifrados. |
| OSPF | Ethernet; IPv4 protocolo 89, sin puertos TCP/UDP; Hello, Router ID, área, vecinos y LSAs. Los enlaces internos /30 usan tipo point-to-point: no eligen DR/BDR, aunque el medio sea Ethernet. Identificar el multicast 224.0.0.5 cuando aparezca. |
| EIGRP | Ethernet; IPv4 protocolo 88, sin puertos TCP/UDP; Hello y Update, AS 100, vecinos y métrica. Multicast usual 224.0.0.10. |
| BGP | Ethernet/IPv4/TCP; servicio TCP/179; OPEN, KEEPALIVE y UPDATE; AS local/remoto, prefijos y AS_PATH. Un vecino estable puede mostrar solo KEEPALIVE hasta que cambien rutas. |

En un switch de capa 2 cambia el puerto de salida según MAC/VLAN; no se decrementa TTL. Un router consulta la ruta, decrementa TTL y construye otra cabecera Ethernet para el siguiente salto. Los puertos TCP/UDP identifican aplicaciones; los números 88/89 son identificadores de protocolo IP.

## Wireshark: cuatro escenarios reales

Abrir `Wireshark/captura_wireshark_202010298.pcapng`: 42 tramas. TCP 1–3, consulta/respuesta DNS 10/13, HTTP GET/200 en 4/6, TLS ClientHello 17, ServerHello 19, certificado 20 y Application Data 26/28. ICMP: cuatro pares con secuencias 1–4. Las cifras pertenecen a este archivo; no copiarlas a una captura nueva.

Los números TCP mostrados son relativos: SYN usa SEQ 0, SYN-ACK ACK 1 y el ACK final SEQ/ACK 1. El TTL de DNS expresa vigencia de caché; el de IP limita el tránsito. ICMP no tiene puertos. La VM utiliza NAT: la MAC de destino de una trama saliente es la del siguiente salto local, no la del servidor público.

## Preguntas de diseño

- **¿Por qué /25 en FibraNet?** /26 ofrece 62 hosts y no alcanza 75. /25 ofrece 126; dos /25 consumen exactamente el /24.
- **¿Por qué /26 en MoonLink?** 62 direcciones útiles, 53 concesiones tras excluir nueve para infraestructura; soporta 45 clientes por departamento.
- **¿Por qué direcciones estáticas en routers?** La restricción se refiere a dispositivos finales; la infraestructura necesita direcciones estables para adyacencias, relay y gateways. Los 20 hosts finales usan DHCP, incluido el servidor.
- **¿Por qué una ruta Null0?** Origina el agregado local para BGP; las rutas departamentales más específicas prevalecen. No sustituye DHCP ni configura IP estática en clientes.
- **¿Por qué no se permite iniciar hacia Seguridad?** La prohibición específica prevalece sobre los permisos generales de Administración y Soporte. Se permiten respuestas a sesiones iniciadas desde Seguridad. Es una interpretación documentada de una tabla con reglas superpuestas.
- **¿`established` es un firewall con estado?** No. Comprueba ACK/RST, no mantiene una tabla completa de conexiones.
- **¿Por qué el servidor cambia de IP por DHCP?** Su pool /30 tiene una única dirección disponible, .242; el gateway .241 está excluido. Obtiene esa dirección dinámicamente de AndinaCom.
- **¿LACP duplica la velocidad de una sola sesión?** No necesariamente. Agrega capacidad entre flujos y tolera la falla de un miembro; el balanceo puede asignar una sesión a un solo enlace.

## Cierre administrativo

Publicar los commits del Proyecto 2 en el repositorio original, comprobar que el auxiliar tenga acceso y entregar el enlace por UEDI antes del 23/10/2026. El PDF no especifica hora de cierre ni identifica al auxiliar: muestra `XXXX`. Consultar esos datos en UEDI/avisos del curso. El objetivo menciona calificación el 24/10 y el cronograma indica 24–28/10; respetar el turno oficial. No borrar ni bloquear la celda de otra persona: el enunciado establece una penalización del 25% de la nota final.
