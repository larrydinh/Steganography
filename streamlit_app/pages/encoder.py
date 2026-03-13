import base64
import streamlit as st

from streamlit_app.api_client import encode_image, APIClientError


def render_metrics(metrics: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PSNR", f'{metrics["psnr"]:.2f}')
    c2.metric("SSIM", f'{metrics["ssim"]:.4f}')
    c3.metric("BPP", f'{metrics["bpp"]:.4f}')
    c4.metric("Embed Time", f'{metrics["embed_time_sec"]:.4f}s')


st.title("Encoder")
st.write("Upload an image, enter a secret message and password, then generate a stego image.")

uploaded_file = st.file_uploader(
    "Upload cover image",
    type=["png", "jpg", "jpeg", "bmp"],
    key="encoder_file",
)

secret_text = st.text_area(
    "Secret text",
    placeholder="Type the hidden message here...",
    height=180,
)

password = st.text_input("Password", type="password")
method = st.selectbox("Method", ["LSB"], index=0)

if uploaded_file is not None:
    st.subheader("Original Image")
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

if st.button("Encode", type="primary"):
    if uploaded_file is None:
        st.warning("Please upload an image.")
    elif not secret_text.strip():
        st.warning("Please enter a secret message.")
    elif not password:
        st.warning("Please enter a password.")
    else:
        try:
            file_bytes = uploaded_file.getvalue()

            with st.spinner("Encoding secret into image..."):
                result = encode_image(
                    file_bytes=file_bytes,
                    filename=uploaded_file.name,
                    secret_text=secret_text,
                    password=password,
                    method=method,
                )

            image_bytes = base64.b64decode(result["image_base64"])

            st.success("Encoding successful.")

            st.subheader("Stego Image")
            st.image(image_bytes, caption=result["filename"], use_container_width=True)

            st.subheader("Metrics")
            render_metrics(result["metrics"])

            st.download_button(
                "Download Stego Image",
                data=image_bytes,
                file_name=result["filename"],
                mime="image/png",
            )

        except APIClientError as exc:
            st.error(f"Encoding failed: {exc}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
