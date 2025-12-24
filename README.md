# The Voyager
#### Video Demo:  <URL HERE>
#### Description:

An AI-powered travel itinerary generator that creates personalized multi-day trip plans using OpenAI's GPT-5-nano model.

## Features

- **AI-Powered Itinerary Generation**: Generates detailed day-by-day travel itineraries based on destination and preferences
- **User Authentication**: Secure user registration and login system
- **Trip Management**: Save and view multiple trip itineraries
- **Day Regeneration**: Regenerate individual days if you want alternative suggestions
- **Personalization**: Customize itineraries with preferences (budget, interests, dietary restrictions, etc.)

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **AI**: OpenAI API (gpt-5-nano model)
- **Frontend**: HTML, CSS, Bootstrap
- **Security**: CSRF protection, password hashing, session management

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd voyager
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database**
   ```bash
   mysql -u root -p
   ```
   
   Then run the following SQL commands:
   ```sql
   CREATE DATABASE voyager_db;
   CREATE USER 'voyager_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON voyager_db.* TO 'voyager_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

5. **Initialize the database schema**
   ```bash
   mysql -u voyager_user -p voyager_db < schema.sql
   ```

6. **Configure environment variables**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   
   - Edit `.env` and add your credentials:
     ```
     SECRET_KEY=<generate-with-python-secrets>
     OPENAI_API_KEY=<your-openai-api-key>
     DB_PASSWORD=<your-mysql-password>
     ```
   
   - Generate a secure SECRET_KEY:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

## Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:5000`

3. **Create an account and start planning trips!**

## Usage

1. **Register**: Create a new account
2. **Login**: Sign in with your credentials
3. **Create Trip**: 
   - Click "New Trip"
   - Enter destination (e.g., "Paris", "Tokyo")
   - Specify number of days (1-30)
   - Add preferences (optional): budget level, interests, dietary restrictions, etc.
   - Click "Generate Itinerary"
4. **View Itinerary**: See your AI-generated day-by-day plan
5. **Regenerate Days**: Click regenerate on any day to get alternative suggestions

## Project Structure

```
voyager/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models and operations
├── openai_service.py     # OpenAI API integration
├── schema.sql            # Database schema
├── .env                  # Environment variables (not in git)
├── .env.example          # Example environment variables
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── new_trip.html
│   └── itinerary.html
├── static/               # Static files (CSS, JS, images)
└── requirements.txt      # Python dependencies
```

## API Information

This application uses the OpenAI API with the `gpt-5-nano` model and the `responses.create()` method. Make sure your API key has access to this model.

## Security Notes

- Never commit your `.env` file to version control
- Always use environment variables for sensitive information
- Change default passwords in production
- Use HTTPS in production environments
- Keep your API keys secure

## Troubleshooting

### Port 5000 already in use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill //F //PID <PID>
```

### Database connection errors
- Verify MySQL is running
- Check credentials in `.env` file
- Ensure database and user exist

### OpenAI API errors
- Verify your API key is correct
- Check you have API credits
- Ensure the key has access to gpt-5-nano model

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for the GPT-5-nano API
- Flask framework
- Bootstrap for UI components 
- Claude AI for coding assistance
