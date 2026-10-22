#!/usr/bin/env bash
set -euo pipefail
for command_name in ip tshark curl dig ping; do
  command -v "$command_name" >/dev/null || { echo "Falta: $command_name"; exit 1; }
done
iface="$(ip -4 route show default | awk 'NR==1 {print $5}')"
test -n "$iface" || { echo 'No hay interfaz con ruta por defecto'; exit 1; }
output='captura_wireshark_202010298.pcapng'
test ! -e "$output" || { echo "Ya existe $output; conserva esa evidencia o cambia su nombre antes de repetir."; exit 1; }
echo "Ejecutar solo dentro de la VM Linux con adaptador NAT. Interfaz: $iface"
sudo -v
sudo tshark -i "$iface" -F pcapng -w "$output" -f 'tcp port 80 or tcp port 443 or udp port 53 or icmp' >/tmp/proyecto2_tshark.log 2>&1 &
capture_pid=$!
trap 'sudo kill -INT "$capture_pid" 2>/dev/null || true' EXIT
sleep 3
curl --noproxy '*' --http1.1 --connect-timeout 10 --max-time 20 http://example.com/ -o /dev/null || echo 'Revisar escenario HTTP'
dig @1.1.1.1 example.com A +time=5 +tries=1 || echo 'Revisar escenario DNS'
curl --noproxy '*' --http1.1 --connect-timeout 10 --max-time 20 https://example.com/ -o /dev/null || echo 'Revisar escenario HTTPS'
ping -c 4 -W 3 1.1.1.1 || echo 'Revisar escenario ICMP'
sleep 3
sudo kill -INT "$capture_pid" 2>/dev/null || true
wait "$capture_pid" || true
trap - EXIT
echo "Captura guardada: $output. Verifica los cuatro escenarios antes de entregar."
