# Aviation Conversational BI Chatbot 🛫

A secure, conversational Business Intelligence application for aviation data analysis with AI-powered natural language to SQL conversion.

## Features ✨

- 🔒 **Secure Authentication** - User login system to protect your BI data
- 💬 **Conversational Interface** - Chat-like UI with conversation history
- 🤖 **AI-Powered SQL Generation** - Uses Google Gemini to convert natural language to SQL
- 📊 **Automatic Visualizations** - Bar charts, pie charts, and line charts
- 📝 **Query History** - Keep track of all your queries and results
- 🎨 **Clean UI** - Modern, user-friendly Streamlit interface

## Authentication 🔐

The app includes a built-in authentication system to secure access to your BI data.

### Default Users

| Username | Password   | Role    |
| -------- | ---------- | ------- |
| admin    | admin123   | Admin   |
| analyst  | analyst123 | Analyst |

### Customizing Users

To add or modify users, edit the `.env` file:

```env
# Add new users
USER1_USERNAME=your_username
USER1_PASSWORD=your_password

USER2_USERNAME=another_user
USER2_PASSWORD=another_password
```

**⚠️ Important Security Notes:**

- Change default passwords before deploying to production
- Consider implementing password hashing for production use
- Never commit the `.env` file to version control
- For production, consider using a proper authentication service (OAuth, Auth0, etc.)

## Installation 🚀

1. **Clone or download the project**

2. **Install dependencies**

   ```bash
   pip install streamlit pandas sqlalchemy matplotlib python-dotenv requests
   ```

3. **Set up environment variables**

   - Create a `.env` file in the project root
   - Add your Gemini API key and user credentials:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here

   USER1_USERNAME=admin
   USER1_PASSWORD=admin123

   USER2_USERNAME=analyst
   USER2_PASSWORD=analyst123
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Usage 📖

1. **Login** - Enter your username and password on the login page
2. **Ask Questions** - Type natural language questions about the aviation data
3. **View Results** - See the generated SQL, query results, and visualizations
4. **Review History** - Scroll through past queries and responses
5. **Logout** - Click the logout button when finished

### Example Questions

- "Count passengers by Nationality"
- "Show top 5 airports by passenger count"
- "What is the average age of passengers?"
- "List all flights with delayed status"
- "How many passengers traveled to each continent?"

## Security Best Practices 🛡️

For production deployment:

1. **Use Environment Variables** - Already implemented via `.env` file
2. **Implement Password Hashing** - Use bcrypt or similar libraries
3. **Add Rate Limiting** - Prevent brute force attacks
4. **Use HTTPS** - Deploy with SSL/TLS encryption
5. **Session Timeout** - Add automatic logout after inactivity
6. **Audit Logging** - Track user access and queries
7. **Role-Based Access Control** - Implement different permission levels

## Project Structure 📁

```
airlineStreamlit/
├── app.py                 # Main application file
├── load_data.py          # Data loading script
├── aviation.db           # SQLite database
├── Airline_Dataset.csv   # Raw data file
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Technologies Used 🛠️

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation
- **SQLAlchemy** - Database connectivity
- **Matplotlib** - Data visualization
- **Google Gemini AI** - Natural language to SQL conversion
- **Python-dotenv** - Environment variable management
- **SQLite** - Database

## Future Enhancements 🔮

- [ ] Advanced password hashing with bcrypt
- [ ] Multi-factor authentication (MFA)
- [ ] Role-based access control (RBAC)
- [ ] User registration and password reset
- [ ] Session management with expiration
- [ ] Audit logs for compliance
- [ ] OAuth integration (Google, Microsoft, etc.)
- [ ] Admin dashboard for user management

## License 📄

This project is for educational purposes.

## Support 💪

For issues or questions, please create an issue in the repository.

---

**⚠️ Security Reminder**: Always change default credentials before deploying to production!
