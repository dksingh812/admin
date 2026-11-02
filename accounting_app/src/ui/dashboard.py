import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, current_user, current_business, **kwargs):
        super().__init__(master, **kwargs)
        self.current_user = current_user
        self.current_business = current_business

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Accounting App", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.business_label = ctk.CTkLabel(self.sidebar_frame, text=self.current_business.name, font=ctk.CTkFont(size=12))
        self.business_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, text="Dashboard")
        self.dashboard_button.grid(row=2, column=0, padx=20, pady=10)

        # Main Content
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.header_label = ctk.CTkLabel(self.main_content, text="Dashboard Overview", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=20)

        self.info_label = ctk.CTkLabel(self.main_content, text=f"Currently managing: {self.current_business.name}\nGST: {self.current_business.is_gst_registered}")
        self.info_label.pack(pady=10)
