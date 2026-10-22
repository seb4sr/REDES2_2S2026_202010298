import ipaddress, json
from pathlib import Path
from build_project import OUT, devices, links

DEPTS = {
 'FG-ADM': ('172.16.18.0/25',10,'FG-R4','172.16.18.1','Administracion'),
 'FG-ATC': ('172.16.18.128/25',20,'FG-R5','172.16.18.129','Atencion_al_Cliente'),
 'AC-VEN': ('172.16.28.0/26',30,'AC-R4','172.16.28.1','Ventas'),
 'AC-FAC': ('172.16.28.64/26',40,'AC-R4','172.16.28.65','Facturacion'),
 'ML-SOP': ('172.16.32.0/26',50,'ML-R2','172.16.32.1','Soporte'),
 'ML-SEG': ('172.16.32.64/26',60,'ML-R3','172.16.32.65','Seguridad'),
}
DHCP='192.168.98.254'
DNS='192.168.98.242'
configs={d['name']:['enable','configure terminal','hostname '+d['name'],'no ip domain-lookup'] for d in devices if d['model'] in ['Router-PT-Empty','2960-24TT']}
addresses=[]
def add(n,*lines): configs[n].extend(lines)
def addr(n,port,ip,mask,description,helper=False):
 add(n,'interface '+port,'description '+description,'ip address '+ip+' '+mask,'no shutdown')
 if helper: add(n,'ip helper-address '+DHCP)
 add(n,'exit')
 addresses.append(dict(device=n,interface=port,ip=ip,mask=mask,description=description))

# Allocate the three eBGP links first, then the internal point-to-point links.
fiber=[l for l in links if l['cable']=='fiber']
offset={'FG':16,'AC':32,'ML':64}
bgp_offset=0
for l in sorted(fiber,key=lambda l:not l.get('bgp',False)):
 if l.get('bgp'):
  o=bgp_offset; bgp_offset+=4
 else:
  p=l['a'][:2]; o=offset[p]; offset[p]+=4
 l['subnet']=f'192.168.98.{o}/30'
 l['a_ip']=f'192.168.98.{o+1}'
 l['b_ip']=f'192.168.98.{o+2}'
 addr(l['a'],l['ap'],l['a_ip'],'255.255.255.252',l['b'])
 addr(l['b'],l['bp'],l['b_ip'],'255.255.255.252',l['a'])

# Unique positive link costs provide deterministic primary/backup OSPF paths.
for i,l in enumerate([l for l in fiber if l['a'].startswith('AC') and not l.get('bgp')]):
 for n,port in [(l['a'],l['ap']),(l['b'],l['bp'])]:
  add(n,'interface '+port,'ip ospf cost '+str(2**i),'exit')

for prefix,(cidr,vlan,router,gateway,title) in DEPTS.items():
 net=ipaddress.ip_network(cidr)
 if prefix.startswith('AC'):
  for r,host,priority in [('AC-R4',2,115 if vlan==30 else 100),('AC-R5',3,100 if vlan==30 else 115)]:
   port='GigabitEthernet6/0.'+str(vlan)
   add(r,'interface GigabitEthernet6/0','no shutdown','exit','interface '+port,'encapsulation dot1Q '+str(vlan),'exit')
   addr(r,port,str(net.network_address+host),str(net.netmask),title,True)
   add(r,'interface '+port,f'standby {vlan} ip {gateway}',f'standby {vlan} priority {priority}',f'standby {vlan} preempt',f'standby {vlan} track GigabitEthernet0/0',f'standby {vlan} track GigabitEthernet1/0','exit')
 else:
  addr(router,'GigabitEthernet6/0',gateway,str(net.netmask),title,True)

addr('FG-R3','GigabitEthernet6/0','192.168.98.241','255.255.255.252','DNS_HTTP_DHCP_CLIENT',True)
addr('AC-R5','Loopback0',DHCP,'255.255.255.255','DHCP_CENTRAL')
for i in [4,5]: addr(f'ML-R{i}','Loopback0',f'192.168.99.{i}','255.255.255.255','SPOKE_INFRAESTRUCTURA')

