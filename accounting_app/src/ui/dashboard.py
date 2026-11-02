import customtkinter as ctk
from src.ui.customer_tab import CustomerTabView

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
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Accounting App", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.business_label = ctk.CTkLabel(self.sidebar_frame, text=self.current_business.name, font=ctk.CTkFont(size=12))
        self.business_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.dashboard_btn = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_home)
        self.dashboard_btn.grid(row=2, column=0, padx=20, pady=10)

        self.customer_btn = ctk.CTkButton(self.sidebar_frame, text="Customers", command=self.show_customers)
        self.customer_btn.grid(row=3, column=0, padx=20, pady=10)

        # Main Content Container
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.current_tab = None
        self.show_home()

    def clear_main_content(self):
        if self.current_tab:
            self.current_tab.destroy()

    def show_home(self):
        self.clear_main_content()
        self.current_tab = ctk.CTkFrame(self.main_content)
        self.current_tab.pack(fill="both", expand=True)
        ctk.CTkLabel(self.current_tab, text="Dashboard Overview", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

    def show_customers(self):
        self.clear_main_content()
        self.current_tab = CustomerTabView(self.main_content, self.current_business)
        self.current_tab.pack(fill="both", expand=True)
