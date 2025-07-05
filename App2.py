import databutton as db
import streamlit as st
import openai
import time
import requests
import base64
import json
from google.cloud import texttospeech as tts
from my_pdf_lib import get_index_for_pdf
from key_check import check_for_openai_key
from streamlit_extras.switch_page_button import switch_page
tts_key=db.secrets.get("TTS_KEY")
openai.api_key = db.secrets.get("OPENAI_API_KEY")
subscription_key ="a9739b8eeaf04be2962ab99b746ed99f"
endpoint = "https://api.bing.microsoft.com/"
url=f"{endpoint}v7.0/images/search"
new_offset=0
@st.cache_data
def create_vectordb(files):
    vectordb = get_index_for_pdf(files, openai.api_key)
    return vectordb

@st.cache_data
def retrieve_pdf_content(pdf_keys):
    return [db.storage.binary.get(key) for key in pdf_keys]
import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
pdf_keys = ["the-historyof-apple1-pdf"]
pdf_content = retrieve_pdf_content(pdf_keys)
vectordb = create_vectordb(pdf_content)
def delete_chat_logs():
    db.storage.json.put("chat_logs1", [])
def chat_logs_page():
    chat_logs = db.storage.json.get('chat_logs1', default=[])
    if len(chat_logs) > 0:
        for index, item in enumerate(chat_logs):
            question = item.get('question', '')
            bot = item.get('bot', '')
            st.write(f"Message {index + 1}:")
            st.write(f"Question: {question}")
            st.write(f"Bot Response: {bot}")
    else:
        st.header("No chat logs available.")

def save_chat_logs(bot_response):
    question = st.session_state.get("current_question")
    chat_log = {"question": question, "bot": bot_response}
    chat_logs = db.storage.json.get('chat_logs1', default=[])
    chat_logs.append(chat_log)
    db.storage.json.put('chat_logs1', chat_logs)

def update_chat_logs(prompt, response):
    prompt.append({"role": "assistant", "content": response})
    save_chat_logs(response)
