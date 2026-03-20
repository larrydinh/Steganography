import uuid
import requests
import streamlit as st
import streamlit.components.v1 as components

from streamlit_app.api_client import decode_image, retrieve_file, APIClientError


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


def render_copy_button(text_to_copy: str, button_text: str = "Copy") -> None:
    escaped = text_to_copy.replace("\\", "\\\\").replace("'", "\\'")
    components.html(
        f"""
        <div style="display:flex;align-items:center;gap:8px;">
            <input
                id="copy-input-decoder"
                value="{escaped}"
                readonly
                style="position:absolute; left:-9999px;"
            />

            <button
                onclick="
                    const input = document.getElementById('copy-input-decoder');
                    input.style.display = 'block';
                    input.select();
                    input.setSelectionRange(0, 99999);
                    document.execCommand('copy');
                    input.style.display = 'none';

                    const msg = document.getElementById('copy-msg-decoder');
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

            <span id="copy-msg-decoder" style="font-size:14px;color:#2e7d32;"></span>
        </div>
        """,
        height=45,
    )


def clear_decoder_state() -> None:
    st.session_state["decoder_uploaded_name"] = None
    st.session_state["decoder_uploaded_bytes"] = None
    st.session_state["decoder_result"] = None
    st.session_state["retrieve_result"] = None
    st.session_state["decoder_password"] = ""
    st.session_state["decoder_method"] = "LSB"
    st.session_state["retrieve_code_input"] = ""
    st.session_state["decoder_file"] = None
    st.session_state["decode_trigger"] = False


def get_selected_source_label(uploaded_file) -> str | None:
    if st.session_state.get("retrieve_result") and st.session_state.get("decoder_uploaded_name"):
        return f"Retrieved image: {st.session_state['decoder_uploaded_name']}"
    if uploaded_file is not None and st.session_state.get("decoder_uploaded_name"):
        return f"Uploaded image: {st.session_state['decoder_uploaded_name']}"
    return None


session_id = get_or_create_session_id()

# Persistent state
if "decoder_uploaded_name" not in st.session_state:
    st.session_state["decoder_uploaded_name"] = None
if "decoder_uploaded_bytes" not in st.session_state:
    st.session_state["decoder_uploaded_bytes"] = None
if "decoder_result" not in st.session_state:
    st.session_state["decoder_result"] = None
if "retrieve_result" not in st.session_state:
    st.session_state["retrieve_result"] = None
if "decoder_password" not in st.session_state:
    st.session_state["decoder_password"] = ""
if "decoder_method" not in st.session_state:
    st.session_state["decoder_method"] = "LSB"
if "retrieve_code_input" not in st.session_state:
    st.session_state["retrieve_code_input"] = ""
if "decode_trigger" not in st.session_state:
    st.session_state["decode_trigger"] = False

st.title("Decoder")
st.caption("Upload or retrieve a stego image, then decode the hidden plaintext.")
st.caption(f"Browser session: {session_id}")

