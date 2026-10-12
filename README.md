# 🎮 Nexus Game Hub

### Play More. Pay Less.

**Nexus Game Hub** is a full-stack PC gaming discovery and price-intelligence platform that helps gamers explore games, compare prices across supported storefronts, check PC system requirements, and get gaming recommendations from an integrated AI assistant named **Chawchaa**.

Discover your next game, compare available offers, and make more informed purchasing decisions — all in one place.

🌐 **Live Website:** https://fronttt-h5fz.onrender.com  

---

## ✨ Features

### 🎯 Game Discovery
- Search for PC games by their official titles.
- Explore game information, descriptions, artwork, and available platform details.
- Use a gaming-focused interface with multiple visual themes.
- Keep track of recently searched games through search history.

### 💰 Game Price Intelligence
- Compare available game offers across supported digital storefronts.
- View current prices returned by supported pricing providers.
- Explore historical lowest-price information where available.
- Access storefront links to check offers and purchase games.
- Display prices in the India-region context when supported by the provider.

### 🖥️ PC System Requirements
- View minimum PC system requirements when available.
- Check recommended requirements when supplied by the data source.
- Explore hardware and software compatibility information before purchasing a game.

### 🤖 Meet Chawchaa — Your AI Gaming Companion
Chawchaa is the integrated AI assistant that brings personality to Nexus Game Hub.

- Get gaming-related answers and recommendations.
- Discover games based on genres and preferences.
- Ask questions about games and compare titles.
- Enjoy a casual, desi-memer-inspired conversational personality.
- Keep conversations focused on gaming-related topics.

Chawchaa uses Ollama Cloud to generate responses. As with other AI systems, its answers may occasionally be inaccurate.

### ⭐ Player Reviews
- Rate the application and share written feedback.
- Read reviews submitted by other users.
- Edit or delete your own reviews.
- Use Supabase-backed authentication and database policies to support account and review management.

### 🎨 Multiple Visual Themes
- Explore different gaming-inspired visual styles.
- Switch themes through the Theme Studio.
- Experience a customizable interface without changing the core application functionality.

---

## 🖼️ Application Preview

Explore the live application to see the interface, game pricing, AI assistant, and community feedback in action.

| Area | What it offers |
|---|---|
| Home page | Game discovery and theme customization |
| Game details | Game metadata, available offers, and system requirements |
| Chawchaa | AI-powered gaming conversations and recommendations |
| Reviews | Ratings, written feedback, and community opinions |

*Screenshots can be added to this section later to give visitors a visual preview directly on GitHub.*

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Game metadata | IGDB |
| IGDB authentication | Twitch Developer API / OAuth 2.0 |
| Game prices and historical lows | IsThereAnyDeal (ITAD) |
| PC system requirements | RAWG API |
| AI assistant | Ollama Cloud |
| AI model | Gemma model, as configured |
| Authentication and database | Supabase |
| Deployment | Render |
| Version control | Git and GitHub |

---

## 🏗️ Architecture

Nexus Game Hub uses a separate frontend and backend architecture.

```text
                   USER
                    |
                    v
          NEXUS GAME HUB FRONTEND
             HTML / CSS / JS
                    |
              REST API Requests
                    |
                    v
             FASTAPI BACKEND
                    |
       +------------+-------------+
       |            |             |
       v            v             v
      IGDB          ITAD          RAWG
   Game Metadata   Game Prices   PC Requirements
       |
       +-------------------------+
                    |
                    v
              Ollama Cloud
             Chawchaa AI

       Supabase: Authentication,
           Profiles and Reviews
```

**How it works:**

1. A user searches for a game through the frontend.
2. The FastAPI backend retrieves the relevant information from configured data providers.
3. Available pricing and historical-low information is retrieved from the pricing provider.
4. PC requirements are requested from RAWG when available.
5. Chawchaa sends gaming-related requests to the configured Ollama Cloud model.
6. Supabase supports user authentication, profiles, and reviews.
7. The frontend presents the returned information in the user interface.

The information displayed depends on provider availability, API credentials, regional coverage, and the data returned for each game.

---

## 🚀 Running the Project Locally

### Prerequisites

Install or obtain the following:

