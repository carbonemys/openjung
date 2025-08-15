
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv, dotenv_values
import os
import random

def calculate_mbti_analysis(scores, attitude_scores):
    analysis = {}
    mbti_type = ""
    total_strength = 0
    preference_count = 0

    def get_strength_label(strength_val):
        if strength_val > 0.75:
            return "Strong"
        elif strength_val > 0.60:
            return "Moderate"
        else:
            return "Weak"

    # I/E
    i_score = attitude_scores.get('i', 0)
    e_score = attitude_scores.get('e', 0)
    total_ie = i_score + e_score
    if total_ie > 0:
        i_percent = i_score / total_ie
        e_percent = e_score / total_ie
        preference = 'I' if i_percent > e_percent else 'E'
        strength = abs(i_percent - e_percent)
        analysis['I/E'] = {
            'positive': 'Introversion',
            'negative': 'Extraversion',
            'opposite': 'E',
            'percentage': i_percent,
            'preference': preference,
            'strength': f"{strength:.0%}",
            'strength_label': get_strength_label(max(i_percent, e_percent))
        }
        mbti_type += preference
        total_strength += max(i_percent, e_percent)
        preference_count += 1

    # N/S
    n_score = scores.get('N', 0)
    s_score = scores.get('S', 0)
    total_ns = n_score + s_score
    if total_ns > 0:
        n_percent = n_score / total_ns
        s_percent = s_score / total_ns
        preference = 'N' if n_percent > s_percent else 'S'
        strength = abs(n_percent - s_percent)
        analysis['N/S'] = {
            'positive': 'Intuition',
            'negative': 'Sensing',
            'opposite': 'S',
            'percentage': n_percent,
            'preference': preference,
            'strength': f"{strength:.0%}",
            'strength_label': get_strength_label(max(n_percent, s_percent))
        }
        mbti_type += preference
        total_strength += max(n_percent, s_percent)
        preference_count += 1

    # T/F
    t_score = scores.get('T', 0)
    f_score = scores.get('F', 0)
    total_tf = t_score + f_score
    if total_tf > 0:
        t_percent = t_score / total_tf
        f_percent = f_score / total_tf
        preference = 'T' if t_percent > f_percent else 'F'
        strength = abs(t_percent - f_percent)
        analysis['T/F'] = {
            'positive': 'Thinking',
            'negative': 'Feeling',
            'opposite': 'F',
            'percentage': t_percent,
            'preference': preference,
            'strength': f"{strength:.0%}",
            'strength_label': get_strength_label(max(t_percent, f_percent))
        }
        mbti_type += preference
        total_strength += max(t_percent, f_percent)
        preference_count += 1

    # J/P
    # Determine the dominant function from all detailed functions
    all_functions = {
        'Te': scores.get('Te', 0), 'Ti': scores.get('Ti', 0),
        'Fe': scores.get('Fe', 0), 'Fi': scores.get('Fi', 0),
        'Ne': scores.get('Ne', 0), 'Ni': scores.get('Ni', 0),
        'Se': scores.get('Se', 0), 'Si': scores.get('Si', 0)
    }
    
    # Find the function with the highest score
    # In case of a tie, the first one encountered will be chosen, which is an acceptable simplification
    dominant_function = max(all_functions, key=all_functions.get)

    # Determine J/P based on the dominant function's type (Rational/Judging vs. Irrational/Perceiving)
    # Rational/Judging functions: T and F
    # Irrational/Perceiving functions: N and S
    if dominant_function[0] in ['T', 'F']:
        preference = 'J'
    else: # N or S
        preference = 'P'

    # Calculate a 'strength' for J/P based on the dominance of that function type
    judging_score = scores.get('T', 0) + scores.get('F', 0)
    perceiving_score = scores.get('N', 0) + scores.get('S', 0)
    total_jp = judging_score + perceiving_score

    if total_jp > 0:
        j_percent = judging_score / total_jp
        p_percent = perceiving_score / total_jp
        jp_strength = abs(j_percent - p_percent)
        percentage = j_percent
    else:
        jp_strength = 0
        percentage = 0.5 # Default to neutral if no scores

    analysis['J/P'] = {
        'positive': 'Judging',
        'negative': 'Perceiving',
        'opposite': 'P' if preference == 'J' else 'J',
        'percentage': percentage,
        'preference': preference,
        'strength': f"{jp_strength:.0%}",
        'strength_label': get_strength_label(max(j_percent, p_percent))
    }
    mbti_type += preference
    total_strength += max(j_percent, p_percent)
    preference_count += 1

    # Overall strength
    overall_strength_value = total_strength / preference_count if preference_count > 0 else 0
    analysis['overall_strength'] = get_strength_label(overall_strength_value)
    analysis['mbti_type'] = mbti_type

    return analysis

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
        # The session object contains user, access_token, etc.
        st.session_state.session = response.session
        st.success("Logged in successfully!")
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
    except Exception as e:
        st.error(f"Error during sign out: {e}")
    finally:
        # Always clear the session state as a fallback
        st.session_state.session = None
        st.session_state.user = None
        st.session_state.user_role = None
        st.success("Logged out successfully!")

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
    st.session_state.session = None # No session for mock user
    st.session_state.user_role = 'moderator' # Assume dev user is a mod
    st.warning("DEV MODE: Skipping login. You are logged in as a mock user.")

