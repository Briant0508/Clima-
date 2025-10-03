import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración desde variables de entorno
BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
PORT = int(os.environ.get('PORT', 8443))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    user = update.message.from_user
    welcome_text = f"""
¡Hola {user.first_name}! 👋 🌤️

Soy tu bot del clima personal.

📍 **Cómo usarme:**
Simplemente escribe el nombre de cualquier ciudad y te diré el clima actual.

**Ejemplos:**
• Madrid
• Buenos Aires  
• Mexico City
• Tokyo

¡Prueba ahora! ✨
    """
    await update.message.reply_text(welcome_text)

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtiene y envía el clima de la ciudad solicitada"""
    city = update.message.text.strip()
    
    if not city:
        await update.message.reply_text("❌ Por favor, escribe el nombre de una ciudad.")
        return
    
    try:
        # Hacer petición a la API del clima
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            # Extraer información del clima
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            city_name = data['name']
            country = data['sys']['country']
            wind_speed = data['wind']['speed']
            
            # Emojis según el clima
            weather_emoji = get_weather_emoji(data['weather'][0]['main'])
            
            # Crear mensaje formateado
            message = (
                f"{weather_emoji} **Clima en {city_name}, {country}**\n\n"
                f"🌡️ **Temperatura:** {temp}°C\n"
                f"🤔 **Sensación térmica:** {feels_like}°C\n"
                f"💧 **Humedad:** {humidity}%\n"
                f"💨 **Viento:** {wind_speed} m/s\n"
                f"📝 **Descripción:** {description.title()}\n\n"
                f"¡Que tengas un buen día! ☀️"
            )
            
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(
                "❌ No pude encontrar esa ciudad.\n"
                "• Verifica que el nombre esté bien escrito\n"
                "• Intenta en inglés si es una ciudad pequeña\n"
                "• Ejemplo: 'New York' en lugar de 'Nueva York'"
            )
    
    except requests.exceptions.RequestException:
        await update.message.reply_text("🌐 Error de conexión. Intenta nuevamente en un momento.")
    except Exception as e:
        await update.message.reply_text("⚠️ Ocurrió un error inesperado. Intenta más tarde.")

def get_weather_emoji(weather_main):
    """Devuelve emoji según el tipo de clima"""
    emoji_map = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️'
    }
    return emoji_map.get(weather_main, '🌤️')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /help"""
    help_text = """
🆘 **Ayuda - Bot del Clima** 🌤️

**Comandos disponibles:**
/start - Iniciar el bot
/help - Mostrar esta ayuda

**Uso básico:**
Simplemente escribe el nombre de cualquier ciudad y recibirás información actualizada del clima.

**Ejemplos de ciudades:**
• Madrid
• London
• Tokyo
• New York
• Paris

**Soporte:**
Si encuentras problemas, verifica que el nombre de la ciudad esté correctamente escrito.
    """
    await update.message.reply_text(help_text)

def main():
    """Función principal para iniciar el bot"""
    if not BOT_TOKEN or not WEATHER_API_KEY:
        print("❌ Error: BOT_TOKEN o WEATHER_API_KEY no están configurados")
        return
    
    # Crear aplicación
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Añadir handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))
    
    # Iniciar el bot en Render (usando webhook)
    if 'RENDER' in os.environ:
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
        print(f"🤖 Bot iniciado en modo webhook: {webhook_url}")
    else:
        # Modo local (para pruebas)
        application.run_polling()
        print("🤖 Bot iniciado en modo polling (local)")
    
    print("✅ Bot del clima está funcionando...")

if __name__ == "__main__":
    main()


