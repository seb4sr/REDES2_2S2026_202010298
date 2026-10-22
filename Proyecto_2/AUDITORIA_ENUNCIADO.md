# Auditoría exhaustiva del enunciado

**Estudiante:** Sergio Sandoval, 202010298. **Revisión:** 22/10/2026, Guatemala.

**Dictamen:** la configuración técnica dispone de pruebas satisfactorias, pero la entrega no debe marcarse como cerrada mientras falten las capturas de pantalla de comunicación en Packet Tracer, la publicación de los commits, la verificación del acceso del auxiliar y la entrega puntual en UEDI. La exposición y la evaluación oral se realizan durante la calificación y no se pueden dar por aprobadas a partir de los archivos.

Se revisaron las 18 páginas de `975_Proyecto_2_2S2026.pdf`, incluyendo las tablas, el dibujo de interconexión de la página 5, la política de la página 7, las condiciones de acceso a calificación y cada criterio de la rúbrica. Las instrucciones del documento se usan como criterios de esta auditoría; no equivalen a autorización para publicar o presentar la entrega en nombre del estudiante.

## 1. Condiciones que pueden dejar la nota en cero

La sección 8.1, página 13, indica cero puntos si no se cumplen sus condiciones previas. No basta con sumar el resto de la rúbrica.

| Condición | Estado | Evidencia o acción necesaria |
|---|---|---|
| Entrega puntual en UEDI | **Pendiente de acreditar** | Fecha límite 23/10/2026. El PDF no especifica hora. Entregar y conservar comprobante. |
| Todos los dispositivos finales por DHCP | Verificado | 20/20: 18 PC, una laptop y el servidor DNS/WEB. `evidencias/hosts_dhcp.json`, opciones y pruebas adicionales en `auditoria_web_40.json`. |
| DNS y HTTP/HTTPS desde la topología | Verificado mediante pruebas | Dominio exacto `www.proyecto2_202010298.com`; acceso por ambos protocolos con páginas nuevas. `pruebas_web.json` y `auditoria_web_40.json`. |
| HSRP con conmutación efectiva | Verificado | `prueba_hsrp.json`: activo/respaldo antes de falla, apagado de AC-R4, AC-R5 activo y ping 4/4 tras el cambio. Roles actuales también comprobados. |
| Captura `.pcapng` en el repositorio y abrible | Archivo local verificado; **publicación pendiente** | Nombre y ruta exactos en `Wireshark/`. Cabecera pcapng, Capinfos, apertura real en Wireshark y SHA-256 documentados. |
| Configuración desde CLI | Evidencia de implementación conforme | Routers y switches configurados mediante comandos IOS usando `CiscoDevice.enterCommand`. Scripts, registros y 26 configuraciones efectivas incluidos. Servicios de hosts y WRT sin CLI IOS se configuran mediante sus procesos nativos. |

## 2. Trazabilidad de todos los requisitos técnicos

