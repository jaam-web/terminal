#!/usr/bin/python3
import os
import pty
import tornado.ioloop
import tornado.web
import tornado.websocket
import termios
import fcntl
import struct
import signal
import argparse
import urllib.request
import socket
# Configuración de rutas para recursos locales
DIRECTORIO_RECURSOS = "recursos_web"
os.makedirs(DIRECTORIO_RECURSOS, exist_ok=True)

def obtener_direccion_ip():
    """Obtiene la dirección IP del equipo"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
# Rutas locales de los archivos
ARCHIVOS = {
    'xterm.js': {
        'url': "https://unpkg.com/xterm@5.1.0/lib/xterm.js",
        'local': os.path.join(DIRECTORIO_RECURSOS, "xterm.js")
    },
    'xterm.css': {
        'url': "https://unpkg.com/xterm@5.1.0/css/xterm.css",
        'local': os.path.join(DIRECTORIO_RECURSOS, "xterm.css")
    },
    'xterm-addon-fit.js': {
        'url': "https://unpkg.com/xterm-addon-fit@0.7.0/lib/xterm-addon-fit.js",
        'local': os.path.join(DIRECTORIO_RECURSOS, "xterm-addon-fit.js")
    },
    'xterm-addon-web-links.js': {
        'url': "https://unpkg.com/xterm-addon-web-links@0.8.0/lib/xterm-addon-web-links.js",
        'local': os.path.join(DIRECTORIO_RECURSOS, "xterm-addon-web-links.js")
    }
}

def descargar_recursos():
    """Descarga los recursos web necesarios si no existen localmente"""
    for nombre, datos in ARCHIVOS.items():
        if not os.path.exists(datos['local']):
            print(f"Descargando {nombre}...")
            urllib.request.urlretrieve(datos['url'], datos['local'])
            print(f"{nombre} descargado correctamente")

class TerminalWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.pty = None
        self.fd = None
        self.child_pid = None

    def open(self):
        """Abre una nueva conexión WebSocket y crea una terminal PTY"""
        entorno = os.environ.copy()
        entorno.update({
            'TERM': 'xterm-256color',
            'COLORTERM': 'truecolor',
            'SHELL': '/bin/bash',
            'LANG': 'en_US.UTF-8'
        })

        filas, columnas = 40, 120

        pid, fd = pty.fork()
        if pid == 0:
            os.execvpe('/bin/bash', ['bash', '--login'], entorno)
        else:
            self.fd = fd
            self.child_pid = pid
            self.establecer_tamano_pty(filas, columnas)

            flags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            tornado.ioloop.IOLoop.current().add_handler(
                self.fd,
                self.manejar_lectura,
                tornado.ioloop.IOLoop.READ
            )

    def establecer_tamano_pty(self, filas, columnas):
        """Establece el tamaño de la terminal PTY"""
        tamano_ventana = struct.pack("HHHH", filas, columnas, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, tamano_ventana)

    def manejar_lectura(self, fd, eventos):
        """Maneja datos recibidos desde la PTY"""
        try:
            datos = os.read(fd, 1024 * 20)
            if datos:
                self.write_message(datos)
            else:
                self.close()
        except (OSError, tornado.websocket.WebSocketClosedError):
            self.close()

    def on_message(self, mensaje):
        """Maneja mensajes recibidos desde el cliente web"""
        if isinstance(mensaje, str):
            os.write(self.fd, mensaje.encode('utf-8'))
        else:
            if mensaje.startswith(b'\x01'):
                try:
                    partes = mensaje[1:].split(b',')
                    filas = int(partes[0])
                    columnas = int(partes[1])
                    self.establecer_tamano_pty(filas, columnas)
                except:
                    pass
            else:
                os.write(self.fd, mensaje)

    def on_close(self):
        """Limpia los recursos al cerrar la conexión"""
        if self.fd:
            tornado.ioloop.IOLoop.current().remove_handler(self.fd)
            os.close(self.fd)
        if self.child_pid:
            try:
                os.kill(self.child_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

class ManejadorPrincipal(tornado.web.RequestHandler):
    def get(self):
        """Maneja las solicitudes GET a la raíz del servidor"""
        self.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Terminal Remota</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    background: #000;
                    color: #f0f0f0;
                    font-family: 'Courier New', monospace;
                    overflow: hidden;
                }}
                #contenedor-terminal {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    padding: 0;
                    margin: 0;
                    box-sizing: border-box;
                }}
                #terminal {{
                    width: 100%;
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
                .xterm {{
                    padding: 0 !important;
                    margin: 0 !important;
                }}
                .xterm-viewport {{
                    background-color: #000 !important;
                }}
                .xterm-screen {{
                    padding: 0 !important;
                    margin: 0 !important;
                }}
            </style>
            <link rel="stylesheet" href="/xterm.css">
            <script src="/xterm.js"></script>
            <script src="/xterm-addon-fit.js"></script>
            <script src="/xterm-addon-web-links.js"></script>
        </head>
        <body>
            <div id="contenedor-terminal">
                <div id="terminal"></div>
            </div>

            <script>
                const contenedorTerminal = document.getElementById('contenedor-terminal');
                const elementoTerminal = document.getElementById('terminal');

                const terminal = new Terminal({{
                    cursorBlink: true,
                    macOptionIsMeta: true,
                    scrollback: 1000,
                    allowTransparency: true,
                    theme: {{
                        background: '#000000',
                        foreground: '#f0f0f0',
                        cursor: '#f0f0f0',
                        selection: 'rgba(255, 255, 255, 0.3)'
                    }}
                }});

                const complementoAjuste = new FitAddon.FitAddon();
                terminal.loadAddon(complementoAjuste);
                terminal.loadAddon(new WebLinksAddon.WebLinksAddon());

                terminal.open(elementoTerminal);
                complementoAjuste.fit();

                const protocolo = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const ws = new WebSocket(protocolo + '//' + window.location.host + '/websocket');

                ws.onopen = () => {{
                    console.log('Conexión WebSocket establecida');
                    enviarTamanoTerminal();
                }};

                ws.onmessage = (evento) => {{
                    terminal.write(evento.data);
                }};

                ws.onclose = () => {{
                    console.log('Conexión WebSocket cerrada');
                    terminal.write('\\r\\nConexión cerrada.\\r\\n');
                }};

                ws.onerror = (error) => {{
                    console.error('Error en WebSocket:', error);
                    terminal.write('\\r\\nError en WebSocket. Revise los logs del servidor.\\r\\n');
                }};

                terminal.onData(datos => {{
                    ws.send(datos);
                }});

                function enviarTamanoTerminal() {{
                    if (ws.readyState === WebSocket.OPEN) {{
                        const filas = terminal.rows;
                        const columnas = terminal.cols;
                        ws.send(new Uint8Array([0x01, ...new TextEncoder().encode(`${{filas}},${{columnas}}`)]));
                    }}
                }}

                window.addEventListener('resize', () => {{
                    complementoAjuste.fit();
                    enviarTamanoTerminal();
                }});

                new ResizeObserver(() => {{
                    complementoAjuste.fit();
                    enviarTamanoTerminal();
                }}).observe(contenedorTerminal);

                terminal.focus();
            </script>
        </body>
        </html>
        """)

