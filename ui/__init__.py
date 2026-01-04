class AddStockWindow:
    def __init__(self, parent, refresh_callback, pre_selected_id=None):
        self.refresh_callback = refresh_callback
        # ... (keep existing window setup code) ...

        # Update the dropdown part:
        self.product_combo = ttk.Combobox(self.window, values=self.display_options, state="readonly", width=30)
        self.product_combo.pack(pady=5)
        
        # New: Auto-select if ID is passed
        if pre_selected_id:
            for option in self.display_options:
                if option.startswith(f"{pre_selected_id} -"):
                    self.product_combo.set(option)
                    break