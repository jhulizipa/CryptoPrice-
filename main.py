import discord
import requests
import asyncio
import os
import webserver

# 🔐 Token desde variables de entorno (Render / Railway / etc)
TOKEN = os.getenv("TOKEN")

# 📌 ID de tu canal (voz o texto)
CHANNEL_ID = 1185451174665650252  # <-- CAMBIA ESTO por tu ID real

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
    canal = client.get_channel(CHANNEL_ID)

    if canal is None:
        print("❌ No se encontró el canal. Revisa el CHANNEL_ID.")
        return

    while not client.is_closed():
        try:
            precio, cambio = obtener_datos_nxpc()
            icono = obtener_icono(cambio)

            # Formato limpio
            precio = round(precio, 4)
            cambio = round(cambio, 2)

            nuevo_nombre = f"{icono} NXPC ${precio} | {cambio:+}%"

            # Solo cambia el nombre si es diferente (evita rate limit de Discord)
            if canal.name != nuevo_nombre:
                await canal.edit(name=nuevo_nombre)
                print(f"Actualizado: {nuevo_nombre}")
            else:
                print("Sin cambios en el precio")

        except Exception as e:
            print("⚠️ Error actualizando el canal:", e)

        # ⏱️ 120 segundos = seguro para evitar límites de Discord
        await asyncio.sleep(120)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")
    client.loop.create_task(actualizar_canal())

# 🚀 Iniciar bot
if TOKEN is None:
    raise ValueError("El TOKEN no está configurado en las variables de entorno.")

webserver.keep_alive()  # Iniciar el servidor web para mantener el bot activo

client.run(TOKEN)
