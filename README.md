# EMU-Autonomous-Golf-Cart-Project

## Table of Contents
1. [About the Project](#about-the-project)
2. [Getting Started with GitHub](#getting-started-with-github)
   - [Step 1: Create a GitHub Account](#step-1-create-a-github-account)
   - [Step 2: Set Up GitHub Desktop](#step-2-set-up-github-desktop)
   - [Step 3: Clone the Repository](#step-3-clone-the-repository)
3. [Setting Up a Virtual Environment](#setting-up-a-virtual-environment)
4. [Updating Dependencies](#updating-dependencies)
5. [Usage](#usage)
6. [Contributing to the Project](#contributing-to-the-project)

---

### About the Project

An affordable retrofit project transforming standard golf carts into autonomous vehicles, aimed at enhancing transportation on the Eastern Michigan University campus through advanced navigation, obstacle avoidance, and safety-focused design.

---

### Getting Started with GitHub

This project is hosted on GitHub, a popular platform for sharing code and collaborating on projects. Follow these steps to set up GitHub for this project.

#### Step 1: Create a GitHub Account

1. Go to [GitHub](https://github.com/) and click **Sign up** if you don’t already have an account.
2. Follow the prompts to create an account, verify your email, and set up GitHub.

#### Step 2: Set Up GitHub Desktop

Using **GitHub Desktop** makes it easy to interact with GitHub without using the command line.

1. Download **GitHub Desktop** from [desktop.github.com](https://desktop.github.com/).
2. Install and open GitHub Desktop.
3. **Sign in** with your GitHub account.
4. Familiarize yourself with GitHub Desktop’s interface, including the options to **Clone a Repository**, **Commit Changes**, and **Push to Origin**.

#### Step 3: Clone the Repository

Cloning the repository means copying it from GitHub to your local machine so you can work on it.

1. Go to the project’s repository page on GitHub.
2. Click the **Code** button, then **Open with GitHub Desktop**.
3. GitHub Desktop will open and ask where to save the repository on your computer. Choose a folder you can easily find.
4. Click **Clone** to copy the repository to your computer.

You now have a local copy of the project on your computer!

---

### Setting Up a Virtual Environment

A virtual environment keeps project-specific dependencies separate from other projects, helping avoid version conflicts.

1. **Open a Terminal**:
   - On Windows, open Command Prompt or PowerShell.
   - On Mac, open Terminal.

2. **Navigate to the Project Folder**:
   ```bash
   # On Mac/Linux
   python3 -m venv venv
   # On Windows
   py -m venv venv

3. **Activate the Virtual Environment**:
   ```bash
   # On Mac/Linux
   source venv/bin/activate
   # On Windows
   .\venv\Scripts\activate

4. **Navigate to the Project Folder**:
   ```bash
   cd path/to/project-folder

4. **Install Existing Dependencies**:
   ```bash
   pip install -r requirements.txt

5. **Install New Packages as Needed (Example: Pandas)**:
   ```bash
   pip install <package-name>

5. **Update requirements.txt with the Latest Dependencies**:
   ```bash
   pip freeze > requirements.txt

5. **Deactivate the Virtual Environment When Finished**:
   ```bash
   deactivate


---

### Notes on This README

- **Detailed GitHub Setup**: Explains GitHub setup and usage for beginners, using GitHub Desktop to simplify the process.
- **Clear Instructions for Virtual Environment**: Walks through creating, activating, and deactivating the virtual environment.
- **Step-by-Step for Dependencies**: Shows how to keep `requirements.txt` updated whenever a package is added.
- **Guidance on Contributing**: Detailed steps for updating, committing, and pushing changes ensure everyone stays in sync.

This guide will make it easy for anyone to get started, even if they’re entirely new to GitHub!


