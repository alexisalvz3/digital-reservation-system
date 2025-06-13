# 🍽️ Digital Reservation System

A cloud-native, containerized table reservation and notification system built for restaurants. This application serves as a real-world showcase of DevOps, backend engineering, and cloud architecture skills using **FastAPI**, **Docker**, **AWS**, and **CI/CD pipelines**.

---

## 🚀 Features

- 🗓️ **Table Reservations:** Customers can reserve tables via a RESTful API.
- 🔐 **Admin Controls:** Basic auth-protected endpoints for admins to delete or update reservations.
- ✉️ **Notification Logging:** Logs every notification event with time, status, and delivery method.
- 📲 **SMS Alerts:** Integration with Twilio for outbound SMS reservation confirmations.
- 📦 **Containerized App:** Runs in Docker, fully isolated and reproducible.
- ☁️ **Secrets Management:** AWS Secrets Manager securely stores sensitive credentials.
- 🔁 **CI/CD with GitHub Actions:** Automated test pipeline for every push to `main`.

---

## 🏗️ Tech Stack

| Category        | Technology                     |
|----------------|---------------------------------|
| Backend         | FastAPI (Python 3.11)          |
| Database        | SQLite (local dev), SQLAlchemy |
| Containerization| Docker, docker-compose         |
| Messaging       | Twilio API (SMS)               |
| Cloud Services  | AWS Secrets Manager            |
| CI/CD           | GitHub Actions + Pytest        |

---


## 🧪 Running Tests

This project uses **Pytest** and GitHub Actions to verify functionality.

To run tests locally:

```bash
source venv/bin/activate
pytest tests/
```

# Build and run the container
docker-compose up --build

# Access the app locally
http://localhost:8000/docs

# 🔐 Environment Variables & Secrets

The application uses AWS Secrets Manager to manage:

* `ADMIN_USERNAME`
* `ADMIN_PASSWORD`
* `TWILIO_ACCOUNT_SID`
* `TWILIO_AUTH_TOKEN`

When developing locally, use a `.env` file or set environment variables manually.

## 🛠️ AWS Services Used

* **Secrets Manager** — Securely stores admin credentials & Twilio keys
* **EC2 (for future deployment)** — Run containers with scaling potential
* **CloudWatch (optional)** — Monitor logs and metrics
* **ECS (optional)** — Container orchestration platform for future deployment

## 🔒 Security

* Admin-only routes are protected with HTTP Basic Auth.
* Sensitive keys never live in code—loaded at runtime via Secrets Manager.
* Uses `secrets.compare_digest()` to prevent timing attacks.

## ✅ Roadmap

* Containerize FastAPI app
* Add admin authentication
* Implement reservation CRUD routes
* Send SMS via Twilio
* Log all notification attempts
* GitHub Actions test workflow
* Deploy to ECS or EC2 using IaC
* Replace SQLite with RDS (MySQL/PostgreSQL)
* Add ordering system and menu integration

## 👤 Author

**Alexis Alvarez** Cloud & DevOps Engineer in training  
📫 alexis-cloud.com • GitHub: @alexisalvarez

📄 License

MIT — Free to use, fork, and build upon.

