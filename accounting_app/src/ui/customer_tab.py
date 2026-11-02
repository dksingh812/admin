import customtkinter as ctk
from src.database.session import get_db
from src.services.customer import get_customers_by_business, create_customer

class CustomerTabView(ctk.CTkFrame):
    def __init__(self, master, current_business, **kwargs):
        super().__init__(master, **kwargs)
        self.current_business = current_business

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.title_label = ctk.CTkLabel(self.header_frame, text="Customer Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left", padx=10)

        self.add_btn = ctk.CTkButton(self.header_frame, text="+ Add Customer", command=self.open_add_modal)
        self.add_btn.pack(side="right", padx=10)

        # Customer List
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.load_customers()

    def load_customers(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        db = next(get_db())
        customers = get_customers_by_business(db, self.current_business.id)
        db.close()

        if not customers:
            ctk.CTkLabel(self.list_frame, text="No customers found.").pack(pady=20)
            return

        for c in customers:
            f = ctk.CTkFrame(self.list_frame)
            f.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(f, text=f"{c.name} ({c.code})", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(f, text=f"Bal: {c.opening_balance} {c.opening_balance_type}").pack(side="right", padx=10, pady=5)

    def open_add_modal(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Customer")
        dialog.geometry("400x500")
        dialog.transient(self.winfo_toplevel())

        ctk.CTkLabel(dialog, text="Name:").pack(pady=(10,0))
        name_entry = ctk.CTkEntry(dialog)
        name_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Code:").pack(pady=(10,0))
        code_entry = ctk.CTkEntry(dialog)
        code_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Opening Balance:").pack(pady=(10,0))
        bal_entry = ctk.CTkEntry(dialog)
        bal_entry.insert(0, "0.0")
        bal_entry.pack(pady=5)

        type_var = ctk.StringVar(value="Dr")
        ctk.CTkRadioButton(dialog, text="Dr (Receivable)", variable=type_var, value="Dr").pack(pady=5)
        ctk.CTkRadioButton(dialog, text="Cr (Advance)", variable=type_var, value="Cr").pack(pady=5)

        def save():
            data = {
                "name": name_entry.get(),
                "code": code_entry.get(),
                "opening_balance": float(bal_entry.get() or 0.0),
                "opening_balance_type": type_var.get()
            }
            db = next(get_db())
            create_customer(db, self.current_business.id, data)
            db.close()
            dialog.destroy()
            self.load_customers()

        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=20)
