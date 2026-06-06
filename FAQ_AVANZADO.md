# 📋 Preguntas Frecuentes y Configuración Avanzada

## ❓ Preguntas Frecuentes

### ¿Cómo obtengo mi token de Telegram?

1. Abre Telegram
2. Busca `@BotFather` (es un bot oficial de Telegram)
3. Envía el comando `/newbot`
4. Sigue las instrucciones. Debes:
   - Darle un nombre a tu bot (ej: "Mi Bot de Capturas")
   - Elegir un username (debe terminar en `_bot`, ej: `mi_bot_capturas_bot`)
5. BotFather te enviará un token, cópialo

### ¿Es seguro? ¿Alguien más puede ver mis capturas?

**Depende de cómo lo configures:**
- El bot solo envía capturas a tu cuenta de Telegram (el usuario que lo creó)
- Nadie más tiene acceso al token, así que nadie más puede controlar el bot
- ⚠️ **IMPORTANTE**: No compartas tu token con nadie
- Las capturas se guardan en los servidores de Telegram (están encriptadas)

### ¿Puedo ejecutar el bot en segundo plano?

**Sí, hay varias formas:**

#### Opción 1: Usar el Programador de Tareas de Windows
1. Abre "Programador de Tareas"
2. Crea una nueva tarea
3. Configúrala para ejecutar `ejecutar.bat`
4. El bot se ejecutará automáticamente cuando inicies Windows

#### Opción 2: Servicio de Windows
Usa NSSM (Non-Sucking Service Manager) para convertir el bot en servicio

#### Opción 3: Usar Screen o similar
En PowerShell:
```powershell
Start-Job -FilePath ".\ejecutar.bat"
```

### El bot no responde, ¿qué hago?

1. **Verifica que el script sigue corriendo:**
   - La ventana de `ejecutar.bat` debe estar abierta
   - Si se cierra sola, hay un error

2. **Verifica el token:**
   - Abre `bot.py` o `.env`
   - Asegúrate de que el token está correcto (no tiene espacios, es completo)

3. **Busca el bot correctamente:**
   - En Telegram, búscalo por el **username** que creaste (@mi_bot_capturas_bot)
   - NO por el nombre que le diste

4. **Verifica la conexión:**
   - El PC debe tener conexión a internet para que el bot funcione

### ¿Cómo capturo solo una parte de la pantalla?

Edita el archivo `bot.py` o `bot_env.py` en la función `screenshot()`:

**Para capturar solo una región:**
```python
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("📸 Tomando captura de pantalla...")
        
        with mss.mss() as sct:
            # Capturar región específica (x, y, ancho, alto)
            # Ejemplo: región de 100x100 a 500x500
            monitor = {"top": 100, "left": 100, "width": 400, "height": 400}
            screenshot_data = sct.grab(monitor)
            
            img = Image.frombytes('RGB', screenshot_data.size, screenshot_data.rgb)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            await update.message.reply_photo(photo=buffer)
```

### ¿Puedo guardar las capturas en una carpeta?

**Sí, aquí está el código modificado:**

```python
import os
from datetime import datetime

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("📸 Tomando captura...")
        
        # Crear carpeta si no existe
        if not os.path.exists("capturas"):
            os.makedirs("capturas")
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot_data = sct.grab(monitor)
            
            img = Image.frombytes('RGB', screenshot_data.size, screenshot_data.rgb)
            
            # Guardar en archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capturas/screenshot_{timestamp}.png"
            img.save(filename)
            
            # También enviar por Telegram
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            await update.message.reply_photo(
                photo=buffer,
                caption=f"📸 Guardada en: {filename}"
            )
```

### ¿Puedo hacer capturas automáticas cada cierto tiempo?

**Sí, usando trabajos programados:**

```python
from telegram.ext import Application, CommandHandler, ContextTypes, Application
from datetime import datetime
import asyncio

# En la función main(), agrega esto después de crear la aplicación:
async def periodic_screenshot():
    """Envía una captura cada 30 minutos"""
    while True:
        await asyncio.sleep(1800)  # 30 minutos = 1800 segundos
        
        # Aquí va el código para tomar captura y guardarla
        # o enviarla a tu chat
```

### ¿Cómo envío las capturas a un grupo de Telegram?

Necesitas agregar el bot al grupo y configurar el chat_id. Esto es más avanzado, consulta la documentación de python-telegram-bot.

---

## 🔧 Configuración Avanzada

### Cambiar monitor a capturar

Si tienes varios monitores, puedes cambiar cuál se captura:

```python
# En la función screenshot():
with mss.mss() as sct:
    # sct.monitors[0] = todas las pantallas
    # sct.monitors[1] = primer monitor
    # sct.monitors[2] = segundo monitor, etc.
    
    monitor = sct.monitors[2]  # Cambiar a tu monitor
    screenshot_data = sct.grab(monitor)
```

### Cambiar formato de imagen

En lugar de PNG, puedes usar JPG (más pequeño):

```python
# Cambiar esta línea:
img.save(buffer, format='PNG')

# A esto:
img.save(buffer, format='JPEG', quality=85)
```

### Agregar marca de agua

```python
from PIL import ImageDraw, ImageFont
from datetime import datetime

# Después de capturar
draw = ImageDraw.Draw(img)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
draw.text((10, 10), f"Captura: {timestamp}", fill=(255, 255, 255))
```

### Registrar todos los comandos

Las acciones ya se registran en el log. Puedes verlas en la consola donde ejecutas el bot.

---

## 🚨 Solución de Problemas

### Error: "No module named 'telegram'"

```bash
pip install python-telegram-bot
```

### Error: "No module named 'mss'"

```bash
pip install mss
```

### Error: "No module named 'PIL'"

```bash
pip install Pillow
```

### Error: "Invalid token"

- El token no es válido
- Obtén uno nuevo desde @BotFather
- Asegúrate de copiarlo completo (sin espacios)

### La captura se ve pixelada

Intenta con otro formato o aumenta la calidad:

```python
# En lugar de PNG
img.save(buffer, format='JPEG', quality=95)
```

---

## 📚 Links útiles

- [python-telegram-bot Docs](https://python-telegram-bot.readthedocs.io/)
- [MSS (Python Screen Capture)](https://python-mss.readthedocs.io/)
- [Pillow (PIL) Documentation](https://pillow.readthedocs.io/)

---

¿Preguntas? Consulta la documentación oficial o intenta buscar en StackOverflow.
