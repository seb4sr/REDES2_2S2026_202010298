import asyncio,json,re,time
from build_project import OUT,call
from packet_tracer_mcp.server import mcp
HOSTS=['FG-ADM-PC1','FG-ATC-PC1','AC-VEN-PC1','AC-FAC-PC1','ML-SOP-PC1','ML-SEG-PC1']

async def run_tool(name,args):
 r=await mcp.call_tool(name,args)
 return r[1] if isinstance(r,tuple) else r

async def inventory():
 from build_project import devices
 names=[d['name'] for d in devices if d['model'] in ['PC-PT','Server-PT','Laptop-PT']]
 js='var ns='+json.dumps(names)+';var out=[];for(var i=0;i<ns.length;i++){var d=ipc.network().getDevice(ns[i]);var pn=ns[i].indexOf("LAP")>=0?"Wireless0":"FastEthernet0";var p=d.getPort(pn);out.push({name:ns[i],interface:pn,ip:p.getIpAddress(),mask:p.getSubnetMask(),dhcp:p.isDhcpClientOn()});}reportResult(JSON.stringify(out));'
 result=await run_tool('pt_send_raw',dict(js_code=js,wait_result=True))
 rows=json.loads(result['result'])
 (OUT/'evidencias'/'hosts_dhcp.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 print('DHCP inventory:',json.dumps(rows),flush=True)
 return {r['name']:r['ip'] for r in rows}

async def matrix():
 ips=await inventory()
 results=[]
 for offset in range(1,6):
  tasks=[]
  for i,n in enumerate(HOSTS):
   dest=HOSTS[(i+offset)%6]
   expected=not (dest.startswith('ML-SEG') or {n.split('-PC')[0],dest.split('-PC')[0]}=={'FG-ATC','AC-FAC'})
   tasks.append((n,dest,expected))
  js='var out=[];'
  for n,dest,expected in tasks:
   js+='var cl=ipc.network().getDevice('+json.dumps(n)+').getCommandLine();cl.enterCommand("");var o=String(cl.getOutput());var m=o.match(/Packets: Sent/g);out.push({name:'+json.dumps(n)+',base:m?m.length:0});cl.enterCommand('+json.dumps('ping '+ips[dest])+');'
  armed=await run_tool('pt_send_raw',dict(js_code=js+'reportResult(JSON.stringify(out));',wait_result=True))
  bases=json.loads(armed['result'])
  print('Round',offset,'started',flush=True)
  deadline=time.time()+100
  pending={n:(dest,expected) for n,dest,expected in tasks}
  while pending and time.time()<deadline:
   await asyncio.sleep(2)
   js='var ns='+json.dumps(bases)+';var out=[];for(var i=0;i<ns.length;i++){var cl=ipc.network().getDevice(ns[i].name).getCommandLine();var o=String(cl.getOutput());var m=o.match(/Packets: Sent/g);if(m&&m.length>ns[i].base){out.push({name:ns[i].name,output:o.substring(o.lastIndexOf("Ping statistics"))});}}reportResult(JSON.stringify(out));'
   observed=await run_tool('pt_send_raw',dict(js_code=js,wait_result=True))
   for o in json.loads(observed['result']):
    if o['name'] not in pending:continue
    dest,expected=pending.pop(o['name'])
    received=re.search(r'Received = (\d+)',o['output'])
    row=dict(source=o['name'],destination=dest,destination_ip=ips[dest],expected=expected,received=int(received[1]) if received else None,output=o['output'])
    results.append(row)
    print(json.dumps(row),flush=True)
  for n,(dest,expected) in pending.items():results.append(dict(source=n,destination=dest,expected=expected,error='No completed ping within 100 seconds'))
  (OUT/'evidencias'/'matriz_ping.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')

async def main():
 import sys
 if len(sys.argv)>1 and sys.argv[1]=='inventory':await inventory()
 elif len(sys.argv)>1 and sys.argv[1]=='retry':
  path=OUT/'evidencias'/'matriz_ping.json'
  rows=json.loads(path.read_text(encoding='utf-8'))
  for row in rows:
   if not row['expected'] or row.get('received')==4:continue
   n=row['source']; ip=row['destination_ip']
   js='var cl=ipc.network().getDevice('+json.dumps(n)+').getCommandLine();var o=String(cl.getOutput());var m=o.match(/Packets: Sent/g);cl.enterCommand('+json.dumps('ping '+ip)+');reportResult(String(m?m.length:0));'
   base=int((await run_tool('pt_send_raw',dict(js_code=js,wait_result=True)))['result'])
   deadline=time.time()+80
   while time.time()<deadline:
    await asyncio.sleep(2)
    js='var o=String(ipc.network().getDevice('+json.dumps(n)+').getCommandLine().getOutput());var m=o.match(/Packets: Sent/g);reportResult(m&&m.length>'+str(base)+'?o.substring(o.lastIndexOf("Ping statistics")):"WAIT");'
    result=(await run_tool('pt_send_raw',dict(js_code=js,wait_result=True)))['result']
    if result=='WAIT':continue
    previous={k:row[k] for k in ['received','output'] if k in row}
    row.setdefault('previous_attempts',[]).append(previous)
    row['output']=result
    match=re.search(r'Received = (\d+)',result)
    row['received']=int(match[1]) if match else None
    print(n,row['destination'],row['received'],flush=True)
    break
  path.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
 else:await matrix()
asyncio.run(main())
