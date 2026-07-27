"""Streamlit interface for the Wk calculator."""

import streamlit as st
import streamlit.components.v1 as components

from wkcalc.diagrams import cross_section_svg
from wkcalc.explanations import explain_result
from wkcalc.exports import result_to_csv, result_to_html, result_to_json
from wkcalc.models import BoundaryType, RoadInput, SideInput, TravelledElement
from wkcalc.rules import calculate_travelled_width, calculate_wk
from wkcalc.validation import GeometryError

st.set_page_config(page_title="Wk Calculator", page_icon="↔️", layout="wide")

BOUNDARY_LABELS = {
    "Kerb at travelled-way edge": BoundaryType.KERB_AT_TRAVELLED_EDGE,
    "Kerb beyond traffic-edge line": BoundaryType.KERB_BEYOND_EDGE_LINE,
    "Sealed road beyond traffic-edge line": BoundaryType.SEALED_EDGE,
    "Unsealed road beyond traffic-edge line": BoundaryType.UNSEALED_EDGE,
    "Designed edge line": BoundaryType.DESIGNED_EDGE_LINE,
    "Authority-defined boundary": BoundaryType.AUTHORITY_OVERRIDE,
}
STEPS = ["Road arrangement", "Travelled way", "Left boundary", "Right boundary", "Limits", "Result"]


