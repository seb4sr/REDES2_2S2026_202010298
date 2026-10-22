import asyncio,json,time
from build_project import OUT
from packet_tracer_mcp.server import mcp
PORTS={'FG-ADM-SW1':['FastEthernet0/1'],'FG-ATC-SW1':['FastEthernet0/1'],'AC-SW1':['FastEthernet0/1','FastEthernet0/3'],'ML-SOP-SW1':['FastEthernet0/1'],'ML-SEG-SW1':['FastEthernet0/1']}
HOSTS=['FG-ADM-PC1','FG-ATC-PC1','AC-VEN-PC1','AC-FAC-PC1','ML-SOP-PC1','ML-SEG-PC1']
async def raw(js):
 r=await mcp.call_tool('pt_send_raw',dict(js_code=js,wait_result=True));return r[1]['result']
async def ports(up):
 js='var out=[];'
 for n,ports in PORTS.items():
  cmds=['configure terminal']
  for p in ports:cmds+=['interface '+p,'no shutdown' if up else 'shutdown','exit']
  cmds+=['end']
  js+='var d=ipc.network().getDevice('+json.dumps(n)+');var cmds='+json.dumps(cmds)+';for(var i=0;i<cmds.length;i++)d.enterCommand(cmds[i],"");out.push({name:'+json.dumps(n)+',summary:d.enterCommand("show etherchannel summary","enable")});'
 return json.loads(await raw(js+'reportResult(JSON.stringify(out));'))
async def main():
 e={}
 try:
  e['with_one_member_down']=await ports(False)
  js='var ns='+json.dumps(HOSTS)+';var out=[];for(var i=0;i<ns.length;i++){var cl=ipc.network().getDevice(ns[i]).getCommandLine();var o=String(cl.getOutput());var m=o.match(/Packets: Sent/g);out.push({name:ns[i],base:m?m.length:0});cl.enterCommand("ping 192.168.98.242");}reportResult(JSON.stringify(out));'
  bases=json.loads(await raw(js));deadline=time.time()+80;pending=set(HOSTS);pings=[]
  while pending and time.time()<deadline:
   await asyncio.sleep(2)
   js='var ns='+json.dumps(bases)+';var out=[];for(var i=0;i<ns.length;i++){var o=String(ipc.network().getDevice(ns[i].name).getCommandLine().getOutput());var m=o.match(/Packets: Sent/g);if(m&&m.length>ns[i].base)out.push({name:ns[i].name,output:o.substring(o.lastIndexOf("Ping statistics"))});}reportResult(JSON.stringify(out));'
   for p in json.loads(await raw(js)):
    if p['name'] in pending:pings.append(p);pending.remove(p['name'])
  e['pings']=pings;e['timeouts']=list(pending)
 finally:
  e['restored']=await ports(True)
  (OUT/'evidencias'/'prueba_lacp.json').write_text(json.dumps(e,indent=2),encoding='utf-8')
 print(json.dumps(e),flush=True)
asyncio.run(main())
