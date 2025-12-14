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
        self._history.append(f"Setor Rp {amount:,}")

    def withdraw(self, amount):
        if amount > self._balance:
            return False
        self._balance -= amount
        self._history.append(f"Tarik Rp {amount:,}")
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
            f"Tarik Rp {amount:,} (Admin Rp {admin_fee:,})"
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
        from_acc.add_history(f"Transfer Rp {amount:,} ke {to_acc}")

        self.accounts[to_acc]["balance"] += amount
        self.accounts[to_acc]["history"].append(
            f"Terima transfer Rp {amount:,} dari {from_acc._acc_number}"
        )

        self.update_account(from_acc)
        self.save()
        return True, "Transfer berhasil"


# ================= GUI =================
class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Simulator")
        self.root.geometry("500x650")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        
        self.bank = Bank()
        self.current_account = None
        
        # Color scheme
        self.bg_primary = "#1a1a2e"
        self.bg_secondary = "#16213e"
        self.accent = "#0f3460"
        self.highlight = "#e94560"
        self.text_light = "#ffffff"
        self.text_secondary = "#a0a0a0"
        self.success = "#06d6a0"
        self.warning = "#ffd60a"
        
        self.login_screen()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def create_header(self, title):
        """Create a styled header"""
        header_frame = tk.Frame(self.root, bg=self.bg_secondary, height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="💳 ATM SIMULATOR",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_secondary,
            fg=self.text_secondary
        ).pack(pady=(15, 5))
        
        tk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_secondary,
            fg=self.text_light
        ).pack()

    def create_button(self, parent, text, command, style="primary"):
        """Create a styled button"""
        if style == "primary":
            bg_color = self.highlight
            fg_color = self.text_light
        elif style == "secondary":
            bg_color = self.accent
            fg_color = self.text_light
        else:
            bg_color = self.bg_secondary
            fg_color = self.text_light
            
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg=fg_color,
            activebackground=self.highlight,
            activeforeground=self.text_light,
            relief="flat",
            cursor="hand2",
            width=30,
            height=2
        )
        return btn

    def create_entry(self, parent, show=None):
        """Create a styled entry"""
        entry = tk.Entry(
            parent,
            font=("Segoe UI", 12),
            bg=self.bg_secondary,
            fg=self.text_light,
            insertbackground=self.text_light,
            relief="flat",
            bd=0,
            show=show if show else ""
        )
        return entry

    def create_label(self, parent, text, size=11, bold=False):
        """Create a styled label"""
        font_weight = "bold" if bold else "normal"
        label = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, font_weight),
            bg=self.bg_primary,
            fg=self.text_secondary
        )
        return label

    # ---------- LOGIN ----------
    def login_screen(self):
        self.clear()
        self.create_header("LOGIN")

        content_frame = tk.Frame(self.root, bg=self.bg_primary)
        content_frame.pack(expand=True, fill="both", padx=40)

        # Account Number
        self.create_label(content_frame, "Nomor Rekening").pack(anchor="w", pady=(0, 5))
        entry_frame1 = tk.Frame(content_frame, bg=self.bg_secondary, height=45)
        entry_frame1.pack(fill="x", pady=(0, 20))
        entry_frame1.pack_propagate(False)
        
        self.ent_rek = self.create_entry(entry_frame1)
        self.ent_rek.pack(fill="both", padx=15, pady=10)

        # PIN
        self.create_label(content_frame, "PIN").pack(anchor="w", pady=(0, 5))
        entry_frame2 = tk.Frame(content_frame, bg=self.bg_secondary, height=45)
        entry_frame2.pack(fill="x", pady=(0, 30))
        entry_frame2.pack_propagate(False)
        
        self.ent_pin = self.create_entry(entry_frame2, show="●")
        self.ent_pin.pack(fill="both", padx=15, pady=10)

        # Buttons
        self.create_button(content_frame, "🔓 LOGIN", self.login, "primary").pack(pady=8)
        self.create_button(content_frame, "📝 REGISTER", self.register, "secondary").pack(pady=8)

    def login(self):
        acc = self.bank.authenticate(self.ent_rek.get(), self.ent_pin.get())
        if acc:
            self.current_account = acc
            self.main_menu()
        else:
            messagebox.showerror("❌ Error", "Login gagal! Periksa kembali rekening dan PIN Anda.")

    def register(self):
        if not self.ent_rek.get() or not self.ent_pin.get():
            messagebox.showerror("❌ Error", "Mohon isi semua field!")
            return
            
        if self.bank.add_account(self.ent_rek.get(), self.ent_pin.get()):
            messagebox.showinfo("✅ Sukses", "Akun berhasil dibuat!")
        else:
            messagebox.showerror("❌ Error", "Rekening sudah ada!")

    # ---------- MENU UTAMA ----------
    def main_menu(self):
        self.clear()
        self.create_header("MENU UTAMA")

        # Welcome message
        welcome_frame = tk.Frame(self.root, bg=self.bg_secondary, height=80)
        welcome_frame.pack(fill="x", padx=40, pady=(0, 20))
        welcome_frame.pack_propagate(False)
        
        tk.Label(
            welcome_frame,
            text=f"Selamat datang",
            font=("Segoe UI", 10),
            bg=self.bg_secondary,
            fg=self.text_secondary
        ).pack(pady=(15, 0))
        
        tk.Label(
            welcome_frame,
            text=f"Rek. {self.current_account._acc_number}",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_secondary,
            fg=self.success
        ).pack()

        content_frame = tk.Frame(self.root, bg=self.bg_primary)
        content_frame.pack(expand=True, fill="both", padx=40)

        # Menu buttons
        self.create_button(content_frame, "💰 CEK SALDO", self.check_balance, "secondary").pack(pady=5)
        self.create_button(content_frame, "📥 SETOR TUNAI", self.setor_screen, "secondary").pack(pady=5)
        self.create_button(content_frame, "📤 TARIK TUNAI", self.tarik_screen, "secondary").pack(pady=5)
        self.create_button(content_frame, "💸 TRANSFER", self.transfer_screen, "secondary").pack(pady=5)
        self.create_button(content_frame, "📋 HISTORY", self.show_history, "secondary").pack(pady=5)
        
        tk.Frame(content_frame, bg=self.bg_primary, height=20).pack()
        self.create_button(content_frame, "🚪 LOGOUT", self.login_screen, "primary").pack(pady=5)

    # ---------- SETOR ----------
    def setor_screen(self):
        self.clear()
        self.create_header("SETOR TUNAI")

        content_frame = tk.Frame(self.root, bg=self.bg_primary)
        content_frame.pack(expand=True, fill="both", padx=40)

        # Balance display
        balance_frame = tk.Frame(content_frame, bg=self.bg_secondary, height=60)
        balance_frame.pack(fill="x", pady=(0, 30))
        balance_frame.pack_propagate(False)
        
        tk.Label(
            balance_frame,
            text=f"Saldo Saat Ini: Rp {self.current_account.get_balance():,}",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_secondary,
            fg=self.success
        ).pack(pady=20)

        self.create_label(content_frame, "Jumlah Setoran", 12, True).pack(anchor="w", pady=(0, 10))
        
        entry_frame = tk.Frame(content_frame, bg=self.bg_secondary, height=50)
        entry_frame.pack(fill="x", pady=(0, 30))
        entry_frame.pack_propagate(False)
        
        ent = self.create_entry(entry_frame)
        ent.pack(fill="both", padx=15, pady=12)
        ent.insert(0, "0")

        def proses():
            try:
                amt = int(ent.get())
                if amt <= 0:
                    messagebox.showerror("❌ Error", "Jumlah harus lebih dari 0!")
                    return
                self.current_account.deposit(amt)
                self.bank.update_account(self.current_account)
                messagebox.showinfo("✅ Sukses", f"Setor Rp {amt:,} berhasil!")
                self.main_menu()
            except:
                messagebox.showerror("❌ Error", "Input tidak valid!")

        self.create_button(content_frame, "✔ PROSES SETOR", proses, "primary").pack(pady=8)
        self.create_button(content_frame, "← KEMBALI", self.main_menu, "secondary").pack(pady=8)

    # ---------- TARIK ----------
    def tarik_screen(self):
        self.clear()
        self.create_header("TARIK TUNAI")

        content_frame = tk.Frame(self.root, bg=self.bg_primary)
        content_frame.pack(expand=True, fill="both", padx=40)

        # Balance display
        balance_frame = tk.Frame(content_frame, bg=self.bg_secondary, height=60)
        balance_frame.pack(fill="x", pady=(0, 20))
        balance_frame.pack_propagate(False)
        
        tk.Label(
            balance_frame,
            text=f"Saldo Saat Ini: Rp {self.current_account.get_balance():,}",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_secondary,
            fg=self.success
        ).pack(pady=20)

        # Info
        info_label = tk.Label(
            content_frame,
            text="⚠ Biaya admin Rp 2.000 per transaksi",
            font=("Segoe UI", 9),
            bg=self.bg_primary,
            fg=self.warning
        )
        info_label.pack(pady=(0, 15))

        self.create_label(content_frame, "Jumlah Penarikan", 12, True).pack(anchor="w", pady=(0, 10))
        
        entry_frame = tk.Frame(content_frame, bg=self.bg_secondary, height=50)
        entry_frame.pack(fill="x", pady=(0, 30))
        entry_frame.pack_propagate(False)
        
        ent = self.create_entry(entry_frame)
        ent.pack(fill="both", padx=15, pady=12)
        ent.insert(0, "0")

        def proses():
            try:
                amt = int(ent.get())
                if amt <= 0:
                    messagebox.showerror("❌ Error", "Jumlah harus lebih dari 0!")
                    return
                if not self.current_account.withdraw(amt):
                    messagebox.showerror("❌ Error", "Saldo tidak cukup!\n(Termasuk biaya admin Rp 2.000)")
                    return
                self.bank.update_account(self.current_account)
                messagebox.showinfo("✅ Sukses", f"Tarik Rp {amt:,} berhasil!")
                self.main_menu()
            except:
                messagebox.showerror("❌ Error", "Input tidak valid!")

        self.create_button(content_frame, "✔ PROSES TARIK", proses, "primary").pack(pady=8)
        self.create_button(content_frame, "← KEMBALI", self.main_menu, "secondary").pack(pady=8)

    # ---------- TRANSFER ----------
    def transfer_screen(self):
        self.clear()
        self.create_header("TRANSFER")

        content_frame = tk.Frame(self.root, bg=self.bg_primary)
        content_frame.pack(expand=True, fill="both", padx=40)

        # Balance display
        balance_frame = tk.Frame(content_frame, bg=self.bg_secondary, height=60)
        balance_frame.pack(fill="x", pady=(0, 30))
        balance_frame.pack_propagate(False)
        
        tk.Label(
            balance_frame,
            text=f"Saldo Saat Ini: Rp {self.current_account.get_balance():,}",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_secondary,
            fg=self.success
        ).pack(pady=20)

        # Target account
        self.create_label(content_frame, "Rekening Tujuan", 12, True).pack(anchor="w", pady=(0, 10))
        entry_frame1 = tk.Frame(content_frame, bg=self.bg_secondary, height=50)
        entry_frame1.pack(fill="x", pady=(0, 20))
        entry_frame1.pack_propagate(False)
        
        ent_rek = self.create_entry(entry_frame1)
        ent_rek.pack(fill="both", padx=15, pady=12)

        # Amount
        self.create_label(content_frame, "Jumlah Transfer", 12, True).pack(anchor="w", pady=(0, 10))
        entry_frame2 = tk.Frame(content_frame, bg=self.bg_secondary, height=50)
        entry_frame2.pack(fill="x", pady=(0, 30))
        entry_frame2.pack_propagate(False)
        
        ent_amt = self.create_entry(entry_frame2)
        ent_amt.pack(fill="both", padx=15, pady=12)
        ent_amt.insert(0, "0")

        def proses():
            try:
                amt = int(ent_amt.get())
                if amt <= 0:
                    messagebox.showerror("❌ Error", "Jumlah harus lebih dari 0!")
                    return
                ok, msg = self.bank.transfer(
                    self.current_account,
                    ent_rek.get(),
                    amt
                )
                if ok:
                    messagebox.showinfo("✅ Sukses", f"{msg}\nJumlah: Rp {amt:,}")
                    self.main_menu()
                else:
                    messagebox.showerror("❌ Error", msg)
            except:
                messagebox.showerror("❌ Error", "Input tidak valid!")

        self.create_button(content_frame, "✔ PROSES TRANSFER", proses, "primary").pack(pady=8)
        self.create_button(content_frame, "← KEMBALI", self.main_menu, "secondary").pack(pady=8)

    # ---------- OTHER ----------
    def check_balance(self):
        messagebox.showinfo(
            "💰 Saldo Anda",
            f"Saldo: Rp {self.current_account.get_balance():,}\n\n"
            f"Rekening: {self.current_account._acc_number}"
        )

    def show_history(self):
        h = self.current_account.get_history()
        if h:
            history_text = "\n".join([f"• {item}" for item in h[-10:]])  # Show last 10
            messagebox.showinfo("📋 History Transaksi", history_text)
        else:
            messagebox.showinfo("📋 History Transaksi", "Belum ada transaksi")


# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    ATMApp(root)
    root.mainloop()