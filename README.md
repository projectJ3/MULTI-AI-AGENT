# 🚀 End-to-End LLMOps Project  
LLM-powered application built with **Groq**, **Tavily**, **FastAPI**, **Streamlit**, **Docker**, **Jenkins**, **SonarQube**, and **AWS (ECR + Fargate)**.

This project demonstrates a complete **LLMOps workflow**, including model integration, backend + frontend development, containerization, CI/CD automation, code quality checks, and cloud deployment.

---

## 📌 Features

### **LLM Application**
- Integrated **Groq LLM API** for high-speed inference  
- Integrated **Tavily Search API** for real-time retrieval  
- Core business logic modularized inside `/core`  

### **Backend**
- Built with **FastAPI**
- Well-structured API routing
- Scalable and container-friendly architecture

### **Frontend**
- Built using **Streamlit**
- Clean, interactive UI
- Communicates with FastAPI backend via REST

---

## 🏗️ Project Architecture

```

Streamlit UI → FastAPI Backend → Groq LLM API
↓
Tavily Search API

````

---

## 🐳 Docker Support
The entire application (backend + frontend) is containerized.

### **Build Image**
```bash
docker build -t llm-app .
````

### **Run Container**

```bash
docker run -p 8000:8000 llm-app
```

---

## 🔁 CI/CD with Jenkins

A full automation pipeline is configured using **Jenkins**:

* **GitHub → Jenkins Webhook Trigger**
* **SonarQube Quality Gate**
* **Docker Image Build**
* **Push to AWS ECR**
* **Deploy to AWS Fargate**

### **Pipeline Stages**

1. Checkout code
2. Run SonarQube code analysis
3. Build Docker image
4. Push image to AWS ECR
5. Deploy container to AWS Fargate

---

## ☁️ Deployment on AWS

* Docker image stored in **AWS ECR**
* Application deployed via **AWS Fargate**
* Serverless, scalable, secure environment

---

## 📁 Folder Structure

```
├── core/                # Core business logic
├── api/                 # FastAPI routes & backend logic
├── frontend/            # Streamlit UI
├── config/              # Env & configuration files
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

---

## 🚀 Run Locally

### **Step 1: Install dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: Start FastAPI backend**

```bash
uvicorn api.main:app --reload
```

### **Step 3: Start Streamlit frontend**

```bash
streamlit run frontend/app.py
```

---
