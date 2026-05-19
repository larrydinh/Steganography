# from pathlib import Path
# import streamlit as st

# from streamlit_app.api_client import health_check, APIClientError
# from streamlit_app.ui_helpers import apply_global_styles, render_sidebar_status

# st.set_page_config(
#     page_title="Image Steganography",
#     page_icon="🔐",
#     layout="wide",
# )

# apply_global_styles()
# render_sidebar_status(health_check, APIClientError)

# with st.sidebar:
#     BASE_DIR = Path(__file__).resolve().parent
#     profile_path = BASE_DIR / "assets" / "images" / "profile.png"

#     st.markdown("### Developed by")
#     st.markdown("**Phuc Dinh**")
#     st.image(str(profile_path), width=140)

#     st.markdown("[LinkedIn](https://www.linkedin.com/in/huuphucdinh/)")
#     st.markdown("[GitHub](https://github.com/larrydinh/Steganography)")


# st.markdown(
#     """
#     <div class="hero-card">
#         <div class="hero-title">Image Steganography</div>
#         <div class="hero-subtitle">
#             Hide encrypted messages inside images, generate stego images, retrieve them with a code,
#             and decode them again with the correct password.
#         </div>
#         <div class="pill-row">
#             <span class="pill">🔒 AES-encrypted payload</span>
#             <span class="pill">🖼 LSB / DCT / DWT methods</span>
#             <span class="pill">☁️ AWS S3 retrieval flow</span>
#             <span class="pill">🛡 Statistical stego detection</span>
#         </div>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# st.markdown(
#     """
#     ### What is steganography?

#     Steganography is a technique for hiding information inside ordinary media such as images, audio, or video.
#     Unlike encryption, which makes a message unreadable, steganography hides the existence of the message itself.

#     In this project, the secret message is first encrypted with a password and then embedded into an image.
#     The receiver can later decode the image and recover the original message using the correct password.
#     """
# )

# st.divider()

# st.subheader("How the system works")

# workflow = [
#     ("1", "Upload Image", "Choose a cover image that will carry the hidden encrypted message."),
#     ("2", "Encrypt Message", "The plaintext is protected with a password before embedding."),
#     ("3", "Generate Stego Image", "The backend embeds the encrypted payload using the selected method."),
#     ("4", "Decode or Detect", "Download, retrieve by code, decode with password, or analyze suspicious patterns."),
# ]

# cols = st.columns(4)

# for col, (num, title, body) in zip(cols, workflow):
#     with col:
#         st.markdown(
#             f"""
#             <div class="mini-card">
#                 <div class="step-number">{num}</div>
#                 <h3>{title}</h3>
#                 <p>{body}</p>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

# st.divider()

# st.subheader("Try the demo")

# cta1, cta2, cta3 = st.columns(3)

# with cta1:
#     st.page_link(
#         "pages/1_Encoder.py",
#         label="Start Encoding",
#         icon="🔒",
#         use_container_width=True,
#     )

# with cta2:
#     st.page_link(
#         "pages/2_Decoder.py",
#         label="Decode Message",
#         icon="🔓",
#         use_container_width=True,
#     )

# with cta3:
#     st.page_link(
#         "pages/3_Detector.py",
#         label="Analyze Suspicious Image",
#         icon="🛡",
#         use_container_width=True,
#     )

# st.info(
#     "Recommended demo flow: encode a short message first, copy the retrieval code, "
#     "then open Decode Message and retrieve the image by code."
# )


# # =========================# =========================# =========================
# from pathlib import Path
# import streamlit as st
# from textwrap import dedent
# from streamlit_app.api_client import health_check, APIClientError
# from streamlit_app.ui_helpers import apply_global_styles, render_sidebar_status

# st.set_page_config(
#     page_title="Image Steganography",
#     page_icon="🔐",
#     layout="wide",
# )

# apply_global_styles()
# render_sidebar_status(health_check, APIClientError)

