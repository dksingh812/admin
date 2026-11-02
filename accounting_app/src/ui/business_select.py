import customtkinter as ctk
from src.database.session import get_db
from src.services.business import get_active_businesses

class BusinessSelectView(ctk.CTkFrame):
    def __init__(self, master, current_user, on_business_selected, **kwargs):
        super().__init__(master, **kwargs)
        self.current_user = current_user
        self.on_business_selected = on_business_selected

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, width=500, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(self.main_frame, text=f"Welcome, {self.current_user.username}", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(self.main_frame, text="Select a Business to Continue", font=ctk.CTkFont(size=14))
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Business List
        self.load_businesses()

    def load_businesses(self):
        db = next(get_db())
        businesses = get_active_businesses(db)
        db.close()

        if not businesses:
            lbl = ctk.CTkLabel(self.main_frame, text="No active businesses found.", text_color="red")
            lbl.grid(row=2, column=0, pady=20)
            return

        for idx, business in enumerate(businesses):
            btn = ctk.CTkButton(
                self.main_frame,
                text=f"{business.name} ({'GST' if business.is_gst_registered else 'Non-GST'})",
                width=350,
                height=40,
                command=lambda b=business: self.on_business_selected(b)
            )
            btn.grid(row=2+idx, column=0, padx=20, pady=10)
