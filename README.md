# RASA_mysql

## Installation

```bash
pip install rasa rasa-pro 
```

# Setup mysql database : 

```sql
CREATE DATABASE bank;

USE bank;

CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    balance DECIMAL(10, 2)
);

INSERT INTO accounts (name, balance) VALUES ('John Doe', 1000.00), ('Jane Doe', 1500.50);
```