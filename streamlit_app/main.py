import streamlit as st

from streamlit_app.api_client import health_check, APIClientError

st.set_page_config(
    page_title="Secure Image Steganography MVP",
    page_icon="🔐",
    layout="wide",
)

st.title("Secure Image Steganography MVP")
st.write(
    "This app provides a Streamlit frontend connected to a FastAPI backend "
    "for encrypted text embedding and extraction in images."
)

with st.sidebar:
    st.header("Backend Status")
    try:
        status = health_check()
        st.success(f'Status: {status["status"]}')
    except APIClientError as exc:
        st.error(str(exc))

st.markdown(
    """
### Available pages
- **Encoder**: embed encrypted plaintext into an image
- **Decoder**: recover and decrypt plaintext from a stego image

Use the sidebar to navigate between pages.
"""
)