# BASE_DIR = Path(__file__).resolve().parent

# with st.sidebar:
#     profile_path = BASE_DIR / "assets" / "images" / "profile.png"

#     st.markdown("### Developed by")
#     st.markdown("**Phuc Dinh**")

#     st.image(str(profile_path), width=140)

#     st.markdown(
#         "[LinkedIn](https://www.linkedin.com/in/huuphucdinh/)"
#     )

#     st.markdown(
#         "[GitHub](https://github.com/larrydinh/Steganography)"
#     )

# # =========================
# # HERO SECTION
# # =========================

# st.markdown(
#     dedent("""
#     <div class="hero-card">
#         <div class="hero-title">
#             Secure Image Steganography
#         </div>

#         <div class="hero-subtitle">
#             Hide encrypted messages inside images, generate stego images,
#             retrieve them with a code, and decode them again with
#             the correct password.
#         </div>

#         <div class="pill-row">
#             <span class="pill">🔒 AES-encrypted payload</span>
#             <span class="pill">🖼 LSB / DCT / DWT methods</span>
#             <span class="pill">☁️ AWS S3 retrieval flow</span>
#             <span class="pill">🛡 Statistical stego detection</span>
#         </div>
#     </div>
#     """),
#     unsafe_allow_html=True,
# )

# # =========================
# # STEGANOGRAPHY BANNER
# # =========================

# banner_path = BASE_DIR / "assets" / "images" / "stego_banner.png"

# st.image(
#     str(banner_path),
#     use_container_width=True,
# )

# # =========================
# # INTRODUCTION
# # =========================

# st.markdown(
#     """
#     ### What is steganography?

#     Steganography is a technique for hiding information inside ordinary media
#     such as images, audio, or video.

#     Unlike encryption, which makes a message unreadable, steganography hides
#     the existence of the message itself.

#     In this project, the secret message is first encrypted with a password
#     and then embedded into an image.

#     The receiver can later decode the image and recover the original message
#     using the correct password.
#     """
# )

# st.divider()

# # =========================
# # WORKFLOW
# # =========================

# st.subheader("How the system works")

# workflow = [
#     (
#         "1",
#         "Upload Image",
#         "Choose a cover image that will carry the hidden encrypted message.",
#     ),
#     (
#         "2",
#         "Encrypt Message",
#         "The plaintext is protected with a password before embedding.",
#     ),
#     (
#         "3",
#         "Generate Stego Image",
#         "The backend embeds the encrypted payload using the selected method.",
#     ),
#     (
#         "4",
#         "Decode or Detect",
#         "Download, retrieve by code, decode with password, or analyze suspicious patterns.",
#     ),
# ]

# cols = st.columns(4)

# for col, (num, title, body) in zip(cols, workflow):
#     with col:
#         st.markdown(
#             dedent(f"""
#             <div class="mini-card">

#                 <div class="step-number">
#                     {num}
#                 </div>

#                 <h3>{title}</h3>

#                 <p>{body}</p>

#             </div>
#             """),
#             unsafe_allow_html=True,
#         )

# st.divider()

# # =========================
# # DEMO ACTIONS
# # =========================

# st.subheader("Try the demo")

# cta1, cta2, cta3 = st.columns(3)

# with cta1:
#     st.page_link(
#         "pages/1_Encoder.py",
#         label="Start Encoding",
#         icon="🔒",
#         use_container_width=True,
#     )

# with cta2:
#     st.page_link(
#         "pages/2_Decoder.py",
#         label="Decode Message",
#         icon="🔓",
#         use_container_width=True,
#     )

# with cta3:
#     st.page_link(
#         "pages/3_Detector.py",
#         label="Analyze Suspicious Image",
#         icon="🛡",
#         use_container_width=True,
#     )

# st.info(
#     "Recommended demo flow: encode a short message first, "
#     "copy the retrieval code, then open Decode Message "
#     "and retrieve the image by code."
# )
from pathlib import Path
import streamlit as st