# --- Authentication & Session Management ---
# On every script run, re-authenticate the Supabase client if a session exists in state.
if 'session' in st.session_state and st.session_state.session:
    try:
        # Use the stored session to re-authenticate the client
        supabase.auth.set_session(
            st.session_state.session.access_token, 
            st.session_state.session.refresh_token
        )
        # After setting the session, get the user details
        user_response = supabase.auth.get_user()
        st.session_state.user = user_response.user
        
        # Fetch user role from profiles table
        profile_response = supabase.table("profiles").select("role").eq("id", st.session_state.user.id).execute()
        if profile_response.data:
            st.session_state.user_role = profile_response.data[0]['role']
        else:
            # This handles cases where a user exists in auth but not profiles
            st.session_state.user_role = 'user'
            supabase.table("profiles").insert({"id": st.session_state.user.id, "role": "user"}).execute()

    except Exception as e:
        # This can happen if the token is expired or invalid
        st.error("Your session has expired. Please log in again.")
        st.session_state.user = None
        st.session_state.session = None
        st.session_state.user_role = None
        print(f"Error setting session: {e}")

# Initialize variables for the rest of the app
current_user = st.session_state.get('user')
current_role = st.session_state.get('user_role')

# --- Sidebar ---
st.sidebar.title("Navigation")

# Initialize page state if it doesn't exist
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# --- Navigation Buttons ---
# A function to set the page, for cleaner button code
def set_page(page_name):
    st.session_state.page = page_name

# Use columns for a more compact layout if desired, or just buttons
if st.sidebar.button("Home", use_container_width=True):
    set_page("Home")
if st.sidebar.button("Take Test", use_container_width=True):
    set_page("Take Test")
if st.sidebar.button("Question Bank", use_container_width=True):
    set_page("Question Bank")

# Conditional Moderator Tools button
if current_user:
    if st.sidebar.button("Submit Question", use_container_width=True):
        set_page("Submit Question")
if current_role == 'moderator':
    if st.sidebar.button("Edit Questions", use_container_width=True):
        set_page("Edit Questions")

st.sidebar.divider()

# --- Authentication Section ---
if current_user:
    st.sidebar.write(f"Logged in as: {current_user.email}")
    if st.sidebar.button("Logout", use_container_width=True):
        sign_out()
        st.rerun()
else:
    st.sidebar.info("You are browsing as a guest. Login to vote or submit questions.")
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

page = st.session_state.page

