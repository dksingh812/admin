# AlgoTech Trading Engine

Welcome to your automated trading software! This guide is designed to get you running in minutes, even with zero coding knowledge.

## 🚀 How to Start (The "Plug-and-Play" Way)

You do not need to type commands manually. I have created shortcuts for you.

### Step 1: First Time Setup
1.  Open the folder containing these files.
2.  Double-click on the file named **`install.bat`** (or just `install`).
3.  A black window will open and verify that you have the necessary "ingredients" (libraries) installed.
4.  Once it says "Setup Complete", close that window.
    *   *Note: If it closes immediately with an error, ensure you have installed Python from [python.org](https://www.python.org/downloads/) and checked "Add to PATH" during installation.*

### Step 2: Running the App
1.  Double-click on **`run.bat`** (or just `run`).
2.  A black window will appear—**do not close it**. This is the "Engine" running in the background.
3.  After a few seconds, the **AlgoTech Dashboard** (GUI) will open on your screen.

---

## 🖥️ How to Use the App

### 1. Home Tab (Dashboard)
*   **Indices:** Shows live prices of NIFTY 50, BANKNIFTY, etc.
*   **P&L:** Your total profit/loss for the day is displayed here in large text. Green means profit, Red means loss.
*   **FII/DII:** Shows the institutional buying/selling data fetched from NSE.

### 2. Login Tab (Connecting to Upstox)
*   **Mode:** Select **"Live Trading"** (real money) or **"Sandbox"** (testing with fake money).
*   **API Credentials:** Enter your `API Key` and `API Secret` provided by Upstox.
*   **Click "Login":**
    *   Your web browser will open Upstox login page.
    *   Login with your mobile number/PIN.
    *   Once successful, the app status will turn **Green (Connected)** automatically.

### 3. Strategy Tab (Trading)
*   **Strategy Algorithm:** Currently selected: `SMA_RSI` (Simple Moving Average + RSI).
*   **Trading Symbol:** Type the name of the stock or option you want to trade (e.g., `RELIANCE`, `NIFTY`, `BANKNIFTY`).
    *   *Tip: It searches through 50,000+ symbols, so type carefully!*
*   **Parameters:**
    *   **Capital:** Max money to use for this strategy.
    *   **Stop Loss %:** If price drops by this %, exit trade.
    *   **Target %:** If price rises by this %, book profit.
*   **Start Engine:** Click to begin auto-trading on that symbol.
*   **Logs:** The black box on the right shows exactly what the bot is thinking (e.g., "Price is 100, SMA is 95... Buy Signal!").

---

## ⚠️ Important Notes
*   **Carry Forward:** All trades are placed as **Delivery (CNC/NRML)** by default. This allows you to hold positions overnight if needed.
*   **Internet:** The app needs stable internet to fetch live prices (refreshing every 1 second) and download instrument lists.
*   **Data Storage:** Your trade logs and settings are saved in the `Data` and `Logs` folders. Do not delete them.

## ❓ Troubleshooting
*   **"App is not starting":** Run `install.bat` again to make sure everything is installed.
*   **"Login failed":** Check your API Key and Secret. Ensure you chose the right mode (Live vs Sandbox).
*   **"Loading Instruments...":** On the very first run, the app downloads a large file from Upstox. This can take 30-60 seconds. Please be patient.
