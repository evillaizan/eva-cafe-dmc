"""Pantalla de CaféDMC. Consume la API (no toca la base directamente)."""
import os

import httpx
import streamlit as st

API = os.environ.get("CAFE_API", "http://127.0.0.1:8000")

st.set_page_config(page_title="CaféDMC", page_icon="☕")
st.title("☕ CaféDMC")

try:
    productos = httpx.get(f"{API}/productos", timeout=5).json()
except httpx.HTTPError:
    st.error(f"No se pudo conectar con la API en {API}. ¿Está corriendo uvicorn?")
    st.stop()

categorias = sorted({p["categoria"] for p in productos})
filtro = st.selectbox("Categoría", ["Todas", *categorias])
visibles = [p for p in productos if filtro == "Todas" or p["categoria"] == filtro]
st.dataframe(visibles, width="stretch", hide_index=True)

st.subheader("Nuevo pedido")
with st.form("pedido"):
    cliente_id = st.number_input("ID de cliente", min_value=1, value=1)
    nombres = {p["nombre"]: p["id"] for p in productos}
    elegido = st.selectbox("Producto", list(nombres))
    cantidad = st.number_input("Cantidad", min_value=1, max_value=20, value=1)
    if st.form_submit_button("Crear pedido"):
        r = httpx.post(f"{API}/pedidos", json={
            "cliente_id": int(cliente_id),
            "items": [{"producto_id": nombres[elegido], "cantidad": int(cantidad)}]})
        if r.status_code == 201:
            st.success(f"Pedido #{r.json()['id']} creado. Total: S/ {r.json()['total']:.2f}")
        else:
            st.error(f"Error {r.status_code}: {r.json().get('detail')}")