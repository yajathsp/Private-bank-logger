# Bank Logger 

A simple command-line personal finance tracker built with Python. Bank Logger helps you keep track of your savings, pocket money, transactions, and investment records.

## Features

- **Track transactions:** Record money coming in and going out, with notes.
- **Manage balances:** Keep separate savings and pocket money balances.
- **Transfer money:** Move pocket money into savings.
- **Log investments:** Record investments in Gold, SIPs, Stocks, or custom categories.
- **View balances:** Check individual balances and your total money.
- **Transaction history:** View your 20 most recent transactions.
- **Investment history:** View recent investments and totals grouped by type.
- **Edit balances:** Update balances with an optional reason.
- **Manage investments:** Edit or delete investment records.

## Requirements

- Python 3.x
- No external Python packages are required; the program uses Python's standard library.

## How to Run

1. Clone or download this repository.
2. Open the project folder in a terminal.
3. Run:

   ```bash
   python bank_logger.py
   ```

   On some systems, you may need to use `python3 bank_logger.py` instead.

4. Follow the numbered menu options.

## Data Storage

The program stores balances, transactions, and investment records in a local JSON file named `bank_data.json`, created in the same directory as the Python script when data is saved.

**Note:** The JSON file may contain personal financial information. Keep your real financial records private and do not publish them in a public repository.

## Project Structure

```text
Bank_logger/
├── bank_logger.py
├── README.md
└── bank_data.json  # Created when data is saved
```

## Purpose

This project was built to practise Python programming, working with JSON files, handling user input, and managing records through a command-line interface.