import streamlit as st
from src.api.model_integration import stream_response
from src.utils.prompt_templates import (
    get_translation_prompt,
    get_sentiment_analysis_prompt,
    get_cultural_reference_explanation_prompt,
    get_interactive_translation_prompt,
    get_grammar_focus,
    get_comms_focus,
)
from config.config import Config


def setup_page():
    """
    Sets up the page with custom styles and page configuration.
    """
    st.set_page_config(
        page_title="Advanced Translator",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        :root {
            --llama-color: #4e8cff;
            --llama-color-light: #e6f0ff;
            --llama-color-dark: #1a3a6c;
            --llama-gradient-start: #4e54c8;
            --llama-gradient-end: #8f94fb;
        }
        .stApp {
            margin: auto;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
        }
        .logo-container img {
            width: 150px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    setup_page()

    # Header section with title and subtitle
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 class="header-title">🦙 Translator</h1>
            <p class="header-subtitle">Powered by IBM Watson X language models</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Meta logo
    st.markdown(
        """
        <div class="logo-container">
            <img src="https://www.translatedright.com/wp-content/uploads/2021/10/why-you-shouldnt-use-google-translate-for-business-1-scaled-2560x1280.jpg" alt="Translation Logo">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Remove the Llama image display

    # Sidebar for settings
    with st.sidebar:
        st.title("🦙 Settings")
        
        # Warn if IBM_MODEL_ID is set (overrides dropdown)
        import os
        ibm_model_id = os.getenv("IBM_MODEL_ID")
        if ibm_model_id:
            st.warning(
                f"⚠️ **Model Override Active**\n\n"
                f"Your `.env` file has `IBM_MODEL_ID={ibm_model_id}` set.\n\n"
                f"This overrides the dropdown selection. To use the dropdown, remove or comment out `IBM_MODEL_ID` in your `.env` file."
            )
        
        model_name = st.selectbox("Choose a model", Config.AVAILABLE_MODELS)

        decoding = st.selectbox("Choose Method", ["greedy", "sampling"])

        tokens = st.number_input("Choose Number of Tokens", value=200, min_value=100, max_value=1000) 

        temperature = st.slider("Choose Temperature", value=0.5, min_value=0.1, max_value=1.0, step=0.1)

        top_k = st.number_input("Choose Top K", value=50, min_value=10, max_value=100)

        top_p = st.slider("Choose Top P", value=0.5, min_value=0.1, max_value=1.0, step=0.1)

        params = {
            "decoding_method": decoding,
            "max_new_tokens": tokens,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p
        }

        langs = ["English", "Spanish", "French", "German", "Japanese"]

        source_lang = st.selectbox(
            "From", langs
        )

        selected = source_lang

        target_lang = st.selectbox(
            "To", [lang for lang in langs if lang != selected]
        )
        cultural_context = st.selectbox(
            "Context", ["Formal", "Casual", "Business", "Youth Slang", "Poetic"]
        )

    # Main container with border
    main_container = st.container(border=True)

    # sidebar results output
    session_results = {"session": None, "results": None, "score": None}

    with main_container:
        st.header("Enter Text for Translation and Analysis")
        text = st.text_area(
            "Text to translate",
            "It was the best of times, it was the worst of times...",
            height=200,
        )
        st.caption(f"Character count: {len(text)}")

        if st.button("Translate and Analyze", type="primary"):
            if text:
                # Tabs for different analysis types
                tab1, tab2, tab5, tab6 = st.tabs(
                    [
                        "Translation",
                        "Sentiment Analysis",
                        "Grammar Focus",
                        "Comms Companion"
                    ]
                )

                # Tab 1: Translation
                with tab1:
                    st.subheader("Result")
                    translation_container = st.empty()
                    translation_prompt = get_translation_prompt(
                        text, source_lang, target_lang, cultural_context
                    )
                    translation = stream_response(
                        [{"role": "user", "content": translation_prompt}],
                        translation_container,
                        model_name,
                        params
                    )
                    ret_trans = None
                    try: 
                        translation = [el for el in translation.split("\n") if el != "" and el != " " and "[" not in el]
                        ret_trans = translation
                        print("ret_trans_try: ", ret_trans["body"])
                    except Exception as e:
                        print("ret_trans_except: ", e)

                # Tab 2: Sentiment Analysis
                with tab2:
                    st.subheader("Sentiment Analysis")
                    sentiment_container = st.empty()
                    sentiment_prompt = get_sentiment_analysis_prompt(text, source_lang)
                    sentiment_analysis = stream_response(
                        [{"role": "user", "content": sentiment_prompt}],
                        sentiment_container,
                        model_name,
                        params
                    )
                    try: 
                        sentiment = [el for el in sentiment_analysis.split("\n") if el != "" and el != " " and "[" not in el]
                        ret_sentiment = sentiment
                        #print("sentiment output: ", sentiment)
                    except Exception as e:
                        print("error: ", e)
                        ret_sentiment = "Error: " + str(e)

                '''# Tab 3: Cultural References
                with tab3:
                    st.subheader("Cultural References")
                    cultural_container = st.empty()
                    cultural_prompt = get_cultural_reference_explanation_prompt(
                        text, source_lang, target_lang
                    )
                    cultural_references = stream_response(
                        [{"role": "user", "content": cultural_prompt}],
                        cultural_container,
                        model_name,
                    )
                '''

                '''# Tab 4: Interactive Translation
                with tab4:
                    st.subheader("Interactive Translation")
                    interactive_container = st.empty()
                    interactive_prompt = get_interactive_translation_prompt(
                        text, source_lang, target_lang
                    )
                    interactive_translation = stream_response(
                        [{"role": "user", "content": interactive_prompt}],
                        interactive_container,
                        model_name,
                    )'''

                # Tab 5: Grammar Focus
                with tab5:
                    st.subheader("Grammar")
                    grammar_container = st.empty()
                    grammar_prompt = get_grammar_focus(
                        text, source_lang, target_lang
                    )
                    grammar_analysis = stream_response(
                        [{"role": "user", "content": grammar_prompt}],
                        grammar_container,
                        model_name,
                        params
                    )
                    try:
                        grammar = [el for el in grammar_analysis.split("\n") if el != "" and el != " " and "[" not in el]
                        ret_grammar = grammar
                        print("grammar output: ", grammar)
                    except Exception as e:
                        print("error: ", e)
                        ret_grammar = "Error: " + str(e)

                # Tab 6: Teacher Comms Companion
                with tab6:
                    st.subheader("Companion")
                    comms_container = st.empty()
                    comms_prompt = get_comms_focus(
                        text, source_lang, target_lang
                    )
                    comms_analysis = stream_response(
                        [{"role": "user", "content": comms_prompt}],
                        comms_container,
                        model_name,
                        params
                    )
                    try:
                        comms = [el for el in comms_analysis.split("\n") if el != "" and el != " " and "[" not in el]
                        ret_comms = comms
                        #print("comms output: ", comms)
                    except Exception as e:
                        print("error: ", e)
                        ret_comms = "Error: " + str(e)

                    session_results["results"] = {
                        "translation": ret_trans,
                        "sentiment": ret_sentiment,
                        "grammar": ret_grammar,
                        "comms": ret_comms
                    }

    # Sidebar for additional information and feedback
    with st.sidebar:
        st.subheader("About")
        st.info("This app demonstrates Meta's Llama 3.1 capabilities.")
    
    # Sidebar for session summary 
    with st.sidebar:
        import datetime
        st.subheader("Session")

        score = st.number_input("Session Score", value=5, min_value=1, max_value=10)
        session_results["score"] = score

        session_results["session"] = params.copy()
        session_results["session"]["model"] = model_name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_results["session"]["timestamp"] = timestamp 
        session_results["session"]["lang"] = {"source": source_lang, "target": target_lang, "cultural_context": cultural_context}

        st.json(session_results)

        


if __name__ == "__main__":
    main()