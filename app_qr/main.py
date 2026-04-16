from fastapi import FastAPI, Response, Request
import qrcode
from io import BytesIO

app = FastAPI()

@app.get("/get-auth-qr/")
async def get_qr(request: Request): # В реальности токен берется из заголовков или сессии
    # Формируем данные для QR
    token = request.cookies.get("users_access_token")
    data = f"https://{request.base_url}/verify?token={token}"
    
    # Генерация QR-кода
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохраняем в буфер, чтобы не писать на диск
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")