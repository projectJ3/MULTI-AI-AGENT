# 🚀 End-to-End LLMOps Project  
LLM-powered application built with **Groq**, **Tavily**, **FastAPI**, **Streamlit**, **Docker**, **Jenkins**, **SonarQube**, and **AWS (ECR + Fargate)**.

This project demonstrates complete **LLMOps workflow**, including model integration, backend + frontend development, containerization, CI/CD automation, code quality checks, and cloud deployment.

---

## 📌 Features
### **LLM Application**
- Integrated **Groq LLM API** for high-speed inference  
- Integrated **Tavily Search API** for real-time retrieval  
- Core business logic modularized in `/core`  

### **Backend**
- Built with **FastAPI**
- Well-structured API routing
- Easy to scale and deploy using containers

### **Frontend**
- Developed using **Streamlit**
- Clean and interactive UI
- Connects directly to FastAPI backend

---

## 🏗️ Project Architecture


---
Streamlit UI → FastAPI Backend → LLM (Groq API)
↓
Tavily Search

## 🐳 Docker Support
The entire application (backend + frontend) is containerized.

### **Build Image**
```bash
docker build -t llm-app .

Run Container

docker run -p 8000:8000 llm-app

🔁 CI/CD with Jenkins

Configured a full automation pipeline:

GitHub → Jenkins Webhook Trigger

SonarQube Quality Gate

Docker Image Build

Push to AWS ECR

Deploy to AWS Fargate

Pipeline stages include:

Checkout

Code scan (SonarQube)

Build Docker image

Push to ECR

Deploy to AWS

☁️ Deployment on AWS

Container hosted on AWS ECR

Fully managed deployment using AWS Fargate

Auto-scaling, secure, pay-per-use

🔑 Environment Variables

Create a .env file:

🚀 Run Locally

Step 1: Install dependencies
pip install -r requirements.txt

Step 2: Start FastAPI
uvicorn api.main:app --reload

Step 3: Start Streamlit
streamlit run frontend/app.py
