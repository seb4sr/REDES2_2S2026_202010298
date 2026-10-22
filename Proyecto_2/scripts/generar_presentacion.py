"""Executive PDF for the academic Packet Tracer pilot, not a market quotation."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'.pdf-tools'))
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

OUT=Path(__file__).resolve().parents[1]
FONTDIR=Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Segoe',str(FONTDIR/'segoeui.ttf')))
pdfmetrics.registerFont(TTFont('SegoeBold',str(FONTDIR/'segoeuib.ttf')))
pdfmetrics.registerFontFamily('Segoe',normal='Segoe',bold='SegoeBold')
W,H=960,540
NAVY=HexColor('#13243d');BLUE=HexColor('#075eaa');INK=HexColor('#172b44');GRAY=HexColor('#52647a')
c=canvas.Canvas(str(OUT/'Proyecto2_Presentacion_202010298.pdf'),pagesize=(W,H))
c.setTitle('Conectividad XXI - Sergio Sandoval - 202010298')
c.setAuthor('Sergio Sandoval')
page=0
def text(s,x,y,size=20,color=INK,bold=False,width=840):
 style=ParagraphStyle('body',fontName='SegoeBold' if bold else 'Segoe',fontSize=size,leading=size*1.32,textColor=color)
 p=Paragraph(s,style); _,height=p.wrap(width,H)
 if y-height<38: raise ValueError('Text overflows slide: '+s)
 p.drawOn(c,x,y-height)
 return y-height
def start(title):
 global page
 page+=1;c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
 text(title,54,493,32,bold=True)
 c.setFont('Segoe',10);c.setFillColor(GRAY);c.drawString(54,22,'Conectividad XXI - Sergio Sandoval - 202010298');c.drawRightString(906,22,str(page))
def end():c.showPage()
def row(values,y,widths,size=18,bold=False):
 x=54
 for value,width in zip(values,widths):text(str(value),x,y,size,bold=bold,width=width-14);x+=width

# 1. Cover.
page+=1;c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
text('Conectividad XXI',64,390,50,white,True)
text('Integración de operadores nacionales',66,300,28,white)
text('Sergio Sandoval<br/>Carné 202010298',66,185,20,white)
text('Redes de Computadoras 2<br/>USAC - Segundo semestre 2026',610,185,17,white,width=290)
end()

# 2. Business purpose.
start('Tres operadores conectados')
text('Una red común permite compartir servicios y mantener separados los departamentos.',54,420,26,width=820)
text('FibraNet GT',54,312,24,BLUE,True,width=260)
text('DNS y sitio web central.<br/>Árbol con OSPF.',54,268,20,width=260)
text('AndinaCom',354,312,24,BLUE,True,width=260)
text('DHCP centralizado.<br/>Jerarquía con OSPF y HSRP.',354,268,20,width=260)
text('MoonLink',654,312,24,BLUE,True,width=250)
text('Soporte y Seguridad.<br/>Hub con EIGRP y WiFi.',654,268,20,width=250)
text('BGP conecta los tres sistemas autónomos por fibra óptica.',54,134,22,bold=True)
end()

# 3. Actual evidence, not an illustrative generated topology.
start('Arquitectura del piloto')
image=ImageReader(str(OUT/'evidencias'/'topologia_completa.png'))
iw,ih=image.getSize();scale=min(570/iw,400/ih)
c.drawImage(image,54,62,width=iw*scale,height=ih*scale,preserveAspectRatio=True)
text('15 routers<br/>11 switches<br/>18 PC y una laptop<br/>Un servidor DNS/WEB',635,403,22,width=270)
text('17 enlaces de fibra<br/>Seis grupos LACP<br/>Dos gateways HSRP',635,235,21,width=270)
text('La captura completa y las configuraciones están en el manual técnico.',635,105,15,GRAY,width=270)
end()

# 4. Continuity.
start('Continuidad ante una falla')
text('HSRP conserva el gateway de Ventas cuando falla AC-R4.',54,420,26,width=820)
row(['Prueba','Resultado observado'],333,[445,400],20,True)
row(['Apagar el gateway AC-R4','AC-R5 pasa de respaldo a activo'],280,[445,400])
row(['Ping al servidor después del cambio','4 enviados, 4 recibidos'],229,[445,400])
row(['Agregación de enlaces','Seis grupos LACP activos'],178,[445,400])
text('HSRP protege el gateway. El servicio DHCP en AC-R5 sigue siendo un punto único para nuevas concesiones.',54,98,17,GRAY,width=840)
end()

# 5. Security and operations.
start('Servicios accesibles y departamentos aislados')
text('Todos los hosts finales, incluido el servidor, reciben su IP por DHCP.',54,420,25,width=830)
text('DNS y web',54,325,23,BLUE,True,width=360)
text('www.proyecto2_202010298.com<br/>HTTP y HTTPS desde los seis departamentos y la laptop.',54,278,20,width=390)
text('Reglas de comunicación',505,325,23,BLUE,True,width=390)
text('Seguridad inicia conexiones.<br/>Atención al Cliente y Facturación permanecen aislados.<br/>Las ACL permiten DNS, DHCP y los mensajes HSRP necesarios.',505,278,20,width=390)
text('Las pruebas incluyen tráfico permitido y tráfico que debe bloquearse.',54,102,20,bold=True)
end()

# 6. Academic budget, deliberately not presented as actual prices.
start('Presupuesto académico del piloto')
text('Supuestos en USD. No son cotizaciones ni un presupuesto de despliegue nacional.',54,434,17,GRAY)
widths=[430,135,135,150]
row(['Concepto','Cantidad','Unitario','Subtotal'],385,widths,17,True)
items=[('Routers modulares equivalentes',15,600),('Switches de acceso',11,250),('Interfaces ópticas',34,50),('Router WiFi',1,80),('Servidor de servicios',1,700),('Materiales y cableado',1,800),('Instalación y configuración',1,2000)]
y=345
for label,qty,cost in items:
 row([label,str(qty),f'${cost:,.0f}',f'${qty*cost:,.0f}'],y,widths,17);y-=31
base=sum(qty*cost for _,qty,cost in items);total=base*1.15
text(f'Base ${base:,.0f} + contingencia 15% = <b>${total:,.2f}</b>',54,105,24,BLUE)
text('No incluye terreno, obra civil de larga distancia, licencias, soporte, impuestos ni equipos de usuario.',54,59,13,GRAY)
end()

# 7. Actual tests and explicit boundary.
start('Validación y límites del prototipo')
text('BGP intercambia rutas entre los tres operadores.<br/>OSPF y EIGRP conectan las redes internas.<br/>La laptop usa WiFi y obtiene DHCP desde AndinaCom.',54,419,24,width=830)
text('Evidencia disponible',54,250,23,BLUE,True)
text('Matriz de ping, pruebas web por HTTP/HTTPS, estados LACP y prueba de conmutación HSRP.',54,207,21,width=825)
text('Pendiente de la entrega',54,125,21,BLUE,True)
text('Captura auténtica de Wireshark dentro de una VM y análisis de sus paquetes.',54,86,18,width=825)
end()

# 8. Rollout and business next step.
start('Despliegue por etapas')
row(['Etapa','Resultado esperado'],414,[280,570],21,True)
row(['Piloto técnico','Verificar protocolos, servicios y aislamiento con evidencia.'],348,[280,570],21)
row(['Validación de capacidad','Medir tráfico, dimensionar enlaces y validar equipos físicos.'],260,[280,570],21)
row(['Producción','Añadir redundancia de servicios, operación y monitoreo.'],172,[280,570],21)
text('La simulación demuestra el diseño lógico. La inversión real requiere ingeniería de campo y cotizaciones.',54,80,18,GRAY,width=840)
end()
c.save()
print(OUT/'Proyecto2_Presentacion_202010298.pdf')