page_selection = st.sidebar.selectbox("Select a page", ["Home", "Chat History"])
if page_selection == "Home":
    
    grade_options = {
        "Grade 6th":{
            "Maths":[
                "Knowing our numbers",
                "Whole Numbers",
                "Playing with Numbers",
                "Basic Geometric Ideas",
                "Understanding Elementary Shapes",
                "Integers",
                "Fractions",
                "Decimals",
                "Data Handling",
                "Mensuration",
                "Algebra",
                "Ratio and Proportion"
            ],
            "Science":[
                "Food",
                "Materials",
                "The World of the Living",
                "Moving Things,People and Ideas",
                "How things work",
                "Natural Phenomena",
                "Natural Resources"
            ],
            "Social Science":[
                "When,Where and How",
                "From Hunting – Gathering to Growing Food",
                "In the Earliest Cities",
                "What Books and Burials Tell Us",
                "Kingdoms, Kings and an Early Republic",
                "New Questions and Ideas",
                "From a Kingdom to an Empire",
                "Villages, Towns and Trade",
                "New Empires and Kingdoms",
                "Buildings, Paintings and Books",
                 "Diversity",
                "Government",
                "Local Government",
                "Rural Administration",
                "Urban Administration",
                "Rural Livelihoods",
                "Urban Livelihoods"
                "The Earth in the Solar System",
                "Globe: Latitudes and Longitudes",
                "Motions of the Earth",
                "Maps",
                "Major Domains of the Earth",
                "Our Country: India"
            ],
            "English":[
                "Who Did Patrick’s Homework?",
                "A House, A Home",
                "How the Dog Found Himself a New Master!",
                "The Kite",
                "Taro’s Reward",
                "The Quarrel",
                "An Indian – American Woman in Space: Kalpana Chawla",
                "Beauty",
                "A Different Kind of School",
                "Where Do All the Teachers Go?",
                "Who I Am",
                "The Wonderful Words",
                "Fair Play",
                "Vocation",
                "The Banyan Tree",
                "A Tale of Two Birds",
                "The Friendly Mongoose",
                "The Shepherd’s Treasure",
                "Tansen",
                "The Monkey and the Crocodile",
                "The Wonder Called Sleep",
                "A Pact with the Sun"
            ],
        },
        "Grade 7th":{
            "Maths":[
                "Integers",
                "Fractions and Decimals",
                "Data Handling",
                "Lines and Angles",
                "The Triangle and its Properties",
                "Comparing Quantities",
                "Rational Numbers",
                "Perimeter and Area",
                "Algebraic Expressions",
                "Exponents and Powers",
                "Symmetry",
                "Visualising Solid Shapes"
            ],
            "Science":[
                "Nutrition in Plants",
                "Nutrition in Animals",
                "Fibre to Fabric",
                "Acids, Bases and Salts",
                "Physical and Chemical Changes",
                "Respiration in Organisms",
                "Transportation in Animals and Plants",
                "Reproduction in Plants",
                "Motion and Time",
                "Electric Current and its Effects",
                "Light",
                "Forests – Our Lifeline",
                "Wastewater Story"
            ],
            "English":[
                "Three Questions & The Squirrel",
                "A Gift of Chappals & The Rebel",
                "Gopal and the Hilsa Fish & The Shed",
                "The Ashes That Made Trees Bloom & Chivvy",
                "Quality & Trees",
                "Expert Detectives & Mystery of the Talking Fan",
                "The Invention of Vita-Wonk & Dad and the Cat and the Tree & Garden Snake",
                "A Homage to Our Brave Soldiers & Meadow Surprises",
                "The Tiny Teacher",
                "Bringing Up Kari",
                "Golu Grows a Nose",
                "Chandni",
                "The Bear Story",
                "A Tiger in the House",
                "An Alien Hand English"
            ],
            "Social Science":[
                    "Tracing Changes through a Thousand Years",
                    "Kings and Kingdoms",
                    "Delhi: 12th to 15th Century",
                    "The Mughal Empire: 16th to 17th Century",
                    "Tribes, Nomads and Settled Communities",
                    "Devotional Paths to the Divine",
                    "The Making of Regional Cultures",
                    "Eighteenth Century Political Formations"
                    "On Equality",
                    "Role of the Government in Health",
                    "How the State Government Works",
                    "Growing up as Boys and Girls",
                    "Women Change the World",
                    "Understanding Media",
                    "Markets Around Us",
                    "A Shirt in the Market"
                    "Environment",
                    "Inside Our Earth",
                    "Our Changing Earth",
                    "Air",
                    "Water",
                    "Human Environment Interactions – The Tropical and the Subtropical Region",
                    "Life in the Deserts"
                
            ]
        },
        "Grade 8th":{
            "Maths":[
                "Rational Numbers",
                "Linear Equations in one Variable",
                "Understanding Quadilaterals",
                "Data Handling",
                "Square and Square Roots",
                "Cubes and Cube Roots",
                "Comparing Quantities",
                "Algebraic Expressions and Identities",
                "Mensuration",
                "Exponents and Powers",
                "Direct and Inverse Proportions",
                "Factorisation",
                "Introduction to Graphs"
            ],
            "Science":[
                "Crop Production and Management",
                "Microorganisms: Friend and Foe",
                "Coal and Petroleum",
                "Combustion and Flame",
                "Conservation of Plants and Animals",
                "Reproduction in Animals",
                "Reaching the Age of Adolescence",
                "Force and Pressure",
                "Friction",
                "Sound",
                "Chemical Effects of Electric Current",
                "Some Natural Phenomena",
                "Light"
            ],
            "Social Science":[
                    "How, When and Where",
                    "From Trade to Territory The Company Establishes Power",
                    "Ruling the Countryside",
                    "Tribals, Dikus and the Vision of a Golden Age",
                    "When People Rebel 1857 and After",
                    "Civilising the “Native”, Educating the Nation",
                    "Women, Caste and Reform",
                    "The Making of the National Movement: 1870s–1947"
                    "The Indian Constitution",
                    "Understanding Secularism",
                    "Parliament and the Making of Laws",
                    "Judiciary",
                    "Understanding Marginalisation",
                    "Confronting Marginalisation",
                    "Public Facilities",
                    "Law and Social Justice"
                    "Resources",
                    "Land, Soil, Water, Natural Vegetation and Wildlife Resources",
                    "Agriculture",
                    "Industries",
                    "Human Resources"
            ],
            "English":[
                "The Best Christmas Present in the World",
                "The Ant and the Cricket",
                "The Tsunami",
                "Geography Lesson",
                "Glimpses of the Past",
                "Bepin Choudhury’s Lapse of Memory",
                "The Last Bargain",
                "The Summit Within",
                "The School Boy",
                "This is Jody’s Fawn",
                "A Visit to Cambridge",
                "A Short Monsoon Diary",
                "On the Grasshopper and Cricket",
                "How the Camel Got His Hump",
                "Children at Work",
                "The Selfish Giant",
                "The Treasure Within",
                "Princess September",
                "The Fight",
                "Jalebis",
                "Ancient Education System of India"
            ]
        },
        "Grade 9th":{
            "Maths":[
                "Real Numbers",
                "Polynomials",
                "Linear Equations in Two Variables",
                "Coordinate Geometry",
                "Introduction to Euclid'd Geometry",
                "Lines and Angles",
                "Triangles",
                "Quadilaterals",
                "Circles",
                "Areas",
                "Surface areas and vloumes",
                "Statistics"
            ],
            "Science":[
                "Nature and Matter",
                "Particle Nature and Their Basic Units",
                "Structure of Atoms",
                "Basic Unit of Life",
                "Tissues,Organs,Organ System,Organism",
                "Motion",
                "Force and Newton's Laws",
                "Gravitation",
                "Floatation",
                "Work,Energy and Power",
                "Sound",
                "Food Production"
            ],
            "Social Science":[
                    "The French Revolution",
                    "Socialism in Europe and the Russian Revolution"
                    "Nazism and the Rise of Hitler",
                    "Forest, Society and Colonialism",
                    "Pastoralists in the Modern World"
                    "India - Size and Location",
                    "Physical Features of India",
                    "Drainage",
                    "Climate",
                    "Natural Vegetation and Wildlife ",
                    "Population"
                    "What is Democracy? & Why Democracy?",
                    "Constitutional Design",
                    "Electoral Politics",
                    "Working of Institutions",
                    "Democratic Rights"
                    "The Story of Village Palampur",
                    "People as Resource",
                    "Poverty as a Challenge",
                    "Food Security in India"
                ],
            "English":[
                "The Fun They had",
                "The Sound of Music",
                "The Little Girl",
                "A Truly Beautiful Mind",
                "The Snake and the Mirror",
                "My Childhood",
                "Reach For the top",
                "Kathmandu",
                "If I were you",
                "The road not taken",
                "Wind",
                "Rain on the roof"
                "The lake Isle of innisfree",
                "A Legend of The Northland",
                "No Men Are Foreign",
                "On killing a tree",
                " A Slumber Did My Spirit Seal"
            ]
        },
        "Grade 10th":{
            "Maths":[
                "Real Numbers",
                "Polynomials",
                "Pair of Linear Equations in Two Variables",
                "Quadratic Equations",
                "Arithmetic Progressions",
                "Coordinate Geometry",
                "Triangles",
                "Circles",
                "Introduction to Trigonometry",
                "Trigonometric Identities",
                "Heights and Distances",
                "Areas Related to Circles",
                "Surface Area and Volumes",
                "Statistics",
                "Probability"
            ],
            "Science":[
                "Chemical Reactions",
                "Acids,Bases and Salts",
                "Metals and Non-metals",
                "Carbon Compounds",
                "Life Processes",
                "Control and Co-ordination in Animals and Plants",
                "Reproduction",
                "Hereditary and Evolution",
                "Reflection of Light by Curved Surfaces",
                "Refraction",
                "Refraction of Light by Spherical Lens",
                "Refraction of Light Through a Prism",
                "Electric Current, Potential Difference and Electric Current",
                "Magnetic Effects of Current",
                "Our Environment"
            ],
            "Social Science":[
                    "The Rise of Nationalism in Europe",
                    "Nationalism In India",
                    "The Making of a Global World",
                    "The Age of Industrialization",
                    "Print Culture and the Modern World"
                    "Resources and Development",
                    "Forest and Wildlife Resources",
                    "Water Resources",
                    "Agriculture",
                    "Minerals and Energy Resources",
                    "Manufacturing Industries",
                    "Lifelines of National Economy"
                    "Power – sharing",
                    "Federalism",
                    "Gender, Religion and Caste",
                    "Political Parties",
                    "Outcomes of Democracy"
                    "Development",
                    "Sectors of the Indian Economy",
                    "Money and Credit",
                    "Globalisation and The Indian Economy",
                    "Consumer Rights"
                ],
            "English":[
                "A Letter to God",
                "Nelson Mandela - Long Walk to Freedom",
                "Two Stories About Flying",
                "Diary of a young girl",
                "Glimpses of India",
                "Mijbil the Otter",
                "Madam Rides the Bus",
                "The Sermon at Benares",
                "The Proposal",
                "Dust of Snow",
                "Fire and Ice",
                "A Tiger in the Zoo",
                "How to Tell Wild Animals",
                "The Ball Poem",
                "Amanda!",
                "The Trees",
                "Fog",
                "The Tale of Custard the Dragon",
                "For Anne Gregory"
            ]
        },
        "Grade 11th":{
            "Physics":[
                "Units and Measurements",
                "Motion in a Straight Line",
                "Motion in a Plane",
                "Laws of Motion",
                "Work, Energy and Power",
                "System of Particles and Rotational Motion",
                "Gravitation",
                "Mechanical Properties of Solids",
                "Mechanical Properties of Fluids",
                "Thermal Properties of Matter",
                "Thermodynamics",
                "Kinetic Theory",
                "Oscillations",
                "Waves"
            ],
            "Chemistry":[
                "Some Basic Concepts of Chemistry",
                "Structure of Atom",
                "Classification of Elements and Periodicity in Properties",
                "Chemical Bonding and Molecular Structure",
                "Chemical Thermodynamics",
                "Equilibrium",
                "Redox Reactions",
                "Organic Chemistry: Some Basic Principles and Techniques",
                "Hydrocarbons"
            ],
            "Maths":[
                "Sets",
                "Relations and Functions",
                "Trigonometric Functions",
                "Complex Numbers and Quadratic Equations",
                "Linear inequalities",
                "Permutations and Combinations",
                "Binomial Theorem",
                "Sequence and Series",
                "Straight Lines",
                "Conic Sections",
                "Introduction to three-dimensional geometry",
                "Limits and Derivatives",
                "Probability",
                "Statistics"
            ],
            "Biology":[
                 "Diversity of Living Organisms",
                 "Structural Organisation in Plants and Animals",
                "Cell: Structure and Function",
                "Plant Physiology",
                "Human Physiology"
            ],
            "English":[
                "The Peacock",
                "Let me Not to the Marriage of True Minds William Shakespeare",
                "Coming- Philip Larkin",
                "Telephone Conversation – Wole Soyinka",
                "The World is too Much With Us"
                "Mother Tongue",
                "Hawk Roosting",
                "Ode to a Nightingale",
                "My Watch",
                "My Three Passions",
                "Patterns of Creativity",
                "Tribal Verse",
            ],
            "Accountancy":[
                "Introduction to Accountancy",
                "Theory base of accounting",
                "Recording of Transactions 1",
                "Recording of Transactions 2",
                "Bank Reconciliation Statement",
                "Trial Balance and Rectification of Errors",
                "Depreciation, Provisions and Reserves",
                "Financial Statements 1",
                "Financial Statements 2",
            ],
            "Business Studies":[
                "Business, Trade and Commerce",
                "Forms of Business Organisation",
                "Private, Public and Global Enterprises",
                "Business Services",
                "Emerging Modes of Business",
                "Social Responsibilities of Business and Business Ethics",
                "Formation of a Company",
                "Sources of Business Finance",
                "Small Business and Entrepreneurship",
                "Internal Trade",
                "International Business"
            ],
            "Economics":[
                "Indian Economy on the Eve of Independence",
                "Indian Economy (1950-1990)",
                "Liberalisation, Privatisation and Globalisation: An Appraisal",
                "Human Capital Formation in India",
                "Rural Development",
                "Employment Growth, Informalisation and Other Issues",
                "Environment and Sustainable Development",
                "Comparative development Experiences of India and Its Neighbours",
            ],
        },
        "Grade 12th":{
            "Physics":[
                "Electric Charges and Fields",
                "Electrostatic Potential and Capacitance",
                "Current Electricity",
                "Moving Charges and Magnetism",
                "Magnetism and Matter",
                "Electromagnetic Induction",
                "Alternating Current",
                "Electromagnetic Waves",
                "Ray Optics and Optical Instruments",
                "Wave Optics",
                "Dual Nature of Radiation and Matter",
                "Atoms",
                "Nuclei",
                "Semiconductor Electronics: Materials, Devices and Simple Circuits"
            ],
            "Chemistry":[
                "Solutions",
                "Electrochemistry",
                "Chemical Kinetics",
                "d -and f -Block Elements",
                "Coordination Compounds",
                "Haloalkanes and Haloarenes",
                "Alcohols, Phenols and Ethers",
                "Aldehydes, Ketones and Carboxylic Acids",
                "Amines",
                "Biomolecules",
            ],
            "Maths":[
                "Relations and Functions",
                "Inverse Trigonometric Functions",
                "Matrices",
                "Determinants",
                "Continuity and Differentiability",
                "Applications of Derivatives",
                "Integrals",
                "Applications of the Integrals",
                "Differential Equations",
                "Vectors",
                "Three – dimensional Geometry",
                "Linear Programming",
                "Probability",
            ],
            "Biology":[
                "Sexual Reproduction in Flowering Plants",
                "Human Reproduction",
                "Reproductive Health",
                "Principles of Inheritance and Variation",
                "Molecular Basis of Inheritance",
                "Evolution",
                "Human Health and Diseases",
                "Microbes in Human Welfare",
                "Biotechnology – Principles and Processes",
                "Biotechnology and its Applications",
                "Organisms and Populations",
                "Ecosystem",
                "Biodiversity and Its Conservation",
            ],
            "English":[
                "The Last Lesson",
                "Lost Spring",
                "Deep Water",
                "The Rattrap",
                "Indigo",
                "Poets and Pancakes",
                "The Interview",
                "Going Places",
                "My Mother at Sixty-six",
                "An Elementary School Classroom in a Slum",
                "Keeping Quiet",
                "A Thing of Beauty",
                "A Roadside Stand",
                "Aunt Jennifer’s Tigers",
                "The Third Level",
                "The Tiger King",
                "Journey to the end of the Earth",
                "The Enemy",
                "Should Wizard Hit Mommy?",
                "On the Face of It",
                "Evans Tries an O-level",
                "Memories of Childhood"
            ],
            
        }
    }
    st.write("Have other doubts? Try this app")
    want_to_contribute = st.button("Click Here")
    if want_to_contribute:
        switch_page("App1")
    grade=st.selectbox("Select your grade",list(grade_options.keys()))
    if grade:
        subjects=grade_options[grade]
        sub=st.selectbox("Select your Subject",list(subjects.keys()))
        if sub:
            chapters=subjects[sub]
            chap=st.selectbox("Select your chapter",chapters)
            if chap:
                default_query=f"Information about {chap} chapter in {sub} subject for {grade} for CBSE"
                with st.chat_message("assistant"):
                    st.write(default_query)
                if st.button("Send"):
                    question=default_query
                    check_for_openai_key()
                    vectordb=vectordb
                    search_results=vectordb.similarity_search(question,k=5)
                    pdf_extract="\n".join([result.page_content for result in search_results])
                    prompt_template = """
                         You need to provide answers to any and all questions
                         in any way possible
                    """
                    prompt=[]
                    prompt.append({
                        "role":"system",
                        "content":prompt_template.format(pdf_extract=pdf_extract)
                    })
                    prompt.append({"role":"user","content":question})
                    max_context_length = 4097
                    prompt_length = sum(len(message["content"]) for message in prompt if message["content"] is not None)
                    if prompt_length > max_context_length:
                        excess_length = prompt_length - max_context_length
                        excess_messages = []
                        while excess_length > 0:
                            message = prompt.pop(0)
                            message_length = len(message["content"])
                            if excess_length >= message_length:
                                excess_messages.append(message)
                                excess_length -= message_length
                            else:
                                message["content"] = message["content"][:-excess_length]
                                prompt.insert(0, message)
                                excess_length = 0
                        excess_message_count = len(excess_messages)
                        st.warning(f"The prompt was truncated to fit within the maximum context length. {excess_message_count} message(s) were removed.")
                    with st.chat_message("user"):
                        st.write(question)
                    with st.chat_message("assistant"):
                        botmsg = st.empty()
                    response = []
                    result = ""
                    for chunk in openai.ChatCompletion.create(
                        model="gpt-3.5-turbo", messages=prompt, stream=True
                    ):
                        text = chunk.choices[0].get("delta", {}).get("content")
                        if text is not None:
                            response.append(text)
                            result = "".join(response).strip()
                            botmsg.info(result)
                    update_chat_logs(prompt, result)
                    st.session_state["prompt"] = prompt
                    headers={"Ocp-Apim-Subscription-Key":subscription_key}
                    params={
                        "q":f"{chap} ",
                        "license":"public",
                        "imageType":"photo",
                        "safeSearch":"Strict",
                        "count":4,
                        "offset":0,
                    }
                    contentUrls=[]
                    while new_offset is not None and new_offset<=4:
                        params["offset"]=new_offset
                        response = requests.get(url, headers=headers, params=params)
                        response.raise_for_status()
                        result = response.json()
                        time.sleep(1)
                        new_offset = result.get("nextOffset",None)
                        for item in result["value"]:
                            contentUrls.append(item["contentUrl"])
                            params["offset"]=1
                    for item in result["value"]:
                        st.image(item["contentUrl"], caption="Image")


            
            else:
                st.info("Please select a chapter.")
        else:
            st.info("Please select a subject.")
    else:
        st.info("Please select a grade.")
test=st.checkbox("Chat History")
if test:
    if st.button("Delete Chat History"):
            delete_chat_logs()
            st.success("Chat History Deleted")
    chat_logs_page()