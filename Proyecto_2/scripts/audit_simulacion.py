"""Preserve actual Packet Tracer OSI event decisions for an HTTP request."""
import asyncio,json
from build_project import OUT
from packet_tracer_mcp.server import mcp
async def tool(name,args=None):
 r=await mcp.call_tool(name,args or {});v=r[1]['result']
 try:return json.loads(v)
 except (ValueError,TypeError):return v
async def main():
 evidence={'scenario':'HTTP desde FG-ADM-PC1 al servidor central por su IP, con eventos OSI reales','steps':[]}
 try:
  evidence['start']=await tool('pt_simulation_mode',{'on':True})
  evidence['request']=await tool('pt_send_raw',{'js_code':'var h=ipc.network().getDevice("FG-ADM-PC1").getProcess("HttpClient");h.setHttps(false);h.go("http://192.168.98.242/");reportResult("HTTP requested");','wait_result':True})
  for _ in range(4):
   evidence['steps'].append(await tool('pt_simulation_step',{'action':'forward','times':15}))
   trace=await tool('pt_read_packet_trace',{'limit':200,'include_decisions':True})
   evidence['trace']=trace
   if isinstance(trace,dict) and any('HTTP reply' in d.get('description','') for f in trace.get('trace',[]) for d in f.get('decisions',[])):break
 finally:
  evidence['restore']=await tool('pt_simulation_mode',{'on':False})
 (OUT/'evidencias'/'auditoria'/'simulacion_http.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
 trace=evidence.get('trace',{})
 print('Trace types:',sorted(set(f.get('traffic_type','?') for f in trace.get('trace',[]))))
 print('Frames:',len(trace.get('trace',[])))
 print('Realtime restored:',evidence['restore'])
asyncio.run(main())
