# AI-LLM-RAG: Student-Centric Education System

An intelligent education assistant that combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), semantic search, and SQL-based querying to provide students with context-aware answers from educational documents and structured academic data.

## Overview

The AI-LLM-RAG Student-Centric Education System is a student-focused question-answering application designed to provide a unified interface for accessing academic information from different sources.

The system handles two major types of information:

- Unstructured information such as syllabus, course materials, and educational PDFs.
- Structured information such as student details, marks, attendance, and faculty information.

A Decision LLM analyzes the user's query and routes it to the appropriate processing pipeline:

- RAG Pipeline for document-based questions
- SQL Pipeline for structured database questions
- General LLM for general questions

The final response is presented through a Streamlit web interface.

## Problem Statement

Educational information is distributed across multiple sources such as documents, academic records, and databases.

Students may need to:

- Search through lengthy educational documents.
- Find specific information from academic databases.
- Query structured student information.
- Ask questions in natural language without knowing SQL or database structure.

A conventional LLM-based system may not have direct access to institution-specific documents or structured academic data and may generate unsupported responses.

Therefore, this project aims to develop an intelligent system that can identify the type of information required and use the appropriate knowledge source to generate the response.

## Proposed Solution

The proposed system uses a Decision LLM as the central query-routing component.

The Decision LLM analyzes the user's question and routes it to one of three processing paths:

1. RAG Pipeline
2. SQL Pipeline
3. General LLM

The RAG pipeline retrieves relevant information from educational documents and uses the retrieved context to generate an answer.

The SQL pipeline processes structured academic information stored in an SQLite database.

The General LLM handles questions that do not require information from the project's document collection or database.

## System Architecture

The overall system follows the workflow:

User Query → Streamlit Interface → Decision LLM → RAG / SQL / General LLM → Final Answer

### RAG Pipeline

Educational PDFs → PDF Text Extraction / OCR → Text Chunking → Text Embeddings → FAISS Vector Store → Semantic Similarity Search → Relevant Context → RAG LLM → Final Answer

### SQL Pipeline

User Query → Decision LLM → Database Schema → SQL Query Generation → SQLite Database → SQL Execution → Database Result → Natural Language Response

## Key Components

### 1. Decision LLM

The Decision LLM acts as the query-routing component. It analyzes the user's question and determines whether it should be processed through the RAG, SQL, or General LLM pipeline.

### 2. RAG Module

The RAG module retrieves relevant information from the educational document collection and provides the retrieved context to the LLM for answer generation.

### 3. Document Processing

Educational PDF documents are processed using text extraction and OCR when required. The extracted content is divided into smaller chunks for efficient retrieval.

### 4. Embedding and FAISS Retrieval

Document chunks are converted into vector representations using an embedding model. FAISS is used for semantic similarity search to retrieve the most relevant document chunks for a user query.

### 5. SQL Module

The SQL module handles structured academic information stored in SQLite. Natural-language database questions are converted into SQL queries, executed against the database, and converted into a natural-language response.

### 6. Streamlit Interface

Streamlit provides the user-facing web interface through which students can enter questions and view generated responses.

## Technology Stack

- Python
- Large Language Models
- Retrieval-Augmented Generation (RAG)
- Sentence Transformers
- FAISS
- PyPDF
- PyMuPDF
- Tesseract OCR
- Pillow
- SQLite
- Streamlit
- Git
- GitHub

## Project Structure

student-centric-rag-education-system/

    app/
        decision/
        rag/
        sql/
        ui/

    documents/

    vector_store/

    database/

    evaluation/

    research/

    docs/

    requirements.txt
    .gitignore
    README.md

## Installation and Setup

### Clone the Repository

    git clone https://github.com/<organization-name>/student-centric-rag-education-system.git

    cd student-centric-rag-education-system

### Create a Virtual Environment

For Windows:

    python -m venv venv
    venv\Scripts\activate

For Linux/macOS:

    python3 -m venv venv
    source venv/bin/activate

### Install Dependencies

    pip install -r requirements.txt

### Add Educational Documents

Place the required educational PDF documents inside the documents/ directory.

### Run the Application

    streamlit run app.py

If the main Streamlit application is located inside the app directory:

    streamlit run app/main.py

## Example Queries

### RAG Queries

- What is Retrieval-Augmented Generation?
- Explain backpropagation.
- What is semantic search?
- Explain the topics covered in the syllabus.

These questions are processed using the educational document knowledge base.

### SQL Queries

- What is the attendance of student 101?
- What are the marks of student 102?
- Show the details of student 103.
- Which faculty teaches a particular subject?

These questions are processed using the structured SQLite database.

### General Queries

- What is Artificial Intelligence?
- What is Machine Learning?
- What is a Large Language Model?

These questions can be handled through the General LLM route.

## Current Implementation

The following components have been implemented in the current project:

- Query routing using a Decision LLM
- Educational document processing
- PDF text extraction
- OCR-based text extraction
- Text chunking
- Text embeddings
- FAISS vector indexing
- Semantic similarity search
- RAG-based response generation
- SQLite database
- SQL-based querying
- Integration of RAG and SQL pipelines
- Streamlit user interface
- Handling of unavailable database records

## Future Enhancements

- Improve query-routing accuracy
- Improve retrieval accuracy
- Add more educational documents
- Expand the academic database
- Implement query rewriting
- Implement document reranking
- Explore hybrid retrieval
- Improve prompt engineering
- Evaluate larger local LLMs
- Perform systematic answer evaluation
- Analyze hallucination and unsupported responses
- Add student authentication and role-based access
- Deploy the application to the cloud

## Research References

1. Gao, Y. et al. "Retrieval-Augmented Generation for Large Language Models: A Survey."

2. Nan, L. et al. "Enhancing Text-to-SQL Capabilities of Large Language Models: A Study on Prompt Design Strategies." EMNLP 2023.

## Project Team

### Project Guide

Dr.T.Kameswara Rao  
Professor 
CSM,VVITU

### Team Members

- T.Yasaswini
- Y.Sirisha
- P.Harika
- Sk.Baji vali
- P.Beni Bavadeep
- P.Suresh

## Academic Information

Project Title: AI-LLM-RAG: Student-Centric Education System

Program: B.Tech – CSE (AI & ML)

Institution: VVIT, Nambur

Academic Year: 2026–2027

Project Status: Under Development
