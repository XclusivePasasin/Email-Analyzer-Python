# Email-Analyzer-Python
The objective of this project is to develop an automated procedure to analyze email inboxes, identify and download attachments in .json and .pdf format, and perform subsequent analysis on these files. If no files with the specified extensions are found, the procedure is skipped.

## Installation

In order to install the project, we will create a .venv to install the dependencies

# Step One
```bash
  pip install virtualenv
```
# In case of error
```bash
  Set-ExecutionPolicy Bypass -Scope Process
```
# Step Two
```bash
  python -m venv venv
  virtualenv venv
```
# Step Three
```bash
  .\venv\Scripts\activate  
```
Once the .venv terminal is installed and running, install the dependencies by running
# Step Four
```bash
  pip install -r requirements.txt
```
To disable the virtual environment
```bash
  deactivate 
```