| Sección y página | Requisito | Verificación y resultado |
|---|---|---|
| 2.1, 4; 4.1.1, 5 | Tres ISP y BGP entre bordes | FibraNet GT/AS65001, AndinaCom/AS65002 y MoonLink/AS65003; triángulo como el dibujo. Dos vecinos establecidos por borde y prefijos recibidos. |
| 4.1.1, 5 | Red de interconexión según últimos dos dígitos | Carné termina en 98. Diecisiete enlaces /30 dentro de `192.168.98.0/24`, contenido en el /16 normalizado. Tabla por interfaz y enlace incluida. |
| 4.1.1, 5 | Fibra óptica entre routers | Los 17 enlaces se consultaron en vivo: tipo óptico real 8117 en Packet Tracer 9.0.1. `auditoria/estado_cli.json`. |
| 4.1.2, 5–6 | FibraNet: red 172.16.1X.0/24, X último dígito | X=8 → `172.16.18.0/24`. Administración y Atención: dos /25 sin solapamiento. |
| 4.1.2, 5 | Soportar 75 hosts por subred | /25: 126 útiles; 107 concesiones tras exclusiones de infraestructura. /26 no alcanzaría. |
| 4.1.2, 6 | Árbol, OSPF, cinco routers, cinco hosts, dos LACP | Cinco routers con cuatro enlaces internos en árbol; OSPF área 0 con vecinos FULL; seis PC más servidor; dos Port-channel LACP independientes de dos miembros. |
| 4.1.2, 6; 2.1, 16 | FibraNet presta DNS, HTTP y HTTPS | Servidor en FG-R3, IP .242 concedida por DHCP de AndinaCom. Registro A y página propios, ambos servicios habilitados y probados. |
| 4.1.3, 6 | AndinaCom: 172.16.2X.0/24, dos departamentos | X=8 → `172.16.28.0/24`; Ventas `.0/26`, Facturación `.64/26`. Tamaño permitido a discreción; dos /26 adicionales libres. |
| 4.1.3, 6 | Modelo jerárquico, OSPF, cinco routers y cinco hosts | Núcleo, dos routers de distribución y dos gateways; cinco routers, seis PC; OSPF con rutas principales y respaldo. |
| 4.1.3, 6 | Dos LACP en AndinaCom | Po1 SW1↔SW2 y Po2 SW1↔SW3, dos miembros activos por grupo. |
| 4.1.3, 6 | Redundancia obligatoria HSRP | Dos gateways para ambas VLAN, prioridades, preemption y tracking. Prueba real de apagado y restauración. |
| 4.1.3, 6; 4.4, 8 | DHCP de toda la topología desde AndinaCom | Siete pools en AC-R5 y relay en gateways. WRT sin DHCP local. Todos los hosts finales dinámicos, incluido servidor. |
| 4.1.4, 6 | MoonLink: 172.16.3X.0/24, X primer dígito | Primer dígito 2 → `172.16.32.0/24`; Soporte `.0/26`, Seguridad `.64/26`. |
| 4.1.4, 6 | Soportar 45 hosts por departamento | /26: 62 útiles y 53 concesiones tras excluir nueve direcciones de infraestructura. |
| 4.1.4, 6 | Hub-and-spoke, EIGRP, cinco routers y cinco hosts | ML-R1 hub con cuatro spokes; EIGRP AS100, vecinos presentes; seis PC más laptop y WRT adicional. |
| 4.1.4, 6 | Dos LACP y al menos un router inalámbrico funcional | Dos Port-channel de dos miembros; WRT300N como puente LAN, laptop asociada y con DHCP central. |
| 4.2, 7 | ACL extendidas según tabla, ICMP y servicios | 30 pares dirigidos ICMP y 60 casos HTTP/HTTPS (los 30 pares por protocolo). Todos coinciden con la interpretación documentada. |
| 4.2, 7 | Justificación de interfaz y dirección de cada ACL | Manual especifica gateways inbound: Gi6/0 en FG/ML y subinterfaces .30/.40 de ambos gateways AC. Se justifica filtrado cerca del origen y preservación tras HSRP. |
| 4.3, 7 | Dominio y datos del estudiante/curso | `www.proyecto2_202010298.com`; Sergio Sandoval, 202010298, Redes de Computadoras 2, USAC y descripción del proyecto. |
| 4.5, 8 | Captura dentro de VM con NAT o red interna | Ubuntu 24.04 en VMware, adaptador NAT, interfaz ens64. Procedencia, filtro, IP, herramientas y registros conservados. |
| 4.5.1, 8 | Handshake TCP con flags y secuencias | Tramas 1/2/3: SYN, SYN-ACK, ACK; SEQ/ACK relativos documentados. |
| 4.5.1, 8 | DNS público: consulta, respuesta, registro, TTL, UDP | Tramas 10/13, servidor 1.1.1.1, registro A, TTL observado 23 s y puertos identificados. |
| 4.5.1, 8 | HTTP frente a HTTPS, handshake TLS y cifrado | HTTP 4/6 con GET/200. TLS 1.2: ClientHello 17, ServerHello 19, certificado 20, datos cifrados 26/28; explicación de metadatos visibles y contenido protegido. |
| 4.5.1, 8 | Ping externo y Echo Request/Reply | Cuatro solicitudes a 1.1.1.1 y cuatro respuestas; identificador, secuencia, TTL y RTT. |
| 4.5.2, 8 | Nombre, carpeta y apertura de captura | `Proyecto_2/Wireshark/captura_wireshark_202010298.pcapng`, 42 tramas, apertura real en Wireshark con cinco imágenes. |
| 4.6, 8–9 | Presentación ejecutiva, arquitectura, costos, dispositivos y tecnologías | PDF de ocho diapositivas y guion de 7 min 20 s. Costos estimados explícitamente académicos; no se presentan como cotizaciones reales. |
| 4.7, 9 | Individual y conocimiento claro del diseño | Identificación individual en archivos; el dominio de la explicación se demuestra personalmente durante la defensa. |
| 4.7, 9 | Carpeta del Proyecto 2 dentro del repo del Proyecto 1 | Ruta `Proyecto_2/` en el repositorio indicado por el estudiante; Proyecto 1 conservado. |
| 4.7, 9 | Nombres exactos de simulación y presentación | `Proyecto2_202010298.pkt` y `Proyecto2_Presentacion_202010298.pdf`, ambos en `Proyecto_2/`. |
| 4.7, 9 | Un intento formal para ping | Registrado en la guía: esperar convergencia y estabilizar red antes del turno. No es una propiedad que un archivo pueda garantizar por sí solo. |
| 4.8, 9 | Análisis de ≥3 protocolos capa por capa en manual | TCP/HTTP, DNS, HTTPS/TLS e ICMP analizados; tabla por capas en manual y detalle con tramas en documento enlazado. |
| 4.8, 9; 1.4, 15 | Explicar paquetes en modo simulación PT | Guía preparada para DHCP DORA, DNS, HTTP/HTTPS, OSPF, EIGRP y BGP. La evaluación oral en vivo queda por realizar. |
| 4.9, 10 | Packet Tracer ≥8.2 y Wireshark | Usados PT 9.0.1 y Wireshark 4.2.2; usar 9.0.1 en la evaluación para evitar incompatibilidad de apertura con versiones anteriores. |
| 4.10, 11 | Manual: diagramas por ISP, subneteo, direcciones y configuraciones | Tres diagramas Mermaid, tablas de subredes y 17 enlaces, JSON de interfaces, 26 configuraciones efectivas IOS y estado de servicios en evidencia XML. |
| 4.10, 11 | Capturas de pantalla de pruebas de comunicación | **Pendiente documental:** hay topología real, cinco imágenes Wireshark y registros de pruebas, pero faltan pantallas de ping y navegador de Packet Tracer. Los JSON no sustituyen ese requisito literal. |
| 4.10, 11 | Repositorio con acceso del auxiliar y enlace UEDI | **Pendiente:** remoto comprobado aún en commit del Proyecto 1. Acceso del auxiliar no comprobable porque el PDF lo identifica como `XXXX`. |

