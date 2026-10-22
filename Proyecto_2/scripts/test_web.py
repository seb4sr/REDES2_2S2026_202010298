import asyncio,json,time
from build_project import OUT,call
HOSTS=['FG-ADM-PC1','FG-ATC-PC1','AC-VEN-PC1','AC-FAC-PC1','ML-SOP-PC1','ML-SEG-PC1','ML-SOP-LAP1']
async def main():
 html=(OUT/'diseno'/'index.html').read_text()
 await call('pt_send_raw',dict(js_code="var h=ipc.network().getDevice('FG-DNS-WEB').getProcess('HttpsServer');h.setEnable(true);h.setPageContents('index.html',"+json.dumps(html)+");reportResult('HTTPS configured');",wait_result=True))
 results=[]
 for protocol in ['http','https']:
  marker='VALIDACION_'+protocol.upper()+'_'+str(int(time.time()))
  page=html.replace('</body>','<p>'+marker+'</p></body>')
  process='HttpsServer' if protocol=='https' else 'HttpServer'
  await call('pt_send_raw',dict(js_code="var h=ipc.network().getDevice('FG-DNS-WEB').getProcess("+json.dumps(process)+");h.setEnable(true);h.setPageContents('index.html',"+json.dumps(page)+");reportResult('Server marker configured');",wait_result=True))
  js='var ns='+json.dumps(HOSTS)+';var out=[];for(var i=0;i<ns.length;i++){var d=ipc.network().getDevice(ns[i]);var h=d.getProcess("HttpClient");h.setHttps('+str(protocol=='https').lower()+');out.push({name:ns[i],dns:d.getProcess("DnsClient").getServerIp(),started:h.go('+json.dumps(protocol+'://www.proyecto2_202010298.com/')+')});}reportResult(JSON.stringify(out));'
  started=await call('pt_send_raw',dict(js_code=js,wait_result=True))
  deadline=time.time()+60
  pending=set(HOSTS)
  while pending and time.time()<deadline:
   await asyncio.sleep(2)
   js='var ns='+json.dumps(list(pending))+';var out=[];for(var i=0;i<ns.length;i++){var h=ipc.network().getDevice(ns[i]).getProcess("HttpClient");out.push({name:ns[i],page:h.getLastPageContent()});}reportResult(JSON.stringify(out));'
   r=await call('pt_send_raw',dict(js_code=js,wait_result=True))
   for row in json.loads(r['result']):
    if marker in row['page']:
     results.append(dict(protocol=protocol,host=row['name'],ok=True,page=row['page']))
     pending.remove(row['name'])
  results.extend(dict(protocol=protocol,host=n,ok=False) for n in pending)
  (OUT/'evidencias'/'pruebas_web.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
  print(protocol,'completed; failures:',pending,flush=True)
asyncio.run(main())
