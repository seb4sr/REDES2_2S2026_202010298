import asyncio, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT if ROOT.name=='Proyecto_2' else ROOT / 'REDES2_2S2026_202010298' / 'Proyecto_2'
for folder in ['configs', 'diseno', 'evidencias', 'Wireshark', 'scripts']:
    (OUT / folder).mkdir(parents=True, exist_ok=True)

devices = []
modules = []
links = []
def dev(name, model, x, y, **extra):
    devices.append(dict(name=name, model=model, x=x, y=y, **extra))
def link(a, ap, b, bp, cable='fiber', **extra):
    links.append(dict(a=a, ap=ap, b=b, bp=bp, cable=cable, **extra))
def router(name, x, y, fiber, copper=False):
    dev(name, 'Router-PT-Empty', x, y)
    for slot in range(fiber):
        modules.append(dict(device=name, slot=str(slot), module='PT-ROUTER-NM-1FGE'))
    if copper:
        modules.append(dict(device=name, slot='6', module='PT-ROUTER-NM-1CGE'))
def trunk_pair(prefix, x, y, vlan):
    for i, dx in [(1,-50),(2,50)]:
        dev(f'{prefix}-SW{i}', '2960-24TT', x+dx, y+(i-1)*100, vlan=vlan)
    for p in [1,2]:
        link(f'{prefix}-SW1', f'FastEthernet0/{p}', f'{prefix}-SW2', f'FastEthernet0/{p}', 'cross', bundle=1, vlans=[vlan])

# FibraNet: border -> distribution -> departmental gateways (a tree).
for i,x,y,n,c in [(1,500,200,4,False),(2,250,400,2,False),(3,750,400,2,True),(4,250,570,1,True),(5,750,570,1,True)]:
    router(f'FG-R{i}',x,y,n,c)
for a,ap,b,bp in [(1,2,2,0),(1,3,3,0),(2,1,4,0),(3,1,5,0)]:
    link(f'FG-R{a}',f'GigabitEthernet{ap}/0',f'FG-R{b}',f'GigabitEthernet{bp}/0')
for prefix,x,vlan,r in [('FG-ADM',250,10,4),('FG-ATC',750,20,5)]:
    trunk_pair(prefix,x,730,vlan)
    link(f'FG-R{r}','GigabitEthernet6/0',f'{prefix}-SW1','GigabitEthernet0/1','straight',access=vlan)
    for i in range(1,4):
        dev(f'{prefix}-PC{i}','PC-PT',x+(i-2)*100,970,department=prefix)
        link(f'{prefix}-SW2',f'FastEthernet0/{i+2}',f'{prefix}-PC{i}','FastEthernet0','straight',access=vlan)
dev('FG-DNS-WEB','Server-PT',1000,430,department='SERVICIOS')
link('FG-R3','GigabitEthernet6/0','FG-DNS-WEB','FastEthernet0','straight')

# AndinaCom: core, dual distribution, two redundant HSRP gateways.
for i,x,y,n,c in [(1,2200,200,4,False),(2,2000,400,3,False),(3,2400,400,3,False),(4,2000,580,2,True),(5,2400,580,2,True)]:
    router(f'AC-R{i}',x,y,n,c)
for a,ap,b,bp in [(1,2,2,0),(1,3,3,0),(2,1,4,0),(2,2,5,0),(3,1,4,1),(3,2,5,1)]:
    link(f'AC-R{a}',f'GigabitEthernet{ap}/0',f'AC-R{b}',f'GigabitEthernet{bp}/0')
for name,x,y in [('AC-SW1',2000,740),('AC-SW2',2400,740),('AC-SW3',2200,900)]:
    dev(name,'2960-24TT',x,y)
for p in [1,2]:
    link('AC-SW1',f'FastEthernet0/{p}','AC-SW2',f'FastEthernet0/{p}','cross',bundle=1,vlans=[30,40])
for p in [3,4]:
    link('AC-SW1',f'FastEthernet0/{p}','AC-SW3',f'FastEthernet0/{p-2}','cross',bundle=2,vlans=[30,40])
for r,s in [(4,1),(5,2)]:
    link(f'AC-R{r}','GigabitEthernet6/0',f'AC-SW{s}','GigabitEthernet0/1','straight',trunk=[30,40])
for dept,vlan,x in [('VEN',30,2050),('FAC',40,2400)]:
    for i in range(1,4):
        name=f'AC-{dept}-PC{i}'
        dev(name,'PC-PT',x+(i-2)*100,1070,department=f'AC-{dept}')
        port=i+2 if dept=='VEN' else i+5
        link('AC-SW3',f'FastEthernet0/{port}',name,'FastEthernet0','straight',access=vlan)

# MoonLink: the border is the hub, with four independent fiber spokes.
router('ML-R1',1350,1230,6)
for i,x,y,c in [(2,1030,1450,True),(3,1670,1450,True),(4,1000,1260,False),(5,1700,1260,False)]:
    router(f'ML-R{i}',x,y,1,c)
    link('ML-R1',f'GigabitEthernet{i}/0',f'ML-R{i}','GigabitEthernet0/0')