# Explicit internal routing interfaces avoid accidentally running IGP over eBGP.
for d in devices:
 n=d['name']
 if d['model']!='Router-PT-Empty':continue
 prefix=n[:2]
 internal=[l['ap'] if l['a']==n else l['bp'] for l in fiber if not l.get('bgp') and n in [l['a'],l['b']]]
 rid={'FG':1,'AC':2,'ML':3}[prefix]*10+int(n[-1])
 if prefix in ['FG','AC']:
  add(n,'router ospf 1',f'router-id {rid}.{rid}.{rid}.{rid}','passive-interface default')
  for port in internal: add(n,'no passive-interface '+port)
  for a in addresses:
   if a['device']==n and a['interface'] not in [l['ap'] if l['a']==n else l['bp'] for l in fiber if l.get('bgp') and n in [l['a'],l['b']]]:
    add(n,f'network {a["ip"]} 0.0.0.0 area 0')
  if n.endswith('R1'): add(n,'redistribute bgp '+('65001' if prefix=='FG' else '65002')+' subnets')
  add(n,'exit')
 else:
  add(n,'router eigrp 100','no auto-summary','passive-interface default')
  for port in internal:add(n,'no passive-interface '+port)
  for a in addresses:
   if a['device']==n and (n!='ML-R1' or a['interface'] not in ['GigabitEthernet0/0','GigabitEthernet1/0']):
    add(n,f'network {a["ip"]} 0.0.0.0')
  if n=='ML-R1':add(n,'redistribute bgp 65003 metric 100000 10 255 1 1500')
  add(n,'exit')

for prefix,asn,lan in [('FG',65001,'172.16.18.0'),('AC',65002,'172.16.28.0'),('ML',65003,'172.16.32.0')]:
 n=prefix+'-R1'
 add(n,f'ip route {lan} 255.255.255.0 Null0','router bgp '+str(asn),'bgp log-neighbor-changes',f'network {lan} mask 255.255.255.0')
 if prefix=='FG':add(n,'network 192.168.98.240 mask 255.255.255.252')
 if prefix=='AC':add(n,'network 192.168.98.254 mask 255.255.255.255')
 for l in fiber:
  if l.get('bgp') and n in [l['a'],l['b']]:
   peer=l['b'] if n==l['a'] else l['a']
   ip=l['b_ip'] if n==l['a'] else l['a_ip']
   peer_as={'FG':65001,'AC':65002,'ML':65003}[peer[:2]]
   add(n,f'neighbor {ip} remote-as {peer_as}')
 add(n,'exit')

# The only DHCP service is in AndinaCom. Infrastructure IPs are excluded.
add('AC-R5','service dhcp')
for prefix,(cidr,vlan,r,gateway,title) in DEPTS.items():
 net=ipaddress.ip_network(cidr)
 excluded=9 if prefix.startswith('ML') else 19
 add('AC-R5',f'ip dhcp excluded-address {net.network_address+1} {net.network_address+excluded}',f'ip dhcp pool {prefix}',f'network {net.network_address} {net.netmask}','default-router '+gateway,'dns-server '+DNS,'domain-name proyecto2_202010298.com','exit')
add('AC-R5','ip dhcp excluded-address 192.168.98.241','ip dhcp pool DNS_WEB','network 192.168.98.240 255.255.255.252','default-router 192.168.98.241','dns-server '+DNS,'exit')

