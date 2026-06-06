import logging
import io
import os
import ctypes
import tempfile
import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import mss
from PIL import Image
import win32gui
import win32con
import win32api
import win32clipboard
import psutil

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))
PASSWORD = os.getenv("TELEGRAM_PASSWORD")

DURACIONES = [10, 20, 30, 60]

def is_authorized(update: Update) -> bool:
    return update.effective_user.id == ALLOWED_USER_ID

def is_authenticated(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.user_data.get('authenticated', False)

async def require_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not is_authorized(update):
        await update.message.reply_text("❌ No autorizado.")
        return False
    if not is_authenticated(context):
        context.user_data['waiting_password'] = True
        context.user_data['pending_command'] = update.message.text
        await update.message.reply_text("🔐 Ingresá la contraseña:")
        return False
    return True

def get_visible_windows():
    windows = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and title not in ('Program Manager', 'Windows Input Experience'):
                windows.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return windows

def teclado_ventanas(action: str, windows: list) -> InlineKeyboardMarkup:
    botones = [
        [InlineKeyboardButton(title[:40], callback_data=f"win_{action}_{i}")]
        for i, (_, title) in enumerate(windows[:20])
    ]
    return InlineKeyboardMarkup(botones)

# ── /start y /help ────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    await update.message.reply_text(
        "🤖 Bot de control remoto\n\n"
        "📸 Capturas\n"
        "/screenshot - Captura de pantalla completa\n"
        "/winshot - Captura de ventana específica\n\n"
        "🪟 Ventanas\n"
        "/cerrar - Cerrar una ventana\n"
        "/minimizar - Minimizar una ventana\n"
        "/maximizar - Maximizar una ventana\n\n"
        "🎥 Multimedia\n"
        "/camara - Graba video\n"
        "/microfono - Graba audio\n"
        "/dispositivos - Lista cámaras y micrófonos\n\n"
        "⌨️ Control remoto\n"
        "/escribir <texto> - Escribe texto\n"
        "/tecla <key> - Presiona una tecla\n"
        "/mouse <x> <y> - Mueve el cursor\n"
        "/click <x> <y> - Click en posición\n\n"
        "📋 Portapapeles\n"
        "/clip - Ver portapapeles\n"
        "/setclip <texto> - Escribir en portapapeles\n\n"
        "💻 Sistema\n"
        "/sysinfo - Info del sistema\n"
        "/procesos - Procesos activos\n"
        "/red - Velocidad de red\n"
        "/abrir <ruta> - Abrir archivo o programa\n"
        "/notificacion <texto> - Mostrar notificación\n"
        "/bloquear - Bloquear pantalla\n"
        "/suspender - Suspender la PC\n"
        "/reiniciar - Reiniciar la PC\n"
        "/apagar - Apagar la PC\n"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

# ── /screenshot ───────────────────────────────────────────────────────────────

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        await update.message.reply_text("📸 Tomando captura...")
        with mss.mss() as sct:
            data = sct.grab(sct.monitors[1])
            img = Image.frombytes('RGB', data.size, data.rgb)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            await update.message.reply_photo(photo=buffer, caption="📸 Captura de pantalla")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /winshot ──────────────────────────────────────────────────────────────────

async def winshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        windows = get_visible_windows()
        if not windows:
            await update.message.reply_text("❌ No se encontraron ventanas.")
            return
        context.user_data['windows'] = windows
        await update.message.reply_text(
            "Seleccioná la ventana:",
            reply_markup=teclado_ventanas("screenshot", windows)
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /cerrar, /minimizar, /maximizar ──────────────────────────────────────────

async def cerrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    windows = get_visible_windows()
    context.user_data['windows'] = windows
    await update.message.reply_text(
        "Seleccioná la ventana a cerrar:",
        reply_markup=teclado_ventanas("cerrar", windows)
    )

async def minimizar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    windows = get_visible_windows()
    context.user_data['windows'] = windows
    await update.message.reply_text(
        "Seleccioná la ventana a minimizar:",
        reply_markup=teclado_ventanas("minimizar", windows)
    )

async def maximizar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    windows = get_visible_windows()
    context.user_data['windows'] = windows
    await update.message.reply_text(
        "Seleccioná la ventana a maximizar:",
        reply_markup=teclado_ventanas("maximizar", windows)
    )

# ── /clip y /setclip ──────────────────────────────────────────────────────────

async def clip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        win32clipboard.OpenClipboard()
        try:
            texto = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        except:
            texto = None
        win32clipboard.CloseClipboard()

        if texto:
            await update.message.reply_text(f"📋 Portapapeles:\n\n{texto[:3000]}")
        else:
            await update.message.reply_text("📋 El portapapeles está vacío o tiene contenido no textual.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def setclip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    if not context.args:
        await update.message.reply_text("Uso: /setclip <texto>")
        return
    try:
        texto = " ".join(context.args)
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, texto)
        win32clipboard.CloseClipboard()
        await update.message.reply_text(f"📋 Portapapeles actualizado.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /notificacion ─────────────────────────────────────────────────────────────

async def notificacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    if not context.args:
        await update.message.reply_text("Uso: /notificacion <texto>")
        return
    try:
        texto = " ".join(context.args)
        def _mostrar():
            win32api.MessageBox(0, texto, "📱 Mensaje desde Telegram", win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_SYSTEMMODAL)
        asyncio.get_event_loop().run_in_executor(None, _mostrar)
        await update.message.reply_text("✅ Notificación enviada.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /escribir, /tecla, /mouse, /click ────────────────────────────────────────

async def escribir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    if not context.args:
        await update.message.reply_text("Uso: /escribir <texto>")
        return
    try:
        import pyautogui
        texto = " ".join(context.args)
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, texto)
        win32clipboard.CloseClipboard()
        pyautogui.hotkey('ctrl', 'v')
        await update.message.reply_text(f"⌨️ Escrito: {texto}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def tecla(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    if not context.args:
        await update.message.reply_text("Uso: /tecla <key>\nEjemplos: enter, esc, f5, ctrl+c, alt+tab")
        return
    try:
        import pyautogui
        key = context.args[0].lower()
        if '+' in key:
            keys = key.split('+')
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)
        await update.message.reply_text(f"⌨️ Tecla presionada: {key}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def mouse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /mouse <x> <y>")
        return
    try:
        import pyautogui
        x, y = int(context.args[0]), int(context.args[1])
        pyautogui.moveTo(x, y, duration=0.3)
        await update.message.reply_text(f"🖱 Cursor movido a ({x}, {y})")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def agregar_grilla(img: Image.Image, paso: int = 100) -> Image.Image:
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    w, h = img.size
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    for x in range(0, w, paso):
        draw.line([(x, 0), (x, h)], fill=(255, 0, 0, 128), width=1)
        draw.text((x + 2, 2), str(x), fill=(255, 0, 0), font=font)
    for y in range(0, h, paso):
        draw.line([(0, y), (w, y)], fill=(255, 0, 0, 128), width=1)
        draw.text((2, y + 2), str(y), fill=(255, 0, 0), font=font)
    return img

async def click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        import pyautogui
        img = pyautogui.screenshot()
        img = agregar_grilla(img)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        await update.message.reply_photo(photo=buffer, caption="🖱 ¿En qué posición querés hacer click?\nRespondé con: x y")
        context.user_data['waiting_click'] = True
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return

    texto = update.message.text.strip()

    # Verificación de contraseña
    if context.user_data.get('waiting_password'):
        if texto == PASSWORD:
            context.user_data['authenticated'] = True
            context.user_data['waiting_password'] = False
            await update.message.reply_text("✅ Autenticado correctamente.")
            pending = context.user_data.pop('pending_command', None)
            if pending:
                await update.message.reply_text(f"Ahora podés ejecutar: {pending}")
        else:
            await update.message.reply_text("❌ Contraseña incorrecta.")
        return

    # Coordenadas de click
    if context.user_data.get('waiting_click'):
        if not is_authenticated(context):
            context.user_data['waiting_password'] = True
            await update.message.reply_text("🔐 Ingresá la contraseña:")
            return
        try:
            import pyautogui
            partes = texto.split()
            if len(partes) < 2:
                await update.message.reply_text("Mandá dos números: x y")
                return
            x, y = int(partes[0]), int(partes[1])
            context.user_data['waiting_click'] = False
            pyautogui.click(x, y)
            time.sleep(0.3)
            img = pyautogui.screenshot()
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            await update.message.reply_photo(photo=buffer, caption=f"✅ Click en ({x}, {y})")
        except (ValueError, IndexError):
            await update.message.reply_text("Formato incorrecto. Mandá dos números: x y")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

# ── /red ──────────────────────────────────────────────────────────────────────

async def red(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        await update.message.reply_text("📡 Midiendo velocidad de red (3s)...")

        def _medir():
            antes = psutil.net_io_counters()
            time.sleep(3)
            despues = psutil.net_io_counters()
            enviados = (despues.bytes_sent - antes.bytes_sent) / 3
            recibidos = (despues.bytes_recv - antes.bytes_recv) / 3
            return enviados, recibidos

        enviados, recibidos = await asyncio.to_thread(_medir)

        def fmt(bps):
            if bps > 1024 * 1024:
                return f"{bps / 1024 / 1024:.2f} MB/s"
            elif bps > 1024:
                return f"{bps / 1024:.1f} KB/s"
            return f"{bps:.0f} B/s"

        await update.message.reply_text(
            f"📡 Velocidad de red\n\n"
            f"⬇️ Descarga: {fmt(recibidos)}\n"
            f"⬆️ Subida: {fmt(enviados)}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /abrir ────────────────────────────────────────────────────────────────────

async def abrir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    if not context.args:
        await update.message.reply_text("Uso: /abrir <ruta o programa>\nEjemplo: /abrir notepad")
        return
    try:
        ruta = " ".join(context.args)
        os.startfile(ruta)
        await update.message.reply_text(f"✅ Abriendo: {ruta}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /dispositivos ─────────────────────────────────────────────────────────────

async def dispositivos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        import cv2
        import sounddevice as sd

        await update.message.reply_text("🔍 Buscando dispositivos...")

        camaras = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                camaras.append(f"  [{i}] Cámara {i}")
                cap.release()

        mics = []
        for i, d in enumerate(sd.query_devices()):
            if d['max_input_channels'] > 0:
                mics.append(f"  [{i}] {d['name']}")

        msg = "📷 Cámaras:\n"
        msg += "\n".join(camaras) if camaras else "  Ninguna"
        msg += "\n\n🎙 Micrófonos:\n"
        msg += "\n".join(mics) if mics else "  Ninguno"

        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /camara ───────────────────────────────────────────────────────────────────

async def camara(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        import cv2
        await update.message.reply_text("🔍 Buscando cámaras...")

        botones = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                botones.append(InlineKeyboardButton(f"📷 Cámara {i}", callback_data=f"cam_dev_{i}"))
                cap.release()

        if not botones:
            await update.message.reply_text("❌ No se encontraron cámaras.")
            return

        await update.message.reply_text(
            "Seleccioná la cámara:",
            reply_markup=InlineKeyboardMarkup([botones])
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /microfono ────────────────────────────────────────────────────────────────

async def microfono(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        import sounddevice as sd

        mics = [(i, d['name']) for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0]

        if not mics:
            await update.message.reply_text("❌ No se encontraron micrófonos.")
            return

        botones = [
            [InlineKeyboardButton(f"🎙 {nombre[:30]}", callback_data=f"mic_dev_{i}")]
            for i, nombre in mics
        ]

        await update.message.reply_text(
            "Seleccioná el micrófono:",
            reply_markup=InlineKeyboardMarkup(botones)
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /sysinfo ──────────────────────────────────────────────────────────────────

async def sysinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        import socket
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        ip = socket.gethostbyname(socket.gethostname())
        await update.message.reply_text(
            f"💻 Info del sistema\n\n"
            f"CPU: {cpu}%\n"
            f"RAM: {ram.percent}% ({ram.used // 1024**2}MB / {ram.total // 1024**2}MB)\n"
            f"Disco: {disk.percent}% usado ({disk.free // 1024**3}GB libres)\n"
            f"IP local: {ip}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /procesos ─────────────────────────────────────────────────────────────────

async def procesos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']),
                       key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:15]
        lines = ["⚙️ Top 15 procesos por CPU:\n"]
        for p in procs:
            lines.append(f"{p.info['cpu_percent']:5.1f}%  {p.info['name']} (PID {p.info['pid']})")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /matar ────────────────────────────────────────────────────────────────────

async def matar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']),
                       key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:15]

        botones = [
            [InlineKeyboardButton(
                f"{p.info['name']} ({p.info['pid']})",
                callback_data=f"matar_{p.info['pid']}"
            )]
            for p in procs
        ]

        await update.message.reply_text(
            "⚙️ Seleccioná el proceso a matar:",
            reply_markup=InlineKeyboardMarkup(botones)
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /bloquear ─────────────────────────────────────────────────────────────────

async def bloquear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    try:
        ctypes.windll.user32.LockWorkStation()
        await update.message.reply_text("🔒 Pantalla bloqueada.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /suspender, /reiniciar, /apagar ──────────────────────────────────────────

async def suspender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    await update.message.reply_text(
        "⚠️ ¿Seguro que querés suspender la PC?\n\n"
        "⚠️ Una vez suspendida no vas a poder despertarla desde acá.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sí, suspender", callback_data="confirm_suspender"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancelar"),
        ]])
    )

async def reiniciar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    await update.message.reply_text(
        "⚠️ ¿Seguro que querés reiniciar la PC?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sí, reiniciar", callback_data="confirm_reiniciar"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancelar"),
        ]])
    )

async def apagar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_auth(update, context):
        return
    await update.message.reply_text(
        "⚠️ ¿Seguro que querés apagar la PC?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sí, apagar", callback_data="confirm_apagar"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancelar"),
        ]])
    )

# ── helpers grabación ─────────────────────────────────────────────────────────

def teclado_duracion(prefix: str, device_idx: int) -> InlineKeyboardMarkup:
    botones = [
        InlineKeyboardButton(f"{s}s", callback_data=f"{prefix}_dur_{s}_{device_idx}")
        for s in DURACIONES
    ]
    return InlineKeyboardMarkup([botones])

async def grabar_video(query, cam_idx: int, segundos: int) -> None:
    tmp_path = None
    try:
        import cv2
        await query.edit_message_text(f"🎥 Grabando {segundos}s con cámara {cam_idx}...")

        tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        tmp_path = tmp.name
        tmp.close()

        def _grabar():
            cap = cv2.VideoCapture(cam_idx)
            if not cap.isOpened():
                raise RuntimeError("No se pudo abrir la cámara.")
            fps = 20
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(tmp_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
            for _ in range(fps * segundos):
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
            cap.release()
            out.release()

        await asyncio.to_thread(_grabar)

        with open(tmp_path, 'rb') as f:
            await query.message.reply_video(video=f, caption=f"🎥 Video {segundos}s · cámara {cam_idx}",
                                            read_timeout=120, write_timeout=120)
    except Exception as e:
        await query.message.reply_text(f"❌ Error: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

async def grabar_audio(query, mic_idx: int, segundos: int) -> None:
    tmp_path = None
    try:
        import sounddevice as sd
        import scipy.io.wavfile as wav

        mic_nombre = sd.query_devices(mic_idx)['name']
        await query.edit_message_text(f"🎙 Grabando {segundos}s con {mic_nombre[:30]}...")

        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp.name
        tmp.close()

        sample_rate = 44100

        def _grabar():
            recording = sd.rec(int(segundos * sample_rate), samplerate=sample_rate, channels=1, device=mic_idx)
            sd.wait()
            wav.write(tmp_path, sample_rate, recording)

        await asyncio.to_thread(_grabar)

        with open(tmp_path, 'rb') as f:
            await query.message.reply_voice(voice=f, caption=f"🎙 Audio {segundos}s · {mic_nombre[:30]}",
                                            read_timeout=120, write_timeout=120)
    except Exception as e:
        await query.message.reply_text(f"❌ Error: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

# ── handler de todos los botones ─────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.from_user.id != ALLOWED_USER_ID:
        await query.answer("❌ No autorizado.")
        return
    await query.answer()
    data = query.data

    # Winshot / ventanas
    if data.startswith("win_"):
        parts = data.split("_")
        action = parts[1]
        idx = int(parts[2])
        windows = context.user_data.get('windows', [])
        if idx >= len(windows):
            await query.edit_message_text("❌ Ventana no encontrada, repetí el comando.")
            return
        hwnd, title = windows[idx]

        if action == "screenshot":
            try:
                await query.edit_message_text(f"📸 Capturando: {title[:40]}...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                rect = win32gui.GetWindowRect(hwnd)
                x, y, x2, y2 = rect
                w, h = x2 - x, y2 - y
                if w <= 0 or h <= 0:
                    await query.message.reply_text("❌ La ventana no tiene área visible.")
                    return
                with mss.mss() as sct:
                    data_img = sct.grab({"top": y, "left": x, "width": w, "height": h})
                    img = Image.frombytes('RGB', data_img.size, data_img.rgb)
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    await query.message.reply_photo(photo=buffer, caption=f"📸 {title[:40]}")
            except Exception as e:
                await query.message.reply_text(f"❌ Error: {e}")

        elif action == "cerrar":
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                await query.edit_message_text(f"✅ Cerrando: {title[:40]}")
            except Exception as e:
                await query.message.reply_text(f"❌ Error: {e}")

        elif action == "minimizar":
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                await query.edit_message_text(f"✅ Minimizando: {title[:40]}")
            except Exception as e:
                await query.message.reply_text(f"❌ Error: {e}")

        elif action == "maximizar":
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                await query.edit_message_text(f"✅ Maximizando: {title[:40]}")
            except Exception as e:
                await query.message.reply_text(f"❌ Error: {e}")

    # Matar proceso
    elif data.startswith("matar_"):
        pid = int(data.split("_")[1])
        try:
            proc = psutil.Process(pid)
            nombre = proc.name()
            proc.kill()
            await query.edit_message_text(f"✅ Proceso {nombre} (PID {pid}) terminado.")
        except psutil.NoSuchProcess:
            await query.edit_message_text("❌ El proceso ya no existe.")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}")

    # Cámara: elegir dispositivo → mostrar duración
    elif data.startswith("cam_dev_"):
        cam_idx = int(data.split("_")[-1])
        await query.edit_message_text(
            f"📷 Cámara {cam_idx} seleccionada\n¿Cuánto tiempo?",
            reply_markup=teclado_duracion("cam", cam_idx)
        )

    # Cámara: elegir duración → grabar
    elif data.startswith("cam_dur_"):
        _, _, segundos, cam_idx = data.split("_")
        await grabar_video(query, int(cam_idx), int(segundos))

    # Micrófono: elegir dispositivo → mostrar duración
    elif data.startswith("mic_dev_"):
        mic_idx = int(data.split("_")[-1])
        import sounddevice as sd
        mic_nombre = sd.query_devices(mic_idx)['name']
        await query.edit_message_text(
            f"🎙 {mic_nombre[:30]} seleccionado\n¿Cuánto tiempo?",
            reply_markup=teclado_duracion("mic", mic_idx)
        )

    # Micrófono: elegir duración → grabar
    elif data.startswith("mic_dur_"):
        _, _, segundos, mic_idx = data.split("_")
        await grabar_audio(query, int(mic_idx), int(segundos))

    # Apagar / reiniciar / suspender
    elif data == "confirm_apagar":
        await query.edit_message_text("🔴 Apagando la PC...")
        os.system("shutdown /s /t 3")
    elif data == "confirm_reiniciar":
        await query.edit_message_text("🔁 Reiniciando la PC...")
        os.system("shutdown /r /t 3")
    elif data == "confirm_suspender":
        await query.edit_message_text("💤 Suspendiendo la PC...")
        ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
    elif data == "cancelar":
        await query.edit_message_text("✅ Cancelado.")

# ── error handler y main ──────────────────────────────────────────────────────

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} causó error {context.error}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("screenshot", screenshot))
    application.add_handler(CommandHandler("winshot", winshot))
    application.add_handler(CommandHandler("cerrar", cerrar))
    application.add_handler(CommandHandler("minimizar", minimizar))
    application.add_handler(CommandHandler("maximizar", maximizar))
    application.add_handler(CommandHandler("clip", clip))
    application.add_handler(CommandHandler("setclip", setclip))
    application.add_handler(CommandHandler("notificacion", notificacion))
    application.add_handler(CommandHandler("escribir", escribir))
    application.add_handler(CommandHandler("tecla", tecla))
    application.add_handler(CommandHandler("mouse", mouse))
    application.add_handler(CommandHandler("click", click))
    application.add_handler(CommandHandler("dispositivos", dispositivos))
    application.add_handler(CommandHandler("camara", camara))
    application.add_handler(CommandHandler("microfono", microfono))
    application.add_handler(CommandHandler("sysinfo", sysinfo))
    application.add_handler(CommandHandler("procesos", procesos))
    application.add_handler(CommandHandler("matar", matar))
    application.add_handler(CommandHandler("red", red))
    application.add_handler(CommandHandler("abrir", abrir))
    application.add_handler(CommandHandler("bloquear", bloquear))
    application.add_handler(CommandHandler("suspender", suspender))
    application.add_handler(CommandHandler("reiniciar", reiniciar))
    application.add_handler(CommandHandler("apagar", apagar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    logger.info("🤖 Bot iniciado.")
    print("\n✅ Bot ejecutándose correctamente.\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
