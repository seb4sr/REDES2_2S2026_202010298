# Captura real de tráfico controlado

Estado: pendiente. Se detectó VMware Workstation instalado, sin máquinas virtuales en ejecución al consultar el entorno.

El enunciado contiene una mención general a loopback/servidor local, pero su rúbrica específica exige cuatro escenarios capturados dentro de una VM. Se adopta el requisito más completo: VM Linux con adaptador NAT, sin modo puente.

## Preparación dentro de la VM

Instalar Wireshark/tshark, curl, dnsutils y ping mediante el gestor de paquetes de la distribución. Copiar `capturar_vm.sh` dentro de la VM. Ejecutarlo allí, no en Windows:

```bash
bash capturar_vm.sh
```

El script captura únicamente en la interfaz de salida de la VM. Genera TCP/HTTP, DNS hacia 1.1.1.1, HTTPS y ping. Si algún servicio externo no responde, no asumir que el escenario se capturó: revisar sus salidas y repetirlo antes de detener la captura.

Copiar el archivo auténtico resultante a esta carpeta con el nombre `captura_wireshark_202010298.pcapng`.

## Filtros y evidencia requerida

| Escenario | Filtro Wireshark | Qué documentar |
|---|---|---|
| Three-way handshake | `tcp.flags.syn == 1 || tcp.flags.ack == 1` | Un mismo flujo: SYN, SYN/ACK, ACK; números de trama, SEQ y ACK |
| DNS | `dns` | Consulta A y respuesta, identificador, UDP/53 y TTL |
| HTTP | `http` | Host, método GET, respuesta y contenido visible |
| HTTPS | `tls` | ClientHello/ServerHello y Application Data cifrado |
| ICMP | `icmp` | Echo Request/Reply, identificador, secuencia y TTL |

Verificar apertura con Wireshark y usar `capinfos` para comprobar formato y cantidad de paquetes. Para describir cada protocolo, separar Ethernet, IP, transporte y aplicación. ICMP pertenece a la capa de red y no utiliza puertos TCP/UDP.

No confundir los paquetes de la VM con los de la red simulada en Packet Tracer: son dos evidencias diferentes que pide el proyecto.