for prefix,x,vlan,r in [('ML-SOP',1030,50,2),('ML-SEG',1670,60,3)]:
    trunk_pair(prefix,x,1610,vlan)
    link(f'ML-R{r}','GigabitEthernet6/0',f'{prefix}-SW1','GigabitEthernet0/1','straight',access=vlan)
    for i in range(1,4):
        dev(f'{prefix}-PC{i}','PC-PT',x+(i-2)*100,1850,department=prefix)
        link(f'{prefix}-SW2',f'FastEthernet0/{i+2}',f'{prefix}-PC{i}','FastEthernet0','straight',access=vlan)
dev('ML-WIFI','Linksys-WRT300N',780,1740)
link('ML-SOP-SW2','FastEthernet0/6','ML-WIFI','Ethernet 1','straight',access=50)
dev('ML-SOP-LAP1','Laptop-PT',720,1870,department='ML-SOP',wireless=True,wireless_module='Linksys-WPC300N',ssid='Default',dhcp=True)

# eBGP triangle, matching the diagram on page 5.
link('FG-R1','GigabitEthernet0/0','AC-R1','GigabitEthernet0/0',bgp=True)
link('FG-R1','GigabitEthernet1/0','ML-R1','GigabitEthernet0/0',bgp=True)
link('AC-R1','GigabitEthernet1/0','ML-R1','GigabitEthernet1/0',bgp=True)

manifest = dict(student='Sergio Sandoval', carnet='202010298', devices=devices, modules=modules, links=links)
(OUT/'diseno'/'topologia.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')

async def call(name, args):
    from packet_tracer_mcp.server import mcp
    result=await mcp.call_tool(name,args)
    data=result[1] if isinstance(result,tuple) else result
    print(name, data, flush=True)
    with (OUT/'evidencias'/'despliegue.log').open('a',encoding='utf-8') as f:
        f.write(name+' '+str(data)+'\n')
    return data

async def main(stage):
    if stage=='devices':
        for start in range(0,len(devices),5):
            group=devices[start:start+5]
            js='var res=[];'
            for d in group:
                n=json.dumps(d['name'])
                js+=f'if(!ipc.network().getDevice({n})){{addDevice({n},{json.dumps(d["model"])},{d["x"]},{d["y"]});}}res.push({n});'
            await call('pt_send_raw',dict(js_code=js+'reportResult(res.join(","));',wait_result=True))
    elif stage=='modules':
        for prefix in ['FG','AC','ML']:
            batch=[m for m in modules if m['device'].startswith(prefix) and m['device']!='FG-R1']
            await call('pt_install_modules_batch',dict(modules=batch))
    elif stage=='links':
        for start in range(0,len(links),8):
            js='var res=[];'
            for l in links[start:start+8]:
                args=','.join(json.dumps(l[k]) for k in ['a','ap','b','bp','cable'])
                js+=f'res.push(String(addLink({args})));'
            await call('pt_send_raw',dict(js_code=js+'reportResult(res.join(","));',wait_result=True))
    elif stage=='fiber9':
        for l in [l for l in links if l['cable']=='fiber']:
            args=','.join(json.dumps(l[k]) for k in ['a','ap','b','bp'])
            js='var lw=ipc.appWindow().getActiveWorkspace().getLogicalWorkspace();'
            js+='var p=ipc.network().getDevice('+json.dumps(l['a'])+').getPort('+json.dumps(l['ap'])+');'
            js+='reportResult(p.getLink()!=null?"already linked":String(lw.createLink('+args+',8117)));'
            await call('pt_send_raw',dict(js_code=js,wait_result=True))
    elif stage=='save':
        await call('pt_save_project',dict(filename='Proyecto2_202010298.pkt',directory=str(OUT)))
    elif stage=='wireless':
        js="var d=ipc.network().getDevice('ML-SOP-LAP1');var w=ipc.network().getDevice('ML-WIFI');w.getProcess('DhcpServer').setEnable(false);w.getProcess('WirelessServer').setSsid('Default');if(!d.getPort('Wireless0')){d.setPower(false);d.removeModule('0');d.addModule('0',9,'Linksys-WPC300N');d.setPower(true);}var wp=w.getPhysicalObject();d.getPhysicalObject().moveTo(wp.getX()+5,wp.getY()+5);d.getProcess('WirelessClient').setSsid('Default');var p=d.getPort('Wireless0');p.setDhcpClientFlag(true);var dh=d.getProcess('DhcpClient');if(!dh.isPortExisted('Wireless0'))dh.addPortDataEntry('Wireless0');dh.dhcpRun('Wireless0');reportResult('WiFi configured; wait for association and DHCP');"
        await call('pt_send_raw',dict(js_code=js,wait_result=True))

if __name__=='__main__':
    asyncio.run(main(sys.argv[1]))
