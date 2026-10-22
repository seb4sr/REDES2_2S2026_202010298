import asyncio,json
from build_project import OUT,devices
from packet_tracer_mcp.server import mcp
async def raw(js):
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True));return r[1]['result']
async def main():
 target=OUT/'configs_aplicadas';target.mkdir(exist_ok=True)
 for d in devices:
  if d['model'] not in ['Router-PT-Empty','2960-24TT']:continue
  js='var d=ipc.network().getDevice('+json.dumps(d['name'])+');d.enterCommand("write memory","enable");reportResult(JSON.stringify(d.enterCommand("show running-config","enable")));'
  result=json.loads(await raw(js))
  if result['first']!=0:raise RuntimeError('Configuration export failed for '+d['name'])
  (target/(d['name']+'.cfg')).write_text(result['second'].replace('\\n','\n'),encoding='utf-8')
 print('Exported',len(list(target.glob('*.cfg'))),'actual running configurations')
asyncio.run(main())
