# Zoho Books MCP Server

This project provides a Python/FastAPI application to manage multiple Zoho Books accounts and expose an MCP (Micro Control Protocol) interface to interact with them via automated tools.

The application allows you to:

*   **Manage Zoho Accounts:** Connect, select, and manage multiple Zoho Books accounts.
*   **OAuth Authentication:** Use Zoho's OAuth flow to obtain and refresh access tokens.
*   **MCP Interface:** Expose a dedicated URL (`/mcp`) for an external MCP server to fetch credentials and perform Zoho Books operations.
*   **Integrated Documentation:** Access the tools documentation directly from the web interface.

## Prerequisites

*   **Docker:** Ensure you have [Docker](https://docs.docker.com/get-docker/) installed and running.
*   **Docker Compose:** Ensure you have [Docker Compose](https://docs.docker.com/compose/install/) installed.

## Project Setup

1.  **Clone the Repository:**

    ```bash
    git clone <URL_OF_YOUR_REPOSITORY>
    cd <NAME_OF_YOUR_REPOSITORY>
    ```

2.  **Configure Environment Variables:**

    Create a `.env` file in the project root based on the `.env.example` (if it exists) or according to the variables needed as defined in `config.py` and `docker-compose.yml`. You will need to define at least the following variables (adjust values according to your Zoho environment):

    *   `ZOHO_CLIENT_ID`: Your Zoho application's Client ID.
    *   `ZOHO_CLIENT_SECRET`: Your Zoho application's Client Secret.
    *   `ZOHO_REDIRECT_URI`: The redirect URI configured in your Zoho application (default is `http://localhost:8000/oauth/callback`).
    *   `MCP_PORT`: Internal port for the MCP interface (default is `8001`).
    *   `APP_PORT`: External port for the web interface (default is `8000`).

    Example `.env` content:
    ```env
    ZOHO_CLIENT_ID=your_client_id_here
    ZOHO_CLIENT_SECRET=your_client_secret_here
    ZOHO_REDIRECT_URI=http://localhost:8000/oauth/callback
    MCP_PORT=8001
    APP_PORT=8000
    ```

3.  **Build and Run with Docker Compose:**

    ```bash
    docker-compose up -d --build
    ```

    This command will build the application image (if needed) and start the containers defined in `docker-compose.yml` in the background (`-d`).

## Usage

1.  **Access the Web Interface:**

    Open your web browser and navigate to `http://localhost:[APP_PORT]` (default is `http://localhost:8000`).
    *   Here, you can manage your Zoho Books accounts (connect new ones, select the active one, delete).
    *   You will see the MCP server URL that your external agent or tool should use.

2.  **Connect a Zoho Account:**

    *   In the web interface, click the "🚀 Connect Zoho Books" button.
    *   Log in to your Zoho account and authorize the application.
    *   If it's a new account without an organization, you will be redirected to the Zoho Books setup page to create one.

3.  **Use the MCP Interface:**

    Your external MCP server should point to `http://localhost:[APP_PORT]/mcp` (e.g., `http://localhost:8000/mcp`) to interact with Zoho Books through this application.

4.  **Access Tools Documentation:**

    *   In the main web interface, click the "📘 Tools Documentation" button.
    *   A new page will open with detailed documentation on the available tools and their responses.

5.  **Stop the Containers:**

    ```bash
    docker-compose down
    ```

## Project Structure

*   `docker-compose.yml`: Defines the Docker services (app, db) and their configurations.
*   `Dockerfile`: Instructions to build the Docker image for the Python application.
*   `.env`: File to define sensitive environment variables (not included in version control).
*   `src/`: Main directory for the Python application code.
    *   `main.py`: Main application entry point (if applicable).
    *   `routes.py`: Defines web routes and business logic.
    *   `auth.py`: Handles Zoho OAuth authentication and token management.
    *   `templates.py`: Contains HTML template rendering functions.
    *   `docs.py`: Contains the HTML template for tools documentation.
    *   `utils.py`: Utility functions.
*   `config.py`: Configuration settings (e.g., ports, Zoho API details).
*   `zoho_tokens.db`: SQLite database file (persists inside the container's volume by default).

## Notes

*   The application uses SQLite to store account information and tokens. The database file `zoho_tokens.db` is typically persisted using a Docker volume.
*   Ensure the `ZOHO_REDIRECT_URI` matches exactly the one configured in your Zoho Developer Console for the OAuth callback to work correctly.
*   This application acts as an intermediary, managing Zoho credentials and providing an MCP endpoint. Ensure its security when deployed.
