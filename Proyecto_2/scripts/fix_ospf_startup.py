"""Use point-to-point OSPF on dedicated two-router optical /30 links."""
import asyncio,json
from build_project import OUT,links
from packet_tracer_mcp.server import mcp
async def main():
 evidence=[]
 for l in links:
  if l['cable']!='fiber' or l.get('bgp') or not l['a'].startswith(('FG','AC')):continue
  for n,port in [(l['a'],l['ap']),(l['b'],l['bp'])]:
   commands=['configure terminal','interface '+port,'ip ospf network point-to-point','end','write memory']
   js='var d=ipc.network().getDevice('+json.dumps(n)+');d.getCommandLine().enterCommand("");d.enterCommand("end","enable");var cs='+json.dumps(commands)+';var out=[];for(var i=0;i<cs.length;i++)out.push({command:cs[i],result:d.enterCommand(cs[i],"")});reportResult(JSON.stringify(out));'
   r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True));rows=json.loads(r[1]['result'])
   evidence.append({'device':n,'port':port,'commands':rows})
   if any(x['result']['first']!=0 or 'Invalid input' in x['result']['second'] for x in rows):raise RuntimeError(str(evidence[-1]))
 print('Updated',len(evidence),'OSPF interfaces',flush=True)
 (OUT/'evidencias'/'auditoria'/'ajuste_ospf_punto_a_punto.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
asyncio.run(main())
