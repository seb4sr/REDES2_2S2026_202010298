"""Temporary departmental HTTP/HTTPS endpoints; removed after verification."""
import asyncio,json,time
from build_project import OUT
from generate_configs import DEPTS
from packet_tracer_mcp.server import mcp

async def raw(js):
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True))
 return r[1]['result']

async def main():
 endpoints={}
 results=[]
 try:
  for i,(dept,(cidr,vlan,*_)) in enumerate(DEPTS.items()):
   name='TEST-'+dept
   sw='AC-SW3' if dept.startswith('AC') else dept+'-SW2'
   port='FastEthernet0/'+str(10 if dept=='AC-VEN' else 11) if dept.startswith('AC') else 'FastEthernet0/8'
   endpoints[dept]=dict(name=name,switch=sw,port=port)
   js='addDevice('+json.dumps(name)+',"Server-PT",'+str(200+i*120)+',2100);'
   js+='addLink('+json.dumps(sw)+','+json.dumps(port)+','+json.dumps(name)+',"FastEthernet0","straight");'
   cmds=['configure terminal','interface '+port,'switchport mode access','switchport access vlan '+str(vlan),'spanning-tree portfast','no shutdown','end']
   js+='var d=ipc.network().getDevice('+json.dumps(sw)+');var cmds='+json.dumps(cmds)+';for(var i=0;i<cmds.length;i++)d.enterCommand(cmds[i],"");'
   js+='var s=ipc.network().getDevice('+json.dumps(name)+');var procs=["HttpServer","HttpsServer"];for(var i=0;i<procs.length;i++){var h=s.getProcess(procs[i]);h.setEnable(true);h.setPageContents("index.html",'+json.dumps('<html><body>ACL_TEST_'+dept+'</body></html>')+');}configurePcIp('+json.dumps(name)+',true);reportResult("created");'
   print(name,await raw(js),flush=True)
  deadline=time.time()+80
  while time.time()<deadline:
   await asyncio.sleep(2)
   js='var ns='+json.dumps(list(endpoints.values()))+';var out=[];for(var i=0;i<ns.length;i++)out.push({name:ns[i].name,ip:ipc.network().getDevice(ns[i].name).getPort("FastEthernet0").getIpAddress()});reportResult(JSON.stringify(out));'
   rows=json.loads(await raw(js))
   if all(r['ip'] not in ['0.0.0.0',''] and not r['ip'].startswith('169.254') for r in rows):break
  ips={r['name']:r['ip'] for r in rows}
  origin=list(DEPTS)
  rounds=[('http',['ML-SEG','AC-VEN','AC-FAC','FG-ATC','FG-ADM','ML-SOP']),('http',['FG-ATC','AC-FAC','FG-ATC','AC-VEN','ML-SEG','FG-ADM']),('https',['AC-FAC','AC-VEN','AC-FAC','AC-VEN','FG-ATC','AC-VEN']),('https',['ML-SEG','ML-SOP','FG-ADM','FG-ATC','AC-FAC','FG-ATC'])]
  for protocol,dests in rounds:
   js='var out=[];'
   cases=[]
   for src,dest in zip(origin,dests):
    host=src+'-PC1'; ip=ips['TEST-'+dest]
    expected=dest!='ML-SEG' and {src,dest}!={'FG-ATC','AC-FAC'}
    if protocol=='https': expected=expected and (src in ['FG-ADM','ML-SOP','ML-SEG'] or dest in ['FG-ADM','ML-SOP'])
    cases.append(dict(source=src,destination=dest,host=host,ip=ip,protocol=protocol,expected=expected))
    js+='var h=ipc.network().getDevice('+json.dumps(host)+').getProcess("HttpClient");h.setHttps('+str(protocol=='https').lower()+');h.go('+json.dumps(protocol+'://'+ip+'/')+');'
   await raw(js+'reportResult("requests started");')
   await asyncio.sleep(25)
   js='var cs='+json.dumps(cases)+';var out=[];for(var i=0;i<cs.length;i++){var c=cs[i];var h=ipc.network().getDevice(c.host).getProcess("HttpClient");c.page=h.getLastPageContent();c.received=c.page.indexOf("ACL_TEST_"+c.destination)>=0;c.passed=c.expected===c.received;out.push(c);}reportResult(JSON.stringify(out));'
   rows=json.loads(await raw(js))
   results.extend(rows)
   (OUT/'evidencias'/'pruebas_acl_web.json').write_text(json.dumps(dict(temporary_endpoints=endpoints,tests=results),indent=2),encoding='utf-8')
   print(protocol,'cases',json.dumps(rows),flush=True)
 finally:
  for e in endpoints.values():
   await raw('var lw=ipc.appWindow().getActiveWorkspace().getLogicalWorkspace();if(ipc.network().getDevice('+json.dumps(e['name'])+'))lw.removeDevice('+json.dumps(e['name'])+');reportResult("removed");')
 print('Temporary endpoints removed',flush=True)
asyncio.run(main())
