"""
Exemplo de validação de Webhook da Nuvemshop usando FastAPI.

Este exemplo demonstra como verificar a assinatura HMAC para garantir
que a requisição realmente veio da Nuvemshop e não foi alterada.
"""

from fastapi import FastAPI, Request, Header, HTTPException
from nuvemshop_sdk.utils.webhook import verify_webhook_signature
import os

app = FastAPI()

# O CLIENT_SECRET do seu app (disponível no painel de parceiros)
CLIENT_SECRET = os.environ.get("NUVEMSHOP_CLIENT_SECRET", "seu_secret")

@app.post("/webhook/nuvemshop")
async def handle_nuvemshop_webhook(
    request: Request,
    x_linkedstore_hmac_sha256: str = Header(None),
    x_linkedstore_timestamp: str = Header(None)
):
    # 1. Obter o corpo bruto da requisição
    body = await request.body()

    # 2. Verificar a assinatura
    is_valid = verify_webhook_signature(
        body=body,
        signature=x_linkedstore_hmac_sha256,
        secret=CLIENT_SECRET,
        timestamp=float(x_linkedstore_timestamp) if x_linkedstore_timestamp else 0,
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail="Assinatura inválida")

    # 3. Processar o payload JSON
    payload = await request.json()
    event = payload.get("event")
    
    print(f"Recebido evento: {event}")
    
    # Lógica de processamento...
    # Ex: if event == "order/created": ...

    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
