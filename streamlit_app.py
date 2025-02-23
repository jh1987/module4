import pysqlite3
import sys
sys.modules['sqlite3'] = pysqlite3

import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import tracemalloc
import warnings
import os

# Start tracemalloc
tracemalloc.start()

# Suppress all warnings
warnings.filterwarnings('ignore', category=ResourceWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message=".*schema.*")
warnings.filterwarnings('ignore', message=".*deprecated.*")
warnings.filterwarnings('ignore', message=".*ConfigDict.*")
warnings.filterwarnings('ignore', message=".*validator.*")
warnings.filterwarnings('ignore', message=".*Field.*")
warnings.filterwarnings('ignore', message=".*config.*")

# Set environment variable to disable deprecation warnings
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

# Load environment variables
os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ['SERPER_API_KEY'] = st.secrets['SERPER_API_KEY']

# Initialize Serper API tool for web search
search_tool = SerperDevTool()

# --- Agents ---
trendspotter_ai = Agent(
    role="AI Trend Researcher",
    goal="Identify emerging AI trends across industries",
    backstory=(
        "You are an AI-powered analyst with an insatiable curiosity for technological breakthroughs. "
        "Your expertise lies in scanning academic papers, startup funding rounds, AI patent filings, "
        "and government innovation grants to detect upcoming disruptions before they go mainstream. "
        "You provide thought leadership in identifying trends that will define the future of AI."
    ),
    tools=[search_tool],
    verbose=True,
)

market_analyzer_ai = Agent(
    role="Market Strategist",
    goal="Assess market demand and feasibility of AI solutions",
    backstory=(
        "You are a strategic business analyst with deep expertise in evaluating commercial viability. "
        "Your role involves analyzing market trends, understanding customer pain points, and benchmarking "
        "against existing competitors. With an eye for investment opportunities, you assess funding landscapes "
        "and adoption barriers, providing insights that drive smart business decisions."
    ),
    tools=[search_tool],
    verbose=True,
)

business_model_ai = Agent(
    role="Business Model Architect",
    goal="Develop sustainable monetization strategies for AI solutions",
    backstory=(
        "You are a financial strategist with an extensive understanding of AI-driven business models. "
        "Drawing from successful AI startups and established enterprises, you design pricing strategies, "
        "explore revenue streams (SaaS, API licensing, data monetization), and simulate market adoption scenarios. "
        "Your ability to forecast profitability ensures that AI innovations are commercially viable."
    ),
    tools=[],
    verbose=True,
)

technical_feasibility_ai = Agent(
    role="AI Infrastructure & Feasibility Expert",
    goal="Evaluate the technical feasibility and risks of AI solutions",
    backstory=(
        "You are an AI engineer specializing in infrastructure scalability, model selection, and risk analysis. "
        "Your expertise helps determine whether off-the-shelf models are sufficient or if custom AI solutions are needed. "
        "You assess data requirements, compute power needs, security risks, and ethical concerns like bias and explainability. "
        "Your evaluations ensure AI solutions are technically sound and ready for deployment."
    ),
    tools=[],
    verbose=True,
)

storytelling_ai = Agent(
    role="AI Use Case Communicator",
    goal="Create compelling narratives and pitch decks to showcase AI solutions",
    backstory=(
        "You are a master storyteller with a knack for simplifying complex AI concepts. "
        "Your expertise lies in crafting engaging presentations, executive summaries, and investor-friendly narratives. "
        "By understanding audience psychology, you translate technical ideas into compelling business opportunities, "
        "ensuring AI projects receive the attention they deserve."
    ),
    tools=[],
    verbose=True,
)

# --- Streamlit Interface ---
st.title("💡 AI Use Case Generator")
st.write("Chat with AI agents to discover emerging AI trends and business opportunities.")

# User input box
user_query = st.text_input("Enter a topic (e.g., 'AI in supply chain'):")

