import asyncio,json
from build_project import OUT
from packet_tracer_mcp.server import mcp
async def main():
 result={}
 for name in ['pt_project_metadata','pt_health_check','pt_export_topology']:
  r=await mcp.call_tool(name,{})
  value=r[1]['result']
  try:value=json.loads(value)
  except ValueError:pass
  result[name]=value
 js='reportResult(JSON.stringify({simulation:ipc.simulation().isSimulationMode()}));'
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True));result['mode']=json.loads(r[1]['result'])
 (OUT/'evidencias'/'auditoria'/'estado_final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Healthy:',result['pt_health_check'].get('healthy'))
 print('Down links:',result['pt_health_check'].get('down_links'))
 print('Duplicate IPs:',result['pt_health_check'].get('duplicate_ips'))
 print('Simulation:',result['mode']['simulation'])
 print('Export keys:',list(result['pt_export_topology']) if isinstance(result['pt_export_topology'],dict) else type(result['pt_export_topology']).__name__)
asyncio.run(main())
