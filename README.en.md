# 🍽️ Weekly Menu App

Local Python app to manage recipes and generate a weekly meal plan with fixed selection rules.

## ✨ What the app does

- Stores a local text-based recipe database in `data/recipes.json`
- Imports and syncs the initial recipe base from `Receitas Dia a Dia.xlsx`
- Generates a full weekly plan from `Sunday` to `Saturday`
- Forces `Sunday / Dinner` to always be `Coffee`
- Avoids repeating the same dish within the same week
- Gives higher weight to `Hamburguer`, `Pizza`, `Esfiha`, and `Lanche` on `Friday` and `Saturday`

## 🧱 Main structure

- `app.py`: local application entrypoint
- `cardapio/spreadsheet.py`: `.xlsx` spreadsheet reader
- `cardapio/planner.py`: weekly menu generation rules
- `cardapio/storage.py`: JSON persistence layer
- `data/recipes.json`: local text-based recipe database

## ⚙️ Requirements

- Python `3.11+`
- `Receitas Dia a Dia.xlsx` in the project root

## 🚀 How to Run

### Windows

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Start the app:

```powershell
streamlit run app.py
```

4. To use a different port:

```powershell
streamlit run app.py --server.port 8502
```

### Linux / macOS

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

4. To expose it on a different port or network interface:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8502
```

5. To keep it running on Linux with `systemd`:

```ini
[Unit]
Description=App Cardapio Streamlit
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/.venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8502
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cardapio
sudo systemctl start cardapio
sudo systemctl status cardapio
```

## 🗂️ How to Use

### `Weekly menu` tab

- Click `Gerar cardápio semanal`
- The app builds 7 fixed days, starting on Sunday and ending on Saturday
- Each day gets one `Lunch` and one `Dinner`
- The same dish is never repeated within the same week

### `Recipes` tab

- Use `Importar / sincronizar planilha` to load or refresh the base from `Receitas Dia a Dia.xlsx`
- Add dishes that are missing from the spreadsheet, such as:
  - `Café`
  - `Pizza`
  - `Esfiha`
- Edit or delete existing recipes
- Search by recipe name or ingredient

## 📌 Generator rules

- Always generates exactly 7 days
- Fixed order: `Sunday`, `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`
- `Sunday / Dinner` is always `Coffee`
- `Hamburguer`, `Pizza`, `Esfiha`, and dishes containing `Lanche` get higher weight on `Friday` and `Saturday`
- The app requires at least 14 unique recipes to generate a full week

## 💾 Local text database

The app uses JSON as a local database:

- `data/recipes.json`: recipes and ingredients

This allows manually added dishes to remain available even after syncing the spreadsheet again.

## 🧪 Tests

### Windows

```powershell
python -m unittest discover -s tests
```

### Linux / macOS

```bash
python3 -m unittest discover -s tests
```

## 📝 Notes

- The first import may happen automatically when the app starts and the local database is still empty
- If `Café` is not registered, the app blocks weekly generation and asks you to add it
- The spreadsheet remains the mandatory initial import source, but the operational data source is the local JSON file
