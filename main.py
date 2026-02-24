import discord
import requests
import asyncio
import os
import webserver

# 🔐 Token desde variables de entorno (Render / Railway / etc)
TOKEN = os.getenv("TOKEN")

# 📌 ID de tu canal (voz o texto)
CHANNEL_ID = 1185451174665650252  # Tu ID real

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def obtener_datos_nxpc():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=nexpace&vs_currencies=usd&include_24hr_change=true"
    
    response = requests.get(url, timeout=10)
    data = response.json()

    precio = data["nexpace"]["usd"]
    cambio = data["nexpace"]["usd_24h_change"]

    return precio, cambio

def obtener_icono(cambio):
    if cambio > 0:
        return "🟢"
    elif cambio < 0:
        return "🔴"
    else:
        return "⚪"

async def actualizar_canal():
    await client.wait_until_ready()

    # 🔥 CAMBIO CLAVE: fetch_channel en vez de get_channel (mejor para Render)
    try:
        canal = await client.fetch_channel(CHANNEL_ID)
        print(f"✅ Canal encontrado: {canal.name}")
    except Exception as e:
        print("❌ Error obteniendo el canal:", e)
        return

    while not client.is_closed():
        try:
            precio, cambio = obtener_datos_nxpc()
            icono = obtener_icono(cambio)

            # Formato limpio y bonito
            precio = round(precio, 4)
            cambio = round(cambio, 2)

            nuevo_nombre = f"{icono} NXPC ${precio} | {cambio:+}%"

            # Evita rate limit (solo cambia si es diferente)
            if canal.name != nuevo_nombre:
                await canal.edit(name=nuevo_nombre)
                print(f"📊 Actualizado: {nuevo_nombre}")
            else:
                print("⏳ Sin cambios en el precio")

        except Exception as e:
            print("⚠️ Error actualizando el canal:", e)

        # ⏱️ 120 segundos = seguro para Discord
        await asyncio.sleep(120)

@client.event
async def on_ready():
    print(f"🤖 Bot conectado como {client.user}")
    client.loop.create_task(actualizar_canal())

# 🚀 Verificación del token
if TOKEN is None:
    raise ValueError("❌ El TOKEN no está configurado en las variables de entorno en Render.")

# 🌐 Mantener el servicio activo en Render (Flask)
webserver.keep_alive()

# ▶️ Iniciar bot
client.run(TOKEN)
