
Wisdom's Kitchen - Flask app (simple)
-------------------------------------

How to run (VS Code):
1. Open this folder in VS Code.
2. Select the Python interpreter from the workspace virtual environment at `.venv`.
3. Install dependencies if needed:
   pip install -r requirements.txt
4. Run the app using one of these options:
   - Use the VS Code Run and Debug launch configuration: `Python: Run Wisdom's Kitchen`
   - Or run the batch helper: `run_app.bat`
   - Or run directly: `python app.py`
5. Open your browser to http://127.0.0.1:7860

Notes:
- Make sure you are in the project root folder before running the app.
- Replace `static/images/logo.png` and other placeholder images with your real images for better visuals.
- Edit the `MENU` list in `kitchen.py` to add or change dishes and prices.
- Bank details are in `kitchen.py` under `BANK_DETAILS` and can be changed to match your real account.
- This app simulates payments (no real payment gateway). For real card processing integrate Stripe or Paystack.
