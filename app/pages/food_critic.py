import streamlit as st
from pages.sign_in import sign_in_page
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from config.config import reviews_collection, BG_IMAGE_URL

def food_critic_page():
    if not st.session_state.get("authenticated", False):
        sign_in_page()
        return

    st.title("Connoisseur's Corner")

    # Hide all Streamlit default elements and set background
    st.markdown(f"""
        <style>
        /* Hide Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Set page background */
        .stApp {{
            background-image: url({BG_IMAGE_URL});
            background-size: cover;
        }}
        
        /* Remove default padding */
        .block-container {{
            padding-top: 1rem !important;
        }}
        
        /* Message styling */
        .message {{
            margin: 10px 0;
            clear: both;
            overflow: hidden;
        }}
        .message-container {{
            display: flex;
            flex-direction: column;
            max-width: 80%;
        }}
        .message p {{
            padding: 10px 15px;
            border-radius: 15px 15px 15px 15px;
            margin: 0;
            display: inline-block;
        }}
        .user-message {{
            align-items: flex-start;
            float: left;
        }}
        .system-message {{
            align-items: flex-end;
            float: right;
        }}
        .user-message p {{
            background: rgba(227, 242, 253, 0.9);
            color: black;
        }}
        .system-message p {{
            background: rgba(245, 245, 245, 0.9);
            color: black;
        }}
        .timestamp {{
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
            margin: 5px 10px;
            align-self: flex-start;
        }}
        
        /* Welcome text */
        .welcome-text {{
            color: white;
            margin-bottom: 1rem;
        }}
        
        /* Activity section */
        .activity-header {{
            color: white;
            margin: 1rem 0;
        }}
        
        .activity-card {{
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            color: black;
        }}
        
        .legend {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 5px;
            color: white;
        }}
        
        /* Footer */
        .footer {{
            color: white;
            text-align: center;
            padding: 1rem;
            margin-top: 2rem;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.subheader("Unleash your thoughts on Food")
    st.write(f"Welcome, {st.session_state['username']}")
    # Welcome text
    st.markdown('<div class="welcome-text">You can add, modify & change your reviews</div>', unsafe_allow_html=True)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat window
    for msg in st.session_state.chat_history:
        msg_class = "user-message" if msg["role"] == "user" else "system-message"
        # Convert UTC to EST
        est_time = msg["timestamp"].astimezone(ZoneInfo("America/New_York"))
        st.markdown(f"""
            <div class="message">
                <div class="message-container {msg_class}">
                    <p>{msg["content"]}</p>
                    <div class="timestamp">{est_time.strftime('%H:%M')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Type your thoughts...", height=100)
        col1, col2 = st.columns([1, 1])
        with col1:
            send = st.form_submit_button("Send")
        with col2:
            reset = st.form_submit_button("Reset")
            
    if send and user_input:
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now(timezone.utc),
            "type": "insert"
        }
        system_message = {
            "role": "system",
            "content": "Thank you for sharing your thoughts! Your review has been recorded.",
            "timestamp": datetime.now(timezone.utc),
            "type": "insert"
        }
        st.session_state.chat_history.extend([user_message, system_message])
        
        # Save to database
        # reviews_collection.insert_many([user_message, system_message])
        st.rerun()
    
    if reset:
        st.session_state.chat_history = []
        st.rerun()
        
    # Past activity section
    st.subheader("Past Activity")
    
    # Legend
    st.markdown("""
        <div class="legend">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background: #4caf50; border-radius: 4px;"></div>
                <span>Insert</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background: #ff9800; border-radius: 4px;"></div>
                <span>Modify</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 20px; height: 20px; background: #f44336; border-radius: 4px;"></div>
                <span>Delete</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display activities
    activities = list(reviews_collection.find(
        {"username": st.session_state["username"]}
    ).sort("timestamp", -1))
    
    if not activities:
        st.markdown("""
            <div class="activity-card">
                <h3>No Recent Activity</h3>
                <p>Start a conversation to see your activity here!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for activity in activities:
            activity_type = activity.get('type', 'insert')
            background_color = {
                'insert': 'rgba(232, 245, 233, 0.9)',
                'modify': 'rgba(255, 243, 224, 0.9)',
                'delete': 'rgba(255, 235, 238, 0.9)'
            }.get(activity_type, 'rgba(255, 255, 255, 0.9)')
            
            # Convert UTC to EST for activity timestamps
            est_time = activity['timestamp'].astimezone(ZoneInfo("America/New_York"))
            
            st.markdown(f"""
                <div class="activity-card" style="background: {background_color};">
                    <strong>Type:</strong> {activity['role']}<br>
                    <strong>Date:</strong> {est_time.strftime('%Y-%m-%d %H:%M')}<br>
                    <strong>Message:</strong> {activity['content']}
                </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">© 2024 Connoisseur\'s Corner, All rights reserved</div>', unsafe_allow_html=True)