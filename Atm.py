import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = "accounts.json"


# ================= FILE =================
def load_accounts():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_accounts(accounts):
    with open(DATA_FILE, "w") as f:
        json.dump(accounts, f, indent=4)


# ================= ACCOUNT =================
class Account:
    def __init__(self, acc_number, pin, balance=0, history=None):
        self._acc_number = acc_number
        self._pin = pin
        self._balance = balance
        self._history = history if history else []

    def deposit(self, amount):
        self._balance += amount
        self._history.append(f"Setor Rp {amount}")

    def withdraw(self, amount):
        if amount > self._balance:
            return False
        self._balance -= amount
        self._history.append(f"Tarik Rp {amount}")
        return True

    def add_history(self, text):
        self._history.append(text)

    def get_balance(self):
        return self._balance

    def get_history(self):
        return self._history
    
class SavingAccount(Account):
    def withdraw(self, amount):
        admin_fee = 2000
        total = amount + admin_fee
        if total > self._balance:
            return False
        self._balance -= total
        self._history.append(
            f"Tarik Rp {amount} (Admin Rp {admin_fee})"
        )
        return True


# ================= BANK =================
class Bank:
    def __init__(self):
        self.accounts = load_accounts()

    def save(self):
        save_accounts(self.accounts)

    def add_account(self, acc_number, pin):
        if acc_number in self.accounts:
            return False
        self.accounts[acc_number] = {
            "pin": pin,
            "balance": 0,
            "history": []
        }
        self.save()
        return True

    def authenticate(self, acc_number, pin):
        data = self.accounts.get(acc_number)
        if data and data["pin"] == pin:
            return SavingAccount(
                acc_number,
                pin,
                data["balance"],
                data.get("history", [])
            )
        return None

    def update_account(self, account: Account):
        self.accounts[account._acc_number]["balance"] = account.get_balance()
        self.accounts[account._acc_number]["history"] = account.get_history()
        self.save()

    def transfer(self, from_acc: Account, to_acc, amount):
        if to_acc not in self.accounts:
            return False, "Rekening tujuan tidak ditemukan"
        if amount > from_acc.get_balance():
            return False, "Saldo tidak cukup"

        from_acc.withdraw(amount)
        from_acc.add_history(f"Transfer Rp {amount} ke {to_acc}")

        self.accounts[to_acc]["balance"] += amount
        self.accounts[to_acc]["history"].append(
            f"Terima transfer Rp {amount} dari {from_acc._acc_number}"
        )

        self.update_account(from_acc)
        self.save()
        return True, "Transfer berhasil"


# ================= GUI =================
class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Simulator")
        self.bank = Bank()
        self.current_account = None
        self.login_screen()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ---------- LOGIN ----------
    def login_screen(self):
        self.clear()
        tk.Label(self.root, text="LOGIN ATM", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="No Rekening").pack()
        self.ent_rek = tk.Entry(self.root)
        self.ent_rek.pack()

        tk.Label(self.root, text="PIN").pack()
        self.ent_pin = tk.Entry(self.root, show="*")
        self.ent_pin.pack()

        tk.Button(self.root, text="Login", width=25,
                  command=self.login).pack(pady=5)
        tk.Button(self.root, text="Register", width=25,
                  command=self.register).pack()

    def login(self):
        acc = self.bank.authenticate(self.ent_rek.get(), self.ent_pin.get())
        if acc:
            self.current_account = acc
            self.main_menu()
        else:
            messagebox.showerror("Error", "Login gagal")

    def register(self):
        if self.bank.add_account(self.ent_rek.get(), self.ent_pin.get()):
            messagebox.showinfo("Sukses", "Akun berhasil dibuat")
        else:
            messagebox.showerror("Error", "Rekening sudah ada")

    # ---------- MENU UTAMA ----------
    def main_menu(self):
        self.clear()
        tk.Label(self.root, text="MENU UTAMA", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Cek Saldo", width=25,
                  command=self.check_balance).pack(pady=3)
        tk.Button(self.root, text="Setor", width=25,
                  command=self.setor_screen).pack(pady=3)
        tk.Button(self.root, text="Tarik", width=25,
                  command=self.tarik_screen).pack(pady=3)
        tk.Button(self.root, text="Transfer", width=25,
                  command=self.transfer_screen).pack(pady=3)
        tk.Button(self.root, text="History", width=25,
                  command=self.show_history).pack(pady=3)
        tk.Button(self.root, text="Logout", width=25,
                  command=self.login_screen).pack(pady=10)

    # ---------- SETOR ----------
    def setor_screen(self):
        self.clear()
        tk.Label(self.root, text="SETOR TUNAI", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Jumlah").pack()
        ent = tk.Entry(self.root)
        ent.pack()

        def proses():
            try:
                amt = int(ent.get())
                self.current_account.deposit(amt)
                self.bank.update_account(self.current_account)
                messagebox.showinfo("Sukses", "Setor berhasil")
                self.main_menu()
            except:
                messagebox.showerror("Error", "Input tidak valid")

        tk.Button(self.root, text="Proses Setor", width=25,
                  command=proses).pack(pady=5)
        tk.Button(self.root, text="Kembali", width=25,
                  command=self.main_menu).pack()

    # ---------- TARIK ----------
    def tarik_screen(self):
        self.clear()
        tk.Label(self.root, text="TARIK TUNAI", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Jumlah").pack()
        ent = tk.Entry(self.root)
        ent.pack()

        def proses():
            try:
                amt = int(ent.get())
                if not self.current_account.withdraw(amt):
                    messagebox.showerror("Error", "Saldo tidak cukup")
                    return
                self.bank.update_account(self.current_account)
                messagebox.showinfo("Sukses", "Tarik berhasil")
                self.main_menu()
            except:
                messagebox.showerror("Error", "Input tidak valid")

        tk.Button(self.root, text="Proses Tarik", width=25,
                  command=proses).pack(pady=5)
        tk.Button(self.root, text="Kembali", width=25,
                  command=self.main_menu).pack()

    # ---------- TRANSFER ----------
    def transfer_screen(self):
        self.clear()
        tk.Label(self.root, text="TRANSFER", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Rekening Tujuan").pack()
        ent_rek = tk.Entry(self.root)
        ent_rek.pack()

        tk.Label(self.root, text="Jumlah").pack()
        ent_amt = tk.Entry(self.root)
        ent_amt.pack()

        def proses():
            try:
                ok, msg = self.bank.transfer(
                    self.current_account,
                    ent_rek.get(),
                    int(ent_amt.get())
                )
                if ok:
                    messagebox.showinfo("Sukses", msg)
                    self.main_menu()
                else:
                    messagebox.showerror("Error", msg)
            except:
                messagebox.showerror("Error", "Input tidak valid")

        tk.Button(self.root, text="Proses Transfer", width=25,
                  command=proses).pack(pady=5)
        tk.Button(self.root, text="Kembali", width=25,
                  command=self.main_menu).pack()

    # ---------- OTHER ----------
    def check_balance(self):
        messagebox.showinfo("Saldo",
                            f"Saldo Anda: Rp {self.current_account.get_balance()}")

    def show_history(self):
        h = self.current_account.get_history()
        messagebox.showinfo("History", "\n".join(h) if h else "Belum ada transaksi")


# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    ATMApp(root)
    root.mainloop()