- Python 3.10 or a compatible version for the backend dependencies.
- Git.
- A modern web browser.
- API credentials for the services you want to enable.

### 1. Clone the repository

```bash
git clone https://github.com/sensei-desu/game_tracker.git
cd game_tracker
```

### 2. Configure the backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the directory expected by your backend configuration and add the required API credentials.

Example configuration — use the exact variable names expected by your current code:

```env
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret

ITAD_API_KEY=your_itad_api_key
RAWG_API_KEY=your_rawg_api_key

OLLAMA_API_KEY=your_ollama_api_key
OLLAMA_MODEL=your_configured_model

SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
```

Some variables may have different names or may be optional depending on your implementation. Check the backend configuration before running the application.

**Important:** Never commit your `.env` file, API keys, database secrets, or other credentials to GitHub.

Start the FastAPI backend using the command appropriate for your project structure. If `main.py` is in the backend directory:

```bash
uvicorn main:app --reload
```

The local backend will normally be available at:

`http://127.0.0.1:8000`

FastAPI's interactive API documentation is normally available at:

`http://127.0.0.1:8000/docs`

### 3. Configure and run the frontend

Open the frontend directory in your editor.

Make sure the frontend's API base URL points to your local backend:

```javascript
const API_BASE_URL = "http://127.0.0.1:8000";
```

This is an illustrative example. Update the configuration where your actual frontend defines its backend URL; do not create a duplicate variable if one already exists.

Run the frontend using a local HTTP server or the method supported by your project. For example, if the frontend consists of static HTML, CSS, and JavaScript files:

```bash
python -m http.server 5500
```

Then open:

`http://127.0.0.1:5500`

Configure the backend's CORS settings to allow your local frontend origin before making cross-origin API requests.

### 4. Configure Supabase

Set up your Supabase project and configure the required credentials.

The application uses Supabase for authentication and database-backed functionality, including user profiles and reviews. Ensure the required tables, authentication settings, and row-level security policies are configured before testing these features.

### 5. Test the application

- Search for a PC game.
- Check its available details and offers.
- Open the system requirements section.
- Try Chawchaa with a gaming-related question.
- Sign in and test the review functionality.
- Switch themes and navigate through the application.

---

## ☁️ Deployment

Nexus Game Hub is deployed on Render with separate frontend and backend services.

| Service | URL |
|---|---|
| Frontend | https://fronttt-h5fz.onrender.com |

### Backend deployment
- Configure the backend service with the correct root directory and dependencies.
- Set the required API credentials as environment variables in Render.
- Use a production server command compatible with the backend's entry point.
- Configure CORS to allow the deployed frontend origin.

### Frontend deployment
- Deploy the frontend files using the configured static-site service.
- Set the frontend API base URL to the deployed backend.
- Ensure the frontend and backend origins are configured correctly.

Never store private API keys in frontend JavaScript or publish them in the repository.

---

## 🔐 Security and Reliability

- Store private API credentials in environment variables.
- Keep authentication and database secrets out of source control.
- Use Supabase row-level security to protect user-owned records.
- Validate API requests and handle unavailable external services gracefully.
- Treat AI-generated responses as suggestions rather than guaranteed facts.
- Remember that external API availability and pricing data may vary.

---

## 🔮 Future Scope

Potential improvements for future versions include:

- User wishlists and price-drop notifications.
- Expanded historical price tracking.
- More advanced game filters and discovery tools.
- Improved recommendations based on user preferences.
- Additional testing, monitoring, and error handling.

These are possible future enhancements, not claims about existing functionality.

---

## 🎯 Project Goal

Nexus Game Hub aims to make PC game discovery and purchasing research easier by bringing together game information, price intelligence, system requirements, AI-powered gaming assistance, and player reviews.

Instead of switching between multiple websites for every decision, gamers can explore the information available through one unified experience.

---

## 👨‍💻 Author

**GitHub:** [@sensei-desu](https://github.com/sensei-desu)

**Project:** Nexus Game Hub

**Tagline:** *Play More. Pay Less.*

---

## 📄 License

Right now there is no license by my side.
---

⭐ If you find Nexus Game Hub interesting, explore the live application and check out the repository!

