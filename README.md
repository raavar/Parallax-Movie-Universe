# Architectural Documentation

## Project title: Parallax - Movie Universe

### Members:

* Panciu Andre
* Trăistaru Alexandra
* Zaharioiu Robert-Nicolae

## Getting Started (Development Setup)

**To set up the project locally and begin development, please refer to the dedicated guide: [DEVELOPMENT.md](DEVELOPMENT.md)**. This file contains all necessary Docker commands for building, running, and testing code changes.

## Introduction:

The “Parallax - Movie Universe” project aims to develop a comprehensive, Python-predominant web application that serves as a personalized movie discovery and tracking platform. The application is designed to combine the informational depth of a movie database like IMDb with the user-centric, personalized functionalities of a service such as Netflix.

Key features include a detailed movie catalog, personalized user profiles where users can manage “Seen” and “To Watch” lists, and assign individual ratings to films.

A crucial component is the integration of a Machine Learning model designed to provide tailored movie recommendations based on the user’s preferences and viewing history.

## System Overview:

The application will employ a layered architecture built predominantly on Python to ensure a cohesive development experience.

The foundation of the system is the Data Layer, utilizing a robust database to store essential user authentication details, personalized profiles, and the comprehensive movie catalog.

The core business logic resides within the Application Layer (the Python backend, likely utilizing a full-stack framework such as Django/Flask or a combination of FastAPI and a dedicated Python frontend library), which initially focuses on critical User Authentication and Authorization. This layer then manages the CRUD operations (Create, Read, Update, Delete) central to the platform: enabling users to seamlessly interact with the shared movie catalog and manage their private “Seen” and “To Watch” lists, including personal rating.

A key differentiating component is the Machine Learning Recommendation Engine, which operates as a dedicated, asynchronous module to process user interaction data and generate personalized, contextual movie suggestions.

The system will integrate secondary utility features, such as the capability for data exporting (CSV) of movie lists and the functionality to generate and scan unique QR codes for user profiles, enhancing data interoperability and user connectivity.

## Detailed Component Design:

This section outlines the structure and inter-component communication within the project system, detailing the function and interfacing mechanisms of the four major modules.

### Backend / Core Application Layer

This layer serves as the central orchestrator and houses the application’s business logic.

**Functionality:** Manages all client-server interactions (HTTP requests), handles user sessions (Authentication/Authorization), processes CRUD logic for user lists and catalog additions, and coordinates services from other components.

**Interfaces:**

* to Presentation Layer (Frontend [HTML + CSS + JS]): communication occurs via HTTP/HTTPS. (e.g. POST for login, GET for movie details)
* to Data Layer: communication is achieved through the Object-Relational Mapping (ORM) layer
* to ML Engine: the Core Layer triggers the recommendation generation by making an internal module call or query to a dedicated local API endpoint within the application

### Data Layer

This component provides a structured, secure interface for persistent data storage and retrieval.

**Functionality:** Defines the database schemas (models for User, Movie, Rating, Lists) and performs all transactional operational (CRUD) requested by the Backend.

**Interfaces:**

* to Backend: exposes high-level methods defined by the ORM
* to Physical Database: translates ORM calls into optimized SQL queries for the chosen database

### Machine Learning Recommendation Engine

The ML Engine is a specialized, dedicated module responsible for personalized content discovery. We will try to use PyTorch.

**Functionality:** Takes user activity as input, processes it using the recommendation algorithm, and outputs a ranked lists of suggested movies.

**Interfaces:**

* to Data Layer: the engine reads necessary data directly from the Data Layer
* to Backend: the engine returns a Python list of recommended movies

### Utility Modules (Data Export and QR Code)

These modules handle specific output generation tasks that are secondary to the core movie catalog functionality.

**Functionality:**

* QR module: takes a unique User ID and generate a QR code image that encodes the user’s profile URL
* Export module: takes a set of movie data and formats it into a downloadable file (CSV)

**Interfaces:**

* to Backend: both modules are invoked by internal function calls from the Core Layer upon user action
* to Presentation Layer: they return either the image data (QR code) for inline display or a file stream/object that the Backend passes back to the user’s browser for immediate download

## Deployment and Testing:

The application is initially designed for local execution within a standard server environment (local host). Requirements include a Python interpreter (v3.x), the chosen database system, and all necessary Python dependencies.

**Deployment:** containerization (using Docker) may be explored to ensure a consistent execution environment for the team

**Testing:** manual testing and peer code reviews during the development phase

## Conclusion:

The projected complexity is significant, driven by the requirement to master a full-stack web framework and successfully integrate the database and the core Machine Learning component.

We aim to implement all the features outlined above, but the project scope may be adjusted if we realize during development that we have overcomplicated the design and our goals (features).
