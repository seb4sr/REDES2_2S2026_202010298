import os,subprocess,time
from pathlib import Path
base=Path('/home/captura/proyecto2')
env=dict(os.environ,DISPLAY=':99',QT_QPA_PLATFORM='xcb')
logs=(base/'wireshark_gui.log').open('w')
xvfb=subprocess.Popen(['Xvfb',':99','-screen','0','1440x1000x24','-nolisten','tcp'],stdout=logs,stderr=logs)
time.sleep(2)
cases=[('01_tcp_handshake','tcp.port == 80'),('02_dns','dns && ip.addr == 1.1.1.1'),('03_http','http'),('04_https_tls','tls'),('05_icmp','icmp')]
try:
 for name,display_filter in cases:
  args=['wireshark','-r',str(base/'captura_wireshark_202010298.pcapng'),'-Y',display_filter,'-o','gui.geometry_main_width:1440','-o','gui.geometry_main_height:1000']
  app=subprocess.Popen(args,env=env,stdout=logs,stderr=logs)
  time.sleep(5)
  if app.poll() is not None:raise RuntimeError('Wireshark GUI exited before screenshot: '+name)
  screenshot=base/(name+'.png')
  screenshot.unlink(missing_ok=True)
  subprocess.run(['scrot',str(screenshot)],env=env,check=True)
  app.terminate()
  try:app.wait(timeout=5)
  except subprocess.TimeoutExpired:app.kill();app.wait()
  print(name,flush=True)
finally:
 xvfb.terminate();xvfb.wait(timeout=5);logs.close()
