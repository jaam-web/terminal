🚀 Web Terminal Server

Un servidor de terminal ligero basado en web que permite el acceso remoto a una shell de Linux (Bash) a través de cualquier navegador moderno. Ideal para administración remota rápida y entornos de pruebas.

🛠️ Tecnologías utilizadas

Backend: Python 3 con Tornado Web Server.

Frontend: xterm.js para una emulación de terminal fiel y rápida.

Protocolo: WebSockets para comunicación bidireccional en tiempo real.

PTY: Emulación de pseudo-terminal nativa de Unix.

✨ Características

💻 Acceso Total: Shell Bash completa con soporte para 256 colores.

🔄 Conexión WebSocket: Latencia ultra baja.

📏 Auto-ajuste: Soporte para redimensionamiento dinámico de la terminal (FitAddon).

🔗 Links Clickables: Detección automática de URLs en la terminal.

📦 Zero Config: Descarga automáticamente sus dependencias de frontend al iniciar.

📋 Requisitos Previos

Sistema Operativo

Unix-like: Linux, macOS o WSL (Windows Subsystem for Linux).

Nota: No es compatible con Windows nativo debido al uso de pty y fcntl.

Dependencias de Python

Instala la librería necesaria mediante pip:

pip install tornado


🚀 Instalación y Uso

Clona este repositorio o descarga el script:

git clone [https://github.com/tu-usuario/nombre-repo.git](https://github.com/tu-usuario/nombre-repo.git)
cd nombre-repo


Ejecuta el servidor:

python3 terminal.py


Parámetros opcionales:
Puedes especificar un puerto diferente usando -p o --puerto:

python3 terminal.py --puerto 8080


Acceso:
Abre tu navegador en la dirección que se muestra en la consola (normalmente http://localhost:7654).

📂 Estructura del Proyecto

.
├── terminal.py         # Script principal (Servidor + Lógica)
├── README.md           # Documentación
└── recursos_web/       # Cache local de xterm.js (generado automáticamente)


🔒 Seguridad

[!CAUTION]
ADVERTENCIA DE SEGURIDAD: Este software expone una shell con privilegios de usuario a la red.

No lo expongas directamente a Internet.

Úsalo solo en redes locales de confianza.

Para uso remoto, se recomienda utilizar un túnel SSH, una VPN o un proxy inverso con autenticación fuerte.

📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

Generado con ❤️ para administradores de sistemas y desarrolladores.
