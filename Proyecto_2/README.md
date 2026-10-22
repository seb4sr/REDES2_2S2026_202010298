# Conectividad XXI: integración de operadores nacionales

**Estudiante:** Sergio Sandoval · **Carné:** 202010298 · Redes de Computadoras 2, segundo semestre 2026.

Estado: **red implementada y validada en Packet Tracer**. La captura real de Wireshark y su análisis están completos: 42 tramas de una VM Ubuntu en VMware, con los cuatro escenarios requeridos. La [auditoría del enunciado](AUDITORIA_ENUNCIADO.md) identifica los pendientes de capturas de comunicación en Packet Tracer, publicación remota y entrega en UEDI. No se presenta la entrega administrativa como completada.

Pruebas registradas: 20 hosts con DHCP, 30 casos de ping, 24 casos de ACL sobre HTTP/HTTPS, 14 accesos al sitio central, conmutación HSRP con ping 4/4 y falla de un miembro de cada uno de seis grupos LACP con seis pings 4/4. Ver [resultados y evidencia](evidencias/RESULTADOS.md).

La auditoría adicional comprobó **60/60 casos HTTP/HTTPS entre departamentos** y **40/40 accesos al sitio desde los 20 hosts finales**, además del estado CLI de los 26 equipos y el tipo óptico de los 17 enlaces entre routers. La [guía de calificación](GUIA_CALIFICACION.md) prepara la explicación en modo simulación y las preguntas de diseño.

## Archivos

- `diseno/topologia.json`: inventario, posiciones, conexiones y módulos.
- `diseno/direccionamiento.json`: interfaces, subredes y enlaces de fibra.
- `configs/`: comandos IOS por equipo y ACL departamentales separadas.
- `configs_aplicadas/`: configuraciones efectivas leídas de los 26 equipos IOS después de las pruebas.
- `MANUAL_TECNICO.md`: decisiones, tablas y procedimiento de evaluación.
- `evidencias/`: resultados reales de despliegue y verificación.
- `Wireshark/`: captura pcapng real, cinco imágenes, análisis por trama y scripts reproducibles.

El archivo de simulación es [Proyecto2_202010298.pkt](Proyecto2_202010298.pkt). La presentación de ocho diapositivas está en [Proyecto2_Presentacion_202010298.pdf](Proyecto2_Presentacion_202010298.pdf), con un [guion de aproximadamente siete minutos](GUION_PRESENTACION.md). El presupuesto es un supuesto académico explícito, no una cotización.

La evidencia está en [ANALISIS_WIRESHARK.md](Wireshark/ANALISIS_WIRESHARK.md) y [captura_wireshark_202010298.pcapng](Wireshark/captura_wireshark_202010298.pcapng). Los cambios están preparados localmente; no se han publicado automáticamente en GitHub.

No se ha modificado el Proyecto 1 del repositorio.