if page == "Home":
    st.header("Open-source community driven Jung cognitive type test")
    st.write("""
    Philosophy: 
    - Strictly based on Jung's works
    - Open source, free and ad-free forever
    - Community questions with references to original works
    - Addressing shortcomings of overlapping or weak types
    """)
    if st.button("Take the Test Now!"):
        set_page("Take Test")
        st.rerun()

    if client_initialized:
        st.success("Successfully connected to Supabase!")
    else:
        st.error("Failed to connect to Supabase. Please check your credentials.")

elif page == "Take Test":
    st.header("Take the Test")

    # Check if a test was just finished
    if st.session_state.get('test_finished'):
        st.subheader("Your Test Results")
        
        scores = st.session_state.get('final_scores', {})
        attitude_scores = st.session_state.get('attitude_scores', {})

        # --- Attitude Chart ---
        st.write("#### Attitude: Introversion (i) vs. Extraversion (e)")
        attitude_data = {'Introversion (i)': attitude_scores.get('i', 0), 'Extraversion (e)': attitude_scores.get('e', 0)}
        if any(attitude_data.values()):
            import pandas as pd
            import altair as alt

            attitude_df = pd.DataFrame(list(attitude_data.items()), columns=['Attitude', 'Score'])

            attitude_chart = alt.Chart(attitude_df).mark_bar().encode(
                x='Score:Q',
                y='Attitude:N',
                color=alt.Color('Attitude:N', scale=alt.Scale(range=['#ff7f0e', '#1f77b4']))
            ).properties(
                title='Attitude Balance'
            )
            st.altair_chart(attitude_chart, use_container_width=True)
        else:
            st.write("No attitude scores were recorded.")
        
        # --- Chart 1: Ranked Single-Letter Functions ---
        st.write("#### Ranked Primary Functions")
        primary_functions = {key: val for key, val in scores.items() if len(key) == 1}
        
        if primary_functions:
            import pandas as pd
            import altair as alt

            ranked_df = pd.DataFrame(
                list(primary_functions.items()), 
                columns=['Function', 'Score']
            ).sort_values('Score', ascending=False)

            # Map single letters to full names for the chart
            function_map = {
                'N': 'Intuition (N)',
                'S': 'Sensing (S)',
                'T': 'Thinking (T)',
                'F': 'Feeling (F)'
            }
            ranked_df['Function'] = ranked_df['Function'].map(function_map)

            bar = alt.Chart(ranked_df).mark_bar().encode(
                x=alt.X('Score', type='quantitative'),
                y=alt.Y('Function', type='nominal', sort='-x')
            )
            
            text = bar.mark_text(
                align='left',
                baseline='middle',
                dx=3  # Nudges text to right so it doesn't overlap
            ).encode(
                text='Score:Q'
            )

            chart = (bar + text).properties(title='Primary Function Scores')
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("No primary function scores were recorded.")

        # --- Chart 2: Function Dichotomies (Diverging Bar Chart) ---
        st.write("#### Function Dichotomies - Relative")
        dichotomy_pairs = [('Te', 'Ti', 'Thinking'), ('Fe', 'Fi', 'Feeling'), ('Ne', 'Ni', 'Intuition'), ('Se', 'Si', 'Sensing')]
        
        chart_data = []
        for func1, func2, name in dichotomy_pairs:
            score1 = scores.get(func1, 0)
            score2 = scores.get(func2, 0)
            chart_data.append({'pair': name, 'function': func1, 'score': score1, 'abs_score': score1})
            chart_data.append({'pair': name, 'function': func2, 'score': -score2, 'abs_score': score2})

        if chart_data:
            import pandas as pd
            import altair as alt

            df = pd.DataFrame(chart_data)
            y_axis_order = ['Thinking', 'Feeling', 'Intuition', 'Sensing']

            bar = alt.Chart(df).mark_bar().encode(
                x='score:Q',
                y=alt.Y('pair:N', sort=y_axis_order),
                color=alt.Color('function:N',
                                scale=alt.Scale(
                                    domain=['Fe', 'Fi', 'Ne', 'Ni', 'Se', 'Si', 'Te', 'Ti'],
                                    range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
                                ))
            )

            text = alt.Chart(df).mark_text(
                align='left',
                baseline='middle',
                dx=3
            ).encode(
                x='score:Q',
                y=alt.Y('pair:N', sort=y_axis_order),
                text='function:N'
            )

            chart = (bar + text).properties(title='Function Pair Balances')
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("No detailed function scores were recorded.")

        # --- Chart 3: Blended Function Dichotomies ---
        st.write("#### Function dichotomies - Weighed")
        
        blended_chart_data = []
        for func1, func2, name in dichotomy_pairs:
            parent_func = func1[0]
            
            score1 = scores.get(func1, 0) * scores.get(parent_func, 0)
            score2 = scores.get(func2, 0) * scores.get(parent_func, 0)
            
            blended_chart_data.append({'pair': name, 'function': func1, 'score': score1, 'abs_score': score1})
            blended_chart_data.append({'pair': name, 'function': func2, 'score': -score2, 'abs_score': score2})

        if blended_chart_data:
            import pandas as pd
            import altair as alt

            df_blended = pd.DataFrame(blended_chart_data)
            y_axis_order = ['Thinking', 'Feeling', 'Intuition', 'Sensing']

            bar = alt.Chart(df_blended).mark_bar().encode(
                x='score:Q',
                y=alt.Y('pair:N', sort=y_axis_order),
                color=alt.Color('function:N',
                                scale=alt.Scale(
                                    domain=['Fe', 'Fi', 'Ne', 'Ni', 'Se', 'Si', 'Te', 'Ti'],
                                    range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
                                ))
            )

            text = alt.Chart(df_blended).mark_text(
                align='left',
                baseline='middle',
                dx=3
            ).encode(
                x='score:Q',
                y=alt.Y('pair:N', sort=y_axis_order),
                text='function:N'
            )

            blended_chart = (bar + text).properties(title='Blended Function Pair Balances (Weighted by Primary Function)')
            st.altair_chart(blended_chart, use_container_width=True)
        else:
            st.write("No blended function scores could be calculated.")


        # --- MBTI Preference Analysis ---
        st.write("#### MBTI Preference Analysis")
        mbti_analysis = calculate_mbti_analysis(scores, attitude_scores)
        
        st.subheader(f"Your Type: {mbti_analysis.get('mbti_type', '----')}")
        st.write(f"**Overall Strength:** {mbti_analysis.get('overall_strength', 'Unknown')}")
        st.divider()

        for letter, data in mbti_analysis.items():
            if '/' not in letter: continue
            st.write(f"**{data['positive']} ({letter.split('/')[0]}) vs. {data['negative']} ({letter.split('/')[1]})**")
            st.progress(data['percentage'])
            st.write(f"{data['strength']} preference for **{data['preference']}** ({data.get('strength_label', 'Weak')})")


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
            st.info("No approved questions available yet. Please check back later.")
        else:
            total_questions = len(questions)
            current_index = st.session_state.current_question_index
            current_question = questions[current_index]

            # Progress Bar
            progress_percentage = (current_index + 1) / total_questions
            st.progress(progress_percentage, text=f"Question {current_index + 1} of {total_questions}")

            st.subheader(f"Question {current_index + 1}")
            st.write(current_question['question'])

            # Display options
            selected_option = st.radio(
                "Choose an option:",
                [
                    f"A: {current_question['a_answer']}",
                    f"B: {current_question['b_answer']}",
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
                    attitude_scores = {"i": 0, "e": 0}
                    
                    for i, answer in st.session_state.user_answers.items():
                        q = st.session_state.questions[i]
                        functions_to_score = []

                        if answer == "Both":
                            functions_to_score.append(q['a_function'])
                            functions_to_score.append(q['b_function'])
                        elif answer.startswith("A:"):
                            functions_to_score.append(q['a_function'])
                        elif answer.startswith("B:"):
                            functions_to_score.append(q['b_function'])

                        # Process the scoring
                        for func in functions_to_score:
                            if not func: continue # Skip if function is empty string or None

                            # Score the specific function (e.g., Fe, Ni, or F, N)
                            if func in scores:
                                scores[func] += 1
                            
                            # If it's a detailed function (Fe, Ni), score the general one too (F, N)
                            if len(func) > 1 and func[0] in scores:
                                scores[func[0]] += 1
                            
                            # Score attitude (i vs e) for within_functions questions
                            if q.get('question_dimension') == 'within_functions' and len(func) > 1:
                                attitude = func[1]
                                if attitude in attitude_scores:
                                    attitude_scores[attitude] += 1

                    # Set state to show results
                    st.session_state.test_finished = True
                    st.session_state.final_scores = scores
                    st.session_state.attitude_scores = attitude_scores
                    st.rerun()

elif page == "Submit Question":
    st.header("Submit a New Question")
    if current_user: # Protect this page
        st.write("Submit your question for review. It will be added to the question bank with a 'draft' status.")
        with st.form("new_question_form", clear_on_submit=True):
            question_text = st.text_area("Question", key="question_text")
            a_answer = st.text_input("Option A Answer", key="a_answer")
            b_answer = st.text_input("Option B Answer", key="b_answer")
            a_function = st.text_input("Option A Function (e.g., Fe, Ne)", key="a_function")
            b_function = st.text_input("Option B Function (e.g., Fi, Ni)", key="b_function")
            question_dimension = st.selectbox("Question Dimension", ["between_functions", "within_functions"], key="question_dimension")
            question_type = st.selectbox("Question Type", ["scenario_based", "self_reported", "interests"], key="question_type")
            additional_info = st.text_area("Additional Info (Optional)", key="additional_info")

            submitted = st.form_submit_button("Submit for Review")

            if submitted:
                if client_initialized:
                    try:
                        response = supabase.table("questions").insert({
                            "question": question_text,
                            "status": "draft", # All submissions are drafts
                            "a_function": a_function,
                            "b_function": b_function,
                            "a_answer": a_answer,
                            "b_answer": b_answer,
                            "question_dimension": question_dimension,
                            "question_type": question_type,
                            "additional_info": additional_info,
                            "submitted_by": current_user.id # Track who submitted it
                        }).execute()
                        st.success("Question submitted successfully for review!")
                    except Exception as e:
                        st.error(f"Error submitting question: {e}")
                else:
                    st.error("Supabase client not initialized. Cannot submit question.")
    else:
        st.warning("Please log in to submit a question.")

elif page == "Edit Questions":
    st.header("Edit Questions")
    if current_role == 'moderator': # PROTECTED: Moderators only
        try:
            # Fetch all questions for editing
            response = supabase.table("questions").select("*").order("id", desc=True).execute()
            questions = response.data
        except Exception as e:
            st.error(f"Error fetching questions: {e}")
            questions = []

        if not questions:
            st.info("No questions found to edit.")
            st.stop()

        # Display Questions in a DataFrame for context
        import pandas as pd
        df = pd.DataFrame(questions)
        display_columns = [
            'id', 'question', 'status', 'upvotes', 'downvotes', 'question_dimension',
            'a_answer', 'a_function', 'b_answer', 'b_function',
        ]
        display_columns = [col for col in display_columns if col in df.columns]
        st.dataframe(df[display_columns])

        st.divider()

        # Edit Question Form
        st.subheader("Edit a Question")
        questions_dict = {q['id']: q for q in questions}
        question_ids = [q['id'] for q in questions]
        # Format IDs with question text for easier selection
        question_options = {q['id']: f"{q['question'][:60]}... ({q['status']})" for q in questions}
        selected_id = st.selectbox("Select Question to Edit", options=question_ids, format_func=lambda x: question_options[x])

        if selected_id:
            selected_question = questions_dict[selected_id]
            with st.form(key=f"edit_form_{selected_id}"):
                st.write(f"Editing Question ID: {selected_question['id']}")

                status_options = ["draft", "approved", "rejected", "retired", "draft"]
                current_status_index = status_options.index(selected_question.get('status', 'draft'))
                dim_options = ["between_functions", "within_functions"]
                current_dim_index = dim_options.index(selected_question.get('question_dimension', 'between_functions'))

                question_text = st.text_area("Question", value=selected_question.get('question', ''))
                status = st.selectbox("Status", options=status_options, index=current_status_index)
                question_dimension = st.selectbox("Dimension", options=dim_options, index=current_dim_index)
                a_answer = st.text_input("Option A Answer", value=selected_question.get('a_answer', ''))
                a_function = st.text_input("Option A Function", value=selected_question.get('a_function', ''))
                b_answer = st.text_input("Option B Answer", value=selected_question.get('b_answer', ''))
                b_function = st.text_input("Option B Function", value=selected_question.get('b_function', ''))
                additional_info = st.text_area("Additional Info", value=selected_question.get('additional_info', ''))

                col1, col2 = st.columns(2)
                with col1:
                    update_button = st.form_submit_button("Update Question")
                with col2:
                    # Make delete more prominent and dangerous
                    delete_button = st.form_submit_button("⚠️ Delete Question", type="primary")

                if update_button:
                    try:
                        update_data = {
                            "question": question_text,
                            "status": status,
                            "question_dimension": question_dimension,
                            "a_answer": a_answer,
                            "a_function": a_function,
                            "b_answer": b_answer,
                            "b_function": b_function,
                            "additional_info": additional_info
                        }
                        
                        supabase.table("questions").update(update_data).eq("id", selected_id).execute()
                        st.success(f"Successfully updated Question ID: {selected_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update question: {e}")

                if delete_button:
                    # Add a confirmation step to prevent accidental deletion
                    if st.checkbox(f"Confirm deletion of question {selected_id}", key=f"delete_confirm_{selected_id}"):
                        try:
                            supabase.table("questions").delete().eq("id", selected_id).execute()
                            st.success(f"Successfully deleted Question ID: {selected_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete question: {e}")
                    else:
                        st.warning("Please check the confirmation box to delete.")

    else:
        st.error("You do not have permission to access this page.")
        st.info("Only moderators can edit questions.")


elif page == "Question Bank":
    st.header("Question Bank")
    st.write("Here you can view, vote, and comment on questions.")

    st.subheader("Filter and Order Questions")
    
    # --- Filtering and Ordering UI ---
    col1, col2 = st.columns(2)
    with col1:
        # Sort by 'created_at', 'upvotes', 'downvotes'
        order_by = st.selectbox(
            "Order by",
            options=['created_at', 'upvotes', 'downvotes'],
            format_func=lambda x: x.replace('_', ' ').capitalize()
        )
        order_asc = st.checkbox("Ascending", False) # False = descending by default

    with col2:
        # Filter by status
        selected_statuses = st.multiselect(
            "Filter by Status",
            options=['approved', 'pending', 'rejected', 'retired', 'draft'],
            default=['approved', 'pending'] # Default to most common view
        )

    try:
        # Base query
        query = supabase.table("questions").select("*, comments(*, profiles(role))")

        # Apply filters
        if selected_statuses:
            query = query.in_("status", selected_statuses)
        else:
            # If nothing is selected, show nothing, as it's less confusing than showing all.
            st.info("Select at least one status to see questions.")
            st.stop()

        # Apply ordering
        query = query.order(order_by, desc=(not order_asc))
        
        response = query.execute()
        questions = response.data
    except Exception as e:
        st.error(f"Error fetching questions: {e}")
        questions = []

    if not questions:
        st.info("No questions match your current filter settings.")
        st.stop()

    # Fetch all votes by the current user to disable voting buttons
    user_votes = {}
    if current_user:
        try:
            vote_response = supabase.table("votes").select("question_id, vote_type").eq("user_id", current_user.id).execute()
            # Create a dictionary for quick lookup: {question_id: vote_type}
            user_votes = {v['question_id']: v['vote_type'] for v in vote_response.data}
        except Exception as e:
            st.error(f"Error fetching your votes: {e}")

    # Initialize session state for voted questions to prevent re-voting
    if 'voted_on' not in st.session_state:
        st.session_state.voted_on = {}

    for q in questions:
        # Use an expander for each question to keep the UI clean
        with st.expander(f"{q['question']} ({q['status'].capitalize()}) | 👍 {q.get('upvotes', 0)} 👎 {q.get('downvotes', 0)}", expanded=False):
            st.write(f"**Dimension:** {q.get('question_dimension', 'N/A')}")
            st.write(f"**A:** {q.get('a_answer', 'N/A')} ({q.get('a_function', 'N/A')})")
            st.write(f"**B:** {q.get('b_answer', 'N/A')} ({q.get('b_function', 'N/A')})")
            if q.get('additional_info'):
                st.info(f"**Additional Info:** {q['additional_info']}")

            # --- Voting Section ---
            col1, col2, col3 = st.columns([1, 1, 5])
            
            # Check if the user has already voted on this question
            has_voted = q['id'] in user_votes
            vote_disabled = not current_user or has_voted

            with col1:
                if st.button(f"👍 ({q.get('upvotes', 0)})", key=f"up_{q['id']}", disabled=vote_disabled, help="You must be logged in to vote, and can only vote once."):
                    try:
                        # Increment the upvote count in the questions table
                        supabase.rpc('increment_upvotes', {'question_id_to_update': q['id']}).execute()
                        # Record the vote in the votes table
                        supabase.table('votes').insert({
                            'user_id': current_user.id,
                            'question_id': q['id'],
                            'vote_type': 'up'
                        }).execute()
                        # Update local state to disable button immediately
                        user_votes[q['id']] = 'up'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error upvoting: {e}")
            with col2:
                if st.button(f"👎 ({q.get('downvotes', 0)})", key=f"down_{q['id']}", disabled=vote_disabled, help="You must be logged in to vote, and can only vote once."):
                    try:
                        # Increment the downvote count in the questions table
                        supabase.rpc('increment_downvotes', {'question_id_to_update': q['id']}).execute()
                        # Record the vote in the votes table
                        supabase.table('votes').insert({
                            'user_id': current_user.id,
                            'question_id': q['id'],
                            'vote_type': 'down'
                        }).execute()
                        # Update local state to disable button immediately
                        user_votes[q['id']] = 'down'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error downvoting: {e}")
            
            if has_voted and current_user:
                st.caption(f"You have already voted on this question.")


            # --- Comments Section ---
            st.markdown("---")
            st.subheader("Comments")
            comments = sorted(q.get('comments', []), key=lambda c: c['created_at'], reverse=True)
            if comments:
                for comment in comments:
                    commenter_role = "User"
                    if comment.get('profiles') and comment['profiles'].get('role'):
                        commenter_role = comment['profiles']['role'].capitalize()
                    st.markdown(f"**{commenter_role}** ({comment['created_at']}):")
                    st.markdown(f"> {comment['comment_text']}")
            else:
                st.write("No comments yet.")

            # Show comment form ONLY to logged-in users
            if current_user:
                with st.form(key=f"comment_form_{q['id']}", clear_on_submit=True):
                    comment_text = st.text_area("Write a comment...", key=f"comment_text_{q['id']}")
                    submit_comment = st.form_submit_button("Post Comment")
                    if submit_comment and comment_text:
                        try:
                            supabase.table("comments").insert({
                                "question_id": q['id'],
                                "user_id": current_user.id,
                                "comment_text": comment_text
                            }).execute()
                            st.success("Comment posted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error posting comment: {e}")
            # Show message to guests
            else:
                st.info("Log in to vote or post a comment.")




