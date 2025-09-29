import streamlit as st
import time
import base64
from io import BytesIO
from utils import send_email_otp, generate_otp

def ensure_email_in_whitelist(email):
    all_whitelist = st.session_state.db_manager.user_whitelist.get_all_whitelist_domain()
    return len(list(filter(lambda domain_tuple: email.endswith(domain_tuple[0]), all_whitelist))) > 0

def add_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .stApp {
        background: #f8fafc;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Login container */
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 450px;
        margin: 0 auto;
    }
    
    /* Title styling */
    .main-title {
        color: #1e3c72;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .subtitle {
        color: #2a5298;
        font-size: 1.2rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e6ed;
        padding: 12px 16px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background-color: #f8fafc;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2a5298;
        box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
        background-color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff4757, #ff3838);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-size: 1.1rem;
        font-weight: 500;
        width: 100%;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff3838, #ff2f2f);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 71, 87, 0.4);
    }
    
    /* Animated boat container */
    .boat-animation {
        position: fixed;
        bottom: 80px;
        left: 0;
        width: 100%;
        height: 120px;
        z-index: 1;
        overflow: hidden;
    }
    
    .boat-container {
        position: absolute;
        animation: moveBoat 15s linear infinite;
        top: 20px;
    }
    
    @keyframes moveBoat {
        0% { left: -150px; }
        100% { left: 100%; }
    }
    
    /* Water body styling */
    .water-body {
        position: fixed;
        bottom: 50px;
        left: 0;
        width: 100%;
        height: 80px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,60 Q300,30 600,60 T1200,60 L1200,120 L0,120 Z' fill='%2374b9ff'/%3E%3C/svg%3E");
        background-size: cover;
        z-index: 0;
        animation: waveMove 1s ease-in-out infinite;
    }
    
    @keyframes waveMove {
        0%, 100% { background-position-x: 0px; }
        50% { background-position-x: -100px; }
    }
    
    .water-waves {
        position: absolute;
        top: 0;
        left: 0;
        width: 200%;
        height: 100%;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,50 Q300,20 600,50 T1200,50 L1200,120 L0,120 Z' fill='%2374b9ff' fill-opacity='0.3'/%3E%3C/svg%3E");
        animation: wave 1s ease-in-out infinite;
    }
    
    @keyframes wave {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(-50px); }
    }
    
    /* Responsive adjustments */
    @media (max-height: 700px) {
        .boat-animation {
            display: none;
        }
        .water-body {
            display: none;
        }
    }
    
    @media (max-width: 768px) {
        .boat-animation {
            height: 80px;
            bottom: 60px;
        }
        .boat-container svg {
            width: 80px;
            height: 60px;
        }
        .water-body {
            height: 50px;
            bottom: 40px;
        }
    }
    
    /* Wave animation - bottom decoration only */
    .wave {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 40px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z' fill='%2374b9ff' fill-opacity='0.1'/%3E%3C/svg%3E");
        background-size: cover;
        z-index: -1;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 10px;
        left: 0;
        right: 0;
        text-align: center;
        color: #2a5298;
        font-size: 0.9rem;
        font-weight: 400;
        z-index: 1000;
        background: rgba(248, 250, 252, 0.9);
        padding: 5px;
    }
    
    /* Floating particles effect */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    /* Labels */
    .stTextInput > label {
        color: #1e3c72;
        font-weight: 500;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def create_animated_boat():
    """Create an animated boat that moves from left to right"""
    return """
    <div class="boat-animation">
        <div class="boat-container">
            <svg width="120" height="80" viewBox="0 0 140 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Ship hull -->
                <path d="M15 60 L125 60 L120 75 L20 75 Z" fill="#2a5298" stroke="#1e3c72" stroke-width="2"/>
                <!-- Ship deck -->
                <rect x="25" y="45" width="90" height="15" fill="#3d5aa3" stroke="#1e3c72" stroke-width="1"/>
                <!-- Superstructure -->
                <rect x="40" y="30" width="60" height="15" fill="#4a69bd" stroke="#1e3c72" stroke-width="1"/>
                <rect x="55" y="15" width="30" height="15" fill="#5f73c5" stroke="#1e3c72" stroke-width="1"/>
                <!-- Mast -->
                <line x1="70" y1="5" x2="70" y2="30" stroke="#1e3c72" stroke-width="3"/>
                <!-- Flag -->
                <path d="M70 5 L95 12 L70 19 Z" fill="#ff4757"/>
                <!-- Containers -->
                <rect x="30" y="50" width="12" height="10" fill="#ff6b7a"/>
                <rect x="45" y="50" width="12" height="10" fill="#4834d4"/>
                <rect x="60" y="50" width="12" height="10" fill="#00d2d3"/>
                <rect x="75" y="50" width="12" height="10" fill="#ff9f43"/>
                <rect x="90" y="50" width="12" height="10" fill="#6c5ce7"/>
                <!-- Smoke from chimney -->
                <circle cx="85" cy="25" r="3" fill="#ddd" opacity="0.7"/>
                <circle cx="88" cy="20" r="2" fill="#eee" opacity="0.5"/>
                <circle cx="91" cy="15" r="1.5" fill="#f5f5f5" opacity="0.3"/>
            </svg>
        </div>
        <div class="water-waves"></div>
    </div>
    <div class="water-body"></div>
    """

def create_particles():
    """Create floating particles background"""
    return """
    <div class="particles">
        <div class="particle" style="left: 10%; top: 20%; width: 4px; height: 4px; animation-delay: 0s;"></div>
        <div class="particle" style="left: 20%; top: 80%; width: 6px; height: 6px; animation-delay: 1s;"></div>
        <div class="particle" style="left: 60%; top: 30%; width: 3px; height: 3px; animation-delay: 2s;"></div>
        <div class="particle" style="left: 80%; top: 70%; width: 5px; height: 5px; animation-delay: 3s;"></div>
        <div class="particle" style="left: 40%; top: 10%; width: 4px; height: 4px; animation-delay: 4s;"></div>
        <div class="particle" style="left: 90%; top: 40%; width: 3px; height: 3px; animation-delay: 5s;"></div>
    </div>
    """


def show_login_form():
    # st.session_state.current_page = 'input'
    # st.rerun()
    st.set_page_config(
        page_title="Aramco Trading - Vessel Tracking",
        page_icon="🚢",
        # layout="centered",
        # initial_sidebar_state="collapsed"
    )
    
    add_custom_css()
    
    # Add animated boat and water
    st.markdown(create_animated_boat(), unsafe_allow_html=True)
    st.markdown('<div class="wave"></div>', unsafe_allow_html=True)
    
    # Main content
    st.markdown('<div style="height: 150px;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">ARAMCO TRADING</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Vessel Tracking System</p>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "👤 Email",
                placeholder="Enter your email"
            )
            
            logged_on = st.form_submit_button(
                "🔐 Login",
                use_container_width=True,
                type="primary"
            )

            _, _, col3 = st.columns(3)
            
            with col3:
                registered = st.form_submit_button(
                    "📝 Register",
                    use_container_width=True,
                    type="secondary"
                )
            
            if "otp_sent" not in st.session_state:
                st.session_state.otp_sent = False
            if "login_success" not in st.session_state:
                st.session_state.login_success = False
            if 'otp_number' not in st.session_state:
                st.session_state.otp_number = None

            if registered:
                @st.dialog("📝 User Registration")
                def registration_dialog():
                    if "user_registration_data" not in st.session_state:
                        st.session_state.user_registration_data = {}
                    if "registration_success" not in st.session_state:
                        st.session_state.registration_success = False

                    st.write("Please fill in your details to register:")
                    with st.form("registration_form"):
                        first_name = st.text_input("First Name", placeholder="Enter your first name")
                        last_name = st.text_input("Last Name", placeholder="Enter your last name")
                        email = st.text_input("Email", placeholder="Enter your email address")
                        confirm_button = st.form_submit_button(
                            "Confirm Registration",
                            use_container_width=True,
                            type="primary"
                        )
                        
                        if confirm_button:
                            email = email.strip().lower()
                            last_name = last_name.strip().lower()
                            first_name = first_name.strip().lower()
                            
                            if not first_name:
                                st.error("❌ Please enter your first name!")
                            elif not last_name:
                                st.error("❌ Please enter your last name!")
                            elif not email:
                                st.error("❌ Please enter your email address!")
                            elif "@" not in email or "." not in email:
                                st.error("❌ Please enter a valid email address")
                            elif not ensure_email_in_whitelist(email):
                                st.error("❌ Please use only whitelisted email addresses!")
                            elif st.session_state.db_manager.user.get_user_by_email(email) is not None:
                                st.error("❌ User with this email already exists!")
                            else:
                                st.session_state.user_registration_data = {
                                    "first_name": first_name,
                                    "last_name": last_name,
                                    "email": email
                                }
                                st.session_state.otp_number = generate_otp()
                                send_email_otp(email, first_name, st.session_state.otp_number)
                                st.session_state.otp_sent = True

                    if st.session_state.otp_sent:
                        st.info(f"An OTP has been sent to **{email}**")
                        with st.form("otp_verification_form"):
                            otp = st.text_input(
                                "Enter OTP code sent to your email", 
                                placeholder="Enter the 6-digit code",
                                max_chars=6
                            )
                            _, _, col3 = st.columns(3)

                            with col3:
                                verify_button = st.form_submit_button(
                                    "Verify OTP",
                                    use_container_width=True,
                                    type="secondary"
                                )

                            if verify_button:
                                if st.session_state.otp_number == otp:
                                    st.session_state.db_manager.user.add_user(
                                        first_name=st.session_state.user_registration_data["first_name"],
                                        last_name=st.session_state.user_registration_data["last_name"],
                                        email=st.session_state.user_registration_data["email"],
                                        code=st.session_state.otp_number
                                    )
                                    st.success("✅ OTP verified successfully!")
                                    st.session_state.registration_success = True
                                else:
                                    st.error("❌ Invalid OTP. Please try again.")

                    if st.session_state.registration_success:
                        st.success("✅ Registration successful!")
                        st.write("### 🔄 Logging you in...")
                        st.session_state.logged_in = True
                        st.session_state.user = st.session_state.db_manager.user.get_user_by_email(email)

                        if 'vessels' not in st.session_state:
                            st.session_state.vessels = []
                            
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(101):
                            progress_bar.progress(i)
                            if i < 30:
                                status_text.text("Creating your account...")
                            elif i < 60:
                                status_text.text("Setting up your profile...")
                            elif i < 90:
                                status_text.text("Finalizing login...")
                            else:
                                status_text.text("Almost ready...")
                            time.sleep(0.02)
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.balloons()
                        st.success(f"🎉 Welcome to the platform!")
                        # st.session_state.current_page = 'input'
                        st.session_state.current_page = 'results'
                        time.sleep(1.0)
                        st.rerun()

                registration_dialog()

            if logged_on:
                @st.dialog("User Login")
                def login_dialog():
                    with st.form("otp_verification_form"):
                        otp_2 = st.text_input(
                            "Enter OTP code sent to your email", 
                            placeholder="Enter the 6-digit code",
                            max_chars=6
                        )
                        _, _, col3 = st.columns(3)

                        with col3:
                            verify_button_2 = st.form_submit_button(
                                "Verify OTP",
                                use_container_width=True,
                                type="secondary"
                            )

                        if verify_button_2:
                            if otp_2 == st.session_state.user.iloc[0]['code']:
                                st.success("✅ Login successful, bringing you in!")
                                st.session_state.current_page = 'results'
                                st.session_state.logged_in = True
                                # st.session_state.current_page = 'input'
                                st.rerun()
                            else:
                                st.error("❌ Invalid OTP. Please try again.")
                
                test_past_user = st.session_state.db_manager.user.get_user_by_email(email)

                if not email:
                    st.error("❌ Please enter your email!")
                elif test_past_user is None:
                    st.error("❌ No such registered user. Please register! (Emails are in small caps!)")
                else:
                    st.info(f"An OTP has been sent to **{email}**")
                    first_name = test_past_user.iloc[0]['first_name']
                    st.session_state.otp_number = generate_otp()
                    st.session_state.db_manager.user.update_otp_code(email, st.session_state.otp_number)
                    send_email_otp(email, first_name, st.session_state.otp_number)
                    st.session_state.user = st.session_state.db_manager.user.get_user_by_email(email)

                    ## Get all past watchlist of user while waiting for OTP from client
                    if 'vessels' not in st.session_state:
                        user_email = st.session_state.user.iloc[0]['email']
                        vessels = st.session_state.db_manager.get_user_watchlist(user_email)
                        if vessels is not None:
                            st.session_state.vessels = vessels.to_dict(orient="records")
                        else:
                            st.session_state.vessels = []

                    login_dialog()

        
        st.markdown(
            """
            <style>
            .stForm {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                background-color: #fafafa;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="footer">Brought to you by <strong>ATC Innovations</strong></div>',
        unsafe_allow_html=True
    )

