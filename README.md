# envault

A CLI tool to securely manage and sync `.env` files across projects using encrypted local storage.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envault
```

---

## Usage

**Store a `.env` file for a project:**

```bash
envault store --project myapp --file .env
```

**Retrieve and restore a `.env` file:**

```bash
envault pull --project myapp
```

**List all stored projects:**

```bash
envault list
```

**Sync across machines using a passphrase:**

```bash
envault export --project myapp --out myapp.vault
envault import --file myapp.vault
```

All secrets are encrypted locally using AES-256 before being stored or exported. Your plaintext values never leave your machine unencrypted.

---

## How It Works

- Encrypts `.env` files using a master passphrase or auto-generated key
- Stores encrypted vaults in `~/.envault/`
- Portable vault exports for sharing across machines or teammates

---

## License

MIT © [envault contributors](https://github.com/yourname/envault)