import streamlit as st

from streamlit_app.api_client import decode_image, APIClientError

st.title("Decoder")
st.write("Upload a stego image and enter the password to recover the hidden plaintext.")

uploaded_file = st.file_uploader(
    "Upload stego image",
    type=["png", "jpg", "jpeg", "bmp"],
    key="decoder_file",
)

password = st.text_input("Password", type="password")
method = st.selectbox("Method", ["LSB", "DCT", "DWT"], index=0)

if uploaded_file is not None:
    st.subheader("Uploaded Stego Image")
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

if st.button("Decode", type="primary"):
    if uploaded_file is None:
        st.warning("Please upload a stego image.")
    elif not password:
        st.warning("Please enter a password.")
    else:
        try:
            file_bytes = uploaded_file.getvalue()

            with st.spinner("Decoding secret from image..."):
                result = decode_image(
                    file_bytes=file_bytes,
                    filename=uploaded_file.name,
                    password=password,
                    method=method,
                )

            st.success("Decoding successful.")
            st.text_area(
                "Recovered plaintext",
                value=result["plaintext"],
                height=220,
            )
            if result.get("decoded_s3_key"):
                st.subheader("S3 Storage")
                st.write(f"Decoded S3 key: `{result['decoded_s3_key']}`")

            if result.get("decoded_s3_url"):
                st.markdown(f"[Open decoded image in S3]({result['decoded_s3_url']})")
                
        except APIClientError as exc:
            st.error(f"Decoding failed: {exc}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
