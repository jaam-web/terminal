![f06037b5-234a-4901-aa76-e43806b39849](https://github.com/jaam-web/terminal/blob/39ed284d3217b92825d5dc1d9e81671a36035a36/Screenshot.jpg)
Terminal Remota Web (Tornado + Xterm.js)

Este programa es un emulador de terminal basado en web que permite ejecutar una sesión de bash directamente en el navegador. Utiliza WebSockets para una comunicación en tiempo real, permitiendo controlar tu servidor de forma remota a través de una interfaz moderna y fluida.

Características

Terminal Funcional: Proporciona una sesión de shell completa (/bin/bash) con soporte para colores y caracteres especiales.

Redimensionamiento Automático: La terminal se ajusta dinámicamente al tamaño de la ventana del navegador mediante el complemento FitAddon.

Auto-instalable: Descarga automáticamente las librerías necesarias de xterm.js desde un CDN si no existen localmente.

Interfaz Moderna: Estética oscura basada en la consola tradicional con soporte para enlaces web interactivos.

Multisistema: Muestra la URL de acceso local y de red para conectar otros dispositivos fácilmente.

Optimizado: Usa el framework Tornado para manejar múltiples conexiones de forma asíncrona y eficiente.

Requisitos

Python 3.x

Sistemas Unix: Requiere Linux o macOS (debido al uso de los módulos pty y fcntl nativos de Unix).

Tornado:

Instala con:

pip install tornado


Uso

Desde la terminal, navega a la carpeta donde está t1.py y ejecuta:

python terminal.py [OPCIONES]


-p / --puerto: (opcional) Puerto en el que escuchar (por defecto: 7654).

Ejemplos

Python

# Usando el programa de python
python terminal.py
python terminal.py --puerto 8080
python terminal.py --help


Opciones

-h, --help: Muestra el menú de ayuda y sale.

-p, --puerto: Especifica el puerto TCP para el servidor.

Acceso

Al iniciar el programa, aparecerá un banner en la terminal con la información de conexión, por ejemplo:

http://localhost:7654/ o http://192.168.1.100:7654/

Abre tu navegador preferido y accede para obtener el control de la consola.

Seguridad

No utilices este servidor en entornos públicos o inseguros.

Otorga acceso total a la terminal del sistema sin autenticación por defecto.

Se recomienda usar bajo una VPN o un túnel SSH seguro.

Créditos

Programa creado por: JAAM
