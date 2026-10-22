import asyncio,json,time,re
from build_project import OUT,call
from packet_tracer_mcp.server import mcp
async def raw(js):
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True))
 return r[1]['result']
async def show():
 r=await raw("var ns=['AC-R4','AC-R5'];var out=[];for(var i=0;i<ns.length;i++){out.push({device:ns[i],result:ipc.network().getDevice(ns[i]).enterCommand('show standby brief','enable')});}reportResult(JSON.stringify(out));")
 return json.loads(r)
async def port(up):
 return await raw('var d=ipc.network().getDevice("AC-R4");d.setPower('+str(up).lower()+');'+('d.skipBoot();' if up else '')+'reportResult("power:"+d.getPower());')
async def ping():
 n='AC-VEN-PC1';ip='192.168.98.242'
 await raw('var cl=ipc.network().getDevice('+json.dumps(n)+').getCommandLine();var o=String(cl.getOutput());var m=o.match(/Packets: Sent/g);cl.enterCommand('+json.dumps('ping '+ip)+');reportResult(String(m?m.length:0));')
 deadline=time.time()+70
 while time.time()<deadline:
  await asyncio.sleep(2)
  out=await raw('var o=String(ipc.network().getDevice('+json.dumps(n)+').getCommandLine().getOutput());reportResult(o.substring(o.lastIndexOf("ping '+ip+'")));')
  if 'Packets: Sent' in out:return out
 return 'No completed ping'
async def main():
 deadline=time.time()+100
 while True:
  state=await show()
  r4=state[0]['result']['second'].replace('\\n','\n')
  r5=state[1]['result']['second'].replace('\\n','\n')
  if re.search(r'\b30\s+115\s+P\s+Active\s+local',r4) and re.search(r'\b30\s+100\s+P\s+Standby',r5):break
  if time.time()>deadline:raise RuntimeError('HSRP baseline not stable; no failure injected')
  await asyncio.sleep(3)
 evidence={'before':state}
 print('Before',evidence['before'],flush=True)
 try:
  evidence['shutdown']=await port(False)
  deadline=time.time()+100
  while time.time()<deadline:
   await asyncio.sleep(3)
   state=await show()
   text=state[1]['result']['second'].replace('\\n','\n')
   lines=[l for l in text.splitlines() if re.search(r'\b30\s+100\s+P\s+Active\s+local',l)]
   if lines:
    evidence['after_failure']=state
    evidence['ping_after_failover']=await ping()
    break
  else:evidence['error']='HSRP did not reach expected active state before deadline'
 finally:
  evidence['restore']=await port(True)
  (OUT/'evidencias'/'prueba_hsrp.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 print(json.dumps(evidence),flush=True)
asyncio.run(main())
