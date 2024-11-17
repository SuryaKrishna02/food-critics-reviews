import streamlit as st
from config.config import users_collection, BG_IMAGE_URL

def sign_in_page():
    st.title("Connoisseur's Corner")
    
    # Add background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({BG_IMAGE_URL});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.subheader("Can't wait to hear from you")
    
    # Create sign-in form
    with st.form("sign_in_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submit = st.form_submit_button("Sign In")
            
        with col2:
            if st.form_submit_button("Forgot Password?"):
                st.info("Please contact support to reset your password.")
    
    # Handle sign-in logic
    if submit:
        user = users_collection.find_one({
            "name": username,
            "password": password
        })
        
        if user:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success("Successfully signed in!")
            st.rerun()
        else:
            st.error("Invalid Credentials")

    # Footer
    st.markdown("---")
    st.markdown("© 2024 Connoisseur's Corner, All rights reserved")