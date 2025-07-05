import databutton as db
import streamlit as st

def check_for_openai_key():
    try:
        key = db.secrets.get("OPENAI_API_KEY")
    except Exception:
        key = ""

    if len(key) > 10:
        return key

    with st.chat_message("Assistant"):
        mp = st.empty()
        sl = mp.container()
        sl.write(
            """Hi there! It is fantastic that you want to chat with me. However, I need your OpenAI API key to work.
            If you don't have a key, you can sign-up and create one here https://platform.openai.com/account/api-keys.
            Don't worry, your key will be securely stored in the Databutton secrets store, which you can find in the 
            left-side menu under Configure.
                  """
        )

        key = sl.text_input("Type in your OpenAI API key to continue", type="password")
        if key:
            db.secrets.put("OPENAI_API_KEY", key)
            mp.write("Thank you for providing your key. Let's go!")
    st.stop()
    return 1