from streamlit_app.api_client import health_check, APIClientError
from streamlit_app.ui_helpers import apply_global_styles, render_sidebar_status

st.set_page_config(
    page_title="Image Steganography",
    page_icon="🔐",
    layout="wide",
)

apply_global_styles()
render_sidebar_status(health_check, APIClientError)

BASE_DIR = Path(__file__).resolve().parent

with st.sidebar:
    profile_path = BASE_DIR / "assets" / "images" / "profile.png"

    st.markdown("### Developed by")
    st.markdown("**Phuc Dinh**")

    if profile_path.exists():
        st.image(str(profile_path), width=140)

    st.markdown("[LinkedIn](https://www.linkedin.com/in/huuphucdinh/)")
    st.markdown("[GitHub](https://github.com/larrydinh/Steganography)")


# HERO
st.title("Image Steganography")

# st.write(
#     "Hide encrypted messages inside images, generate stego images, retrieve them "
#     "with a code, and decode them again with the correct password."
# )

# pill1, pill2, pill3, pill4 = st.columns(4)

# with pill1:
#     st.info("🔒 AES-encrypted payload")

# with pill2:
#     st.info("🖼 LSB / DCT / DWT methods")

# with pill3:
#     st.info("☁️ AWS S3 retrieval flow")

# with pill4:
#     st.info("🛡 Statistical stego detection")


# BANNER IMAGE
banner_path = BASE_DIR / "assets" / "images" / "stego_banner.png"

if banner_path.exists():
    st.image(str(banner_path), use_container_width=True)
else:
    st.warning(f"Banner image not found: {banner_path}")


# INTRODUCTION
st.subheader("What is image steganography?")

st.write(
    " Image steganography is a technique for hiding information inside an image in a way that is invisible to the human eye."
)

st.write(
    "Unlike encryption, which makes a message unreadable, steganography hides the existence of the message itself."
)

st.write(
    "In this project, the secret text message is first encrypted with a password and "
    "then embedded into an image. The receiver can later decode the image and "
    "recover the original message using the correct password."
)

st.divider()


# WORKFLOW
st.subheader("How the system works ?")

workflow = [
    (
        "Step 1",
        "Upload Image",
        "Users choose a cover image that will carry the hidden encrypted message."
    ),

    (
        "Step 2",
        "Encrypt Message",
        "Users enter a plaintext message and protect it with a password. "
        "Then, they can either download the generated image to their device "
        "or copy the retrieval code generated by the system to retrieve the image later in the Decode tab."
    ),

    (
        "Step 3",
        "Generate Stego Image",
        "Click the Generate Image button to embed the encrypted message "
        "using different steganography algorithms."
    ),

    (
        "Step 4",
        "Decrypt Message",
        "Users upload the encrypted image or retrieve it using the retrieval code from Step 2. "
        "After entering the correct password, the hidden message will be revealed."
    ),

    (
        "Step 5 (Optional)",
        "Detector",
        "Users upload a suspicious image to identify whether the image contains hidden information."
    )
]
cols = st.columns(5)

for col, (num, title, body) in zip(cols, workflow):
    with col:
        with st.container(border=True):
            st.markdown(f"### {num}")
            st.markdown(f"**{title}**")
            st.write(body)

st.divider()


# DEMO ACTIONS
st.subheader("Try the demo")

cta1, cta2, cta3 = st.columns(3)

with cta1:
    st.page_link(
        "pages/1_Encoder.py",
        label="🔒 Start Encoding",
        use_container_width=True,
    )

with cta2:
    st.page_link(
        "pages/2_Decoder.py",
        label="🔓 Decode Message",
        use_container_width=True,
    )

with cta3:
    st.page_link(
        "pages/3_Detector.py",
        label="🛡 Analyze Suspicious Image",
        use_container_width=True,
    )

st.info(
    "Recommended demo flow: encode a short message first, copy the retrieval code, "
    "then open Decode Message and retrieve the image by code."
)