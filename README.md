# Employee Leave Management System

A web application built with **Django** for managing employee leave requests, approvals, and departmental tracking.

## Features
- **User Authentication**: Employee registration, login, and profile management.
- **Leave Application**: Employees can apply for leave specifying leave type, duration, and reason.
- **Leave Tracking & Status**: Track pending, approved, and rejected leave requests.
- **HR / Admin Dashboard**: Review, approve, or reject employee leave applications.
- **Responsive UI**: Clean and intuitive interface built for desktop and mobile devices.

## Tech Stack
- **Backend**: Python, Django
- **Database**: SQLite (default)
- **Frontend**: HTML5, CSS3, JavaScript

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jayavardhan-28/employee-leave-management.git
   cd employee-leave-management
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install django
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

6. Open your browser and navigate to `http://127.0.0.1:8000/`.
