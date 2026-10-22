#!/usr/bin/env bash
set -euo pipefail
mkdir -p /home/captura/proyecto2
cd /home/captura/proyecto2
if test -e captura_wireshark_202010298.pcapng; then mv captura_wireshark_202010298.pcapng "captura_previa_$(date +%s).pcapng"; fi
iface="$(ip -4 route show default | awk 'NR==1 {print $5}')"
test -n "$iface"
vm_ip="$(ip -4 -o addr show dev "$iface" | awk '{print $4}' | cut -d/ -f1)"
target_ip="$(dig +short @1.1.1.1 example.com A | awk '/^[0-9.]+$/ {print; exit}')"
test -n "$target_ip"
capture_filter="host $vm_ip and ((host $target_ip and tcp and (port 80 or port 443)) or (host 1.1.1.1 and (icmp or (udp and port 53))))"
{
  date -Is
  hostname
  systemd-detect-virt
  ip -4 address show dev "$iface"
  ip -4 route
  tshark --version | head -n 2
  echo "Capture filter: $capture_filter"
} > entorno_vm.txt
sudo -n dumpcap -i "$iface" -a duration:50 -f "$capture_filter" -w /tmp/captura_wireshark_202010298.pcapng > captura.log 2>&1 &
capture_pid=$!
sleep 3
{
  echo '=== HTTP: TCP handshake and plaintext GET ==='
  curl --noproxy '*' --resolve "example.com:80:$target_ip" --http1.1 --connect-timeout 10 --max-time 15 -v http://example.com/ -o http_body.html
  echo '=== DNS: explicit A query to 1.1.1.1 ==='
  dig @1.1.1.1 example.com A +time=5 +tries=1
  echo '=== HTTPS: TLS 1.2 handshake and encrypted application data ==='
  curl --noproxy '*' --resolve "example.com:443:$target_ip" --http1.1 --tls-max 1.2 --connect-timeout 10 --max-time 15 -v https://example.com/ -o https_body.html
  echo '=== ICMP: external Echo Request and Echo Reply ==='
  ping -c 4 -W 3 1.1.1.1
} > escenarios.log 2>&1
wait "$capture_pid"
sudo -n install -o captura -g captura -m 0644 /tmp/captura_wireshark_202010298.pcapng captura_wireshark_202010298.pcapng
capinfos captura_wireshark_202010298.pcapng > capinfos.txt
tshark -r captura_wireshark_202010298.pcapng -T json \
  -e frame.number -e frame.time_epoch -e frame.time_relative -e frame.protocols \
  -e eth.src -e eth.dst -e ip.src -e ip.dst -e ip.ttl -e ip.proto \
  -e tcp.stream -e tcp.srcport -e tcp.dstport -e tcp.flags.syn -e tcp.flags.ack \
  -e tcp.seq -e tcp.ack -e tcp.len -e tcp.flags.fin -e tcp.flags.reset \
  -e udp.srcport -e udp.dstport -e dns.id -e dns.flags.response -e dns.qry.name \
  -e dns.qry.type -e dns.resp.ttl -e dns.a -e http.request.method -e http.host \
  -e http.request.uri -e http.response.code -e tls.handshake.type \
  -e tls.handshake.version -e tls.record.content_type -e tls.record.version \
  -e icmp.type -e icmp.code -e icmp.ident -e icmp.seq > paquetes.json
echo 'CAPTURE_COMPLETE'
