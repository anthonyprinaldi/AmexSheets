# AmexSheets
Python code to process Amex expense reports and populate GSheets expense tracking spreadsheet

## Usage

### Installation

Run the below commmand to install the package.

```bash
pip install -e .
```

### Pre-requisites

1. Create a Google Cloud project and enable Google Sheets API.
2. Create a service account and download the credentials JSON file (save at `./token.json`).
3. Share the Google Sheets file with the service account email.
<!-- 4. Create a `.env` file in the root directory with the below content. -->

<!-- ```bash
GOOGLE_SHEETS_CREDENTIALS_FILE_PATH=<path_to_credentials_json_file>
GOOGLE_SHEETS_FILE_ID=<google_sheets_file_id>
``` -->


### Running the code

Run the below command to see the help message.

```bash
python main.py --help
```