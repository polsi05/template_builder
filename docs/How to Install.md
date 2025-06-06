## How to Install

**Requisiti minimi:**

* Python 3.10+ con modulo Tkinter incluso (ad es. `python3-tk` su Linux).
* `pip` aggiornato.

1. **Clona il repository (opzionale se vuoi testare in locale)**

   ```bash
   git clone https://github.com/polsi05/template_builder.git
   cd template_builder
   ```

2. **Crea e attiva un virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate     # Linux/Mac
   venv\Scripts\activate        # Windows
   ```

3. **Installa il pacchetto principale**

   ```bash
   pip install template_builder
   ```

4. **(Opzionale) Installa tutte le dipendenze opzionali**

   ```bash
   pip install "template_builder[dnd,webpreview]"
   ```

5. **(Per sviluppatori) Installa in modalità editable con dipendenze di test**

   ```bash
   pip install -e .[test]
   ```
