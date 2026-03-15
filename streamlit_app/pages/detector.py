from __future__ import annotations

import streamlit as st
from PIL import Image

from streamlit_app.api_client import detect_stego


st.set_page_config(page_title="Stego Detection", page_icon="🕵️", layout="wide")


def _render_risk_badge(risk_band: str) -> None:
    risk_band = risk_band.lower()
    if risk_band == "low":
        st.success("Assessment: Low stego risk")
    elif risk_band == "medium":
        st.warning("Assessment: Medium stego risk")
    else:
        st.error("Assessment: High stego risk")


def main() -> None:
    st.title("Stego Detection")
    st.write(
        "Analyze an uploaded image for suspicious hidden-message patterns. "
        "The result is a statistical risk estimate, not proof."
    )

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "bmp", "tiff"],
        help="PNG/BMP/TIFF are more suitable for simple spatial LSB detection than JPEG.",
    )

    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox(
            "Detector mode",
            options=["auto", "heuristic", "cnn"],
            index=0,
        )
    with col2:
        target = st.selectbox(
            "Target",
            options=["auto", "lsb", "dct"],
            index=0,
        )

    show_technical = st.checkbox("Show technical details", value=True)

    if uploaded_file is None:
        st.info("Upload an image to begin analysis.")
        return

    image = Image.open(uploaded_file)
    st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)

    if st.button("Analyze", type="primary"):
        try:
            with st.spinner("Running stego analysis..."):
                result = detect_stego(
                    file_name=uploaded_file.name,
                    file_bytes=uploaded_file.getvalue(),
                    mime_type=uploaded_file.type or "application/octet-stream",
                    mode=mode,
                    target=target,
                )
        except Exception as exc:
            st.error(f"Detection failed: {exc}")
            return

        st.subheader("Assessment")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Risk score", f"{result['risk_score']:.2f} / 100")
        metric_col2.metric("Risk band", result["risk_band"].title())
        metric_col3.metric("Detector", result["detector_used"])

        _render_risk_badge(result["risk_band"])
        st.info(result["confidence_note"])

        st.subheader("Signal Breakdown")
        for signal in result["signals"]:
            label = f"{signal['name']} — {signal['status']}"
            with st.expander(label):
                st.write(f"**Value:** {signal['value']}")
                st.write(signal["explanation"])

        if show_technical:
            st.subheader("Technical Details")
            st.write(f"**Filename:** {result['filename']}")
            st.write(f"**Image type:** {result['image_type']}")
            st.write(f"**Dimensions:** {result['width']} × {result['height']}")
            st.write(
                f"**Channels analyzed:** {', '.join(result['technical']['channels_analyzed'])}"
            )

            if result["technical"].get("format_warning"):
                st.warning(result["technical"]["format_warning"])

            notes = result["technical"].get("notes", [])
            if notes:
                st.write("**Notes:**")
                for note in notes:
                    st.write(f"- {note}")


if __name__ == "__main__":
    main()