def obtener_ruta_archivo(nombre):
    """Obtiene la ruta local del archivo solicitado"""
    return ARCHIVOS.get(nombre, {}).get('local', '')

class Aplicacion(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", ManejadorPrincipal),
            (r"/websocket", TerminalWebSocket),
            (r"/(xterm\.js|xterm\.css|xterm-addon-fit\.js|xterm-addon-web-links\.js)", 
             tornado.web.StaticFileHandler, {"path": DIRECTORIO_RECURSOS}),
        ]
        super().__init__(handlers)

def analizar_argumentos():
    """Configura y analiza los argumentos de línea de comandos"""
    analizador = argparse.ArgumentParser(
        description='Servidor de terminal web con soporte WebSocket'
    )
    analizador.add_argument(
        '-p', '--puerto',
        type=int,
        default=7654,
        help='Puerto en el que escuchará el servidor'
    )
    return analizador.parse_args()

def main():
    """Función principal del programa"""
    descargar_recursos()
    args = analizar_argumentos()
    
    try:
        aplicacion = Aplicacion()
        aplicacion.listen(args.puerto)
        direccion_ip = obtener_direccion_ip()
        
        # Banner personalizado TERMINAL
        print("\n" + "="*70)
        print("""\
████████╗███████╗██████╗░███╗░░░███╗██╗███╗░░██╗░█████╗░██╗░░░░░
╚══██╔══╝██╔════╝██╔══██╗████╗░████║██║████╗░██║██╔══██╗██║░░░░░
░░░██║░░░█████╗░░██████╔╝██╔████╔██║██║██╔██╗██║███████║██║░░░░░
░░░██║░░░██╔══╝░░██╔══██╗██║╚██╔╝██║██║██║╚████║██╔══██║██║░░░░░
░░░██║░░░███████╗██║░░██║██║░╚═╝░██║██║██║░╚███║██║░░██║███████╗
░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚═╝░░╚═╝╚══════╝""")
        print("="*70)
        
        # Información del servidor
        print("\n" + "═"*70)
        print("                    🌐 SERVIDOR ACTIVADO")
        print("═"*70)
        
        print(f"\n    🔗 URL Local:     http://localhost:{args.puerto}")
        print(f"    🌍 URL Red:       http://{direccion_ip}:{args.puerto}")
        print(f"    🔌 Puerto:        {args.puerto}")
        
        # Estado y controles
        print("\n    📊 Estado:        Servidor Tornado iniciado correctamente")
        print("    ⚡ Activo:        Listo para recibir conexiones")
        
        print("\n" + "─"*70)
        print("    ⚠️  Control:       Presione Ctrl+C para detener el servidor")
        print("─"*70 + "\n")
        
        # Iniciar el servidor
        tornado.ioloop.IOLoop.current().start()
        
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("                    ⏹️  SERVIDOR DETENIDO")
        print("="*70)
        print("\n    ✅ El servidor se ha detenido correctamente")
        print("    👋 ¡Hasta pronto!\n")
        
    except Exception as e:
        print("\n\n" + "!"*70)
        print("                    ❌ ERROR CRÍTICO")
        print("!"*70)
        print(f"\n    🚫 Error: {str(e)}")
        print(f"    📍 Causa: No se pudo iniciar el servidor")
        print(f"    🔧 Solución: Verifique el puerto {args.puerto} y la configuración")
        print("\n" + "!"*70 + "\n")

if __name__ == "__main__":
    main()