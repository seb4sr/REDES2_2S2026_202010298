"""Read-only CLI and service evidence for the final requirements audit."""
import asyncio,json,datetime
from build_project import OUT,devices,links
from packet_tracer_mcp.server import mcp
async def raw(js):
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True));return r[1]['result']
async def main():
 out=OUT/'evidencias'/'auditoria';out.mkdir(exist_ok=True)
 result={'timestamp':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).isoformat(),'devices':{},'fiber':[]}
 for d in devices:
  if d['model'] not in ['Router-PT-Empty','2960-24TT']:continue
  commands=['show running-config','show startup-config','show ip interface brief']
  if d['model']=='Router-PT-Empty':
   commands+=['show ip route','show ip protocols']
   commands+=['show ip eigrp neighbors'] if d['name'].startswith('ML') else ['show ip ospf neighbor']
   if d['name'].endswith('R1'):commands+=['show ip bgp summary','show ip bgp']
   if d['name'] in ['AC-R4','AC-R5']:commands+=['show standby brief']
   if d['name']=='AC-R5':commands+=['show ip dhcp binding','show ip dhcp pool']
  else:commands+=['show etherchannel summary','show interfaces trunk','show vlan brief']
  js='var d=ipc.network().getDevice('+json.dumps(d['name'])+');var cs='+json.dumps(commands)+';var out=[];for(var i=0;i<cs.length;i++)out.push({command:cs[i],result:d.enterCommand(cs[i],"enable")});reportResult(JSON.stringify(out));'
  result['devices'][d['name']]=json.loads(await raw(js))
  print('Read',d['name'],flush=True)
 for l in links:
  if l['cable']!='fiber':continue
  js='reportResult(String(ipc.network().getDevice('+json.dumps(l['a'])+').getPort('+json.dumps(l['ap'])+').getLink().getConnectionType()));'
  result['fiber'].append(dict(a=l['a'],ap=l['ap'],b=l['b'],bp=l['bp'],connection_type=await raw(js)))
 for n in ['FG-DNS-WEB','ML-WIFI','ML-SOP-LAP1','FG-ADM-PC1']:
  xml=await raw('reportResult(ipc.network().getDevice('+json.dumps(n)+').serializeToXml());')
  (out/(n+'.xml')).write_text(xml,encoding='utf-8')
 (out/'estado_cli.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Saved audit evidence',flush=True)
asyncio.run(main())
