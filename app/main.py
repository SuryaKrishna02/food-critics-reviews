import streamlit as st

from pages.sign_in import sign_in_page
from pages.food_critic import food_critic_page

# Set page configuration at the very beginning
st.set_page_config(
    page_title="Connoisseur's Corner",
    layout="centered"
)

def main():
    if not st.session_state.get("authenticated", False):
        sign_in_page()
    else:
        food_critic_page()

if __name__ == "__main__":
    main()