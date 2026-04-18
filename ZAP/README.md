# ZAP EATS - Online Food Ordering System

A modern and responsive online food ordering system specializing in Indian cuisine. Built with Flask, MySQL, and Bootstrap.

## Features

- User authentication (login/signup)
- Browse Indian food menu
- Add items to cart
- View cart and checkout
- Responsive design for all devices
- Modern UI with animations

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd zap-eats
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix/MacOS
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up the MySQL database:
- Open MySQL command line or MySQL Workbench
- Run the SQL commands from `db.sql` to create the database and tables

5. Configure the database connection:
- Open `app.py`
- Update the `db_config` dictionary with your MySQL credentials:
```python
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'zap_eats'
}
```

6. Run the application:
```bash
python app.py
```

7. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
zap-eats/
├── app.py              # Main Flask application
├── db.sql              # Database schema and sample data
├── requirements.txt    # Python dependencies
├── static/            # Static files (images, CSS, JS)
│   └── images/        # Food product images
└── templates/         # HTML templates
    ├── base.html      # Base template
    ├── index.html     # Home page
    ├── login.html     # Login page
    ├── signup.html    # Signup page
    └── cart.html      # Shopping cart page
```

## Technologies Used

- Backend: Python Flask
- Database: MySQL
- Frontend: HTML5, CSS3, Bootstrap 5
- Icons: Font Awesome
- Authentication: Flask-Login

## Contributing

Feel free to submit issues and enhancement requests! 