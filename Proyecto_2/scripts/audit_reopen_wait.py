import asyncio,json,time,datetime
from build_project import OUT,devices
from packet_tracer_mcp.server import mcp
async def main():
 names=[d['name'] for d in devices if d['model'] in ['PC-PT','Server-PT','Laptop-PT']]
 samples=[];deadline=time.time()+180
 while True:
  js='var ns='+json.dumps(names)+';var out=[];for(var i=0;i<ns.length;i++){var p=ipc.network().getDevice(ns[i]).getPort(ns[i].indexOf("LAP")>=0?"Wireless0":"FastEthernet0");out.push({name:ns[i],interface:p.getName(),ip:p.getIpAddress(),mask:p.getSubnetMask(),dhcp:p.isDhcpClientOn()});}reportResult(JSON.stringify(out));'
  r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True));rows=json.loads(r[1]['result'])
  count=sum(x['dhcp'] and x['ip']!='0.0.0.0' and not x['ip'].startswith('169.254') for x in rows)
  samples.append({'time':datetime.datetime.now().isoformat(),'valid_hosts':count,'hosts':rows})
  print('DHCP after reopening:',count,'/20',flush=True)
  if count==20 or time.time()>deadline:break
  await asyncio.sleep(10)
 (OUT/'evidencias'/'auditoria'/'reapertura_dhcp.json').write_text(json.dumps(samples,indent=2),encoding='utf-8')
 if count==20:(OUT/'evidencias'/'hosts_dhcp.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 else:raise RuntimeError('Automatic DHCP has not recovered on all hosts')
asyncio.run(main())
