"""Audit all 60 directed departmental HTTP/HTTPS cases with unique live pages."""
import asyncio,json,time
from build_project import OUT
from packet_tracer_mcp.server import mcp
DEPTS=json.loads((OUT/'diseno'/'direccionamiento.json').read_text(encoding='utf-8'))['departments']

async def raw(js):
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True))
 return r[1]['result']

async def main():
 endpoints={};results=[]
 target=OUT/'evidencias'/'auditoria_acl_60.json'
 try:
  for i,(dept,(_,vlan,*_)) in enumerate(DEPTS.items()):
   name='AUDIT-'+dept
   sw='AC-SW3' if dept.startswith('AC') else dept+'-SW2'
   port='FastEthernet0/'+str(10 if dept=='AC-VEN' else 11) if dept.startswith('AC') else 'FastEthernet0/8'
   endpoints[dept]=dict(name=name,switch=sw,port=port)
   cmds=['configure terminal','interface '+port,'switchport mode access','switchport access vlan '+str(vlan),'spanning-tree portfast','no shutdown','end']
   js='addDevice('+json.dumps(name)+',"Server-PT",'+str(200+i*120)+',2100);addLink('+json.dumps(sw)+','+json.dumps(port)+','+json.dumps(name)+',"FastEthernet0","straight");'
   js+='var d=ipc.network().getDevice('+json.dumps(sw)+');var cs='+json.dumps(cmds)+';for(var i=0;i<cs.length;i++)d.enterCommand(cs[i],"");configurePcIp('+json.dumps(name)+',true);reportResult("created");'
   await raw(js)
  for _ in range(45):
   await asyncio.sleep(2)
   js='var ns='+json.dumps([e['name'] for e in endpoints.values()])+';var out=[];for(var i=0;i<ns.length;i++)out.push({name:ns[i],ip:ipc.network().getDevice(ns[i]).getPort("FastEthernet0").getIpAddress()});reportResult(JSON.stringify(out));'
   rows=json.loads(await raw(js))
   if all(r['ip'] not in ['','0.0.0.0'] and not r['ip'].startswith('169.254') for r in rows):break
  else:raise RuntimeError('Audit endpoint DHCP failed')
  ips={r['name']:r['ip'] for r in rows}
  depts=list(DEPTS)
  for protocol in ['http','https']:
   for offset in range(1,6):
    cases=[];js=''
    for i,src in enumerate(depts):
     dst=depts[(i+offset)%6];name=endpoints[dst]['name']
     marker='AUDIT_'+str(time.time_ns())+'_'+src+'_'+dst+'_'+protocol
     expected=dst!='ML-SEG' and {src,dst}!={'FG-ATC','AC-FAC'}
     if protocol=='https':expected=expected and (src in ['FG-ADM','ML-SOP','ML-SEG'] or dst in ['FG-ADM','ML-SOP'])
     case=dict(source=src,destination=dst,protocol=protocol,expected=expected,marker=marker,ip=ips[name])
     cases.append(case)
     js+='var s=ipc.network().getDevice('+json.dumps(name)+').getProcess('+json.dumps('HttpsServer' if protocol=='https' else 'HttpServer')+');s.setEnable(true);s.setPageContents("index.html",'+json.dumps('<html><body>'+marker+'</body></html>')+');'
    for c in cases:
     js+='var h=ipc.network().getDevice('+json.dumps(c['source']+'-PC1')+').getProcess("HttpClient");h.setHttps('+str(protocol=='https').lower()+');h.go('+json.dumps(protocol+'://'+c['ip']+'/')+');'
    await raw(js+'reportResult("started");')
    await asyncio.sleep(22)
    js='var cs='+json.dumps(cases)+';for(var i=0;i<cs.length;i++){var c=cs[i];c.page=ipc.network().getDevice(c.source+"-PC1").getProcess("HttpClient").getLastPageContent();c.received=c.page.indexOf(c.marker)>=0;c.passed=c.expected===c.received;}reportResult(JSON.stringify(cs));'
    tested=json.loads(await raw(js));results.extend(tested)
    target.write_text(json.dumps(dict(temporary_endpoints=endpoints,tests=results),ensure_ascii=False,indent=2),encoding='utf-8')
    print(protocol,offset,'passed',sum(r['passed'] for r in tested),'/',len(tested),flush=True)
 finally:
  for e in endpoints.values():
   await raw('if(ipc.network().getDevice('+json.dumps(e['name'])+'))ipc.appWindow().getActiveWorkspace().getLogicalWorkspace().removeDevice('+json.dumps(e['name'])+');reportResult("removed");')
  print('Removed all temporary audit endpoints',flush=True)
 if len(results)!=60 or not all(r['passed'] for r in results):raise RuntimeError('Audit found mismatches; see '+str(target))
 print('PASS: all 60 directed protocol cases',flush=True)

asyncio.run(main())
