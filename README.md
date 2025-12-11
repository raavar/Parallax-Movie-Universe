# Parallax - Movie Universe

*Live Access:* [parallax-movie-universe.webredirect.org](http://parallax-movie-universe.webredirect.org)

*Github Repository:* [repository](https://github.com/raavar/Parallax-Movie-Universe)

## About The Project

*Parallax - Movie Universe* is a comprehensive, full-stack web application designed to be your personal gateway to the cinematic world. It combines the utility of a robust movie catalog with the intelligence of a personalized recommendation system.

The platform allows users to explore an extensive library of films, view detailed metadata, and track their personal viewing journey through "Watchlists" and "Seen" histories.

The core philosophy of Parallax is *Discovery*. By leveraging a custom Machine Learning engine, the application analyzes your unique rating patterns to surface movies you are statistically likely to enjoy. Whether you are looking for a hidden gem similar to your favorite indie drama or the next big blockbuster matching your action preferences, Parallax tailors the homepage specifically to you.

---

## Features & Implementation Credits

This project is the result of a collaborative effort, combining backend engineering, frontend design, and data science.

* * User Authentication System
    * Implementation: Secure login and registration functionality using hashed passwords and session management.
    * Credit: *Zaharioiu Robert*

* * Email Verification
    * Implementation: A security layer that sends confirmation emails with unique tokens upon registration to verify user identity before granting access.
    * Credit: *Panciu Andre*

* * Advanced Profile Management
    * Implementation: User settings allowing for username updates, email changes, and password resets.
    * Credit: *Trăistaru Alexandra*

* * QR-Based Profile Sharing
    * Implementation: A social feature that generates a unique QR code for every user profile, allowing friends to instantly scan and view each other's watchlists and histories.
    * Credit: *Trăistaru Alexandra*

* * Movie Database & Catalog
    * Implementation: A paginated, searchable, and filterable catalog view that allows users to browse the entire movie collection by genre and release year.
    * Credit: *Zaharioiu Robert* (Core Logic) & *Trăistaru Alexandra* (UI/UX)

* * AI Recommendation Engine
    * Implementation: A Hybrid Machine Learning system using PyTorch. It utilizes TF-IDF for text analysis and vector space modeling for numerical features (budget, ratings) to predict and display movie suggestions on the homepage based on user ratings.
    * Credit: *Panciu Andre*

* * Movie Details & Actions
    * Implementation: A rich detail view fetching global critic scores, posters, and descriptions. It integrates user actions: rating movies (1-10), toggling "Watchlist" status, and marking films as "Seen".
    * Credit: *Trăistaru Alexandra*

* * Live Search
    * Implementation: An interactive search bar that provides a dropdown of possible movie matches as you type. Pressing enter redirects to a full search results page.
    * Credit: *Trăistaru Alexandra*

* * UI/UX Design
    * Implementation: The complete visual identity of the website, including responsive grid layouts and interactive elements.
    * Credit: *Trăistaru Alexandra*

* * OMDb API Integration
    * Implementation: A data pipeline that fetches missing metadata (Posters, IMDb Votes, Box Office, Metascore) from external APIs to enrich the local database.
    * Credit: *Panciu Andre*

* * Database Architecture
    * Implementation: The initial PostgreSQL schema design and SQLAlchemy models. Additional fields for ML and UI features were iteratively added by the team.
    * Credit: *Zaharioiu Robert* (Core), extended by *Panciu Andre* & *Trăistaru Alexandra*

* * Docker Infrastructure
    * Implementation: Containerization of the application (Web, DB) using Docker and Docker Compose for consistent development environments. *Panciu Andre* implemented the Caddy reverse proxy integration.
    * Credit: *Zaharioiu Robert* & *Panciu Andre*

* * Global Oracle Deployment
    * Implementation: Configuration of the production environment on Oracle Cloud, including firewall management, HTTPS setup with Caddy, and live server maintenance.
    * Credit: *Panciu Andre*

---

## Team Contributions Summary

| Member | Primary Focus Areas | Key Contributions |
| :--- | :--- | :--- |
| *Panciu Andre* | *DevOps & Data Science* | • ML Recommendation Engine (PyTorch)<br>• Oracle Cloud Deployment & Firewall<br>• Caddy Reverse Proxy Setup<br>• External API Data Harvesting<br>• Email Confirmation System |
| *Trăistaru Alexandra* | *Frontend & Features* | • Complete UI/UX Design & CSS<br>• Interactive Search & Movie Details<br>• Profile Management & QR Code<br>• Complex Catalog Filtering & Pagination |
| *Zaharioiu Robert* | *Backend & Architecture* | • Core Flask App Structure & Auth<br>• Database Schema & Initialization<br>• Docker Containerization<br>• Centralized Routing Logic |

---

## Development Challenges & Solutions

Building Parallax was a complex process involving distributed systems, AI integration, and full-stack development. Here are some of the critical scenarios we faced.

### Panciu Andre
1.  *Oracle Cloud Instability:* Implementing the global server was a battle against network configurations. We faced repeated connection timeouts between the Docker containers and the database due to strict iptables rules on the Oracle VM, which required writing custom bash scripts to manage the firewall.
2.  *The "Weighting" Problem:* The initial ML model treated all features equally. This led to poor recommendations where movies were linked purely by genre tags rather than quality. We had to iteratively tune the tensor weights (giving 40% importance to IMDb scores) to make the AI "smart."
3.  *API Rate Limits:* The OMDb API provides a limited number of requests per day. During the database population testing, we hit this limit rapidly, requiring us to implement logic to detect failures and manual intervention to rotate API keys.
4.  *Pagination Bugs:* A persistent bug in the catalog view caused the "Current Page" counter to disappear or show blank values. This was traced back to a disconnect between the backend pagination object and the Jinja2 template, which was fixed by explicitly passing the pagination metadata.

### Trăistaru Alexandra
1.  *Design Complexity:* Creating a cohesive "Movie Universe" theme that looked professional took significant time. Balancing the aesthetic with readable text and ensuring the grid layouts (for movie cards) didn't break on different screen sizes required multiple refactors of the CSS.
2.  *QR Code Logic:* The initial implementation of the QR generator would sometimes create invalid links because it wasn't correctly detecting the application context (local vs. production URL). We had to rewrite the generator to dynamically fetch the external server root.
3.  *Catalog Filtering:* Implementing multi-criteria filtering (Year + Genre + Sort) was challenging. Initially, applying a new filter would reset the others. We had to restructure the form logic to persist all selected parameters across page reloads and pagination clicks.
4.  *Live Search Interaction:* The search bar originally had a "race condition" where clicking a result would close the dropdown menu (due to the blur event) before the click was registered. We solved this by using mousedown events to prioritize the user's selection.

### Zaharioiu Robert
1.  *Docker "Cold Start" Errors:* The initial setup faced a race condition where the Flask app would try to connect to the Database container before PostgreSQL had finished booting up. This was extremely hard to debug, but we solved it by adding a sleep command in the Makefile to synchronize the startup sequence.
2.  *Routing Architecture:* At the start, we attempted to split routes into multiple files for cleanliness, but this caused circular import errors and context issues. We ultimately had to refactor the entire backend to use a centralized routes.py and __init__.py factory pattern.
3.  *Database Persistence:* We struggled with data persistence during development. We had to refine the Docker volume management to ensure user data survived container restarts while still allowing us to wipe the database structure when models changed.
4.  *Model Migrations:* Adding new columns (like poster_url) after the database was already created caused the app to crash. Since we weren't using Alembic, we developed a workflow to wipe and re-seed the database cleanly without breaking the admin configuration.

---

### Conclusion

In the end, this project taught us a lot about Python, database implementations, and backend architecture. It gave us hands-on experience with specific technologies like Flask, PostgreSQL, and APIs, while forcing us to solve real-world problems related to deployment, security, and data management. It bridged the gap between theoretical code and a live, functioning product.