def initialise_state() -> None:
    defaults = {
        "step": 0,
        "arrangement": "Single carriageway",
        "mode": "Simple",
        "travelled_width": 10.5,
        "left_boundary": next(iter(BOUNDARY_LABELS)),
        "right_boundary": "Designed edge line",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def navigation() -> None:
    left, middle, right = st.columns([1, 3, 1])
    with left:
        if st.button("← Back", disabled=st.session_state.step == 0, use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with middle:
        st.progress((st.session_state.step + 1) / len(STEPS), text=f"Step {st.session_state.step + 1} of 6 · {STEPS[st.session_state.step]}")
    with right:
        if st.session_state.step < len(STEPS) - 1 and st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.step += 1
            st.rerun()


def boundary_form(side: str) -> None:
    key = f"{side}_boundary"
    st.selectbox("Boundary condition", BOUNDARY_LABELS, key=key)
    boundary = BOUNDARY_LABELS[st.session_state[key]]
    if boundary == BoundaryType.KERB_BEYOND_EDGE_LINE:
        st.number_input("Distance from traffic-edge line to kerb (m)", min_value=0.0, step=0.1, key=f"{side}_distance")
    elif boundary == BoundaryType.SEALED_EDGE:
        st.number_input("Sealed width available beyond edge line (m)", min_value=0.0, step=0.1, key=f"{side}_sealed")
    elif boundary == BoundaryType.AUTHORITY_OVERRIDE:
        st.number_input("Authority side allowance (m)", min_value=0.0, step=0.1, key=f"{side}_authority")
    elif boundary == BoundaryType.UNSEALED_EDGE:
        st.info("Unsealed area does not add to Wk.")
    elif boundary == BoundaryType.DESIGNED_EDGE_LINE:
        st.info("The standard maximum 3.00 m side allowance will be used.")
    else:
        st.info("The kerb limits the side allowance to zero.")


def side_from_state(side: str) -> SideInput:
    boundary = BOUNDARY_LABELS[st.session_state[f"{side}_boundary"]]
    return SideInput(
        boundary_type=boundary,
        distance_to_kerb=st.session_state.get(f"{side}_distance") if boundary == BoundaryType.KERB_BEYOND_EDGE_LINE else None,
        sealed_width_available=st.session_state.get(f"{side}_sealed") if boundary == BoundaryType.SEALED_EDGE else None,
        authority_allowance=st.session_state.get(f"{side}_authority") if boundary == BoundaryType.AUTHORITY_OVERRIDE else None,
    )


def detailed_width_form() -> float:
    st.caption("Only checked rows contribute to travelled width. Turn lanes default to included.")
    elements = []
    defaults = [("Through lanes", 2, 3.5, True), ("Turn lanes", 1, 3.5, True), ("Parking lanes", 1, 2.3, False), ("Bicycle lanes", 1, 1.5, False), ("Other travelled areas", 1, 1.0, False)]
    for index, (name, quantity, width, included) in enumerate(defaults):
        with st.container(border=True):
            cols = st.columns([2, 1, 1, 1, 2])
            cols[0].markdown(f"**{name}**")
            qty = cols[1].number_input("Quantity", 1, 20, quantity, key=f"qty_{index}")
            item_width = cols[2].number_input("Width (m)", 0.1, 20.0, width, 0.1, key=f"width_{index}")
            use = cols[3].checkbox("Included", included, key=f"included_{index}")
            notes = cols[4].text_input("Notes", key=f"notes_{index}")
            elements.append(TravelledElement(element_type=name, quantity=qty, individual_width=item_width, included=use, notes=notes))
    total = calculate_travelled_width(elements)
    st.metric("Calculated travelled width", f"{total:.2f} m")
    st.session_state.travelled_width = total
    return total


def build_road() -> RoadInput:
    return RoadInput(
        travelled_width=st.session_state.travelled_width,
        left_side=side_from_state("left"),
        right_side=side_from_state("right"),
        kerb_to_kerb_width=st.session_state.get("kerb_to_kerb") if st.session_state.get("use_kerb_limit") else None,
        total_sealed_width=st.session_state.get("sealed_limit") if st.session_state.get("use_sealed_limit") else None,
        authority_wk=st.session_state.get("authority_wk") if st.session_state.get("use_authority_wk") else None,
        sealed_areas_are_travelled=st.session_state.get("sealed_areas_are_travelled", False),
    )


def show_result() -> None:
    try:
        road = build_road()
        result = calculate_wk(road)
    except (GeometryError, ValueError) as error:
        st.error(str(error))
        st.button("Return to limits", on_click=lambda: st.session_state.update(step=4))
        return
    st.success("Calculation complete")
    columns = st.columns(3)
    metrics = [
        ("Travelled width", result.travelled_width), ("Left allowance", result.left_allowance),
        ("Right allowance", result.right_allowance), ("Unrestricted Wk", result.unrestricted_wk),
        ("Limiting width", result.limiting_width), ("Final Wk", result.calculated_wk),
    ]
    for index, (label, value) in enumerate(metrics):
        columns[index % 3].metric(label, "Not supplied" if value is None else f"{value:.2f} m")
    if result.authority_wk is not None:
        st.warning(f"Authority-defined Wk: **{result.authority_wk:.2f} m**. It is shown separately and requires authority review.")
    st.subheader("How this was calculated")
    for line in explain_result(road, result):
        st.write(line)
    for warning in result.warnings:
        st.warning(warning)
    st.subheader("Cross-section")
    components.html(cross_section_svg(result), height=260)
    st.subheader("Export calculation")
    a, b, c = st.columns(3)
    a.download_button("Download JSON", result_to_json(result), "wk-calculation.json", "application/json", use_container_width=True)
    b.download_button("Download CSV", result_to_csv(result), "wk-calculation.csv", "text/csv", use_container_width=True)
    c.download_button("Download HTML report", result_to_html(result), "wk-report.html", "text/html", use_container_width=True)


initialise_state()
st.title("Wk Calculator")
st.caption("A transparent carriageway-width calculation workspace · dimensions in metres")
navigation()
step = st.session_state.step

if step == 0:
    st.header("Choose the road arrangement")
    st.radio("Arrangement", ["Single carriageway", "One carriageway of divided road", "Custom / asymmetric carriageway", "Authority-defined width"], key="arrangement")
    st.info("Each side is configured independently in later steps, including for nominally symmetrical roads.")
elif step == 1:
    st.header("Define the travelled way")
    st.radio("Input mode", ["Simple", "Detailed"], horizontal=True, key="mode")
    if st.session_state.mode == "Simple":
        st.number_input("Total travelled-way width (m)", min_value=0.1, step=0.1, key="travelled_width")
    else:
        detailed_width_form()
elif step == 2:
    st.header("Set the left-side boundary")
    boundary_form("left")
elif step == 3:
    st.header("Set the right-side boundary")
    boundary_form("right")
elif step == 4:
    st.header("Add limiting dimensions")
    st.caption("Enable only dimensions that physically apply. Impossible geometry is rejected at calculation time.")
    st.checkbox("Apply a kerb-to-kerb limit", key="use_kerb_limit")
    if st.session_state.use_kerb_limit:
        st.number_input("Kerb-to-kerb width (m)", min_value=0.1, value=max(14.8, st.session_state.travelled_width), step=0.1, key="kerb_to_kerb")
    st.checkbox("Apply a total sealed-width limit", key="use_sealed_limit")
    if st.session_state.use_sealed_limit:
        st.number_input("Total sealed width (m)", min_value=0.1, value=max(16.0, st.session_state.travelled_width), step=0.1, key="sealed_limit")
    st.checkbox("Provide an authority-specified Wk", key="use_authority_wk")
    if st.session_state.use_authority_wk:
        st.number_input("Authority-specified Wk (m)", min_value=0.1, value=12.0, step=0.1, key="authority_wk")
    st.checkbox("Sealed areas beyond edge lines are intended as travelled way", key="sealed_areas_are_travelled")
else:
    st.header("Wk result")
    show_result()
