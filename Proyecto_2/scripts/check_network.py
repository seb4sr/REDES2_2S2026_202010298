import asyncio,json
from build_project import OUT,call
async def main():
 checks={
  'FG-R1':['show ip bgp summary','show ip route','show ip ospf neighbor'],
  'AC-R1':['show ip bgp summary','show ip route','show ip ospf neighbor'],
  'ML-R1':['show ip bgp summary','show ip route','show ip eigrp neighbors'],
  'AC-R4':['show standby brief','show ip interface brief'],
  'AC-R5':['show standby brief','show ip dhcp pool','show ip dhcp binding'],
  'FG-ADM-SW1':['show etherchannel summary'],
  'FG-ATC-SW1':['show etherchannel summary'],
  'AC-SW1':['show etherchannel summary'],
  'ML-SOP-SW1':['show etherchannel summary'],
  'ML-SEG-SW1':['show etherchannel summary'],
 }
 for n,commands in checks.items():
  js='var d=ipc.network().getDevice('+json.dumps(n)+');var cmds='+json.dumps(commands)+';var out=[];'
  js+='for(var i=0;i<cmds.length;i++){out.push({command:cmds[i],result:d.enterCommand(cmds[i],"enable")});}reportResult(JSON.stringify(out));'
  r=await call('pt_send_raw',dict(js_code=js,wait_result=True))
  (OUT/'evidencias'/(n+'_verificacion.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
asyncio.run(main())