## 3. Tabla completa de comunicación

Los valores describen **inicio** de comunicación desde cada origen, no el tráfico de respuesta. `I/H/S` significa ICMP, HTTP y HTTPS. `I/H` permite ICMP y HTTP, pero bloquea HTTPS. `—` bloquea inicios. Las respuestas permitidas desde Seguridad se contemplan mediante echo-reply y TCP ACK/RST (`established`).

| Origen \ Destino | ADM | ATC | VEN | FAC | SOP | SEG |
|---|---|---|---|---|---|---|
| ADM | Local | I/H/S | I/H/S | I/H/S | I/H/S | — |
| ATC | I/H/S | Local | I/H | — | I/H/S | — |
| VEN | I/H/S | I/H | Local | I/H | I/H/S | — |
| FAC | I/H/S | — | I/H | Local | I/H/S | — |
| SOP | I/H/S | I/H/S | I/H/S | I/H/S | Local | — |
| SEG | I/H/S | I/H/S | I/H/S | I/H/S | I/H/S | Local |

El sitio central tiene red de servicios propia; todos los departamentos pueden usar su DNS, HTTP y HTTPS. No se confunde esa excepción con permitir HTTPS entre Atención/Ventas o Facturación/Ventas. Para probar TCP se emplearon servidores temporales con servicio escuchando y marcadores únicos por prueba; después se retiraron.

## 4. Ambigüedades y aclaraciones reales del PDF

