"""Start ngrok tunnels for Streamlit (8501) and FastAPI (8000) and print public URLs.
Requires `pyngrok` package. Run with the project's virtual env.
"""
from pyngrok import ngrok
import os
import time


def start():
    # Optionally set auth token from NGROK_AUTHTOKEN env var
    token = os.getenv("NGROK_AUTHTOKEN")
    if token:
        try:
            ngrok.set_auth_token(token)
            print("ngrok auth token set from NGROK_AUTHTOKEN")
        except Exception as e:
            print("Failed to set ngrok auth token:", e)

    # create tunnels
    http_tunnel = ngrok.connect(8501, "http")
    api_tunnel = ngrok.connect(8000, "http")
    print("Streamlit public URL:", http_tunnel.public_url)
    print("FastAPI public URL:", api_tunnel.public_url)
    print("Press Ctrl+C to exit and close tunnels.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down tunnels")
        try:
            ngrok.disconnect(http_tunnel.public_url)
        except Exception:
            pass
        try:
            ngrok.disconnect(api_tunnel.public_url)
        except Exception:
            pass


if __name__ == "__main__":
    start()
