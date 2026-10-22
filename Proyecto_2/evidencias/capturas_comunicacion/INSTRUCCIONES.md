# Capturas pendientes para el manual

El apartado 4.10 del enunciado exige capturas de pantalla de las pruebas de comunicación. Los registros JSON de las pruebas ya existen, pero no son capturas de la interfaz. Guardar imágenes auténticas de Packet Tracer en esta carpeta y enlazarlas desde el manual.

1. **`01_ping_inter_isp.png`:** en AC-VEN-PC1 → Desktop → Command Prompt, ejecutar `ping 192.168.98.242`. Capturar el nombre del equipo, el comando y las estadísticas completas. Deben verse cuatro respuestas una vez estabilizada la red. El origen está en AndinaCom y el servidor en FibraNet.
2. **`02_acl_bloqueo_seguridad.png`:** consultar primero `ipconfig` en ML-SEG-PC1 para obtener su IP DHCP vigente. En FG-ADM-PC1 ejecutar ping a esa IP. Capturar el comando y las estadísticas de bloqueo. No usar una IP histórica sin verificar que siga asignada al destino.
3. **`03_web_http.png`:** AC-VEN-PC1 → Desktop → Web Browser, abrir `http://www.proyecto2_202010298.com/`. Mostrar URL, nombre, carné e información del curso.
4. **`04_web_https.png`:** repetir con `https://www.proyecto2_202010298.com/` y mostrar la URL HTTPS.
5. **Recomendado:** `show standby brief` en AC-R4/R5 antes y después de la prueba controlada, `show etherchannel summary` y `ipconfig /all` de la laptop WiFi.

Usar capturas de la aplicación, sin reemplazar el resultado por texto dibujado ni editar las cifras. Evitar que una ventana tape el comando, la URL o la identidad del equipo. Estas pruebas de preparación se realizan antes del único intento formal de ping que permite el enunciado durante la calificación.

Después de abrir el `.pkt`, esperar convergencia de OSPF/EIGRP/BGP y la adquisición DHCP antes de tomar las capturas. El modo Realtime debe estar activo. No configurar direcciones estáticas para acelerar esa espera.
