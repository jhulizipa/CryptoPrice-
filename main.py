import discord
import requests
import asyncio
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 123456789012345678  # ID de tu canal

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def obtener_datos_nxpc():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=nexpace&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url).json()
    
    precio = response["nexpace"]["usd"]
    cambio = response["nexpace"]["usd_24h_change"]
    
    return precio, cambio

def obtener_icono(cambio):
    if cambio > 0:
        return "🟢"  # subiendo
    elif cambio < 0:
        return "🔴"  # bajando
    else:
        return "⚪"  # sin cambio

async def actualizar_canal():
    await client.wait_until_ready()
    canal = client.get_channel(CHANNEL_ID)

    while True:
        try:
            precio, cambio = obtener_datos_nxpc()
            icono = obtener_icono(cambio)

            # Redondear valores para que se vea limpio
            precio = round(precio, 4)
            cambio = round(cambio, 2)

            nuevo_nombre = f"{icono} NXPC: ${precio} ({cambio}%)"
            await canal.edit(name=nuevo_nombre)

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(120)  # cada 2 minutos (recomendado por límites de Discord)

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    client.loop.create_task(actualizar_canal())


client.run(TOKEN)
