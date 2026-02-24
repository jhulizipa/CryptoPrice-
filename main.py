import discord
import requests
import asyncio
import os
import webserver

# 🔐 Token desde variables de entorno (Render)
TOKEN = os.getenv("TOKEN")

# 📌 IDs de los canales (CAMBIA ESTOS)
CHANNEL_BTC = 1475679952052686959  # ID canal BTC
CHANNEL_SOL = 1475680011674587201  # ID canal SOL
CHANNEL_NXPC = 1475680077290279022  # Tu canal actual NXPC

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def obtener_datos_crypto():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana,nexpace&vs_currencies=usd&include_24hr_change=true"
    
    response = requests.get(url, timeout=10)
    data = response.json()

    cryptos = {
        "BTC": {
            "precio": data["bitcoin"]["usd"],
            "cambio": data["bitcoin"]["usd_24h_change"]
        },
        "SOL": {
            "precio": data["solana"]["usd"],
            "cambio": data["solana"]["usd_24h_change"]
        },
        "NXPC": {
            "precio": data["nexpace"]["usd"],
            "cambio": data["nexpace"]["usd_24h_change"]
        }
    }

    return cryptos

def obtener_icono(cambio):
    if cambio > 0:
        return "🟢"
    elif cambio < 0:
        return "🔴"
    else:
        return "⚪"

async def actualizar_canal(channel_id, simbolo, precio, cambio):
    try:
        canal = await client.fetch_channel(channel_id)

        icono = obtener_icono(cambio)

        # Formato profesional
        if simbolo == "BTC":
            nombre = f"{icono} BTC ${precio:,.0f} | {cambio:+.2f}%"
        elif simbolo == "SOL":
            nombre = f"{icono} SOL ${precio:,.2f} | {cambio:+.2f}%"
        else:  # NXPC
            nombre = f"{icono} NXPC ${precio:.4f} | {cambio:+.2f}%"

        if canal.name != nombre:
            await canal.edit(name=nombre)
            print(f"📊 {simbolo} actualizado: {nombre}")
        else:
            print(f"⏳ {simbolo} sin cambios")

    except Exception as e:
        print(f"❌ Error actualizando {simbolo}:", e)

async def loop_precios():
    await client.wait_until_ready()
    print("🚀 Iniciando actualización de precios (BTC, SOL, NXPC)")

    while not client.is_closed():
        try:
            datos = obtener_datos_crypto()

            await actualizar_canal(
                CHANNEL_BTC,
                "BTC",
                round(datos["BTC"]["precio"], 2),
                round(datos["BTC"]["cambio"], 2)
            )

            await actualizar_canal(
                CHANNEL_SOL,
                "SOL",
                round(datos["SOL"]["precio"], 2),
                round(datos["SOL"]["cambio"], 2)
            )

            await actualizar_canal(
                CHANNEL_NXPC,
                "NXPC",
                round(datos["NXPC"]["precio"], 4),
                round(datos["NXPC"]["cambio"], 2)
            )

        except Exception as e:
            print("⚠️ Error general:", e)

        # ⏱️ 120 segundos = seguro para Discord y CoinGecko
        await asyncio.sleep(120)

@client.event
async def on_ready():
    print(f"🤖 Bot conectado como {client.user}")
    client.loop.create_task(loop_precios())

if TOKEN is None:
    raise ValueError("❌ El TOKEN no está configurado en Render.")

# 🌐 Mantener activo en Render
webserver.keep_alive()

client.run(TOKEN)

