# Bot de Control Remoto — Telegram

Bot personal para controlar tu PC con Windows de forma remota desde Telegram.

---

## Requisitos

- Windows 10/11
- Python 3.10 o superior
- Una cuenta de Telegram

---

## Instalación

### 1. Crear el bot en Telegram

1. Abrí Telegram y buscá **@BotFather**
2. Mandá `/newbot` y seguí las instrucciones
3. Copiá el token que te da (ej: `123456:ABC-DEFxxx`)

### 2. Obtener tu user ID

1. Buscá **@userinfobot** en Telegram
2. Mandá cualquier mensaje
3. Copiá el número que dice `Id:`

### 3. Configurar variables de entorno

Abrí PowerShell y ejecutá (reemplazando los valores):

```powershell
[System.Environment]::SetEnvironmentVariable("TELEGRAM_TOKEN", "tu_token_aqui", "User")
[System.Environment]::SetEnvironmentVariable("TELEGRAM_USER_ID", "tu_user_id_aqui", "User")
[System.Environment]::SetEnvironmentVariable("TELEGRAM_PASSWORD", "tu_password_aqui", "User")
```

### 4. Instalar dependencias

```
pip install -r requirements.txt
```

### 5. Ejecutar el bot

```
python bot.py
```

### 6. (Opcional) Arranque automático con Windows

Click derecho en `instalar_autostart.bat` → **Ejecutar como administrador**.

Para desinstalarlo: `desinstalar_autostart.bat` como administrador.

---

## Autenticación

El bot tiene doble capa de seguridad:

1. **Telegram user ID** — solo responde a tu cuenta
2. **Contraseña de sesión** — la primera vez que usás el bot después de cada reinicio, te pide la contraseña configurada en `TELEGRAM_PASSWORD`

Una vez autenticado, no te la vuelve a pedir hasta que se reinicie el bot.

---

## Comandos

### Capturas

| Comando | Descripción |
|---|---|
| `/screenshot` | Captura de pantalla completa |
| `/winshot` | Seleccioná una ventana y capturá solo esa |
| `/click` | Muestra captura con grilla de coordenadas y espera que indiques dónde clickear |

### Ventanas

| Comando | Descripción |
|---|---|
| `/cerrar` | Seleccioná una ventana y cerrala |
| `/minimizar` | Seleccioná una ventana y minimizala |
| `/maximizar` | Seleccioná una ventana y maximizala |

### Multimedia

| Comando | Descripción |
|---|---|
| `/camara` | Seleccioná cámara y duración → graba y manda el video |
| `/microfono` | Seleccioná micrófono y duración → graba y manda el audio |
| `/dispositivos` | Lista cámaras y micrófonos disponibles con su índice |

### Control remoto

| Comando | Descripción |
|---|---|
| `/escribir <texto>` | Escribe el texto en la ventana activa (via portapapeles) |
| `/tecla <key>` | Presiona una tecla. Ej: `enter`, `esc`, `f5`, `ctrl+c`, `alt+tab` |
| `/mouse <x> <y>` | Mueve el cursor a esa posición |

### Portapapeles

| Comando | Descripción |
|---|---|
| `/clip` | Muestra el contenido actual del portapapeles |
| `/setclip <texto>` | Escribe texto en el portapapeles |

### Sistema

| Comando | Descripción |
|---|---|
| `/sysinfo` | CPU, RAM, disco y IP local |
| `/procesos` | Top 15 procesos por uso de CPU |
| `/matar` | Seleccioná un proceso y terminalo |
| `/red` | Velocidad de descarga y subida (mide 3 segundos) |
| `/abrir <ruta>` | Abre un archivo o programa. Ej: `/abrir notepad` |
| `/notificacion <texto>` | Muestra un cuadro de diálogo en la pantalla |
| `/bloquear` | Bloquea la pantalla de Windows |
| `/suspender` | Suspende la PC (requiere confirmación — no se puede despertar remotamente) |
| `/reiniciar` | Reinicia la PC (requiere confirmación) |
| `/apagar` | Apaga la PC (requiere confirmación) |

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `TELEGRAM_TOKEN` | Token del bot obtenido de @BotFather |
| `TELEGRAM_USER_ID` | Tu ID numérico de Telegram (obtenido de @userinfobot) |
| `TELEGRAM_PASSWORD` | Contraseña que el bot te pide al iniciar sesión |

---

## Seguridad

- **No subas este repositorio a GitHub** ni compartas `bot.py` — las variables están fuera del código pero el archivo en sí ya es sensible
- **Activá verificación en dos pasos en Telegram** — es el punto más crítico, si alguien entra a tu cuenta tiene control total de la PC
- **No compartas el token** — cualquiera que lo tenga puede interceptar los mensajes del bot
- Si creés que el token fue comprometido, generá uno nuevo desde @BotFather con `/revoke` y actualizá la variable de entorno

---

## Dependencias

```
python-telegram-bot==21.1
mss==9.0.1
Pillow==11.1.0
python-dotenv==1.0.0
opencv-python
sounddevice
scipy
psutil
pywin32
pyautogui
```
