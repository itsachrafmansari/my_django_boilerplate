# Django Backend Boilerplate
Since I primarily use Django to build the backend of my projects very often, I created this backend boilerplate to speed up the process of creating and configuring new projects.


## Features
- **Pre-configured Django settings** for development and production environments.
- **User authentication system** with login, logout, and registration functionality.

## Project Structure
```
my_django_boilerplate/
├── config/             # Main Django application
├── dummy_app/          # A dummy Django application
├── users/              # Users registeration and authentication app
├── .env.example        # An example of the used environement varibales
├── manage.py
├── requirements.txt    # The project's dependencies
└── setup.py            # The project installer
```

## Getting Started

### Prerequisites
This project is developed and tested using :
- Python 3.13
- Django 5.1

### Installation

#### 1. Clone the Repository
```
git clone https://github.com/itsachrafmansari/my_django_boilerplate.git
cd my_django_boilerplate
```

#### 2. Create a Virtual Environment (optional but recommended)
```
python3 -m venv venv
source venv/bin/activate   # For Linux/macOS
venv\Scripts\activate     # For Windows
```

#### 3. Set Up the Project with setup.py

Run the setup script to install dependencies and configure the environment.
```
python setup.py
```
This will:
- Install all requirements from requirements.txt. 
- Create a .env file from .env.example with a newly generated Django SECRET_KEY.

#### 5. Apply Migrations
```
python manage.py migrate
```

#### 6. Run the Development Server
```
python manage.py runserver
```

## Contributing

Contributions are welcome!

Please fork the repository and create a pull request.

1. Fork the repository 
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature-name`)
5. Open a pull request
