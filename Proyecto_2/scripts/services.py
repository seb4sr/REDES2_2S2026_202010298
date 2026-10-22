import asyncio,json,sys
from build_project import OUT,devices,call
async def main(stage):
 if stage=='dhcp':
  names=[d['name'] for d in devices if d['model'] in ['PC-PT','Server-PT']]
  for start in range(0,len(names),5):
   js='var ns='+json.dumps(names[start:start+5])+';for(var i=0;i<ns.length;i++){configurePcIp(ns[i],true);}reportResult(ns.join(","));'
   await call('pt_send_raw',dict(js_code=js,wait_result=True))
 elif stage=='probe':
  js="var out=[];var names=['FG-DNS-WEB','ML-WIFI'];var procs=['DnsServer','HttpServer','HttpsServer','DhcpServer','WirelessCommon','WirelessClient','DhcpClient'];for(var i=0;i<names.length;i++){var d=ipc.network().getDevice(names[i]);for(var j=0;j<procs.length;j++){try{var p=d.getProcess(procs[j]);out.push(names[i]+' '+procs[j]+' '+String(p));}catch(e){out.push(String(e));}}}reportResult(out.join(' ; '));"
  await call('pt_send_raw',dict(js_code=js,wait_result=True))
 elif stage=='web':
  html='<html><head><title>Conectividad XXI</title></head><body bgcolor="#eff5ff"><h1>Conectividad XXI</h1><h2>Integracion de Operadores Nacionales</h2><p>Estudiante: Sergio Sandoval</p><p>Carne: 202010298</p><p>Universidad de San Carlos de Guatemala - Facultad de Ingenieria</p><p>Redes de Computadoras 2 - Segundo semestre 2026 - Proyecto 2</p><hr><p>FibraNet GT: OSPF, DNS y WEB. AndinaCom: OSPF, HSRP y DHCP. MoonLink: EIGRP y WiFi.</p><p>Interconexion nacional mediante BGP y fibra optica.</p></body></html>'
  (OUT/'diseno'/'index.html').write_text(html,encoding='utf-8')
  js="var d=ipc.network().getDevice('FG-DNS-WEB');var dns=d.getProcess('DnsServer');dns.setEnable(true);var ok=dns.addARecordToNameServerDb('www.proyecto2_202010298.com','192.168.98.242');var http=d.getProcess('HttpServer');http.setEnable(true);http.setPageContents('index.html',"+json.dumps(html)+");reportResult('DNS record:'+ok+' HTTP enabled:'+http.isEnabled());"
  js=js.replace("reportResult('DNS record:'", "var https=d.getProcess('HttpsServer');https.setEnable(true);https.setPageContents('index.html',"+json.dumps(html)+");reportResult('DNS record:'")
  await call('pt_send_raw',dict(js_code=js,wait_result=True))
 elif stage=='xml':
  for n in ['ML-WIFI','ML-SOP-LAP1','FG-DNS-WEB']:
   r=await call('pt_send_raw',dict(js_code='reportResult(ipc.network().getDevice('+json.dumps(n)+').serializeToXml());',wait_result=True))
   (OUT/'evidencias'/(n+'.xml')).write_text(r['result'],encoding='utf-8')
asyncio.run(main(sys.argv[1]))
