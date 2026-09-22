import streamlit as st
from graph import app_graph


st.set_page_config(
    page_title="MediBuddy Weather Advisory Bot",
    page_icon="🌦️",
    layout="centered"
)


st.title("🌦️ MediBuddy Weather Advisory Bot")
st.caption("Live weather-based outdoor activity safety assistant powered by LangGraph + Open-Meteo + Gemini")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []


with st.sidebar:
    st.header("About")

    st.write(
        """
        This assistant:
        - 🌦️ Fetches live weather from Open-Meteo.
        - 📋 Matches weather against SOP rules.
        - 🤖 Uses LangGraph workflow.
        - 💬 Uses Gemini to generate natural-language responses.
        """
    )

    st.divider()

    st.subheader("Supported Activities")

    st.markdown("""
    - 🚴 Cycling
    - 🏃 Running
    - 🥾 Hiking
    - 🚗 Travel
    - 🧺 Picnic
    - 🐶 Pets
    - 👧 Children
    - 👵 Elderly
    """)

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()

user_query = st.text_input(
    "💬 Activity Question",
    placeholder="Example: Is it safe to cycle today?"
)

city = st.text_input(
    "📍 City",
    placeholder="Example: Bengaluru"
)


if st.button("Get Weather Advice", type="primary"):

    if user_query.strip() == "":
        st.warning("Please enter an activity question.")
        st.stop()
    

   
    display_city = city.title() if city else "Previous Location"

    user_message = (
        f"**Question:** {user_query}\n\n"
        f"📍 **City:** {display_city}"
)
    st.session_state.messages.append(
        {"role": "user", "content": user_message}
    )

    with st.chat_message("user"):
        st.markdown(user_message)

   
    with st.spinner("Fetching live weather and checking safety policies..."):

        result = app_graph.invoke({
            "user_query": user_query,
            "city": city,
            "weather": None,
            "matched_sop": None,
            "response": "",
            "history": st.session_state.history
        })

  
    st.session_state.history = result["history"]

    assistant_reply = result["response"]

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )

    
    with st.chat_message("assistant"):

        st.success("Safety recommendation generated.")

        st.markdown(assistant_reply)

        weather = result.get("weather")
        sop = result.get("matched_sop")

      
        if weather:
            st.divider()
            st.subheader("🌤️ Live Weather")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("🌡 Temperature", f"{weather['temperature']} °C")
                st.metric("💨 Wind Speed", f"{weather['wind_speed']} km/h")

            with col2:
                st.metric("🌧 Rain Chance", f"{weather['rain_probability']} %")
                st.metric("☀️ UV Index", weather["uv_index"])

        
        if sop:
            st.divider()
            st.subheader("📋 SOP Applied")

            severity = sop["severity"]

            if severity == "Critical":
                st.error(f"**{sop['id']}** | {sop['category']} | {severity}")

            elif severity == "High":
                st.warning(f"**{sop['id']}** | {sop['category']} | {severity}")

            elif severity == "Medium":
                st.info(f"**{sop['id']}** | {sop['category']} | {severity}")

            else:
                st.success(f"**{sop['id']}** | {sop['category']} | {severity}")

st.divider()
st.caption(
    "Weather source: Open-Meteo • Policy engine: JSON SOP rules • Workflow: LangGraph • Response generation: Gemini"
)