# -------------------------------
# Source selection
# -------------------------------
with st.container(border=True):
    st.subheader("Choose image source")

    uploaded_file = st.file_uploader(
        "Upload stego image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="decoder_file",
    )

    if uploaded_file is not None:
        st.session_state["decoder_uploaded_name"] = uploaded_file.name
        st.session_state["decoder_uploaded_bytes"] = uploaded_file.getvalue()
        st.session_state["retrieve_result"] = None
        st.session_state["decoder_result"] = None

    st.caption("Or retrieve a previously generated encoded image by code.")

    retrieve_col1, retrieve_col2 = st.columns([4, 1])

    with retrieve_col1:
        st.text_input(
            "Retrieval code",
            placeholder="e.g. X7P2-KL9Q",
            key="retrieve_code_input",
        )

    with retrieve_col2:
        get_image_clicked = st.button("Get Image", use_container_width=True)

    if get_image_clicked:
        code = st.session_state["retrieve_code_input"].strip()

        if not code:
            st.warning("Please enter a retrieval code.")
        else:
            try:
                with st.spinner("Retrieving your file..."):
                    result = retrieve_file(code)

                file_url = result.get("file_url")
                if not file_url:
                    st.session_state["retrieve_result"] = None
                    st.session_state["decoder_uploaded_bytes"] = None
                    st.session_state["decoder_uploaded_name"] = None
                    st.error("Retrieved record does not contain a downloadable file URL.")
                else:
                    file_resp = requests.get(file_url, timeout=60)

                    if file_resp.ok:
                        st.session_state["retrieve_result"] = result
                        st.session_state["decoder_uploaded_bytes"] = file_resp.content
                        st.session_state["decoder_uploaded_name"] = result.get("filename", "retrieved.png")
                        st.session_state["decoder_result"] = None
                        st.success("Image loaded successfully.")
                    else:
                        st.session_state["retrieve_result"] = None
                        st.session_state["decoder_uploaded_bytes"] = None
                        st.session_state["decoder_uploaded_name"] = None
                        st.error(f"Failed to download retrieved file. HTTP {file_resp.status_code}")

            except APIClientError as exc:
                st.session_state["retrieve_result"] = None
                st.session_state["decoder_uploaded_bytes"] = None
                st.session_state["decoder_uploaded_name"] = None
                st.error(str(exc))
            except Exception as exc:
                st.session_state["retrieve_result"] = None
                st.session_state["decoder_uploaded_bytes"] = None
                st.session_state["decoder_uploaded_name"] = None
                st.error(f"Unexpected error: {exc}")

    selected_source = get_selected_source_label(uploaded_file)
    if selected_source:
        st.success(f"Selected source: {selected_source}")

# -------------------------------
# Decode settings
# -------------------------------
with st.container(border=True):
    st.subheader("Decode settings")

    st.text_input(
        "Password",
        type="password",
        key="decoder_password",
    )

    st.selectbox(
        "Method",
        ["LSB", "DCT", "DWT"],
        key="decoder_method",
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("Decode", type="primary", use_container_width=True):
            st.session_state["decode_trigger"] = True

    with col2:
        if st.button("Clear", use_container_width=True):
            clear_decoder_state()
            st.rerun()

# -------------------------------
# Preview
# -------------------------------
if st.session_state["decoder_uploaded_bytes"] is not None:
    with st.container(border=True):
        st.subheader("Preview")

        with st.expander("Show selected image", expanded=False):
            st.image(
                st.session_state["decoder_uploaded_bytes"],
                caption=st.session_state["decoder_uploaded_name"],
                width=520,
            )

# -------------------------------
# Decode logic
# -------------------------------
if st.session_state["decode_trigger"]:
    st.session_state["decode_trigger"] = False

    if st.session_state["decoder_uploaded_bytes"] is None:
        st.warning("Please upload or retrieve an image first.")
    elif not st.session_state["decoder_password"]:
        st.warning("Please enter a password.")
    else:
        try:
            with st.spinner("Decoding secret from image..."):
                result = decode_image(
                    file_bytes=st.session_state["decoder_uploaded_bytes"],
                    filename=st.session_state["decoder_uploaded_name"],
                    password=st.session_state["decoder_password"],
                    method=st.session_state["decoder_method"],
                    session_id=session_id,
                )

            st.session_state["decoder_result"] = result
            st.success("Decoding successful.")

        except APIClientError as exc:
            st.error(f"Decoding failed: {exc}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")

# -------------------------------
# Decode result
# -------------------------------
decode_result = st.session_state["decoder_result"]
if decode_result:
    with st.container(border=True):
        st.subheader("Recovered plaintext")
        st.text_area(
            "Recovered plaintext",
            value=decode_result["plaintext"],
            height=220,
            disabled=True,
            label_visibility="collapsed",
        )

        if decode_result.get("decoded_s3_url"):
            st.markdown(f"[Open decoded image in S3]({decode_result['decoded_s3_url']})")