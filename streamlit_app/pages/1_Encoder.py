import base64
import uuid
import streamlit as st
import streamlit.components.v1 as components

from streamlit_app.api_client import encode_image, APIClientError
from streamlit_app.ui_helpers import apply_global_styles, render_page_header, estimate_payload_capacity


def get_or_create_session_id() -> str:
    if "session_id" in st.session_state:
        return st.session_state["session_id"]

    current = st.query_params.get("sid")
    if current:
        st.session_state["session_id"] = current
        return current

    new_id = str(uuid.uuid4())
    st.session_state["session_id"] = new_id
    st.query_params["sid"] = new_id
    return new_id


def render_metrics(metrics: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PSNR", f'{metrics["psnr"]:.2f}')
    c2.metric("SSIM", f'{metrics["ssim"]:.4f}')
    c3.metric("BPP", f'{metrics["bpp"]:.4f}')
    c4.metric("Embed Time", f'{metrics["embed_time_sec"]:.4f}s')


def render_copy_button(text_to_copy: str, button_text: str = "Copy") -> None:
    escaped = text_to_copy.replace("\\", "\\\\").replace("'", "\\'")

    components.html(
        f"""
        <div style="display:flex;align-items:center;gap:8px;">
            <input
                id="copy-input-encoder"
                value="{escaped}"
                readonly
                style="position:absolute; left:-9999px;"
            />

            <button
                onclick="
                    const input = document.getElementById('copy-input-encoder');
                    input.style.display = 'block';
                    input.select();
                    input.setSelectionRange(0, 99999);
                    document.execCommand('copy');
                    input.style.display = 'none';

                    const msg = document.getElementById('copy-msg-encoder');
                    if (msg) {{
                        msg.innerText = 'Copied!';
                        setTimeout(() => msg.innerText = '', 1500);
                    }}
                "
                style="
                    background:#4CAF50;
                    color:white;
                    border:none;
                    padding:8px 14px;
                    border-radius:8px;
                    cursor:pointer;
                    font-size:14px;
                "
            >
                {button_text}
            </button>

            <span id="copy-msg-encoder" style="font-size:14px;color:#2e7d32;"></span>
        </div>
        """,
        height=45,
    )


def clear_encoder_state() -> None:
    st.session_state["encoder_uploaded_name"] = None
    st.session_state["encoder_uploaded_bytes"] = None
    st.session_state["encoder_result"] = None
    st.session_state["encoder_secret_text"] = ""
    st.session_state["encoder_password"] = ""
    st.session_state["encoder_method"] = "LSB"
    st.session_state["encoder_file"] = None


st.set_page_config(page_title="Encode Message", page_icon="🔒", layout="wide")
apply_global_styles()

session_id = get_or_create_session_id()

if "encoder_uploaded_name" not in st.session_state:
    st.session_state["encoder_uploaded_name"] = None
if "encoder_uploaded_bytes" not in st.session_state:
    st.session_state["encoder_uploaded_bytes"] = None
if "encoder_result" not in st.session_state:
    st.session_state["encoder_result"] = None
if "encoder_secret_text" not in st.session_state:
    st.session_state["encoder_secret_text"] = ""
if "encoder_password" not in st.session_state:
    st.session_state["encoder_password"] = ""
if "encoder_method" not in st.session_state:
    st.session_state["encoder_method"] = "LSB"

render_page_header(
    "Encode Message",
    "Upload a cover image, encrypt your secret text, and generate a stego image.",
    session_id,
)

st.markdown("""
<div class="pill-row">
    <span class="pill">Step 1: Upload</span>
    <span class="pill">Step 2: Encrypt</span>
    <span class="pill">Step 3: Embed</span>
    <span class="pill">Step 4: Download / Retrieve</span>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("Step 1 — Choose cover image")
    st.caption("Please choose an image that you want to cover your secret text (it could be any images). However, .png images are recommended for the cleanest LSB embedding result.")

    uploaded_file = st.file_uploader(
        "Upload cover image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="encoder_file",
    )

    if uploaded_file is not None:
        st.session_state["encoder_uploaded_name"] = uploaded_file.name
        st.session_state["encoder_uploaded_bytes"] = uploaded_file.getvalue()
        st.session_state["encoder_result"] = None

    if st.session_state["encoder_uploaded_name"]:
        st.success(f"Selected image: {st.session_state['encoder_uploaded_name']}")
        st.image(st.session_state["encoder_uploaded_bytes"], caption="Cover image preview", width=420)

with st.container(border=True):
    st.subheader("Step 2 — Encoding settings")

    secret_text = st.text_area(
        "Secret text",
        placeholder="Type the hidden message here...",
        height=180,
        key="encoder_secret_text",
    )

    estimate_payload_capacity(st.session_state.get("encoder_uploaded_bytes"), secret_text)

    password = st.text_input(
        "Password",
        type="password",
        key="encoder_password",
        help="The message is encrypted before it is embedded into the image.",
    )

    st.markdown("**Method guide**")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("<div class='method-card'><strong>LSB</strong><span> Recommended in your 1st try ! LSB (Least Significant Bit) is fast and simple. Best for PNG/BMP demo flows.</span></div>", unsafe_allow_html=True)
    with m2:
        st.markdown("<div class='method-card'><strong>DCT</strong><span> DCT (Discrete Cosine Transform) is a Frequency-domain method, recommended for JPEG images due to its robustness and surviving  image compression .</span></div>", unsafe_allow_html=True)
    with m3:
        st.markdown("<div class='method-card'><strong>DWT</strong><span>DWT (Discrete Wavelet Transform) is a Wavelet-domain method, recommended for better visual quality, lower visible distortion, and improved resistance against steganalysis detection.</span></div>", unsafe_allow_html=True)

    method = st.selectbox(
        "Method",
        ["LSB", "DCT", "DWT"],
        key="encoder_method",
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        encode_clicked = st.button("Encode", type="primary", use_container_width=True)

    with col2:
        if st.button("Clear", use_container_width=True):
            clear_encoder_state()
            st.rerun()

# if st.session_state["encoder_uploaded_bytes"] is not None:
#     with st.container(border=True):
#         st.subheader("Preview")

#         with st.expander("Show original image", expanded=False):
#             st.image(
#                 st.session_state["encoder_uploaded_bytes"],
#                 caption=st.session_state["encoder_uploaded_name"],
#                 width=520,
#             )

if encode_clicked:
    if st.session_state["encoder_uploaded_bytes"] is None:
        st.warning("Please upload an image.")
    elif not secret_text.strip():
        st.warning("Please enter a secret message.")
    elif not password:
        st.warning("Please enter a password.")
    else:
        try:
            progress = st.progress(0, text="Preparing image...")
            with st.spinner("Encoding secret into image..."):
                progress.progress(25, text="Encrypting message...")
                progress.progress(55, text="Embedding encrypted payload...")
                result = encode_image(
                    file_bytes=st.session_state["encoder_uploaded_bytes"],
                    filename=st.session_state["encoder_uploaded_name"],
                    secret_text=secret_text,
                    password=password,
                    method=method,
                    session_id=session_id,
                )

            progress.progress(100, text="Stego image generated.")
            st.session_state["encoder_result"] = result
            st.success("Encoding successful.")

        except APIClientError as exc:
            st.error(f"Encoding failed: {exc}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")

result = st.session_state["encoder_result"]
if result:
    image_bytes = base64.b64decode(result["image_base64"])

    with st.container(border=True):
        st.markdown("<div class='result-banner'><strong>✅ Message successfully hidden !.</strong><br>Your stego image is ready to download or retrieve later using the generated code.</div>", unsafe_allow_html=True)
        st.subheader("Stego image")
        st.image(image_bytes, caption=result["filename"], width=520)

        st.download_button(
            "Download Stego Image",
            data=image_bytes,
            file_name=result["filename"],
            mime="image/png",
            use_container_width=True,
        )

    with st.container(border=True):
        st.subheader("Quality metrics")
        st.caption("These values help compare how much the output image changed after embedding.")

        quality_metrics = result.get("metrics", {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("PSNR", f"{quality_metrics.get('psnr', 0):.2f}")
            st.caption("Image quality after embedding. Higher means fewer visible changes.")

        with col2:
            st.metric("SSIM", f"{quality_metrics.get('ssim', 0):.4f}")
            st.caption("Similarity between original and stego image. Closer to 1 means more identical.")

        with col3:
            st.metric("BPP", f"{quality_metrics.get('bpp', 0):.4f}")
            st.caption("Hidden data capacity per pixel. Higher means more data embedded.")

        with col4:
            st.metric("Embed Time", f"{quality_metrics.get('embed_time_sec', 0):.4f}s")
            st.caption("Time needed to hide the message inside the image.")


    if result.get("retrieval_code"):
        with st.container(border=True):
            st.subheader("Retrieval code")
            st.caption(
                "Please copy and save this code before leaving the page. "
                "You can use it later in the Decoder page to retrieve your stego image !"
            )
            st.code(result["retrieval_code"])
            render_copy_button(result["retrieval_code"], "Copy")
            st.caption(f"Code expires in {result['retrieval_expires_in_hours']} hours.")

            st.divider()
            st.markdown("**Are you ready to decode your hidden message?**")
            st.caption("Please click the button below to open the Decoder page, then paste your retrieval code.")

            st.session_state["retrieve_code_input"] = result["retrieval_code"]

            st.page_link(
                "pages/2_Decoder.py",
                label="Go to Decoder",
                icon="🔓",
                use_container_width=True,
            )

    # if result.get("encoded_s3_url"):
    #     with st.container(border=True):
    #         st.subheader("Storage")
    #         st.markdown(f"[Open encoded image in S3]({result['encoded_s3_url']})")