# LACP: two independent port-channel groups per ISP, each using two members.
for d in devices:
 n=d['name']
 if d['model']!='2960-24TT':continue
 vlans=[30,40] if n.startswith('AC') else [d['vlan']]
 for v in vlans:add(n,f'vlan {v}',f'name DEPARTAMENTO_{v}','exit')
 add(n,'spanning-tree mode rapid-pvst')
 bundle_ports={}
 for l in links:
  if n not in [l['a'],l['b']]:continue
  port=l['ap'] if n==l['a'] else l['bp']
  add(n,'interface '+port)
  if l.get('bundle'):
   add(n,'switchport mode trunk','switchport trunk allowed vlan '+','.join(map(str,l['vlans'])),f'channel-group {l["bundle"]} mode active')
   bundle_ports[l['bundle']]=l['vlans']
  elif l.get('trunk'):
   add(n,'switchport mode trunk','switchport trunk allowed vlan '+','.join(map(str,l['trunk'])))
  elif l.get('access'):
   add(n,'switchport mode access',f'switchport access vlan {l["access"]}','spanning-tree portfast')
  add(n,'no shutdown','exit')
 for group,vs in bundle_ports.items():add(n,f'interface Port-channel{group}','switchport mode trunk','switchport trunk allowed vlan '+','.join(map(str,vs)),'exit')
 if n.endswith('SW1'):add(n,'spanning-tree vlan '+','.join(map(str,vlans))+' root primary')

# More-specific isolation wins over the broad Administration/Support rules.
def source(cidr):
 net=ipaddress.ip_network(cidr)
 return f'{net.network_address} {net.hostmask}'
sec=source(DEPTS['ML-SEG'][0])
acls={}
for prefix,(cidr,vlan,router,gateway,title) in DEPTS.items():
 src=source(cidr)
 rules=['ip access-list extended ACL_'+prefix.replace('-','_'),'remark DHCP_DNS_y_respuestas_de_sesiones','permit udp any eq bootpc any eq bootps',f'permit udp {src} host {DNS} eq domain',f'permit tcp {src} host {DNS} eq domain']
 if prefix.startswith('AC'):
  net=ipaddress.ip_network(cidr)
  rules[1:1]=[f'permit udp host {net.network_address+h} eq 1985 host 224.0.0.2 eq 1985' for h in [2,3]]
 if prefix!='ML-SEG':
  rules += [f'permit icmp {src} {sec} echo-reply',f'permit tcp {src} {sec} established',f'deny ip {src} {sec}']
 other={'FG-ATC':'AC-FAC','AC-FAC':'FG-ATC'}.get(prefix)
 if other:rules += [f'deny ip {src} {source(DEPTS[other][0])}']
 rules += [f'permit tcp {src} any established',f'permit icmp {src} host {DNS}',f'permit tcp {src} host {DNS} eq 80',f'permit tcp {src} host {DNS} eq 443']
 for dest,(dcidr,*_) in DEPTS.items():
  if dest==prefix or dest==other or (dest=='ML-SEG' and prefix!='ML-SEG'):continue
  dst=source(dcidr)
  rules += [f'permit icmp {src} {dst}',f'permit tcp {src} {dst} eq 80']
  if prefix in ['FG-ADM','ML-SOP','ML-SEG'] or dest in ['FG-ADM','ML-SOP']:
   rules += [f'permit tcp {src} {dst} eq 443']
 rules += [f'deny ip any any','exit']
 acls[prefix]=rules

for n,lines in configs.items():
 lines += ['end','write memory']
 (OUT/'configs'/f'{n}.cfg').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for prefix,rules in acls.items():
 routers=['AC-R4','AC-R5'] if prefix.startswith('AC') else [DEPTS[prefix][2]]
 for r in routers:
  port='GigabitEthernet6/0'+('.'+str(DEPTS[prefix][1]) if prefix.startswith('AC') else '')
  s=['enable','configure terminal','no ip access-list extended ACL_'+prefix.replace('-','_')]+rules+['interface '+port,'ip access-group ACL_'+prefix.replace('-','_')+' in','end','write memory']
  (OUT/'configs'/f'{r}_{prefix}_ACL.cfg').write_text('\n'.join(s)+'\n',encoding='utf-8')
(OUT/'diseno'/'direccionamiento.json').write_text(json.dumps(dict(interfaces=addresses,departments=DEPTS,fiber_links=fiber),indent=2),encoding='utf-8')
print('Generated',len(configs),'base configurations and',sum(2 if p.startswith('AC') else 1 for p in acls),'ACL files')
