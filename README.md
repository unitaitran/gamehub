# GameHub - Game Store System

## Introduction
GameHub is a game store application with essential features such as:
- User registration, login, and password recovery
- Browse game list and view game details
- Add to cart, checkout, and view purchase history
- Manage account and edit personal information
- Admin interface: add/edit/delete games, manage users
- Search and filter games by various criteria
- AI chat support for users (Gemini AI)

## How to Run the Application

### 1. Run Gemini AI (FastAPI)
```bash
cd gamehub/src/model
uvicorn gemini_AI:app --reload
```

### 2. Run Backend (Flask API)
```bash
cd gamehub/src
python -m backend.app
```

### 3. Run Frontend (Flet)
```bash
cd gamehub
python -m src.app
```

## Documentation & Links
- [Figma UI Design](https://www.figma.com/design/1tk2BtM4w9sLscp4ssbLhZ/CPL_Final_Project?node-id=0-1&t=wmmv9rZChzk2F5M4-1)
- [Requirements and Design Specification](https://docs.google.com/document/d/1rKdDGmA630DaYw4Nl5BXQJIpdEwoJL8bdgVCTyd9e2c/edit?tab=t.0)
- [Integration Test](https://docs.google.com/document/d/1iNejJR00niWY_D9lhouVP0nc_EDWkU_hdqVV7A8B-wU/edit?tab=t.0)
- [Canva Design](https://www.canva.com/design/DAGvigy8Yx8/KyZNtuiPLwn4tyxe-IndAw/edit?ui=eyJBIjp7fX0)
- [Game recommendation system report](https://docs.google.com/document/d/1jAw7uXNod6Ev73ULyTwfOQKOhef_BmFAgv_URpQQijk/edit?tab=t.0#heading=h.9mkqmpy8wv1j)
- [Chatbot system report](https://docs.google.com/document/d/1tQXUmJvIBfwO-fXFrssystOSw3G10HseKrhPbmjFY2Q/edit?tab=t.0#heading=h.3cm3d4oj1x7i)


