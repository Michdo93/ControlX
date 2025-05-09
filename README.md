# 🧠 ControlX

*Control everything. Just like Professor X.*

<div align="center">
  <img src="https://raw.githubusercontent.com/Michdo93/ControlX/refs/heads/main/static/professor-x.png" alt="ControlX Logo" width="300">
</div>

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/built%20with-Flask-%23d44a36)
![License](https://img.shields.io/github/license/Michdo93/ControlX)
![Issues](https://img.shields.io/github/issues/Michdo93/ControlX)
![Stars](https://img.shields.io/github/stars/Michdo93/ControlX?style=social)

## 🧬 The Origin Story

In a world overflowing with devices, APIs, and systems, chaos is the norm. But where others see entropy, **Professor Charles Xavier** sees **potential**—a network of minds and machines, harmonized under a single will.

Inspired by his extraordinary ability to **interface with consciousness**, ControlX was born. Not a weapon. Not a tool. But a **mind behind the system**.

Where **WOLverine** awakens machines with the ferocity of Logan, **ControlX** manages them with the clarity and precision of Xavier. It listens. It thinks. It acts—remotely, securely, and intelligently.

With ControlX, you don’t just control systems.  
You **orchestrate** them.

---

# 🖼️ Screenshots

<p float="left">
  <img src="https://raw.githubusercontent.com/Michdo93/test2/refs/heads/main/controlx.png" width="90%" />
</p>

---

## ⚙️ Features

- 🧠 **Custom API Execution**  
  Define and expose shell commands as secure REST endpoints.

- 🔐 **Authentication Built In**  
  HTTP Basic Auth ensures only the right minds access the controls.

- 💾 **Import/Export**  
  Easily back up and transfer endpoint definitions via CSV.

- 🎛️ **Dynamic Parameters**  
  Define endpoints with placeholders and send values at runtime.

- 📁 **Optional GUI Commands**  
  Launch desktop applications (like `code`, `firefox`, etc.) with proper `DISPLAY` handling.

- 🐚 **Shell-Safe**  
  Input sanitation helps protect against command injection.

---

## 🚀 Getting Started

### 📦 Requirements

- Python 3.8+
- Flask
- SQLAlchemy
- Jinja2
- Werkzeug

Install dependencies:

```bash
pip install -r requirements.txt
````

### ▶️ Launch the App

```bash
python app.py
```

The default interface runs on:
**[http://localhost:5000](http://localhost:5000)**

### 🔑 Default Credentials

* **Username**: `admin`
* **Password**: `controlx`

---

## 📂 Project Structure

```text
ControlX/
├── app.py               # Main Flask app
├── models.py            # SQLAlchemy models
├── templates/           # Jinja2 HTML templates
├── static/              # CSS and JS assets
├── instance/            # SQLite DB and config
├── routes/              # Modularized Flask routes
└── requirements.txt     # Python dependencies
```

---

## 🧪 Usage Examples

### Run a Remote Command

Assuming you’ve defined an API endpoint like:

```json
POST /api/code
{
  "path": "/home/user/project"
}
```

You can trigger it with:

```bash
curl -u admin:controlx \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"path": "/home/user/project"}' \
  http://localhost:5000/api/code
```

### Import/Export API Definitions

Export:

```bash
curl -O http://localhost:5000/export_csv
```

Import:

Upload via web UI or:

```bash
curl -u admin:controlx -F "file=@your_endpoints.csv" http://localhost:5000/import_csv
```

---

## 💡 Pro Tips

* If using GUI commands (e.g. `firefox`, `code`), ensure:

  * Your app runs **outside Docker**, or
  * You implement a **host-side execution agent**
  * The `DISPLAY` environment is set and accessible

* ControlX is meant to be **minimal**, **secure**, and **extendable**.

---

## 🧠 Why “ControlX”?

> “The greatest power on Earth is the magnificent mind of a free man.”
> — *Professor X*

Just as Charles Xavier connects, manages, and empowers mutant minds, ControlX serves as the **central intelligence** of your digital infrastructure. With **precision, foresight, and security**, it turns shell commands into RESTful actions—bridging the gap between terminal and network, brain and system.

**WOLverine wakes machines. ControlX commands them.**

---

## 📜 License

MIT License
See [LICENSE](LICENSE) for details.

---

## ☎️ Contact

Created by [@Michdo93](https://github.com/Michdo93)
Issues and suggestions welcome in the [issue tracker](https://github.com/Michdo93/ControlX/issues).
