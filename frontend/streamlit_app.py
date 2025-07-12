import streamlit as st
import requests

st.set_page_config(page_title="Smart Nutrition Assistant", page_icon="🥗")
st.title("🥗 Smart Nutrition Assistant")
API = "http://localhost:8000"

# ----------------------------
# 🔐 AUTHENTICATION
# ----------------------------
if "token" not in st.session_state:
    st.session_state.token = ""

if st.session_state.token == "":
    with st.form("auth_form"):
        st.subheader("🔐 Login / Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        action = st.radio("Choose Action", ["Login", "Register"])
        submit = st.form_submit_button("Submit")
        
        if submit:
            route = "register" if action == "Register" else "login"
            try:
                res = requests.post(f"{API}/{route}", data={"username": username, "password": password})
                res.raise_for_status()
                data = res.json()
                if "access_token" in data:
                    st.session_state.token = data["access_token"]
                    st.success("✅ Logged in successfully!")
                else:
                    st.error(data.get("detail", "Failed to authenticate"))
            except Exception as e:
                st.error("🚫 Error connecting to backend")
                st.text(str(e))
                st.text(res.text if 'res' in locals() else '')
else:
    token = st.session_state.token
    st.success("🔓 Logged in")

    # ----------------------------
    # 🧠 TEXT TO MEAL PLAN
    # ----------------------------
    st.subheader("🍽️ Generate Meal Plan from Text")
    text_input = st.text_input("Enter your meal goal or dietary condition")
    if st.button("🧠 Generate Meal Plan"):
        try:
            res = requests.post(f"{API}/text", data={"text": text_input, "token": token})
            res.raise_for_status()
            meal_plan = res.json()["plan"]
            st.text_area("Generated Meal Plan", meal_plan, height=300)

            # Export to PDF
            if st.button("⬇️ Export Meal Plan as PDF"):
                pdf_res = requests.post(f"{API}/pdf", data={"text": meal_plan})
                pdf_path = pdf_res.json()["pdf_file"]
                with open(pdf_path, "rb") as file:
                    st.download_button("Download PDF", file, file_name="meal_plan.pdf")
        except Exception as e:
            st.error("❌ Failed to generate meal plan.")
            st.text(str(e))
            st.text(res.text if 'res' in locals() else '')

    # ----------------------------
    # 📸 IMAGE CAPTION TO MEAL
    # ----------------------------
    st.markdown("---")
    st.subheader("🖼️ Upload Image for Meal Suggestion")

    uploaded_file = st.file_uploader("Upload an image of food", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Show the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        if st.button("Analyze Image"):
            try:
                with st.spinner("Analyzing image..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API}/analyze-image", files=files)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "error" in data:
                        st.error(f"❌ {data['error']}")
                    else:
                        st.success("✅ Image analysis successful!")
                        food_items = data.get("food_items", [])
                        
                        if food_items and food_items[0] != "no food items detected":
                            st.write("**Detected food items:**")
                            for i, item in enumerate(food_items, 1):
                                st.write(f"{i}. {item}")
                            
                            # Option to generate meal plan
                            if st.button("Generate Meal Plan from Detected Items"):
                                try:
                                    food_list = ", ".join(food_items)
                                    meal_prompt = f"Create a healthy meal plan using these ingredients: {food_list}"
                                    
                                    with st.spinner("Generating meal plan..."):
                                        res = requests.post(f"{API}/text", data={"text": meal_prompt, "token": token})
                                        res.raise_for_status()
                                        meal_plan = res.json()["plan"]
                                        st.text_area("Generated Meal Plan", meal_plan, height=200)
                                except Exception as e:
                                    st.error(f"❌ Failed to generate meal plan: {str(e)}")
                        else:
                            st.warning("No food items detected in the image. Please try with a clearer food image.")
                            
            except requests.exceptions.RequestException as e:
                st.error("❌ Error connecting to backend")
                st.text(str(e))
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")

    # ----------------------------
    # 🎙️ AUDIO TRANSCRIPTION TO MEAL
    # ----------------------------
    st.subheader("🎙️ Upload Voice Prompt")
    audio = st.file_uploader("Upload a voice command (mp3)", type=["mp3"])
    if audio and st.button("🎧 Analyze Audio"):
        try:
            res = requests.post(f"{API}/voice", files={"file": audio})
            data = res.json()
            st.audio(audio)
            st.write("Transcript:", data["transcript"])
            st.write("Plan:", data["plan"])
        except Exception as e:
            st.error("❌ Audio analysis failed.")
            st.text(str(e))
            st.text(res.text if 'res' in locals() else '')

    # ----------------------------
    # 📊 NUTRITION LOOKUP
    # ----------------------------
    st.subheader("📊 Nutrition Facts")
    nutrition_query = st.text_input("Enter food name for nutrition facts", key="nutrition_input")
    if st.button("Get Nutrition Info"):
        if nutrition_query.strip():  # Check if input is not empty
            try:
                res = requests.post(f"{API}/nutrition", data={"text": nutrition_query})
                res.raise_for_status()
                facts = res.json().get("facts", [])
                if facts:
                    st.json(facts)
                else:
                    st.warning("No nutrition information found for this food item.")
            except Exception as e:
                st.error("❌ Failed to fetch nutrition info.")
                st.text(str(e))
                st.text(res.text if 'res' in locals() else '')
        else:
            st.warning("Please enter a food name to get nutrition facts.")

    # ----------------------------
    # 📜 VIEW MEAL PLAN HISTORY
    # ----------------------------
    st.subheader("📜 View Meal Plan History")
    if st.button("Show History"):
        try:
            res = requests.post(f"{API}/history", data={"token": token})
            for item in res.json().get("history", []):
                st.markdown(f"🕒 **{item['created_at']}**")
                st.markdown(f"**Input:** `{item['input']}`")
                st.markdown(f"**Plan:** {item['plan']}")
        except Exception as e:
            st.error("❌ Failed to fetch history.")
            st.text(str(e))
            st.text(res.text if 'res' in locals() else '')
