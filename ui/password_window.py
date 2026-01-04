import customtkinter as ctk
from db.database import change_admin_password, generate_reset_code, reset_password_with_code

class PasswordSettingsWindow(ctk.CTkToplevel):
    """Window for changing admin password"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Password Settings")
        self.geometry("520x600")  # Increased height significantly
        self.configure(fg_color="#f1f5f9")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="#1e293b", height=70, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🔐 Password Settings", 
                    font=("Arial", 22, "bold"), 
                    text_color="white").pack(pady=20)
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scrollable content area for form fields
        scrollable_content = ctk.CTkScrollableFrame(main_container, fg_color="white", corner_radius=15)
        scrollable_content.pack(fill="both", expand=True, pady=(0, 10))
        
        ctk.CTkLabel(scrollable_content, text="Change Admin Password", 
                    font=("Arial", 16, "bold"), 
                    text_color="#0f172a").pack(pady=(20, 10))
        
        ctk.CTkLabel(scrollable_content, text="Keep your admin password secure!", 
                    font=("Arial", 11), 
                    text_color="#64748b").pack(pady=(0, 20))
        
        # Current password
        ctk.CTkLabel(scrollable_content, text="Current Password:", 
                    font=("Arial", 11), 
                    text_color="#0f172a").pack(anchor="w", padx=30, pady=(10, 5))
        
        self.current_pw = ctk.CTkEntry(scrollable_content, placeholder_text="Enter current password", 
                                      show="*", width=440, height=40)
        self.current_pw.pack(padx=30, pady=(0, 15))
        
        # New password
        ctk.CTkLabel(scrollable_content, text="New Password:", 
                    font=("Arial", 11), 
                    text_color="#0f172a").pack(anchor="w", padx=30, pady=(10, 5))
        
        self.new_pw = ctk.CTkEntry(scrollable_content, placeholder_text="Enter new password (min 4 characters)", 
                                  show="*", width=440, height=40)
        self.new_pw.pack(padx=30, pady=(0, 15))
        
        # Confirm password
        ctk.CTkLabel(scrollable_content, text="Confirm New Password:", 
                    font=("Arial", 11), 
                    text_color="#0f172a").pack(anchor="w", padx=30, pady=(10, 5))
        
        self.confirm_pw = ctk.CTkEntry(scrollable_content, placeholder_text="Re-enter new password", 
                                      show="*", width=440, height=40)
        self.confirm_pw.pack(padx=30, pady=(0, 20))
        
        # Status label
        self.status_label = ctk.CTkLabel(scrollable_content, text="", 
                                        font=("Arial", 11, "bold"))
        self.status_label.pack(pady=(0, 10))
        
        # Buttons frame - FIXED at bottom, always visible
        button_container = ctk.CTkFrame(main_container, fg_color="white", corner_radius=15)
        button_container.pack(fill="x", side="bottom", pady=(0, 0))
        
        self.btn_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        self.btn_frame.pack(pady=15, padx=20)
        
        self.change_btn = ctk.CTkButton(self.btn_frame, text="Change Password", 
                     command=self.change_password,
                     fg_color="#10b981", hover_color="#059669",
                     width=200, height=45, 
                     font=("Arial", 12, "bold"))
        self.change_btn.pack(side="left", padx=10)
        
        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Cancel", 
                     command=self.destroy,
                     fg_color="#64748b", hover_color="#475569",
                     width=120, height=45, 
                     font=("Arial", 12, "bold"))
        self.cancel_btn.pack(side="left", padx=10)
        
        self.grab_set()
    
    def change_password(self):
        """Handle password change"""
        current = self.current_pw.get().strip()
        new = self.new_pw.get().strip()
        confirm = self.confirm_pw.get().strip()
        
        # Validation
        if not current or not new or not confirm:
            self.status_label.configure(text="❌ All fields are required", text_color="#ef4444")
            return
        
        if new != confirm:
            self.status_label.configure(text="❌ New passwords don't match", text_color="#ef4444")
            return
        
        if len(new) < 4:
            self.status_label.configure(text="❌ Password must be at least 4 characters", text_color="#ef4444")
            return
        
        # Try to change password
        success, message = change_admin_password(current, new)
        
        if success:
            self.status_label.configure(text=f"✅ {message}", text_color="#10b981")
            # Clear fields
            self.current_pw.delete(0, 'end')
            self.new_pw.delete(0, 'end')
            self.confirm_pw.delete(0, 'end')
            
            # Hide change and cancel buttons, show confirm button
            self.change_btn.pack_forget()
            self.cancel_btn.pack_forget()
            
            self.confirm_btn = ctk.CTkButton(self.btn_frame, text="✓ Confirm", 
                         command=self.destroy,
                         fg_color="#10b981", hover_color="#059669",
                         width=200, height=45, 
                         font=("Arial", 12, "bold"))
            self.confirm_btn.pack(side="left", padx=10)
        else:
            self.status_label.configure(text=f"❌ {message}", text_color="#ef4444")


class PasswordResetWindow(ctk.CTkToplevel):
    """Window for resetting forgotten password"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Password Reset")
        self.geometry("500x550")
        self.configure(fg_color="#f1f5f9")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        
        self.step = 1  # Current step (1: generate code, 2: verify and reset)
        self.reset_code = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color="#1e293b", height=70, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🔓 Password Reset", 
                    font=("Arial", 22, "bold"), 
                    text_color="white").pack(pady=20)
        
        # Main content
        self.content = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_step_1()
        self.grab_set()
    
    def show_step_1(self):
        """Step 1: Generate reset code"""
        # Clear content
        for widget in self.content.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.content, text="Reset Admin Password", 
                    font=("Arial", 16, "bold"), 
                    text_color="#0f172a").pack(pady=(20, 10))
        
        info_frame = ctk.CTkFrame(self.content, fg_color="#fef3c7", corner_radius=10)
        info_frame.pack(fill="x", padx=30, pady=20)
        
        info_text = ("⚠️ Password Reset Process\n\n"
                    "Click 'Generate Reset Code' below.\n"
                    "You will receive a 6-digit code.\n\n"
                    "⚠️ IMPORTANT: Write this code down immediately!\n"
                    "You'll need it to set a new password.")
        
        ctk.CTkLabel(info_frame, text=info_text, 
                    font=("Arial", 11), 
                    text_color="#92400e",
                    justify="left").pack(pady=15, padx=15)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.content, text="", 
                                        font=("Arial", 11, "bold"))
        self.status_label.pack(pady=20)
        
        # Button
        ctk.CTkButton(self.content, text="🔄 Generate Reset Code", 
                     command=self.generate_code,
                     fg_color="#f59e0b", hover_color="#d97706",
                     width=220, height=40, 
                     font=("Arial", 12, "bold")).pack(pady=10)
        
        ctk.CTkButton(self.content, text="Cancel", 
                     command=self.destroy,
                     fg_color="#64748b", hover_color="#475569",
                     width=100, height=40, 
                     font=("Arial", 12, "bold")).pack(pady=10)
    
    def generate_code(self):
        """Generate reset code"""
        self.reset_code = generate_reset_code()
        
        # Clear content and show code
        for widget in self.content.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.content, text="Reset Code Generated!", 
                    font=("Arial", 16, "bold"), 
                    text_color="#10b981").pack(pady=(20, 10))
        
        # Code display
        code_frame = ctk.CTkFrame(self.content, fg_color="#dcfce7", corner_radius=10)
        code_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(code_frame, text="Your Reset Code:", 
                    font=("Arial", 11), 
                    text_color="#166534").pack(pady=(15, 5))
        
        ctk.CTkLabel(code_frame, text=self.reset_code, 
                    font=("Arial", 32, "bold"), 
                    text_color="#15803d").pack(pady=(5, 15))
        
        warning_frame = ctk.CTkFrame(self.content, fg_color="#fef3c7", corner_radius=10)
        warning_frame.pack(fill="x", padx=30, pady=10)
        
        warning_text = ("⚠️ WRITE THIS CODE DOWN NOW!\n"
                       "You'll need it to complete the password reset.")
        
        ctk.CTkLabel(warning_frame, text=warning_text, 
                    font=("Arial", 11, "bold"), 
                    text_color="#92400e",
                    justify="center").pack(pady=15)
        
        # Button to proceed
        ctk.CTkButton(self.content, text="I've Written It Down - Continue", 
                     command=self.show_step_2,
                     fg_color="#10b981", hover_color="#059669",
                     width=250, height=40, 
                     font=("Arial", 12, "bold")).pack(pady=20)
    
    def show_step_2(self):
        """Step 2: Verify code and set new password"""
        # Clear content
        for widget in self.content.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.content, text="Enter Reset Code & New Password", 
                    font=("Arial", 16, "bold"), 
                    text_color="#0f172a").pack(pady=(20, 10))
        
        # Reset code entry
        ctk.CTkLabel(self.content, text="Reset Code:", 
                    font=("Arial", 11), 
                    text_color="#0f172a").pack(anchor="w", padx=30, pady=(10, 5))
        
        self.code_entry = ctk.CTkEntry(self.content, placeholder_text="Enter 6-digit code", 
                                      width=440, height=40,
                                      font=("Arial", 14))
        self.code_entry.pack(padx=30, pady=(0, 15))
        
        # New password
        ctk.CTkLabel(self.content, text="New Password:", 
                    font=("Arial", 11), 
                    text_color="#0f172a").pack(anchor="w", padx=30, pady=(10, 5))
        
        self.new_pw = ctk.CTkEntry(self.content, placeholder_text="Enter new password (min 4 characters)", 
                                  show="*", width=440, height=40)
        self.new_pw.pack(padx=30, pady=(0, 15))
        
        # Confirm password
        ctk.CTkLabel(self.content, text="Confirm New Password:", 
                    font=("Arial", 11), 
                    text_color="#0f172a").pack(anchor="w", padx=30, pady=(10, 5))
        
        self.confirm_pw = ctk.CTkEntry(self.content, placeholder_text="Re-enter new password", 
                                      show="*", width=440, height=40)
        self.confirm_pw.pack(padx=30, pady=(0, 20))
        
        # Status label
        self.status_label2 = ctk.CTkLabel(self.content, text="", 
                                         font=("Arial", 11, "bold"))
        self.status_label2.pack(pady=(0, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_frame.pack(pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text="✓ Confirm & Reset Password", 
                     command=self.reset_password,
                     fg_color="#10b981", hover_color="#059669",
                     width=240, height=40, 
                     font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", 
                     command=self.destroy,
                     fg_color="#64748b", hover_color="#475569",
                     width=100, height=40, 
                     font=("Arial", 12, "bold")).pack(side="left", padx=5)
    
    def reset_password(self):
        """Reset password with code"""
        code = self.code_entry.get().strip()
        new = self.new_pw.get().strip()
        confirm = self.confirm_pw.get().strip()
        
        # Validation
        if not code or not new or not confirm:
            self.status_label2.configure(text="❌ All fields are required", text_color="#ef4444")
            return
        
        if new != confirm:
            self.status_label2.configure(text="❌ Passwords don't match", text_color="#ef4444")
            return
        
        if len(new) < 4:
            self.status_label2.configure(text="❌ Password must be at least 4 characters", text_color="#ef4444")
            return
        
        # Try to reset password
        success, message = reset_password_with_code(code, new)
        
        if success:
            self.status_label2.configure(text=f"✅ {message}", text_color="#10b981")
            # Close after 1.5 seconds
            self.after(1500, self.destroy)
        else:
            self.status_label2.configure(text=f"❌ {message}", text_color="#ef4444")
