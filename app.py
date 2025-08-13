
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv, dotenv_values

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from .env file
supabase_url = dotenv_values().get("supabaseurl")
supabase_key = dotenv_values().get("SUPABASE_ANON_KEY")

# Initialize Supabase client
# Handle potential errors during initialization
try:
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        client_initialized = True
    else:
        client_initialized = False
except Exception as e:
    client_initialized = False
    st.error(f"Failed to initialize Supabase client: {e}")


import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv, dotenv_values
import os

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from .env file
supabase_url = dotenv_values().get("supabaseurl")
supabase_key = dotenv_values().get("SUPABASE_ANON_KEY")

# Initialize Supabase client
try:
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        client_initialized = True
    else:
        client_initialized = False
except Exception as e:
    client_initialized = False
    st.error(f"Failed to initialize Supabase client: {e}")

# --- Authentication --- #
def get_current_user():
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Attempt to get session from Supabase
    try:
        session_response = supabase.auth.get_session()
        print(f"Session Response: {session_response}") # Debugging line
        if session_response and session_response.session:
            st.session_state.user = session_response.session.user
            print(f"User from session: {st.session_state.user.email}") # Debugging line
        else:
            st.session_state.user = None
            print("No active session found.") # Debugging line
    except Exception as e:
        st.session_state.user = None
        print(f"Could not retrieve session: {e}") # Debugging line
    
    return st.session_state.user