1. **Tres o cuatro ISP y menciones de RIP:** el resumen/objetivo menciona alternativas, pero 4.1 y la rúbrica establecen exactamente tres operadores, OSPF en los dos primeros y EIGRP en MoonLink. Se implementó esa especificación detallada. No hay un cuarto ISP ni un requisito concreto de RIP.
2. **`192.168.98.0/16`:** es una expresión con bits de host; la red /16 canónica es `192.168.0.0/16`. Se retiene 98 en los enlaces /30. No se asigna la misma /16 a cada enlace porque produciría solapamiento y enrutamiento ambiguo. Los loopback 192.168.99.4/32 y .5/32 también quedan dentro del /16.
3. **Permisos generales a “cualquier departamento” frente a prohibición hacia Seguridad:** la tabla se contradice si ambas frases se leen sin precedencia. Se prioriza el bloqueo específico de inicios hacia Seguridad; Administración y Soporte acceden a los otros departamentos. Esta es una interpretación conservadora documentada, no una aclaración oficial emitida por el docente.
4. **“Sin direccionamiento estático”:** 4.4 y 4.8 precisan dispositivos finales. Routers, gateways y enlaces usan IP estable; los 20 hosts finales usan DHCP. Las rutas Null0 para anunciar agregados BGP no son direccionamiento estático de hosts.
5. **Captura local o VM y tres o cuatro escenarios:** 4.10 permite varias fuentes y ≥3 protocolos, pero 4.5 y la rúbrica 1.3 exigen VM y cuatro escenarios. Se aplicó la condición más específica y completa: VM en NAT y los cuatro escenarios.
6. **HSRP “en ningún momento”:** la prueba exigida por la rúbrica es conmutación efectiva. HSRP necesita detección y convergencia; el resultado 4/4 después del cambio no acredita cero pérdida durante la transición. Tampoco HSRP replica DHCP. La limitación de AC-R5 como único servidor de nuevas concesiones está declarada.
7. **Topología inter-ISP:** el dibujo muestra equipos multicapa en triángulo, y el texto permite routers o switches de capa 3. Se usaron routers de borde con la misma interconexión triangular y fibra.
8. **Fechas:** objetivo indica entrega 23/10 y calificación 24/10; cronograma indica calificación 24–28/10. No se inventa un turno ni una hora límite: verificar los publicados por el curso.
9. **Nombre de repositorio:** este PDF pide reutilizar el repositorio del Proyecto 1; no fija otra cadena literal de nombre. Se conserva `REDES2_2S2026_202010298` dado por el estudiante. La nota heredada del README del Proyecto 1 sobre 1S/2S no constituye una nueva instrucción del Proyecto 2.
10. **Comentarios generales:** la página 18 está en blanco. No contiene excepciones, cambios a la rúbrica ni aclaraciones adicionales.

## 5. Rúbrica completa: 100 puntos, ponderación del proyecto 25 puntos

No se atribuye una nota automática. La rúbrica se divide en 40 puntos de habilidades y 60 de conocimientos; el docente determina el puntaje y su conversión a los 25 puntos del curso.

| Criterio | Máximo | Estado auditado y riesgo restante |
|---|---:|---|
| 1.1 Presentación ejecutiva | 10 | Archivo completo. Falta exponer personalmente entre 5 y 10 minutos. |
| 1.2 Manual técnico | 8 | Contenido técnico completo; faltan capturas de comunicación en PT para cumplir también 4.10. |
| 1.3 Wireshark | 14 | Cuatro escenarios auténticos desde VM, apertura y análisis por capas comprobados. Publicación remota pendiente. |
| 1.4 Modo simulación | 5 | Guía de explicación preparada. El evaluador elige el paquete y la defensa se realiza en vivo. |
| 1.5 Seguimiento Git | 3 | Estructura correcta y commits reales; Proyecto 2 desarrollado al final del período. No puede garantizarse máximo por seguimiento progresivo. No se reescribió ni inventó historial. Falta publicar. |
| 2.1 FibraNet | 12 | Árbol, OSPF, /25, dos LACP y DNS/HTTP/HTTPS verificados. |
| 2.2 AndinaCom | 13 | Jerarquía, OSPF, dos LACP, HSRP y DHCP central verificados. |
| 2.3 MoonLink | 12 | Hub-spoke, EIGRP, /26, dos LACP y laptop WiFi verificados. |
| 2.4 BGP | 10 | Triángulo, vecinos, prefijos y 17 enlaces ópticos verificados; asignación /30 documentada. |
| 2.5 ACL | 8 | 30/30 ICMP y 60/60 HTTP/HTTPS. Precedencia de Seguridad documentada por ambigüedad del enunciado. |
| 2.6 Conocimiento oral | 5 | Guía de preguntas y decisiones preparada; depende del estudiante durante la evaluación. |
| **Total** | **100** | No equivale a una calificación concedida. |

## 6. Evidencias y comprobaciones de esta revisión

