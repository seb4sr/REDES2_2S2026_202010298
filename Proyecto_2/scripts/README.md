# Automatización y reproducción

El punto de entrada para usar el proyecto terminado es `../Proyecto2_202010298.pkt`. Los scripts permiten inspeccionar el proyecto y reproducir la construcción en un lienzo nuevo con la extensión V5.2 activa.

## Dependencias

Python 3.11 o superior y `packet-tracer-mcp==0.9.0`. La extensión debe estar autenticada. Los scripts se comunican con el MCP instalado y no necesitan una API de IA ni claves adicionales.

Las configuraciones de routers y switches se aplican con `CiscoDevice.enterCommand`, la API de la CLI de Packet Tracer. DNS, HTTP/HTTPS y los clientes DHCP de los hosts se configuran con sus servicios nativos, ya que esos paneles no tienen CLI IOS.

## Orden de construcción en un lienzo nuevo

1. `python build_project.py devices`
2. `python build_project.py modules`
3. `python build_project.py links`
4. `python build_project.py fiber9`
5. `python generate_configs.py`
6. `python apply_cli.py base`
7. `python build_project.py wireless` para desactivar el DHCP del WRT antes de pedir concesiones.
8. Esperar convergencia OSPF/EIGRP/BGP y confirmar las rutas de servicios.
9. `python services.py dhcp` y `python services.py web`
10. `python apply_cli.py '*_ACL.cfg'`
11. `python validate_project.py inventory` y `python check_network.py`
12. `python build_project.py save`

El paso `links` usa el helper del MCP para cobre. El paso `fiber9` crea los enlaces ópticos con el tipo 8117 observado en Packet Tracer 9.0.1. Esta adaptación no debe trasladarse a otras versiones sin comprobar el tipo de enlace que utiliza su conexión automática.

Si la primera solicitud DHCP se hace antes de que haya rutas al servidor central, repetirla después de la convergencia. Nunca reemplazarla por una IP estática como alternativa.

## Validación

- `validate_project.py`: matriz dirigida de ping. `validate_project.py retry` repite únicamente casos permitidos que no recibieron cuatro respuestas y conserva el resultado previo.
- `test_web.py`: página diferente por protocolo y ejecución para confirmar que la respuesta es nueva, no contenido retenido por el navegador.
- `test_hsrp.py`: espera un activo y un respaldo, apaga AC-R4, comprueba el cambio y vuelve a encenderlo en un bloque `finally`.
- `test_lacp.py`: desactiva un miembro de cada grupo, comprueba seis pings y restaura los puertos en `finally`.
- `test_acl_web.py`: crea seis servidores departamentales temporales, obtiene DHCP, ejecuta 24 casos HTTP/HTTPS y los retira al finalizar.
- `export_evidence.py`: guarda las configuraciones efectivas obtenidas con `show running-config` y ejecuta `write memory`.
- `update_manual.py`: exige que las pruebas registradas cumplan sus condiciones antes de generar la tabla de resultados.
- `audit_acl_all.py`: comprueba 60 casos departamentales (30 pares dirigidos por HTTP y 30 por HTTPS), con marcadores únicos y servidores temporales retirados al terminar.
- `audit_web_hosts.py`: comprueba HTTP y HTTPS desde los 20 hosts finales y exporta sus opciones DHCP; restaura la página original en `finally`.
- `audit_live.py`: reúne lecturas CLI de los 26 equipos y comprueba el tipo de los 17 enlaces ópticos. No modifica su configuración.
- `audit_reopen_wait.py`: observa la adquisición automática de DHCP durante hasta tres minutos tras abrir el archivo. Guarda los resultados incluso si detecta un problema; no lo oculta con direcciones estáticas.
- `fix_ospf_startup.py`: aplica tipo de red OSPF point-to-point en los 20 extremos de los diez enlaces internos de FibraNet/AndinaCom, mediante CLI. El generador de configuración ya incluye ese ajuste.

Ejecutar las pruebas de fallas de una en una y conservar los archivos de evidencia. Los scripts de construcción no vacían el lienzo ni reemplazan equipos existentes; requieren revisar el inventario antes de reutilizarlos.

## Presentación

`generar_presentacion.py` genera el PDF desde la captura real de la topología. Usa ReportLab y las fuentes Segoe UI de Windows. El directorio opcional `.pdf-tools` del workspace contiene las dependencias del entorno de autoría; también pueden estar instaladas en el Python usado para ejecutar el script. El PDF final y el guion ya están incluidos.
