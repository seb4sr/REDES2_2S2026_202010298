# REDES2_1S2026_202010298 — Proyecto 1: Chapin Red

Documentación técnica de la implementación en Cisco Packet Tracer del Proyecto 1 del curso Redes de Computadoras 2.

> **Nota sobre el nombre del repositorio:** el enunciado del proyecto exige el formato `REDES2_1S2026_[Carné]`, por lo que este documento se identifica como `REDES2_1S2026_202010298`. El remoto Git configurado actualmente para este directorio de trabajo apunta a `REDES2_2S2026_202010298` (ciclo `2S2026`). Antes de la entrega debe confirmarse con el curso cuál convención de ciclo corresponde y, si es necesario, renombrar el repositorio remoto para que coincida con lo solicitado.

## Tabla de contenido

1. [Información general del proyecto](#1-información-general-del-proyecto)
2. [Topología](#2-topología)
   - [2.1 Topología completa](#21-topología-completa)
   - [2.2 Red MAN](#22-red-man)
   - [2.3 Edificio izquierdo](#23-edificio-izquierdo)
   - [2.4 Edificio derecho](#24-edificio-derecho)
   - [2.5 Edificio administrativo](#25-edificio-administrativo)
3. [Diseño de direccionamiento IP](#3-diseño-de-direccionamiento-ip)
   - [3.1 Método utilizado](#31-método-utilizado)
   - [3.2 Tabla VLSM de las VLAN](#32-tabla-vlsm-de-las-vlan)
   - [3.3 Tabla FLSM de enlaces enrutados](#33-tabla-flsm-de-enlaces-enrutados)
   - [3.4 Direcciones obtenidas por DHCP](#34-direcciones-obtenidas-por-dhcp)
4. [VLAN y VTP](#4-vlan-y-vtp)
   - [4.1 Tabla de VLAN](#41-tabla-de-vlan)
   - [4.2 VTP](#42-vtp)
5. [DHCP y DHCP Relay](#5-dhcp-y-dhcp-relay)
   - [5.1 Servidor DHCP1](#51-servidor-dhcp1)
   - [5.2 Servidor DHCP2](#52-servidor-dhcp2)
   - [5.3 DHCP Relay](#53-dhcp-relay)
6. [ACL](#6-acl)
7. [Enrutamiento dinámico](#7-enrutamiento-dinámico)
8. [Agregación de enlaces](#8-agregación-de-enlaces)
   - [8.1 LACP del edificio izquierdo](#81-lacp-del-edificio-izquierdo)
   - [8.2 PAgP del edificio derecho](#82-pagp-del-edificio-derecho)
   - [8.3 STP](#83-stp)
   - [8.4 Tolerancia a fallos](#84-tolerancia-a-fallos)
9. [Comandos principales utilizados](#9-comandos-principales-utilizados)
10. [Pruebas de funcionamiento](#10-pruebas-de-funcionamiento)
11. [Conclusiones](#11-conclusiones)
12. [Notas técnicas](#12-notas-técnicas)

---

## 1. Información general del proyecto

| Campo | Valor |
| --- | --- |
| Repositorio (nombre exigido por el enunciado) | `REDES2_1S2026_202010298` |
| Carpeta del proyecto | `Proyecto1` |
| Estudiante | Sergio Sandoval |
| Carné | `202010298` |
| Archivo de Packet Tracer | `proyecto1_202010298.pkt` |
| Protocolo de enrutamiento asignado | OSPF (último dígito del carné par) |
| Valor de `X` (últimos dos dígitos del carné) | `98` |
| Universidad | Universidad de San Carlos de Guatemala |
| Facultad | Facultad de Ingeniería |
| Carrera | Ingeniería en Ciencias y Sistemas |
| Curso | Redes de Computadoras 2 |

### Descripción de Chapin Red

Chapin Red es una organización dedicada a ejecutar proyectos de ayuda humanitaria desde distintos edificios de una misma sede. Su infraestructura de red debía atender necesidades de segmentación lógica entre departamentos, comunicación controlada entre áreas, asignación dinámica de direcciones IP para todos los equipos finales, y redundancia física ante la caída de enlaces o puertos individuales.

### Problema identificado

La red original no contaba con separación por departamentos ni por edificio, no existía un mecanismo centralizado de asignación de direcciones, no había control de qué VLAN podía comunicarse con cuál, y los enlaces entre switches no tenían redundancia, por lo que la falla de un solo cable o puerto podía aislar un edificio completo.

### Objetivo general

Implementar una infraestructura de red corporativa multi-edificio, seguray escalable para Chapin Red, aplicando segmentación por VLAN, enlace troncal administrado mediante VTP, enrutamiento dinámico con OSPF entre los switches multicapa, asignación dinámica de direcciones mediante DHCP y DHCP Relay, control de tráfico entre departamentos mediante listas de acceso, y tolerancia a fallos en los enlaces entre switches mediante EtherChannel (LACP y PAgP) mantenido y protegido por Spanning Tree.

---

## 2. Topología

La red de Chapin Red está compuesta por:

- **9 switches multicapa** (MS1 a MS9), que forman el núcleo, la distribución y el enrutamiento entre VLAN de la organización.
- **4 switches de acceso** (SW1 a SW4), que conectan directamente a los equipos finales.
- **2 servidores DHCP** (DHCP1 y DHCP2), cada uno atendiendo un edificio distinto a través de DHCP Relay.
- **Equipos finales** distribuidos en las VLAN Naranja, Verde y ADMIN, repartidos entre el edificio izquierdo, el edificio derecho y el área administrativa.
- **Enlaces de fibra en la red MAN** que interconectan MS1, MS2, MS6 y MS7 mediante rutas enrutadas redundantes.
- **Arquitectura jerárquica de tres capas** en el edificio izquierdo (núcleo/distribución con switches multicapa y acceso con SW1/SW2).
- **EtherChannel LACP** en el edificio izquierdo y **EtherChannel PAgP** en el edificio derecho, como mecanismo de redundancia y balanceo de carga entre switches.

### 2.1 Topología completa

![Topología completa de Chapin Red](images/Screenshot%202026-09-05%20013649.png)

La imagen anterior muestra la topología completa implementada: los dos servidores DHCP conectados a MS1, el anillo de enlaces enrutados de la MAN (líneas rojas) entre MS1, MS7, MS2 y MS6, el edificio izquierdo (MS7, MS8, MS9, SW1, SW2 con sus equipos Naranja y Verde), el edificio derecho (MS2, MS3, MS4, MS5, SW3, SW4 con sus equipos Naranja y Verde) y el nodo administrativo (MS6 y PC0).

### 2.2 Red MAN

![Red MAN entre MS1, MS2, MS6 y MS7](images/Screenshot%202026-09-05%20013649.png)

En el centro de la topología completa se observa la malla de enlaces enrutados que forma la red MAN: MS1 conecta con MS7 y con MS2; MS7 conecta con MS2 y con MS6; y MS2 conecta con MS6. Estos cinco enlaces (resaltados en rojo en la topología) corresponden a las subredes `/30` de la sección [3.3](#33-tabla-flsm-de-enlaces-enrutados) y son los únicos enlaces donde OSPF forma vecinos.

> **Captura pendiente:** un acercamiento (zoom) exclusivo de MS1, MS2, MS6 y MS7 facilitaría distinguir cada enlace de fibra de forma individual; actualmente solo se cuenta con la vista de la topología completa.

### 2.3 Edificio izquierdo

![Edificio izquierdo: MS7, MS8, MS9, SW1 y SW2](images/Screenshot%202026-09-05%20013649.png)

En la mitad izquierda de la topología se aprecia la arquitectura jerárquica de tres capas de este edificio:

- **Núcleo/distribución:** MS7 concentra el enrutamiento entre VLAN y la salida hacia la MAN; MS8 y MS9 distribuyen el tráfico hacia el acceso.
- **Acceso:** SW1 y SW2 conectan directamente los equipos finales.
- **VLAN 10 (Naranja)** y **VLAN 20 (Verde)** segmentan a los usuarios de este edificio.
- **Cinco grupos EtherChannel LACP** (Po1 a Po5) enlazan MS7–MS9, MS9–MS8, MS7–MS8, MS9–SW1 y MS8–SW2, aportando redundancia entre cada par de switches.

### 2.4 Edificio derecho

![Edificio derecho: MS2, MS3, MS4, MS5, SW3 y SW4](images/Screenshot%202026-09-05%20013649.png)

En la mitad derecha de la topología se observa el segundo edificio:

- **VLAN 30 (Naranja)** y **VLAN 40 (Verde)** segmentan a los usuarios de este edificio.
- **Tres grupos EtherChannel PAgP** (Po6 a Po8) enlazan MS2–MS3, MS3–MS4 y MS4–MS5.
- **SW3 y SW4** son los switches de acceso que conectan a los equipos finales Naranja y Verde del edificio derecho.

### 2.5 Edificio administrativo

![Edificio administrativo: MS6 y PC0](images/Screenshot%202026-09-05%20013649.png)

En la parte inferior central de la topología, MS6 conecta directamente a PC0, el equipo de la **VLAN 99 (ADMIN)**. MS6 participa en la red MAN (enlaces hacia MS7 y MS2) para permitir que el área administrativa alcance el resto de la organización según la política de control de tráfico descrita en la sección [6](#6-acl).

---

## 3. Diseño de direccionamiento IP

### 3.1 Método utilizado

- Para las cinco VLAN de la organización se utilizó el bloque `192.188.98.0/24`.
- Ese bloque se dividió mediante **VLSM** en cinco subredes `/29`, una por cada VLAN.
- Cada subred `/29` entrega ocho direcciones IP: una dirección de red, seis direcciones utilizables y una dirección de broadcast.
- De las seis direcciones utilizables de cada subred, una se reservó de forma fija para el **gateway** (la SVI del switch multicapa correspondiente).
- Las direcciones utilizables restantes se entregan a los equipos finales de forma dinámica mediante **DHCP**.
- Para los enlaces entre switches multicapa y hacia los servidores DHCP se utilizó el bloque `10.4.98.0/24`.
- Ese bloque se dividió mediante **FLSM** en subredes `/30`, adecuadas para enlaces punto a punto porque cada una entrega exactamente dos direcciones utilizables (una por extremo del enlace).

### 3.2 Tabla VLSM de las VLAN

| VLAN | Descripción                | Red/CIDR           | Máscara           | Rango utilizable                | Gateway         | Broadcast       |
| ---: | -------------------------- | ------------------ | ----------------- | -------------------------------- | ---------------- | ---------------- |
|   10 | Naranja edificio izquierdo | `192.188.98.0/29`  | `255.255.255.248` | `192.188.98.1 - 192.188.98.6`   | `192.188.98.1`  | `192.188.98.7`  |
|   20 | Verde edificio izquierdo   | `192.188.98.8/29`  | `255.255.255.248` | `192.188.98.9 - 192.188.98.14`  | `192.188.98.9`  | `192.188.98.15` |
|   30 | Naranja edificio derecho   | `192.188.98.16/29` | `255.255.255.248` | `192.188.98.17 - 192.188.98.22` | `192.188.98.17` | `192.188.98.23` |
|   40 | Verde edificio derecho     | `192.188.98.24/29` | `255.255.255.248` | `192.188.98.25 - 192.188.98.30` | `192.188.98.25` | `192.188.98.31` |
|   99 | Administración             | `192.188.98.32/29` | `255.255.255.248` | `192.188.98.33 - 192.188.98.38` | `192.188.98.33` | `192.188.98.39` |

### 3.3 Tabla FLSM de enlaces enrutados

| Enlace    | Red/CIDR        | Extremo A         | Extremo B           | Broadcast    |
| --------- | --------------- | ------------------ | -------------------- | ------------- |
| MS1–MS7   | `10.4.98.0/30`  | MS1: `10.4.98.1`  | MS7: `10.4.98.2`    | `10.4.98.3`  |
| MS1–MS2   | `10.4.98.4/30`  | MS1: `10.4.98.5`  | MS2: `10.4.98.6`    | `10.4.98.7`  |
| MS7–MS2   | `10.4.98.8/30`  | MS7: `10.4.98.9`  | MS2: `10.4.98.10`   | `10.4.98.11` |
| MS7–MS6   | `10.4.98.12/30` | MS7: `10.4.98.13` | MS6: `10.4.98.14`   | `10.4.98.15` |
| MS2–MS6   | `10.4.98.16/30` | MS2: `10.4.98.17` | MS6: `10.4.98.18`   | `10.4.98.19` |
| MS1–DHCP1 | `10.4.98.20/30` | MS1: `10.4.98.21` | DHCP1: `10.4.98.22` | `10.4.98.23` |
| MS1–DHCP2 | `10.4.98.24/30` | MS1: `10.4.98.25` | DHCP2: `10.4.98.26` | `10.4.98.27` |

Todos los enlaces anteriores utilizan máscara `255.255.255.252`.

### 3.4 Direcciones obtenidas por DHCP

| Dispositivo | VLAN | Dirección       |
| ----------- | ---: | --------------- |
| PC1         |   10 | `192.188.98.2`  |
| Laptop0     |   10 | `192.188.98.3`  |
| PC2         |   20 | `192.188.98.10` |
| Laptop1     |   20 | `192.188.98.11` |
| PC3         |   30 | `192.188.98.18` |
| PC4         |   30 | `192.188.98.19` |
| Laptop2     |   40 | `192.188.98.26` |
| Laptop3     |   40 | `192.188.98.27` |
| PC0         |   99 | `192.188.98.34` |

**Edificio izquierdo:**

![PC1 recibe 192.188.98.2 por DHCP y responde ping a su gateway y a DHCP1](images/Screenshot%202026-09-05%20005745.png)

PC1 (VLAN 10 Naranja) obtuvo `192.188.98.2/29` con gateway `192.188.98.1`; el `ipconfig /all` confirma el servidor DHCP `10.4.98.22`, y los `ping` hacia el gateway y hacia DHCP1 responden sin pérdida.

![PC2 recibe 192.188.98.10 por DHCP y responde ping a su gateway y a DHCP1](images/Screenshot%202026-09-05%20005815.png)

PC2 (VLAN 20 Verde) obtuvo `192.188.98.10/29` con gateway `192.188.98.9`, confirmando el funcionamiento del pool `VERDE_IZQ`.

**Edificio derecho:**

![PC3 recibe 192.188.98.18 por DHCP y responde ping a su gateway y a DHCP2](images/Screenshot%202026-09-05%20012239.png)

PC3 (VLAN 30 Naranja) obtuvo `192.188.98.18/29` con gateway `192.188.98.17`; el `ipconfig /all` confirma el servidor DHCP `10.4.98.26` (DHCP2).

![Laptop3 recibe 192.188.98.27 por DHCP y responde ping a su gateway](images/Screenshot%202026-09-05%20012502.png)

Laptop3 (VLAN 40 Verde) obtuvo `192.188.98.27/29` con gateway `192.188.98.25`, confirmando el funcionamiento del pool `VERDE_DER`.

**Confirmaciones adicionales (panel de configuración IP):**

![Laptop2 con dirección 192.188.98.26 asignada por DHCP](images/Screenshot%202026-09-05%20012922.png)
![PC4 con dirección 192.188.98.19 asignada por DHCP](images/Screenshot%202026-09-05%20012941.png)

Laptop2 y PC4 confirman, desde el panel de configuración IP, la asignación dinámica de `192.188.98.26` y `192.188.98.19` respectivamente, ambas dentro del rango esperado para VLAN 40 y VLAN 30.

> **Captura pendiente:** panel de configuración IP o `ipconfig /all` de PC0 (VLAN 99 ADMIN) mostrando la dirección `192.188.98.34` asignada por DHCP1. Su asignación se infiere indirectamente de las pruebas de la sección [10](#10-pruebas-de-funcionamiento), donde el resto de VLAN reciben "Destination host unreachable" al intentar alcanzar `192.188.98.34`.

---

## 4. VLAN y VTP

### 4.1 Tabla de VLAN

| VLAN | Nombre configurado                   | Edificio       |
| ---: | ------------------------------------- | -------------- |
|   10 | `VLAN_Naranja_EdificioIZQ_202010298` | Izquierdo      |
|   20 | `VLAN_Verde_EdificioIZQ_202010298`   | Izquierdo      |
|   30 | `VLAN_Naranja_EdificioDER_202010298` | Derecho        |
|   40 | `VLAN_Verde_EdificioDER_202010298`   | Derecho        |
|   99 | `VLAN_ADMIN_202010298`               | Administración |

### 4.2 VTP

| Parámetro | Valor |
| --- | --- |
| Dominio | `CHAPIN_RED_202010298` |
| Contraseña | `REDES2_98` |
| Versión | VTP 2 |

| Dominio de capa 2  | VTP Server | VTP Clients              |
| ------------------- | ---------- | ------------------------- |
| Edificio izquierdo  | MS7        | MS9, MS8, SW1 y SW2      |
| Edificio derecho    | MS2        | MS3, MS4, MS5, SW3 y SW4 |
| Administración      | MS6        | No aplica                 |
| Servicios           | MS1        | No aplica                 |

Existen varios servidores VTP porque cada dominio de capa 2 queda aislado por enlaces enrutados (capa 3): los anuncios VTP viajan únicamente dentro de los enlaces troncales de un mismo dominio de broadcast y no atraviesan los enlaces `/30` que interconectan MS1, MS2, MS6 y MS7. Por ello, cada agrupación de switches conectada por troncales propios necesita su propio servidor VTP.

Configuración representativa en un servidor (por ejemplo, MS7):

```cisco
vtp domain CHAPIN_RED_202010298
vtp password REDES2_98
vtp version 2
vtp mode server
```

Configuración representativa en un cliente (por ejemplo, MS9):

```cisco
vtp domain CHAPIN_RED_202010298
vtp password REDES2_98
vtp version 2
vtp mode client
```

> **Captura pendiente:** salida de `show vtp status` en un servidor (MS7 o MS2) y en un cliente (por ejemplo MS9), y salida de `show vlan brief` confirmando que las cinco VLAN se propagaron correctamente dentro de cada dominio de capa 2. Ninguna de las capturas disponibles en `images/` corresponde a estos comandos.

---

## 5. DHCP y DHCP Relay

### 5.1 Servidor DHCP1

Configuración de red de DHCP1: IP `10.4.98.22`, máscara `255.255.255.252`, gateway `10.4.98.21`.

| Pool          | Gateway         | Inicio          | Máscara           | Máximo |
| ------------- | --------------- | --------------- | ------------------ | -----: |
| `NARANJA_IZQ` | `192.188.98.1`  | `192.188.98.2`  | `255.255.255.248` |      5 |
| `VERDE_IZQ`   | `192.188.98.9`  | `192.188.98.10` | `255.255.255.248` |      5 |
| `ADMIN`       | `192.188.98.33` | `192.188.98.34` | `255.255.255.248` |      5 |

DNS entregado a los clientes: `8.8.8.8`.

![Pool NARANJA_IZQ configurado en DHCP1](images/Screenshot%202026-09-05%20005413.png)

![Pools NARANJA_IZQ y VERDE_IZQ activos en DHCP1](images/Screenshot%202026-09-05%20005447.png)

Ambas capturas muestran el servicio DHCP de DHCP1 habilitado (`Service: On`) sobre la interfaz `FastEthernet0`, con los pools `NARANJA_IZQ` y `VERDE_IZQ` correctamente definidos (gateway, DNS, dirección inicial, máscara y máximo de usuarios).

> **Captura pendiente:** evidencia visual del pool `ADMIN` dentro de DHCP1. Su funcionamiento se confirma de forma indirecta porque PC0 recibió `192.188.98.34`, dirección que pertenece exclusivamente a ese pool (ver tabla de la sección [3.4](#34-direcciones-obtenidas-por-dhcp)).

### 5.2 Servidor DHCP2

Configuración de red de DHCP2: IP `10.4.98.26`, máscara `255.255.255.252`, gateway `10.4.98.25`.

| Pool          | Gateway         | Inicio          | Máscara           | Máximo |
| ------------- | --------------- | --------------- | ------------------ | -----: |
| `NARANJA_DER` | `192.188.98.17` | `192.188.98.18` | `255.255.255.248` |      5 |
| `VERDE_DER`   | `192.188.98.25` | `192.188.98.26` | `255.255.255.248` |      5 |

DNS entregado a los clientes: `8.8.8.8`.

`10.4.98.26` es la dirección IP del propio servidor DHCP2 sobre el enlace enrutado hacia MS1, mientras que `192.188.98.26` es la dirección asignada dinámicamente a Laptop2 dentro de la VLAN 40. No existe conflicto entre ambas porque pertenecen a redes completamente distintas (`10.4.98.24/30` frente a `192.188.98.24/29`).

> **Captura pendiente:** panel de configuración de servicios DHCP de DHCP2 mostrando los pools `NARANJA_DER` y `VERDE_DER`. El funcionamiento de ambos pools se comprueba de forma funcional en la sección [3.4](#34-direcciones-obtenidas-por-dhcp), donde PC3, PC4, Laptop2 y Laptop3 obtienen direcciones dentro de sus rangos correspondientes y confirman `10.4.98.26` como servidor DHCP asignador.

### 5.3 DHCP Relay

| Switch multicapa | SVI     | Helper       |
| ----------------- | ------- | ------------- |
| MS7                | VLAN 10 | `10.4.98.22` |
| MS7                | VLAN 20 | `10.4.98.22` |
| MS2                | VLAN 30 | `10.4.98.26` |
| MS2                | VLAN 40 | `10.4.98.26` |
| MS6                | VLAN 99 | `10.4.98.22` |

Comando representativo (SVI de VLAN 10 en MS7):

```cisco
interface Vlan10
 ip address 192.188.98.1 255.255.255.248
 ip helper-address 10.4.98.22
 no shutdown
```

Las capturas de `ipconfig /all` de la sección [3.4](#34-direcciones-obtenidas-por-dhcp) constituyen la evidencia de que el DHCP Relay funciona correctamente: cada cliente, ubicado en una VLAN distinta a la del servidor DHCP, recibió una dirección válida y reconoce como "DHCP Servers" la dirección `10.4.98.22` o `10.4.98.26` según el edificio, lo que solo es posible si el `ip helper-address` configurado en la SVI reenvía la solicitud a través de la red enrutada.

---

## 6. ACL

Las listas de acceso extendidas implementan las siguientes políticas departamentales de Chapin Red:

1. Las VLAN Naranja de ambos edificios pueden comunicarse entre sí.
2. Las VLAN Verde de ambos edificios pueden comunicarse entre sí.
3. Naranja no puede comunicarse con Verde.
4. Verde no puede comunicarse con Naranja.
5. Ninguna VLAN de usuarios puede iniciar comunicación hacia ADMIN.
6. ADMIN puede iniciar comunicación hacia todas las VLAN.
7. Se permiten respuestas ICMP `echo-reply` y sesiones TCP `established` hacia ADMIN, para que las respuestas a comunicaciones iniciadas por ADMIN puedan regresar.
8. Se permite el tráfico DHCP (`bootpc`/`bootps`) antes de cualquier regla de denegación, para no interrumpir la asignación dinámica de direcciones.

| ACL               | Aplicación   | Dirección | Propósito                                                                 |
| ------------------ | ------------ | --------- | --------------------------------------------------------------------------- |
| `ACL_NARANJA_IZQ` | MS7, VLAN 10 | Inbound   | Permitir Naranja izquierda hacia Naranja derecha y bloquear Verde/ADMIN     |
| `ACL_VERDE_IZQ`   | MS7, VLAN 20 | Inbound   | Permitir Verde izquierda hacia Verde derecha y bloquear Naranja/ADMIN       |
| `ACL_NARANJA_DER` | MS2, VLAN 30 | Inbound   | Permitir Naranja derecha hacia Naranja izquierda y bloquear Verde/ADMIN     |
| `ACL_VERDE_DER`   | MS2, VLAN 40 | Inbound   | Permitir Verde derecha hacia Verde izquierda y bloquear Naranja/ADMIN       |

Contenido capturado directamente desde MS7 (`show access-lists`):

```cisco
MS7#show access-lists
Extended IP access list ACL_NARANJA_IZQ
    10 permit udp any eq bootpc any eq bootps
    20 permit ip 192.188.98.0 0.0.0.7 192.188.98.16 0.0.0.7
    30 permit icmp 192.188.98.0 0.0.0.7 192.188.98.32 0.0.0.7 echo-reply
    40 permit tcp 192.188.98.0 0.0.0.7 192.188.98.32 0.0.0.7 established
    50 deny ip 192.188.98.0 0.0.0.7 192.188.98.8 0.0.0.7
    60 deny ip 192.188.98.0 0.0.0.7 192.188.98.24 0.0.0.7
    70 deny ip 192.188.98.0 0.0.0.7 192.188.98.32 0.0.0.7
    80 permit ip 192.188.98.0 0.0.0.7 any
Extended IP access list ACL_VERDE_IZQ
    10 permit udp any eq bootpc any eq bootps
    20 permit ip 192.188.98.8 0.0.0.7 192.188.98.24 0.0.0.7
    30 permit icmp 192.188.98.8 0.0.0.7 192.188.98.32 0.0.0.7 echo-reply
    40 permit tcp 192.188.98.8 0.0.0.7 192.188.98.32 0.0.0.7 established
    50 deny ip 192.188.98.8 0.0.0.7 192.188.98.0 0.0.0.7
    60 deny ip 192.188.98.8 0.0.0.7 192.188.98.16 0.0.0.7
    70 deny ip 192.188.98.8 0.0.0.7 192.188.98.32 0.0.0.7
    80 permit ip 192.188.98.8 0.0.0.7 any

interface Vlan10
 ip access-group ACL_NARANJA_IZQ in
interface Vlan20
 ip access-group ACL_VERDE_IZQ in
```

![show access-lists en MS7 con contadores de coincidencias tras las pruebas](images/Screenshot%202026-09-05%20013941.png)

Contenido capturado directamente desde MS2, con la misma lógica reflejada en sentido opuesto:

```cisco
MS2#show access-lists
Extended IP access list ACL_NARANJA_DER
    10 permit udp any eq bootpc any eq bootps
    20 permit ip 192.188.98.16 0.0.0.7 192.188.98.0 0.0.0.7
    30 permit icmp 192.188.98.16 0.0.0.7 192.188.98.32 0.0.0.7 echo-reply
    40 permit tcp 192.188.98.16 0.0.0.7 192.188.98.32 0.0.0.7 established
    50 deny ip 192.188.98.16 0.0.0.7 192.188.98.24 0.0.0.7
    60 deny ip 192.188.98.16 0.0.0.7 192.188.98.8 0.0.0.7
    70 deny ip 192.188.98.16 0.0.0.7 192.188.98.32 0.0.0.7
    80 permit ip 192.188.98.16 0.0.0.7 any
Extended IP access list ACL_VERDE_DER
    10 permit udp any eq bootpc any eq bootps
    20 permit ip 192.188.98.24 0.0.0.7 192.188.98.8 0.0.0.7
    30 permit icmp 192.188.98.24 0.0.0.7 192.188.98.32 0.0.0.7 echo-reply
    40 permit tcp 192.188.98.24 0.0.0.7 192.188.98.32 0.0.0.7 established
    50 deny ip 192.188.98.24 0.0.0.7 192.188.98.16 0.0.0.7
    60 deny ip 192.188.98.24 0.0.0.7 192.188.98.0 0.0.0.7
    70 deny ip 192.188.98.24 0.0.0.7 192.188.98.32 0.0.0.7
    80 permit ip 192.188.98.24 0.0.0.7 any

interface Vlan30
 ip access-group ACL_NARANJA_DER in
interface Vlan40
 ip access-group ACL_VERDE_DER in
```

![show access-lists en MS2 con contadores de coincidencias tras las pruebas](images/Screenshot%202026-09-05%20013954.png)

En ambas capturas, las líneas `permit`/`deny` que fueron ejercitadas durante las pruebas de ping muestran contadores de coincidencias mayores a cero, lo que confirma que el tráfico real de las pruebas atravesó exactamente las reglas esperadas.

### Verificación de la aplicación de las ACL

Packet Tracer mostró de forma incorrecta el mensaje `Inbound access list is not set` al ejecutar `show ip interface` sobre las SVI de VLAN, a pesar de que las ACL sí estaban activas. Para confirmar la aplicación real se utilizaron dos comandos alternativos:

```cisco
show running-config | include access-group
show access-lists
```

El primero confirma que la sentencia `ip access-group <ACL> in` está presente en cada SVI, y el segundo muestra los contadores de coincidencias por regla, que solo aumentan si el tráfico efectivamente pasó por esa interfaz con esa ACL aplicada.

### Comprobación funcional

- PC1 (Naranja izquierda) alcanzó con éxito a PC3 (Naranja derecha).
- PC1 no pudo alcanzar ninguna dirección de las VLAN Verde ni de ADMIN.
- Las VLAN Verde de ambos edificios se comunicaron entre sí sin restricciones.
- PC0 (ADMIN) pudo iniciar pings hacia todas las VLAN de usuarios sin ser bloqueado.
- Ninguna VLAN de usuarios pudo iniciar pings hacia PC0.

![PC0 (ADMIN) alcanza con éxito a la VLAN Naranja y a la VLAN Verde del edificio izquierdo](images/Screenshot%202026-09-05%20013500.png)

![Un host de la VLAN Naranja izquierda alcanza su propia VLAN y a Naranja derecha, y es bloqueado hacia Verde izquierda, Verde derecha y ADMIN](images/Screenshot%202026-09-05%20013518.png)

La segunda captura evidencia el comportamiento exacto de `ACL_NARANJA_IZQ`: el ping a `192.188.98.3` (mismo segmento) responde de inmediato; el ping a `192.188.98.18` (Naranja derecha) se completa, con una pequeña pérdida inicial atribuible a la resolución ARP; y los pings a `192.188.98.10` (Verde izquierda), `192.188.98.26` (Verde derecha) y `192.188.98.34` (ADMIN) regresan "Destination host unreachable" por la denegación explícita de la ACL.

![Un host de la VLAN Naranja derecha alcanza su propia VLAN y es bloqueado hacia Verde izquierda y ADMIN](images/Screenshot%202026-09-05%20013757.png)

![PC0 (ADMIN) alcanza con éxito a la VLAN Naranja y a la VLAN Verde del edificio derecho](images/Screenshot%202026-09-05%20013854.png)

---

## 7. Enrutamiento dinámico

Se utilizó **OSPF** como protocolo de enrutamiento dinámico porque el último dígito del carné `202010298` es par.

- Proceso OSPF: `1`.
- Área utilizada: `0` (área única).
- Se configuró `passive-interface default` en todos los switches multicapa con OSPF.
- Únicamente los enlaces enrutados `/30` entre switches multicapa (sección [3.3](#33-tabla-flsm-de-enlaces-enrutados)) participan activamente en la formación de vecinos.
- Las redes de las VLAN de usuario y las redes hacia los servidores DHCP se anuncian mediante `network`, pero permanecen pasivas y no forman vecinos, ya que en esos segmentos no hay otros routers OSPF.

| Dispositivo | Router ID |
| ------------ | ---------- |
| MS1          | `1.1.1.1` |
| MS2          | `2.2.2.2` |
| MS6          | `6.6.6.6` |
| MS7          | `7.7.7.7` |

| Dispositivo | Vecinos          |
| ------------ | ----------------- |
| MS1          | MS7 y MS2        |
| MS2          | MS1, MS7 y MS6   |
| MS7          | MS1, MS2 y MS6   |
| MS6          | MS7 y MS2        |

Configuración representativa (MS7):

```cisco
router ospf 1
 router-id 7.7.7.7
 passive-interface default
 no passive-interface GigabitEthernet1/1/1
 no passive-interface GigabitEthernet1/1/2
 no passive-interface GigabitEthernet1/1/3
 network 10.4.98.0 0.0.0.31 area 0
 network 192.188.98.0 0.0.0.7 area 0
 network 192.188.98.8 0.0.0.7 area 0
```

> **Captura pendiente:** salida de `show ip ospf neighbor` en al menos dos switches multicapa (por ejemplo MS7 y MS2) confirmando las vecindades de la tabla anterior, y salida de `show ip route` mostrando las rutas marcadas con `O` aprendidas dinámicamente hacia las VLAN remotas. Ninguna de las capturas disponibles en `images/` corresponde a estos comandos; las pruebas de ping de la sección [10](#10-pruebas-de-funcionamiento) demuestran de forma indirecta que el enrutamiento entre edificios funciona (por ejemplo, PC1 alcanzando `192.188.98.18` en el edificio derecho), pero no sustituyen la evidencia directa de OSPF.

---

## 8. Agregación de enlaces

### 8.1 LACP del edificio izquierdo

| Canal | Extremo A          | Extremo B      | Miembros |
| ------ | -------------------- | ---------------- | -------: |
| Po1    | MS7 `Gig1/0/1-3`    | MS9 `Fa0/1-3`   |        3 |
| Po2    | MS9 `Fa0/4-6`       | MS8 `Fa0/1-3`   |        3 |
| Po3    | MS7 `Gig1/0/4-6`    | MS8 `Fa0/4-6`   |        3 |
| Po4    | MS9 `Fa0/7-8`       | SW1 `Fa0/1-2`   |        2 |
| Po5    | MS8 `Fa0/7-8`       | SW2 `Fa0/1-2`   |        2 |

Protocolo: **LACP**, modo `active` en ambos extremos de cada canal.

```cisco
interface range FastEthernet0/1-3
 channel-group 1 mode active
 no shutdown

interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

### 8.2 PAgP del edificio derecho

| Canal | Extremo A          | Extremo B      | Miembros |
| ------ | -------------------- | ---------------- | -------: |
| Po6    | MS2 `Gig1/0/1-3`    | MS3 `Fa0/1-3`   |        3 |
| Po7    | MS3 `Fa0/4-7`       | MS4 `Fa0/4-7`   |        4 |
| Po8    | MS4 `Fa0/8-9`       | MS5 `Fa0/8-9`   |        2 |

Protocolo: **PAgP**, modo final `desirable` en ambos extremos. Se descartó el modo `auto` porque, en el simulador, dos extremos en `auto` no negocian el canal (ambos quedan a la espera del otro), por lo que fue necesario forzar `desirable`/`desirable` para lograr la formación del Port-channel.

```cisco
interface range FastEthernet0/4-7
 channel-group 7 mode desirable
 no shutdown

interface Port-channel7
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 30,40
```

> **Captura pendiente:** salida de `show etherchannel summary` en al menos un switch de cada edificio (por ejemplo MS7 para LACP y MS2 para PAgP), mostrando el estado `SU` de cada Port-channel y el estado `P` de sus puertos miembro. Ninguna de las capturas disponibles en `images/` corresponde a este comando.

### 8.3 STP

Se utilizó **Rapid-PVST** como modo de Spanning Tree.

- MS7 es el puente raíz para VLAN 10 y VLAN 20 (edificio izquierdo).
- MS2 es el puente raíz para VLAN 30 y VLAN 40 (edificio derecho).
- MS6 es el puente raíz para VLAN 99 (administración).
- En el triángulo redundante del edificio izquierdo (MS7–MS8–MS9), STP bloqueó el Port-channel Po2 para evitar un bucle de capa 2, dejándolo en estado de bloqueo mientras Po1 y Po3 permanecen reenviando.
- El canal bloqueado permanece configurado y disponible: si Po1 o Po3 fallan, STP lo recalcula y coloca a Po2 en estado de reenvío, preservando la conectividad del edificio.

```cisco
spanning-tree mode rapid-pvst
spanning-tree vlan 10,20 root primary
```

> **Captura pendiente:** salida de `show spanning-tree vlan 10` (o `vlan 20`) en MS7, MS8 y MS9, mostrando el puente raíz y el puerto bloqueado (`BLK`) en el enlace correspondiente a Po2.

### 8.4 Tolerancia a fallos

Metodología de la prueba:

1. Se ejecutó un ping continuo entre PC1 (`192.188.98.2`) y PC3 (`192.188.98.18`), atravesando ambos edificios y la red MAN.
2. Con el ping en curso, se apagó individualmente un miembro de cada EtherChannel (`shutdown` en uno de los puertos físicos que forman el Port-channel).
3. El puerto apagado apareció marcado como `(D)` (down) en `show etherchannel summary`, mientras el Port-channel permaneció en estado `SU` (en uso) y los demás miembros conservaron el estado `(P)` (bundled).
4. El ping continuó respondiendo sin interrupción durante la prueba, confirmando que el tráfico se redistribuyó automáticamente entre los puertos activos restantes del canal.
5. Se restauró cada puerto apagado con `no shutdown` y se verificó que todos los miembros del canal regresaran al estado `(P)`.

| Protocolo | Canales probados | Resultado                                             |
| ---------- | ------------------ | ------------------------------------------------------- |
| LACP       | Po1–Po5            | El canal permaneció activo al desconectar un miembro   |
| PAgP       | Po6–Po8            | El canal permaneció activo al desconectar un miembro   |

> **Captura pendiente:** salida de `show etherchannel summary` antes y después de apagar un miembro de un Port-channel (mostrando el flag `(D)` en el puerto caído y `SU` en el canal), junto con la ventana de ping continuo evidenciando cero pérdida de paquetes durante la falla simulada. Se cuenta únicamente con una captura de un ping sostenido de PC1 hacia `192.188.98.18` con respuestas exitosas continuas, pero sin evidencia del paso de apagado/restauración de un puerto, por lo que no se incluyó como prueba de tolerancia a fallos.

---

## 9. Comandos principales utilizados

### VLAN

```cisco
vlan 10
 name VLAN_Naranja_EdificioIZQ_202010298

interface FastEthernet0/10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
```

### Trunk

```cisco
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

### Enrutamiento en switch multicapa

```cisco
ip routing

interface GigabitEthernet1/1/1
 no switchport
 ip address 10.4.98.1 255.255.255.252
 no shutdown
```

### SVI y DHCP Relay

```cisco
interface Vlan10
 ip address 192.188.98.1 255.255.255.248
 ip helper-address 10.4.98.22
 no shutdown
```

### OSPF

Ver ejemplo completo en la sección [7](#7-enrutamiento-dinámico).

### LACP

```cisco
channel-group 1 mode active
```

### PAgP

```cisco
channel-group 6 mode desirable
```

### ACL

```cisco
ip access-list extended ACL_NARANJA_IZQ
ip access-group ACL_NARANJA_IZQ in
```

### Verificación

| Comando | Uso |
| --- | --- |
| `show ip interface brief` | Estado y direccionamiento de cada interfaz física y SVI. |
| `show vlan brief` | VLAN existentes y puertos asignados a cada una. |
| `show vtp status` | Modo VTP, dominio, versión y número de revisión. |
| `show interfaces trunk` | Puertos y Port-channel en modo troncal, VLAN permitidas. |
| `show etherchannel summary` | Estado de cada Port-channel y de sus puertos miembro. |
| `show spanning-tree` | Puente raíz, costos y puertos bloqueados por VLAN. |
| `show ip ospf neighbor` | Vecinos OSPF formados por cada switch multicapa. |
| `show ip route` | Tabla de enrutamiento, incluyendo rutas OSPF marcadas con `O`. |
| `show access-lists` | Reglas de cada ACL y contador de coincidencias por línea. |
| `show running-config \| include access-group` | Confirma en qué interfaces está aplicada cada ACL. |
| `copy running-config startup-config` | Guarda la configuración activa como configuración de arranque. |

---

## 10. Pruebas de funcionamiento

| Origen              | Destino                    | Política   | Resultado esperado | Evidencia |
| -------------------- | --------------------------- | ----------- | -------------------- | --------- |
| Naranja izquierda    | Naranja derecha             | Permitido  | Exitoso             | [013518](images/Screenshot%202026-09-05%20013518.png) |
| Verde izquierda      | Verde derecha               | Permitido  | Exitoso             | [013500](images/Screenshot%202026-09-05%20013500.png) |
| Naranja               | Verde                       | Bloqueado  | Fallido             | [013518](images/Screenshot%202026-09-05%20013518.png), [013757](images/Screenshot%202026-09-05%20013757.png) |
| Verde                 | Naranja                     | Bloqueado  | Fallido             | [013518](images/Screenshot%202026-09-05%20013518.png) |
| ADMIN                 | Cualquier VLAN              | Permitido  | Exitoso             | [013500](images/Screenshot%202026-09-05%20013500.png), [013854](images/Screenshot%202026-09-05%20013854.png) |
| VLAN de usuario       | ADMIN                       | Bloqueado  | Fallido             | [013518](images/Screenshot%202026-09-05%20013518.png), [013757](images/Screenshot%202026-09-05%20013757.png) |
| Cliente               | Gateway                     | Permitido  | Exitoso             | [005745](images/Screenshot%202026-09-05%20005745.png), [005815](images/Screenshot%202026-09-05%20005815.png) |
| Cliente DHCP          | Servidor correspondiente    | Permitido  | Exitoso             | [005745](images/Screenshot%202026-09-05%20005745.png), [012239](images/Screenshot%202026-09-05%20012239.png) |

Adicionalmente, se comprobó la comunicación dentro de una misma VLAN entre dos equipos finales:

![Laptop0 responde ping a su gateway y a PC1, ambos dentro de VLAN 10](images/Screenshot%202026-09-05%20005845.png)

Laptop0 (`192.188.98.3`) alcanza sin restricciones a PC1 (`192.188.98.2`), confirmando que la comunicación intra-VLAN dentro de un mismo edificio no está sujeta a ninguna de las ACL, ya que estas solo se aplican al tráfico entrante hacia la SVI (tráfico entre VLAN distintas).

---

## 11. Conclusiones

1. La segmentación por VLAN (Naranja, Verde y ADMIN, replicadas en ambos edificios) permitió organizar el tráfico de Chapin Red por departamento y por edificio, y sirvió como base para aplicar políticas de control de tráfico diferenciadas sin necesidad de subredes físicas independientes.
2. OSPF, ejecutado únicamente sobre los enlaces `/30` de la red MAN con `passive-interface default`, permitió que MS1, MS2, MS6 y MS7 intercambiaran rutas de forma dinámica hacia las VLAN de ambos edificios; esto se evidenció en que hosts de un edificio alcanzaron con éxito direcciones IP de VLAN ubicadas físicamente en el edificio contrario (por ejemplo, `192.188.98.2` alcanzando `192.188.98.18`).
3. Los EtherChannel LACP (edificio izquierdo) y PAgP (edificio derecho) agregaron múltiples enlaces físicos entre switches en un único enlace lógico, y junto con Rapid-PVST evitaron bucles de capa 2 en la topología redundante sin perder la ruta de respaldo: el bloqueo de Po2 por STP demuestra que la redundancia física existe incluso cuando no está siendo utilizada activamente.
4. El uso de DHCP Relay (`ip helper-address`) permitió centralizar la asignación de direcciones en dos servidores (DHCP1 y DHCP2) atendiendo cinco VLAN distintas a través de enlaces enrutados, evitando desplegar un servidor DHCP físico por cada VLAN o edificio.
5. Las listas de acceso extendidas aplicadas en las SVI de MS7 y MS2 cumplieron simultáneamente las cinco políticas departamentales solicitadas (Naranja-Naranja, Verde-Verde, bloqueo cruzado Naranja/Verde, control unidireccional hacia ADMIN y excepción para DHCP), verificado tanto por los contadores de `show access-lists` como por las pruebas de ping reales entre equipos finales.

---

## 12. Notas técnicas

- Fue necesario limpiar configuraciones residuales de puertos e interfaces `Port-channel` antes de reconstruir algunos EtherChannel, ya que Packet Tracer conserva asociaciones de `channel-group` previas que impiden formar el canal nuevamente si no se retiran primero.
- Algunos comandos de verificación disponibles en IOS real no estaban implementados o se comportaban de forma distinta en el IOS simulado de Packet Tracer.
- `show ip interface` no reportó correctamente el nombre de la ACL aplicada a las SVI (mostraba `Inbound access list is not set` aun con la ACL activa); esto se confirmó como una limitación del simulador y no como una falla de configuración, mediante `show running-config | include access-group` y los contadores de `show access-lists`.
- La pérdida ocasional del primer paquete de un `ping` (visible en algunas capturas, por ejemplo hacia `192.188.98.18`) correspondió al tiempo de resolución ARP inicial entre los dispositivos y no a una falla de conectividad permanente, ya que los paquetes subsiguientes se completaron sin pérdida.
- Todos los puertos apagados intencionalmente durante las pruebas de tolerancia a fallos fueron restaurados con `no shutdown` al finalizar cada prueba, dejando la topología en su estado operativo original.
- El archivo de Packet Tracer del repositorio se llama `proyecto1_202010298.pkt` (en minúsculas), mientras que el nombre sugerido por el enunciado es `Proyecto1_202010298.pkt`; se recomienda verificar si el curso exige distinguir mayúsculas y minúsculas antes de la entrega.