if st.button("Generate AI Insights"):
    if user_query:
        # Create placeholders for each section
        trends_placeholder = st.empty()
        market_placeholder = st.empty()
        business_placeholder = st.empty()
        feasibility_placeholder = st.empty()
        pitch_placeholder = st.empty()

        # --- Tasks and Execution ---
        with st.spinner("🔍 AI Agents are working..."):
            # Function to extract content between headers
            def extract_section(text, header):
                try:
                    if "###" + header in text:
                        parts = text.split("###" + header)
                        if len(parts) > 1:
                            content = parts[1].split("###")[0].strip()
                            return content
                    return text.strip()
                except Exception:
                    return text.strip()

            # Trends Research
            st.write("🔎 Trend Researcher is analyzing...")
            research_task = Task(
                description=(
                    f"Research and analyze the latest AI trends related to {user_query}.\n"
                    "Your response MUST follow this format:\n"
                    "### AI Trends\n"
                    "1. [First Trend]: [Description and impact]\n"
                    "2. [Second Trend]: [Description and impact]\n"
                    "3. [Third Trend]: [Description and impact]"
                ),
                expected_output="A structured analysis of 3 emerging AI trends with clear headers.",
                tools=[search_tool],
                agent=trendspotter_ai,
            )
            trends_crew = Crew(
                agents=[trendspotter_ai],
                tasks=[research_task],
                process=Process.sequential,
                verbose=True
            )
            trends_result = trends_crew.kickoff()
            with trends_placeholder.container():
                st.markdown("### 🚀 **Key AI Trends Identified**")
                st.write(extract_section(str(trends_result), " AI Trends"))

            # Market Analysis
            st.write("📊 Market Analyst is researching...")
            market_analysis_task = Task(
                description=(
                    f"Analyze the market potential for AI solutions in {user_query}.\n"
                    "Your response MUST follow this format:\n"
                    "### Market Analysis\n"
                    "Market Size: [Details]\n"
                    "Key Competitors: [List]\n"
                    "Growth Potential: [Analysis]"
                ),
                expected_output="A structured market analysis with clear sections.",
                tools=[search_tool],
                agent=market_analyzer_ai,
            )
            market_crew = Crew(
                agents=[market_analyzer_ai],
                tasks=[market_analysis_task],
                process=Process.sequential,
                verbose=True
            )
            market_result = market_crew.kickoff()
            with market_placeholder.container():
                st.markdown("### 📊 **Market Analysis & Business Potential**")
                st.write(extract_section(str(market_result), " Market Analysis"))

            # Business Model
            st.write("💰 Business Model Architect is planning...")
            business_model_task = Task(
                description=(
                    f"Create a business model for AI solutions in {user_query}.\n"
                    "Your response MUST follow this format:\n"
                    "### Business Model\n"
                    "Revenue Streams: [List]\n"
                    "Pricing Strategy: [Details]\n"
                    "Target Customers: [Description]"
                ),
                expected_output="A detailed business model breakdown.",
                agent=business_model_ai,
            )
            business_crew = Crew(
                agents=[business_model_ai],
                tasks=[business_model_task],
                process=Process.sequential,
                verbose=True
            )
            business_result = business_crew.kickoff()
            with business_placeholder.container():
                st.markdown("### 💰 **Business Model & Monetization**")
                st.write(extract_section(str(business_result), " Business Model"))

            # Technical Feasibility
            st.write("🛠️ Technical Expert is evaluating...")
            feasibility_task = Task(
                description=(
                    f"Evaluate technical feasibility of AI implementation in {user_query}.\n"
                    "Your response MUST follow this format:\n"
                    "### Technical Feasibility\n"
                    "Required Infrastructure: [List]\n"
                    "Technical Challenges: [Details]\n"
                    "Implementation Timeline: [Estimate]"
                ),
                expected_output="A technical feasibility assessment with clear sections.",
                agent=technical_feasibility_ai,
            )
            feasibility_crew = Crew(
                agents=[technical_feasibility_ai],
                tasks=[feasibility_task],
                process=Process.sequential,
                verbose=True
            )
            feasibility_result = feasibility_crew.kickoff()
            with feasibility_placeholder.container():
                st.markdown("### 🛠️ **Technical Feasibility & Challenges**")
                st.write(extract_section(str(feasibility_result), " Technical Feasibility"))

            # Pitch Summary
            st.write("🎤 Storyteller is crafting the pitch...")
            storytelling_task = Task(
                description=(
                    f"Create a compelling pitch for the AI solution in {user_query}.\n"
                    "Your response MUST follow this format:\n"
                    "### Pitch Summary\n"
                    "Value Proposition: [Clear statement]\n"
                    "Key Differentiators: [List]\n"
                    "Market Opportunity: [Description]"
                ),
                expected_output="A structured pitch with clear sections.",
                agent=storytelling_ai,
            )
            pitch_crew = Crew(
                agents=[storytelling_ai],
                tasks=[storytelling_task],
                process=Process.sequential,
                verbose=True
            )
            pitch_result = pitch_crew.kickoff()
            with pitch_placeholder.container():
                st.markdown("### 🎤 **Final Pitch Summary**")
                st.write(extract_section(str(pitch_result), " Pitch Summary"))

        st.success("✅ Analysis completed!")

    else:
        st.warning("⚠️ Please enter a topic to research.")