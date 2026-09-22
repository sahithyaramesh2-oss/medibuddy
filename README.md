# Weather Advisory Support Bot

A weather-based safety advisory chatbot that provides recommendations for outdoor activities using live weather data and predefined SOP rules. The application uses LangGraph for workflow orchestration, Open-Meteo for weather data, and Gemini for generating user-friendly responses.

## Features

* Fetches live weather data using the Open-Meteo API.

* Matches weather conditions against SOP rules stored in a JSON file.

* Uses LangGraph to manage the workflow and decision-making process.

* Generates natural language safety advice using Gemini.

* Maintains conversation history for follow-up questions.

* Handles invalid locations and weather API failures gracefully.

## Tech Stack

* Python 3.11

* Streamlit

* LangGraph

* LangChain

* Google Gemini API

* Open-Meteo API

## Project Structure

```
weather-advisory-support-bot/
│
├── app.py                # Streamlit user interface
├── graph.py              # LangGraph workflow
├── policy_engine.py      # SOP matching logic
├── weather.py            # Weather API integration
├── geocode.py            # City to coordinates conversion
├── prompts.py            # Gemini system prompt
├── sop_rules.json        # Weather safety SOP rules
├── evals.py              # Evaluation test cases
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Setup Instructions

1. Clone the repository.

2. Create and activate a virtual environment.

3. Install the required packages:

Bash

```
pip install -r requirements.txt
```

4. Create a `.env` file and add your Gemini API key:

env

```
GEMINI_API_KEY=YOUR_API_KEY
```

5. Run the application:

Bash

```
streamlit run app.py
```

## Sample Activities

* Cycling

* Running

* Hiking

* Picnic

* Travel

* Children outdoor play

* Pet walking

* Elderly outdoor safety

## Evaluation

Run the evaluation script to test different scenarios:

Bash

```
python evals.py
```

The evaluation covers:

* SOP matching

* Paraphrased activity queries

* Rain and heat scenarios

* Unsupported activities

* Invalid locations

* Follow-up conversation handling

## Future Improvements

* Hourly weather forecasts.

* More activity-specific SOPs.

* Better semantic understanding of follow-up questions.

* Support for additional weather alerts and locations.