def sign_up(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Sign up successful! Please check your email to confirm your account. You can now log in.")
            st.session_state.user = response.user
            st.session_state.session = response.session # Store the full session
        elif response.error:
            st.error(f"Sign up failed: {response.error.message}")
    except Exception as e:
        st.error(f"An unexpected error occurred during sign up: {e}")

def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            st.success("Logged in successfully!")
            st.session_state.user = response.user
            st.session_state.session = response.session # Store the full session
        elif response.error:
            st.error(f"Login failed: {response.error.message}")
    except Exception as e:
        st.error(f"An unexpected error occurred during login: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.session = None # Clear session on logout
        st.success("Logged out successfully!")
    except Exception as e:
        st.error(f"Error during sign out: {e}")

# --- Main App Layout --- #
st.title("Jungian Cognitive Function Test")

# --- Dev Mode: Skip Login --- #
# WARNING: This is for local development only.
# Set DEV_SKIP_LOGIN="true" in your .env file to bypass authentication.
DEV_SKIP_LOGIN = os.getenv("DEV_SKIP_LOGIN", "false").lower() == "true"

if DEV_SKIP_LOGIN:
    from types import SimpleNamespace
    # Create a mock user object that mimics the structure of a real Supabase user
    st.session_state.user = SimpleNamespace(email="dev-user@local.com", id="mock_user_id")
    st.session_state.session = SimpleNamespace() # Mock session object
    st.warning("DEV MODE: Skipping login. You are logged in as a mock user.")

# Get current user status on each run
# Prioritize session_state, then try to get from Supabase
if 'user' not in st.session_state:
    st.session_state.user = None
if 'session' not in st.session_state:
    st.session_state.session = None

# If user is not in session_state, try to get it from Supabase
if st.session_state.user is None and client_initialized:
    try:
        session_response = supabase.auth.get_session()
        print(f"Attempting to get session from Supabase: {session_response}") # Debugging
        if session_response and session_response.session:
            st.session_state.user = session_response.session.user
            st.session_state.session = session_response.session
            print(f"User from Supabase session: {st.session_state.user.email}") # Debugging
        else:
            print("No active session from Supabase.") # Debugging
    except Exception as e:
        print(f"Error getting session from Supabase: {e}") # Debugging

current_user = st.session_state.user

# Sidebar for navigation and auth status
st.sidebar.title("Navigation")

if current_user:
    st.sidebar.write(f"Logged in as: {current_user.email}")
    if st.sidebar.button("Logout"): 
        sign_out()
        st.rerun()
else:
    st.sidebar.write("Not logged in.")
    with st.sidebar.form("auth_form"):
        st.subheader("Login / Sign Up")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Login"):
                sign_in(email, password)
                st.rerun()
        with col2:
            if st.form_submit_button("Sign Up"):
                sign_up(email, password)
                st.rerun()

page = st.sidebar.radio("Go to", ["Home", "Moderator Tools", "Take Test", "Question Bank"])

if page == "Home":
    st.header("Welcome")
    st.write("This application is under construction.")
    if client_initialized:
        st.success("Successfully connected to Supabase!")
    else:
        st.error("Failed to connect to Supabase. Please check your credentials.")

elif page == "Moderator Tools":
    st.header("Moderator Tools")
    if current_user: # Protect this page
        st.subheader("Add New Question")

        with st.form("new_question_form"):
            question_text = st.text_area("Question", key="question_text")
            a_answer = st.text_input("Option A Answer", key="a_answer")
            b_answer = st.text_input("Option B Answer", key="b_answer")
            a_function = st.text_input("Option A Function (e.g., Fe, Ne)", key="a_function")
            b_function = st.text_input("Option B Function (e.g., Fi, Ni)", key="b_function")
            question_dimension = st.selectbox("Question Dimension", ["between_functions", "within_functions"], key="question_dimension")
            question_type = st.selectbox("Question Type", ["scenario_based", "self_reported", "interests"], key="question_type")
            additional_info = st.text_area("Additional Info (Optional)", key="additional_info")

            submitted = st.form_submit_button("Add Question")

            if submitted:
                if client_initialized:
                    try:
                        response = supabase.table("questions").insert({
                            "question": question_text,
                            "status": "draft",
                            "a_function": a_function,
                            "b_function": b_function,
                            "a_answer": a_answer,
                            "b_answer": b_answer,
                            "question_dimension": question_dimension,
                            "question_type": question_type,
                            "additional_info": additional_info
                        }).execute()
                        st.success("Question added successfully!")
                        st.json(response.data) # Display response data for debugging
                    except Exception as e:
                        st.error(f"Error adding question: {e}")
                else:
                    st.error("Supabase client not initialized. Cannot add question.")
        
            else:
                st.warning("Please log in to access Moderator Tools.")

elif page == "Take Test":
    st.header("Take the Test")

    # Check if a test was just finished
    if st.session_state.get('test_finished'):
        st.subheader("Your Test Results")
        
        scores = st.session_state.get('final_scores', {})
        
        # --- Table 1: Ranked Single-Letter Functions ---
        st.write("#### Ranked Primary Functions")
        primary_functions = {key: val for key, val in scores.items() if len(key) == 1}
        
        if primary_functions:
            import pandas as pd
            # Sort the functions by score
            ranked_df = pd.DataFrame(
                list(primary_functions.items()), 
                columns=['Function', 'Score']
            ).sort_values('Score', ascending=False).reset_index(drop=True)
            st.table(ranked_df)
        else:
            st.write("No primary function scores were recorded.")

        # --- Table 2: Between-Functions Comparison ---
        st.write("#### Function Dichotomies")
        dichotomy_pairs = [('Fe', 'Fi'), ('Ne', 'Ni'), ('Se', 'Si'), ('Te', 'Ti')]
        
        comparison_data = []
        for func1, func2 in dichotomy_pairs:
            comparison_data.append({
                f"{func1} Score": scores.get(func1, 0),
                "vs": f"{func1} vs {func2}",
                f"{func2} Score": scores.get(func2, 0)
            })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            # Reorder columns for clarity
            comparison_df = comparison_df[[
                f"{d[0]} Score" for d in dichotomy_pairs] + 
                ['vs'] + 
                [f"{d[1]} Score" for d in dichotomy_pairs]
            ]
            # A bit of a hack to get the columns in the right order for display
            # Let's build it more robustly
            display_df_data = []
            for func1, func2 in dichotomy_pairs:
                 display_df_data.append({
                     'Function 1': func1,
                     'Score 1': scores.get(func1, 0),
                     '': 'vs',
                     'Function 2': func2,
                     'Score 2': scores.get(func2, 0)
                 })
            display_df = pd.DataFrame(display_df_data)
            st.table(display_df)
        else:
            st.write("No detailed function scores were recorded.")


        if st.button("Take Test Again"):
            # Clear the results and test state to start over
            st.session_state.test_finished = False
            st.session_state.final_scores = {}
            st.session_state.current_question_index = 0
            st.session_state.user_answers = {}
            st.rerun()
        
    else:
        # --- Test taking logic starts here ---
        if 'questions' not in st.session_state or 'current_question_index' not in st.session_state:
            try:
                # Fetch approved questions
                response = supabase.table("questions").select("*").eq("status", "approved").execute()
                st.session_state.questions = response.data
                st.session_state.current_question_index = 0
                st.session_state.user_answers = {} # To store user's answers
            except Exception as e:
                st.error(f"Error fetching questions: {e}")
                st.session_state.questions = []

        questions = st.session_state.get('questions', [])

        if not questions:
            st.info("No approved questions available yet. Please add some via Moderator Tools.")
        else:
            total_questions = len(questions)
            current_index = st.session_state.current_question_index
            current_question = questions[current_index]

            # Progress Bar
            progress_percentage = (current_index + 1) / total_questions
            st.progress(progress_percentage, text=f"Question {current_index + 1} of {total_questions}")

            st.subheader(f"Question {current_index + 1}")
            st.write(current_question['question'])

            # Randomize A and B options
            options = [
                {"text": current_question['a_answer'], "function": current_question['a_function'], "type": "A"},
                {"text": current_question['b_answer'], "function": current_question['b_function'], "type": "B"}
            ]
            import random
            # Use a seed based on the question ID to ensure consistent shuffling for results calculation
            random.seed(current_question['id'])
            random.shuffle(options)

            # Display options
            selected_option = st.radio(
                "Choose an option:",
                [
                    f"A: {options[0]['text']}",
                    f"B: {options[1]['text']}",
                    "Neither",
                    "Both"
                ],
                key=f"question_{current_index}"
            )

            # Store selected answer
            st.session_state.user_answers[current_index] = selected_option

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Previous", disabled=(current_index == 0)):
                    st.session_state.current_question_index -= 1
                    st.rerun()
            with col2:
                if st.button("Next", disabled=(current_index == total_questions - 1)):
                    st.session_state.current_question_index += 1
                    st.rerun()
                elif current_index == total_questions - 1 and st.button("Finish Test"):
                    # --- Results Calculation ---
                    scores = {
                        "Fe": 0, "Fi": 0, "Ne": 0, "Ni": 0,
                        "Se": 0, "Si": 0, "Te": 0, "Ti": 0,
                        "F": 0, "T": 0, "N": 0, "S": 0
                    }
                    
                    for i, answer in st.session_state.user_answers.items():
                        q = st.session_state.questions[i]
                        functions_to_score = []

                        if answer == "Both":
                            functions_to_score.append(q['a_function'])
                            functions_to_score.append(q['b_function'])
                        elif answer != "Neither":  # Handles A or B choices
                            q_options = [
                                {"text": q['a_answer'], "function": q['a_function']},
                                {"text": q['b_answer'], "function": q['b_function']}
                            ]
                            # Re-shuffle with the same seed to find the chosen function
                            random.seed(q['id'])
                            random.shuffle(q_options)

                            chosen_text = answer.split(": ", 1)[1]
                            if q_options[0]['text'] == chosen_text:
                                functions_to_score.append(q_options[0]['function'])
                            elif q_options[1]['text'] == chosen_text:
                                functions_to_score.append(q_options[1]['function'])

                        # Process the scoring
                        for func in functions_to_score:
                            if not func: continue # Skip if function is empty string or None

                            # Score the specific function (e.g., Fe, Ni, or F, N)
                            if func in scores:
                                scores[func] += 1
                            
                            # If it's a detailed function (Fe, Ni), score the general one too (F, N)
                            if len(func) > 1 and func[0] in scores:
                                scores[func[0]] += 1

                    # Set state to show results
                    st.session_state.test_finished = True
                    st.session_state.final_scores = scores
                    st.rerun()

elif page == "Question Bank":
    st.header("Question Bank")
    st.write("Users can view, upvote, downvote, and comment on questions here.")

    if current_user:
        st.subheader("Manage Questions")
        try:
            response = supabase.table("questions").select("*").execute()
            questions = response.data
        except Exception as e:
            st.error(f"Error fetching questions: {e}")
            questions = []

        if questions:
            for q in questions:
                st.write(f"**Question:** {q['question']}")
                st.write(f"**Dimension:** {q.get('question_dimension', 'N/A')}") # Use .get for safety
                st.write(f"**Status:** {q['status']}")
                new_status = st.selectbox(
                    "Update Status",
                    ["draft", "approved", "rejected"],
                    index=["draft", "approved", "rejected"].index(q['status']),
                    key=f"status_{q['id']}"
                )
                if new_status != q['status']:
                    try:
                        supabase.table("questions").update({"status": new_status}).eq("id", q['id']).execute()
                        st.success(f"Question {q['id']} status updated to {new_status}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating question status: {e}")
                st.divider()



