# BulkMail Pro

BulkMail Pro is a Flask-based web application designed to manage bulk email campaigns. It includes features such as user authentication, SMTP configuration, email logs, activity logs, and an admin panel for managing users and monitoring system activity.

---

## Features

- **User Authentication**: Secure login, signup, and password reset functionality.
- **Admin Panel**: Manage users, view activity logs, and monitor email logs.
- **SMTP Configuration**: Users can configure their own SMTP settings for sending emails.
- **File Management**: Temporary file uploads with automated cleanup.
- **Email Sending**: Send bulk emails to addresses extracted from uploaded text files.
- **Activity Tracking**: Logs user actions and email-sending activities.

---

---

## Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/bulkmail-pro.git](https://github.com/your-username/bulkmail-pro.git)
    cd bulkmail-pro
    ```

2.  **Set Up a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` File**
    Create a `.env` file in the root directory with the following content:

    ```env
    SECRET_KEY=your-secret-key
    SMTP_SERVER=smtp.example.com
    SMTP_PORT=587
    SMTP_EMAIL=admin@example.com
    SMTP_PASSWORD=yourpassword
    ```

5.  **Initialize the Database**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

6.  **Run the Application**
    ```bash
    python app.py
    ```

---

## Usage

* Access the application at `http://localhost:5000`.
* Use the `/admin` route to access the admin panel (login required).
* Configure SMTP settings in the `/account` route to send emails.

---

## Example: Sending Emails

1.  Upload a `.txt` file containing email addresses (one per line) to the `/uploads` folder.
2.  Configure your SMTP settings in the `/account` page.
3.  Send emails via the appropriate route or interface.

---

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch:
    ```bash
    git checkout -b feature/YourFeatureName
    ```
3.  Commit your changes:
    ```bash
    git commit -m 'Add some feature'
    ```
4.  Push to the branch:
    ```bash
    git push origin feature/YourFeatureName
    ```
5.  Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Additional Notes

* Ensure that all sensitive information (e.g., SMTP credentials) is stored securely using environment variables.
* For production deployment, use a WSGI server like Gunicorn and host the application on platforms like Heroku, AWS, or DigitalOcean.
* Regularly back up your SQLite database (`instance/users.db`) to prevent data loss.
* For any questions or issues, feel free to open an issue on GitHub.
## Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/bulkmail.git]
    cd bulkmail
    ```

2.  **Set Up a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` File**
    Create a `.env` file in the root directory with the following content:

    ```env
    SECRET_KEY=your-secret-key
    SMTP_SERVER=smtp.example.com
    SMTP_PORT=587
    SMTP_EMAIL=admin@example.com
    SMTP_PASSWORD=yourpassword
    ```

5.  **Initialize the Database**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

6.  **Run the Application**
    ```bash
    python app.py
    ```

---

## Usage

* Access the application at `http://localhost:5000`.
* Use the `/admin` route to access the admin panel (login required).
* Configure SMTP settings in the `/account` route to send emails.

---

## Example: Sending Emails

1.  Upload a `.txt` file containing email addresses (one per line) to the `/uploads` folder.
2.  Configure your SMTP settings in the `/account` page.
3.  Send emails via the appropriate route or interface.

---

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch:
    ```bash
    git checkout -b feature/YourFeatureName
    ```
3.  Commit your changes:
    ```bash
    git commit -m 'Add some feature'
    ```
4.  Push to the branch:
    ```bash
    git push origin feature/YourFeatureName
    ```
5.  Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Additional Notes

* Ensure that all sensitive information (e.g., SMTP credentials) is stored securely using environment variables.
* For production deployment, use a WSGI server like Gunicorn and host the application on platforms like Heroku, AWS, or DigitalOcean.
* Regularly back up your SQLite database (`instance/users.db`) to prevent data loss.
* For any questions or issues, feel free to open an issue on GitHub.
