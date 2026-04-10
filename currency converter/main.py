"""
Real Time Currency Converter Application
Clean Structured Version Without Hyphens or Underscores
"""

import json
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog
from datetime import datetime
import threading
import time
import os


class CurrencyAPI:
    """Handles all API interactions for real time exchange rates"""

    def __init__(self):
        self.baseurl = "https://api.exchangerate-api.com/v4/latest/"
        self.cachedata = {}
        self.cachetimeout = 300

    def fetchRates(self, basecurrency):
        """Fetch live exchange rates from the API"""
        try:
            currenttime = time.time()
            basecurrency = basecurrency.upper()

            if basecurrency in self.cachedata:
                cachedentry = self.cachedata[basecurrency]
                if currenttime - cachedentry['timestamp'] < self.cachetimeout:
                    return cachedentry['apidata']

            url = f"{self.baseurl}{basecurrency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            apidata = response.json()

            self.cachedata[basecurrency] = {
                'apidata': apidata,
                'timestamp': currenttime
            }

            return apidata

        except requests.exceptions.ConnectionError:
            raise Exception("No internet connection available")
        except requests.exceptions.Timeout:
            raise Exception("Request timeout - please try again")
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")

    def convertAmount(self, amount, fromcurr, tocurr):
        """Convert amount from one currency to another"""
        fromcurr = fromcurr.upper()
        tocurr = tocurr.upper()

        ratedata = self.fetchRates(fromcurr)

        if tocurr not in ratedata['rates']:
            raise ValueError(f"Currency {tocurr} is not supported")

        rate = ratedata['rates'][tocurr]
        converted = amount * rate

        return {
            'amount': amount,
            'from': fromcurr,
            'to': tocurr,
            'rate': rate,
            'result': round(converted, 2),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class HistoryManager:
    """Manages conversion history storage and retrieval"""

    def __init__(self):
        self.filename = "conversionhistory.json"
        self.entries = []
        self.loadFromFile()

    def loadFromFile(self):
        """Load history data from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.entries = data if isinstance(data, list) else []
            else:
                self.entries = []
        except Exception as e:
            print(f"Error loading history: {e}")
            self.entries = []

    def saveToFile(self):
        """Save history data to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(self.entries, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False

    def addNewEntry(self, conversiondata):
        """Add a new conversion entry to history"""
        entry = {
            'id': len(self.entries) + 1,
            'amount': conversiondata['amount'],
            'fromcurr': conversiondata['from'],
            'tocurr': conversiondata['to'],
            'rate': conversiondata['rate'],
            'result': conversiondata['result'],
            'timestamp': conversiondata['timestamp']
        }
        self.entries.append(entry)
        return self.saveToFile()

    def getAllEntries(self):
        """Return all history entries"""
        return self.entries

    def clearAllEntries(self):
        """Clear all history entries"""
        self.entries = []
        return self.saveToFile()

    def getEntryCount(self):
        """Return total number of entries"""
        return len(self.entries)


class ConverterGUI:
    """Main GUI application class"""

    def __init__(self, root):
        self.root = root
        self.api = CurrencyAPI()
        self.history = HistoryManager()

        self.popular = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PKR']

        self.setupMainWindow()
        self.buildInterface()
        self.startupTasks()

    def setupMainWindow(self):
        """Configure main window properties"""
        self.root.title("Real Time Currency Converter")
        self.root.geometry("1100x850")
        self.root.configure(bg='SystemButtonFace')

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def buildInterface(self):
        """Build the complete user interface"""
        self.buildHeader()
        self.buildMainContainer()
        self.buildStatusBar()

    def buildHeader(self):
        """Build the header section"""
        headerframe = tk.Frame(self.root)
        headerframe.pack(fill=tk.X, pady=15)

        title = tk.Label(headerframe, text="Real Time Currency Converter",
                         font=('Arial', 20, 'bold'))
        title.pack()

        self.timelabel = tk.Label(headerframe, text="", font=('Arial', 10))
        self.timelabel.pack()
        self.updateClock()

    def buildMainContainer(self):
        """Build the main container with three panels"""
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.buildLeftPanel(container)
        self.buildRightPanel(container)
        self.buildBottomPanel()

    def buildLeftPanel(self, parent):
        """Build the left panel with converter"""
        leftpanel = tk.Frame(parent, relief=tk.RIDGE, bd=2)
        leftpanel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(leftpanel, text="CURRENCY CONVERTER",
                 font=('Arial', 14, 'bold')).pack(pady=15)

        self.buildAmountInput(leftpanel)
        self.buildCurrencySelectors(leftpanel)
        self.buildConvertButton(leftpanel)
        self.buildResultDisplay(leftpanel)
        self.buildMultipleConversions(leftpanel)
        self.buildQuickSelect(leftpanel)

    def buildAmountInput(self, parent):
        """Build amount input section"""
        frame = tk.Frame(parent)
        frame.pack(pady=10)

        tk.Label(frame, text="Amount:", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)

        self.amountvar = tk.StringVar()
        tk.Entry(frame, textvariable=self.amountvar, font=('Arial', 12),
                 width=15).pack(side=tk.LEFT, padx=5)

    def buildCurrencySelectors(self, parent):
        """Build currency selection section"""
        fromframe = tk.Frame(parent)
        fromframe.pack(pady=10)

        tk.Label(fromframe, text="From:", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)

        self.fromvar = tk.StringVar(value='USD')
        fromcombo = ttk.Combobox(fromframe, textvariable=self.fromvar,
                                 values=self.popular, width=10,
                                 font=('Arial', 11), state='readonly')
        fromcombo.pack(side=tk.LEFT, padx=5)

        tk.Button(fromframe, text="Swap", command=self.swapCurrencies,
                  font=('Arial', 10), width=8).pack(side=tk.LEFT, padx=10)

        toframe = tk.Frame(parent)
        toframe.pack(pady=10)

        tk.Label(toframe, text="To:", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)

        self.tovar = tk.StringVar(value='EUR')
        tocombo = ttk.Combobox(toframe, textvariable=self.tovar,
                               values=self.popular, width=10,
                               font=('Arial', 11), state='readonly')
        tocombo.pack(side=tk.LEFT, padx=5)

    def buildConvertButton(self, parent):
        """Build convert button"""
        tk.Button(parent, text="CONVERT", command=self.handleConversion,
                  font=('Arial', 12, 'bold'), width=20, height=2).pack(pady=20)

    def buildResultDisplay(self, parent):
        """Build result display section"""
        resultframe = tk.Frame(parent, relief=tk.SUNKEN, bd=2)
        resultframe.pack(pady=10, padx=20, fill=tk.X)

        self.resultlabel = tk.Label(resultframe, text="",
                                    font=('Arial', 14, 'bold'))
        self.resultlabel.pack(pady=10)

        self.ratelabel = tk.Label(resultframe, text="",
                                  font=('Arial', 10))
        self.ratelabel.pack(pady=5)

        self.converttimelabel = tk.Label(resultframe, text="",
                                         font=('Arial', 9))
        self.converttimelabel.pack(pady=5)

    def buildMultipleConversions(self, parent):
        """Build multiple conversions section"""
        multiframe = tk.LabelFrame(parent, text="Multiple Conversions",
                                   font=('Arial', 11, 'bold'), relief=tk.GROOVE)
        multiframe.pack(pady=15, padx=15, fill=tk.X)

        tk.Label(multiframe, text="Enter amounts (comma separated):",
                 font=('Arial', 10)).pack(pady=5)

        self.multivar = tk.StringVar()
        tk.Entry(multiframe, textvariable=self.multivar,
                 font=('Arial', 11), width=30).pack(pady=5, padx=10)

        tk.Label(multiframe, text="Example: 100, 250, 500, 1000",
                 font=('Arial', 9)).pack()

        tk.Button(multiframe, text="Convert All Amounts",
                  command=self.handleMultipleConversions,
                  font=('Arial', 11, 'bold'), height=2).pack(pady=10, padx=20, fill=tk.X)

    def buildQuickSelect(self, parent):
        """Build quick select buttons"""
        quickframe = tk.LabelFrame(parent, text="Quick Select Currencies",
                                   font=('Arial', 11, 'bold'), relief=tk.GROOVE)
        quickframe.pack(pady=10, padx=15, fill=tk.X)

        row1 = tk.Frame(quickframe)
        row1.pack(pady=5)
        row2 = tk.Frame(quickframe)
        row2.pack(pady=5)

        for i, curr in enumerate(self.popular[:5]):
            btn = tk.Button(row1, text=curr, width=6,
                            command=lambda c=curr: self.setFromCurrency(c),
                            font=('Arial', 10))
            btn.pack(side=tk.LEFT, padx=3)

        for i, curr in enumerate(self.popular[5:]):
            btn = tk.Button(row2, text=curr, width=6,
                            command=lambda c=curr: self.setToCurrency(c),
                            font=('Arial', 10))
            btn.pack(side=tk.LEFT, padx=3)

    def buildRightPanel(self, parent):
        """Build the right panel with live rates"""
        rightpanel = tk.Frame(parent, relief=tk.RIDGE, bd=2)
        rightpanel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(rightpanel, text="LIVE EXCHANGE RATES",
                 font=('Arial', 14, 'bold')).pack(pady=15)

        self.buildRateSelector(rightpanel)
        self.buildRateDisplay(rightpanel)

    def buildRateSelector(self, parent):
        """Build rate selector section"""
        frame = tk.Frame(parent)
        frame.pack(pady=10)

        tk.Label(frame, text="Base Currency:", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)

        self.basevar = tk.StringVar(value='USD')
        basecombo = ttk.Combobox(frame, textvariable=self.basevar,
                                 values=self.popular, width=8,
                                 font=('Arial', 11), state='readonly')
        basecombo.pack(side=tk.LEFT, padx=5)
        basecombo.bind('<<ComboboxSelected>>', lambda e: self.refreshRates())

        tk.Button(frame, text="Refresh", command=self.refreshRates,
                  font=('Arial', 10)).pack(side=tk.LEFT, padx=10)

    def buildRateDisplay(self, parent):
        """Build rate display section"""
        self.ratetext = scrolledtext.ScrolledText(parent, width=40, height=20,
                                                  font=('Courier', 10))
        self.ratetext.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def buildBottomPanel(self):
        """Build the bottom panel with history"""
        bottompanel = tk.Frame(self.root, relief=tk.RIDGE, bd=2)
        bottompanel.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        self.buildHistoryHeader(bottompanel)
        self.buildHistoryDisplay(bottompanel)

    def buildHistoryHeader(self, parent):
        """Build history header section"""
        header = tk.Frame(parent)
        header.pack(fill=tk.X, pady=10, padx=10)

        tk.Label(header, text="CONVERSION HISTORY",
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)

        self.countlabel = tk.Label(header, text="", font=('Arial', 11))
        self.countlabel.pack(side=tk.LEFT, padx=10)

        buttonframe = tk.Frame(header)
        buttonframe.pack(side=tk.RIGHT)

        tk.Button(buttonframe, text="Refresh",
                  command=self.refreshHistoryDisplay,
                  font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=3)

        tk.Button(buttonframe, text="Save History",
                  command=self.onClickSaveHistory,
                  font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=3)

        tk.Button(buttonframe, text="Clear History",
                  command=self.onClickClearHistory,
                  font=('Arial', 10), width=12).pack(side=tk.LEFT, padx=3)

        tk.Button(buttonframe, text="Export",
                  command=self.onClickExportHistory,
                  font=('Arial', 10), width=10).pack(side=tk.LEFT, padx=3)

    def buildHistoryDisplay(self, parent):
        """Build history display section"""
        container = tk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.historybox = tk.Listbox(container,
                                     yscrollcommand=scrollbar.set,
                                     font=('Courier', 10),
                                     selectbackground='lightblue',
                                     height=10)
        self.historybox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.historybox.yview)

        self.historybox.bind('<Double-Button-1>', self.onHistoryDoubleClick)

    def buildStatusBar(self):
        """Build the status bar"""
        self.statuslabel = tk.Label(self.root, text="Ready",
                                    font=('Arial', 10),
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.statuslabel.pack(fill=tk.X, padx=20, pady=(0, 10))

    def startupTasks(self):
        """Perform initial startup tasks"""
        self.refreshRates()
        self.refreshHistoryDisplay()

    def updateClock(self):
        """Update the clock display"""
        current = datetime.now().strftime("%A, %B %d, %Y | %H:%M:%S")
        self.timelabel.config(text=current)
        self.root.after(1000, self.updateClock)

    def setFromCurrency(self, currency):
        """Set the from currency"""
        self.fromvar.set(currency)
        self.statuslabel.config(text=f"From currency set to: {currency}")

    def setToCurrency(self, currency):
        """Set the to currency"""
        self.tovar.set(currency)
        self.statuslabel.config(text=f"To currency set to: {currency}")

    def swapCurrencies(self):
        """Swap from and to currencies"""
        fromcurr = self.fromvar.get()
        tocurr = self.tovar.get()
        self.fromvar.set(tocurr)
        self.tovar.set(fromcurr)
        self.statuslabel.config(text="Currencies swapped")

    def refreshRates(self):
        """Refresh exchange rates display"""

        def fetchTask():
            try:
                base = self.basevar.get()
                self.statuslabel.config(text=f"Fetching rates for {base}...")

                data = self.api.fetchRates(base)
                self.root.after(0, lambda: self.showRates(data, base))

            except Exception as e:
                self.root.after(0, lambda: self.showError(f"Error: {e}"))

        threading.Thread(target=fetchTask, daemon=True).start()

    def showRates(self, data, base):
        """Display rates in text widget"""
        self.ratetext.delete(1.0, tk.END)

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.ratetext.insert(tk.END, f"BASE: {base}\n")
        self.ratetext.insert(tk.END, f"Updated: {timestamp}\n")
        self.ratetext.insert(tk.END, "=" * 45 + "\n")
        self.ratetext.insert(tk.END, f"{'Currency':<12} {'Rate':<12}\n")
        self.ratetext.insert(tk.END, "-" * 45 + "\n")

        rates = data.get('rates', {})
        for currency in self.popular:
            if currency != base and currency in rates:
                rate = rates[currency]
                self.ratetext.insert(tk.END, f"{currency:<12} {rate:.4f}\n")

        self.statuslabel.config(text=f"Rates updated for {base} at {timestamp}")

    def handleConversion(self):
        """Handle single conversion request"""
        try:
            amount = float(self.amountvar.get())
            fromcurr = self.fromvar.get()
            tocurr = self.tovar.get()

            if amount <= 0:
                messagebox.showwarning("Warning", "Please enter a positive amount")
                return

            self.statuslabel.config(text=f"Converting {amount:,.2f} {fromcurr} to {tocurr}...")

            result = self.api.convertAmount(amount, fromcurr, tocurr)

            self.resultlabel.config(
                text=f"{amount:,.2f} {fromcurr} = {result['result']:,.2f} {tocurr}"
            )
            self.ratelabel.config(text=f"Exchange Rate: 1 {fromcurr} = {result['rate']:.6f} {tocurr}")
            self.converttimelabel.config(text=f"Converted at: {result['timestamp']}")

            if self.history.addNewEntry(result):
                self.refreshHistoryDisplay()
                self.statuslabel.config(text=f"Conversion saved. Total entries: {self.history.getEntryCount()}")
            else:
                self.statuslabel.config(text="Conversion done but failed to save history")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            self.statuslabel.config(text="Error: Invalid amount")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.statuslabel.config(text=f"Error: {str(e)}")

    def handleMultipleConversions(self):
        """Handle multiple conversions request"""
        try:
            amountstr = self.multivar.get().strip()
            if not amountstr:
                messagebox.showwarning("Warning", "Please enter amounts to convert")
                return

            amounts = [float(x.strip()) for x in amountstr.split(',') if x.strip()]
            fromcurr = self.fromvar.get()
            tocurr = self.tovar.get()

            if not amounts:
                messagebox.showwarning("Warning", "No valid amounts found")
                return

            resultwindow = tk.Toplevel(self.root)
            resultwindow.title("Multiple Conversions Results")
            resultwindow.geometry("600x500")

            header = tk.Frame(resultwindow)
            header.pack(fill=tk.X, pady=10)

            tk.Label(header, text="BATCH CONVERSION RESULTS",
                     font=('Arial', 14, 'bold')).pack(pady=10)

            textwidget = scrolledtext.ScrolledText(resultwindow, width=60, height=20,
                                                   font=('Courier', 10))
            textwidget.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

            textwidget.insert(tk.END, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            textwidget.insert(tk.END, f"Converting: {fromcurr} to {tocurr}\n")
            textwidget.insert(tk.END, "=" * 60 + "\n\n")

            success = 0
            total = 0

            for amount in amounts:
                try:
                    result = self.api.convertAmount(amount, fromcurr, tocurr)
                    line = f"{amount:>12,.2f} {fromcurr} = {result['result']:>12,.2f} {tocurr}\n"
                    textwidget.insert(tk.END, line)

                    if self.history.addNewEntry(result):
                        success += 1
                        total += result['result']

                except Exception as e:
                    textwidget.insert(tk.END, f"Error converting {amount}: {e}\n")

            textwidget.insert(tk.END, "\n" + "=" * 60 + "\n")
            textwidget.insert(tk.END, f"Successfully converted: {success}/{len(amounts)}\n")
            textwidget.insert(tk.END, f"Total converted amount: {total:,.2f} {tocurr}\n")
            textwidget.insert(tk.END, f"Completed at: {datetime.now().strftime('%H:%M:%S')}\n")

            self.refreshHistoryDisplay()
            self.statuslabel.config(text=f"Batch conversion completed: {success} successful")

            tk.Button(resultwindow, text="CLOSE", command=resultwindow.destroy,
                      font=('Arial', 11, 'bold')).pack(pady=10)

        except ValueError:
            messagebox.showerror("Error", "Invalid amount format")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refreshHistoryDisplay(self):
        """Refresh the history display"""
        self.historybox.delete(0, tk.END)

        entries = self.history.getAllEntries()
        self.countlabel.config(text=f"({len(entries)} entries)")

        if not entries:
            self.historybox.insert(tk.END, "No conversion history yet")
            self.historybox.insert(tk.END, "")
            self.historybox.insert(tk.END, "Make a conversion to see it here")
            return

        header = f"{'Time':<12} {'Amount':<14} {'From':<8} {'To':<8} {'Result':<14} {'Rate':<10}"
        self.historybox.insert(tk.END, header)
        self.historybox.insert(tk.END, "-" * 80)

        for entry in reversed(entries):
            timepart = entry['timestamp'][-8:] if 'timestamp' in entry else 'N/A'
            amountpart = f"{entry['amount']:.2f}"
            resultpart = f"{entry['result']:.2f}"
            ratepart = f"{entry['rate']:.4f}"

            line = f"{timepart:<12} {amountpart:<14} {entry['fromcurr']:<8} {entry['tocurr']:<8} {resultpart:<14} {ratepart:<10}"
            self.historybox.insert(tk.END, line)

    def onClickSaveHistory(self):
        """Handle save history button click"""
        if self.history.saveToFile():
            count = self.history.getEntryCount()
            filepath = os.path.abspath(self.history.filename)
            messagebox.showinfo("Success",
                                f"History saved successfully\n\n"
                                f"{count} entries saved to:\n"
                                f"{filepath}")
            self.statuslabel.config(text=f"History saved - {count} entries")
        else:
            messagebox.showerror("Error", "Failed to save history")
            self.statuslabel.config(text="Failed to save history")

    def onClickClearHistory(self):
        """Handle clear history button click"""
        if messagebox.askyesno("Confirm Clear",
                               "Are you sure you want to clear all history?\n\n"
                               "This cannot be undone"):
            if self.history.clearAllEntries():
                self.refreshHistoryDisplay()
                self.statuslabel.config(text="History cleared")
                messagebox.showinfo("Success", "All history cleared")
            else:
                messagebox.showerror("Error", "Failed to clear history")
                self.statuslabel.config(text="Failed to clear history")

    def onClickExportHistory(self):
        """Handle export history button click"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                entries = self.history.getAllEntries()

                if filename.endswith('.csv'):
                    with open(filename, 'w', encoding='utf-8') as file:
                        file.write("Timestamp,Amount,From,To,Result,Rate\n")
                        for entry in entries:
                            file.write(f"{entry['timestamp']},{entry['amount']},{entry['fromcurr']},"
                                       f"{entry['tocurr']},{entry['result']},{entry['rate']}\n")
                else:
                    with open(filename, 'w', encoding='utf-8') as file:
                        json.dump(entries, file, indent=2)

                messagebox.showinfo("Success", f"History exported to:\n{filename}")
                self.statuslabel.config(text=f"History exported")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
            self.statuslabel.config(text="Export failed")

    def onHistoryDoubleClick(self, event):
        """Handle double click on history item"""
        selection = self.historybox.curselection()
        if not selection:
            return

        selected = self.historybox.get(selection[0])

        if selected.startswith("Time") or selected.startswith("-"):
            return

        messagebox.showinfo("Conversion Details", f"Selected conversion:\n\n{selected}")

    def showError(self, message):
        """Show error message"""
        self.statuslabel.config(text=message)
        messagebox.showerror("Error", message)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()