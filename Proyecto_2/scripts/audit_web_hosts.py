"""Check DHCP options and central HTTP/HTTPS from every final host."""
import asyncio,json,time,xml.etree.ElementTree as ET
from build_project import OUT,devices
from packet_tracer_mcp.server import mcp
async def raw(js):
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True));return r[1]['result']
async def main():
 names=[d['name'] for d in devices if d['model'] in ['PC-PT','Server-PT','Laptop-PT']]
 inventory=[]
 for name in names:
  root=ET.fromstring(await raw('reportResult(ipc.network().getDevice('+json.dumps(name)+').serializeToXml());'))
  ports=[e for e in root.iter() if e.find('PORT_DHCP_ENABLE') is not None and e.findtext('PORT_DHCP_ENABLE')=='true']
  port='Wireless0' if 'LAP' in name else 'FastEthernet0'
  live=json.loads(await raw('var p=ipc.network().getDevice('+json.dumps(name)+').getPort('+json.dumps(port)+');reportResult(JSON.stringify({ip:p.getIpAddress(),mask:p.getSubnetMask(),dhcp:p.isDhcpClientOn()}));'))
  row={'name':name,'gateway':[e.text for e in root.iter('GATEWAY')],'dns':[e.findtext('SERVER_IP') for e in root.iter('DNS_CLIENT')],'dhcp_servers':[e.findtext('DHCP_SERVER_IP') for e in ports],**live}
  inventory.append(row)
 results=[];html=(OUT/'diseno'/'index.html').read_text(encoding='utf-8')
 try:
  for protocol in ['http','https']:
   marker='AUDIT_ALL_HOSTS_'+protocol+'_'+str(time.time_ns());proc='HttpsServer' if protocol=='https' else 'HttpServer'
   await raw('var s=ipc.network().getDevice("FG-DNS-WEB").getProcess('+json.dumps(proc)+');s.setPageContents("index.html",'+json.dumps(html.replace('</body>','<p>'+marker+'</p></body>'))+');reportResult("marker set");')
   js='var ns='+json.dumps(names)+';for(var i=0;i<ns.length;i++){var h=ipc.network().getDevice(ns[i]).getProcess("HttpClient");h.setHttps('+str(protocol=='https').lower()+');h.go('+json.dumps(protocol+'://www.proyecto2_202010298.com/')+');}reportResult("started");'
   await raw(js);pending=set(names);deadline=time.time()+70
   while pending and time.time()<deadline:
    await asyncio.sleep(2)
    js='var ns='+json.dumps(list(pending))+';var out=[];for(var i=0;i<ns.length;i++){var h=ipc.network().getDevice(ns[i]).getProcess("HttpClient");out.push({name:ns[i],page:h.getLastPageContent()});}reportResult(JSON.stringify(out));'
    for r in json.loads(await raw(js)):
     if marker in r['page']:
      results.append(dict(host=r['name'],protocol=protocol,ok=True,page=r['page']));pending.remove(r['name'])
   results.extend(dict(host=n,protocol=protocol,ok=False) for n in pending)
   print(protocol,'passed',len(names)-len(pending),'/',len(names),flush=True)
 finally:
  await raw('var d=ipc.network().getDevice("FG-DNS-WEB");var ps=["HttpServer","HttpsServer"];for(var i=0;i<ps.length;i++)d.getProcess(ps[i]).setPageContents("index.html",'+json.dumps(html)+');reportResult("original pages restored");')
 (OUT/'evidencias'/'auditoria_web_40.json').write_text(json.dumps({'hosts':inventory,'tests':results},ensure_ascii=False,indent=2),encoding='utf-8')
 if len(results)!=40 or not all(r['ok'] for r in results):raise RuntimeError('Some final hosts failed web access')
asyncio.run(main())
