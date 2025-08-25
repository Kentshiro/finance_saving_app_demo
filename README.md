# Finance Saving App  

A **Python-based finance management and savings tracking app** built using **PyQt5**. The application provides a clean and responsive UI for managing wages, shared expenses, and individual expenses for an **individual** or a **group** (e.g., couples, flatmates).  

The app leverages an **SQLite database** to store and manage financial data, supporting cost splits that can be set to **proportional** or **even split** modes. Users can also **customize the app's colour theme** from the Options tab.  

Additionally, the app **projects future savings for each user** and provides **light investment strategy simulations**, helping users plan and visualize potential financial growth.  

---

## Features  
- Manage wages, shared expenses, and individual expenses  
- Save all data using **SQLite** for persistence  
- Flexible **expense split options** (proportional or even)  
- **Theme customization** (colour themes available in settings)  
- **Savings projections** for each user  
- **Light investment strategy simulations**  
- Designed for **individuals and groups** sharing expenses  

---

## Requirements  
- **Python 3.x**  
- **PyQt5**  
- **SQLite** (included by default with Python)  

Install PyQt5 via pip:  
```bash
python -m pip install PyQt5
```

---

## How to Run  

### Option 1: **No coding experience**  
1. Go to the **Releases** section of this repository.  
2. Download the ZIP file for the **Source Code**.  
3. Extract the ZIP file on your machine (**Right-click > Extract All**).  
4. Navigate to:  
   ```
   finance_saving_app/run.bat
   ```  
5. Double-click `run.bat` to launch the application.  

### Option 2: **For developers**  
Run the app from the main Python file:  
```bash
python initialise_app.py
```
You can also run it from `ui.py` if loading the repository into an IDE.  

---

## Known Issues  
- **Theme selection** does not currently persist in the defaults database (will be fixed in a future update).  
- Tested only on **Windows 11** (should work on Windows 10). Not tested on Linux or macOS.  
- This is a **demo project to showcase PyQt5 skills** and will not receive major updates.  

---

## 📄 License  
This project is licensed under the **MIT License** – see the LICENSE file for details.  

---