- `evidencias/auditoria/estado_cli.json`: lecturas directas de 26 equipos, configuración activa/de arranque, interfaces, rutas, protocolos, HSRP y LACP. Los cuerpos de configuración activa y de arranque coinciden; no se detectaron errores de CLI en esas consultas.
- **Prueba de reapertura y corrección de arranque:** la versión inicial dejó el servidor DNS/WEB en APIPA tras la convergencia y solo 19/20 hosts válidos dentro de la observación. Se conserva `auditoria/reapertura_inicial_19_de_20.json`. Se configuró OSPF point-to-point en los veinte extremos de los diez enlaces internos FG/AC, eliminando la elección DR/BDR innecesaria. Se guardó y volvió a abrir el `.pkt`: la nueva observación `auditoria/reapertura_dhcp.json` alcanzó **20/20 automáticamente**, incluido el servidor .242, sin renovar manualmente durante esa segunda prueba ni introducir IP estática. El archivo requiere esperar el arranque y la convergencia antes de evaluar; no se certifica conectividad instantánea al abrirlo.
- Los tres bordes presentan dos vecinos BGP con prefijos recibidos. Los diez routers OSPF tienen adyacencias esperadas y los cinco EIGRP tienen vecinos conforme al hub-spoke.
- Los seis grupos LACP muestran `(SU)` y dos miembros `(P)`. No se confunden seis grupos lógicos con doce cables físicos ni se cuentan los dos extremos como grupos distintos.
- `evidencias/auditoria_acl_60.json`: 30 pares dirigidos, por HTTP y HTTPS, con marcas nuevas para evitar falsos positivos por caché. Los 60 casos coinciden con la política.
- `evidencias/auditoria_web_40.json`: opciones dinámicas y comprobación del sitio central por HTTP/HTTPS desde los 20 hosts finales.
- `evidencias/prueba_hsrp.json` y `prueba_lacp.json`: fallas reales controladas, resultados y restauración. No se sustituyeron por una mera lectura de configuración.
- `Wireshark/resumen_validacion.json`: SHA-256 y números de trama de los cuatro escenarios; `capinfos.txt` identifica formato pcapng/Ethernet. Cinco imágenes reales muestran la captura final de 42 paquetes.
- Presentación: ocho páginas renderizadas, costos y cantidades comprobados, guion de aproximadamente 7 min 20 s.
- Modo simulación comprobado con una petición HTTP y 138 eventos OSI reales (`auditoria/simulacion_http.json`): conexión TCP, petición, respuesta aceptada y entrega al navegador; al terminar se restauró Realtime. Esto complementa la guía, pero no sustituye la explicación oral del paquete que el evaluador elija.
- La consulta al remoto GitHub durante esta revisión devolvió `959cc88d369301860723721ec39c692efb1a4ed3` en main, correspondiente al Proyecto 1. No se presenta la versión local como ya publicada.

## 7. Qué falta para poder marcar la entrega como cerrada

1. **Añadir capturas reales de Packet Tracer:** al menos un ping inter-ISP permitido con sus estadísticas, un bloqueo previsto por ACL, y el navegador mostrando el dominio y los datos del estudiante. Recomendado añadir HSRP antes/después, DHCP de la laptop y LACP. Guardarlas en `evidencias/capturas_comunicacion/` e insertarlas o enlazarlas en el manual. La automatización de ventanas de Windows devolvió `Computer Use native pipe is unavailable`; por ello no se fabricaron capturas a partir del texto de los registros.
2. **Publicar los commits en GitHub** y verificar desde el remoto que estén presentes el `.pkt`, el PDF, el manual y el `.pcapng`. La VM, discos y clave privada de administración no pertenecen a la entrega del repositorio.
3. **Comprobar acceso del auxiliar** y entregar el enlace en UEDI dentro del plazo. El identificador del auxiliar y la hora límite deben tomarse del curso, no del marcador `XXXX` del PDF.
4. **Ensayar y demostrar:** exposición de 5–10 min, único intento formal de ping, análisis del paquete que el evaluador elija y respuestas sobre diseño. Los puntos orales no se pueden certificar anticipadamente.

## 8. Opcionales: no confundirlos con faltantes obligatorios

Autenticación OSPF MD5/EIGRP key-chain/BGP password, VLANs adicionales, comparación de precios reales y análisis TLS completo se enumeran como opcionales en página 10. No implementar autenticación o no disponer de cotizaciones reales no es por sí solo incumplir lo obligatorio. Sí se implementaron VLANs departamentales y se capturó el intercambio TLS 1.2 con certificado. No se reclama una auditoría criptográfica ni descifrado HTTPS.

La restricción de trabajo individual, el dominio personal del diseño y la prohibición de borrar o bloquear la celda de otro usuario siguen vigentes. El documento establece para esta última acción una penalización del 25% de la nota final.
