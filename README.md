# FitFlow

> An AI-powered fitness assistant built with Google's Agent Development Kit (ADK). 

FitFlow helps you find clothes that actually fit by learning from what already fits you well. Upload photos of your wardrobe, and our AI agents recommend marketplace items based on your measurements and fit history.
## 🎯 About The Project

FitFlow demonstrates how AI agents can revolutionize fitness and wellness management by automating and intelligently handling various fitness-related tasks. Built using Google's Agent Development Kit (ADK), this project showcases the practical application of AI agents in the health and fitness domain.

### What It Does

FitFlow leverages AI agents to:
- Add user clothing preferences and measurements to a personalized clothing inventory/wardrobe
- Provide personalized clothing recommendations based on user preferences
- Access to clothing by different vendors

### Key Features

- **📸 Smart Wardrobe**: Add clothes via photo or manual entry
- **🤖 AI Fit Prediction**: Compare marketplace items to your wardrobe
- **🏪 Personalized Shopping**: Search with style preferences and budget

## Prerequisites

- Python 3.8 and above.
- Dependencies listed in requirements.txt

## Setup Instructions

### 1. Clone the Repository
Clone the  repos using git clone command as follows:
```bash
git clone https://github.com/Kim1ni/fitflow
cd FitFlow
```
### 2. Install Dependencies
This project uses `uv` for package management. To install dependencies, run:
```bash
uv sync
```

### 3. Add your Google API Key
Change the name of the file .env.example to .env and add your Google API Key.

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

### 4. Run the Application
#### ADK Web UI
Run the application using the following command to use the ADK web interface.

```bash
uv run adk web
```

#### CLI Interface
To run the command-line interface:

```bash
uv run python -m fit_flow.main
```


The application will be available at http://localhost:8000/ under the name fit_flow in the agents dropdown.

## From the Author

Hope y'all like it.


