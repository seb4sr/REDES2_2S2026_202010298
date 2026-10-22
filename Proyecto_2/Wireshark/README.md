# Captura real de tráfico controlado

Estado: completo. Se preparó una VM Ubuntu 24.04 en VMware Workstation, con 2 CPU, 2 GB de RAM, disco de 12 GB y un adaptador E1000 en NAT. Wireshark/Tshark 4.2.2 produjo la captura real de 42 tramas.

- [Abrir el análisis por trama y las cinco imágenes](ANALISIS_WIRESHARK.md).
- [Archivo pcapng](captura_wireshark_202010298.pcapng).
- `capinfos.txt`, `entorno_vm.txt` y `escenarios.log`: formato, entorno y resultados de los comandos.
- `paquetes.json` y `resumen_validacion.json`: campos exportados y comprobaciones automáticas.

La imagen base se descargó de https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.vmdk y se verificó contra su SHA256SUMS oficial. La VM y su clave SSH permanecen fuera de Git, en `.vm-capture/` del espacio de trabajo. El archivo de VMware es `Proyecto2-Wireshark.vmx`.

## Reproducción

Dentro de la VM, con usuario `captura` y sudo disponible, ejecutar `bash capturar_vm.sh`. Requiere dumpcap, tshark, capinfos, curl, dig y ping. El script conserva la captura anterior, captura durante 50 segundos y genera tráfico HTTP, DNS, HTTPS y cuatro pings. Los destinos pueden resolver a otras IP en futuras ejecuciones; regenerar el análisis desde los nuevos datos.

`analizar_captura.py` se ejecuta junto a los archivos exportados y valida el handshake, DNS, HTTP 200, TLS y los cuatro pares ICMP. Genera el análisis y el resumen con SHA-256. `gui_screenshots.py` se ejecuta dentro de la VM con Wireshark, Xvfb y scrot: toma imágenes de la aplicación real en una pantalla virtual.

La captura corresponde al tráfico de la VM en NAT. Las pruebas de enrutamiento y redundancia del proyecto están documentadas separadamente en Packet Tracer.
