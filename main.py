import tkinter as tk
from tkinter import ttk, messagebox

class BeverageManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Cửa Hàng Đồ Uống")
        self.geometry("1100x700")
        self.state('zoomed') 
        
        self.current_frame = None
        self.tab_bg = '#E8F4F8'

        # ==========================================
        # CẤU HÌNH STYLE MÀU SẮC CHO GIAO DIỆN
        # ==========================================
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 1. Định dạng chung
        self.style.configure('Dashboard.TButton', font=('Arial', 14, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        
        # 2. Đổi màu tiêu đề của các Cột (Treeview Heading)
        self.style.configure('Treeview.Heading', 
                            font=('Arial', 10, 'bold'), 
                            background='#0078D7',  # Màu nền cột (Xanh dương)
                            foreground='white')    # Màu chữ (Trắng)
        self.style.map('Treeview.Heading', 
                        background=[('active', '#005A9E')]) # Đổi màu mờ đi một chút khi di chuột vào (Hover)

        # 3. Đổi màu tiêu đề của các Tab (Notebook Tab)
        self.style.configure('TNotebook.Tab', 
                            font=('Arial', 11, 'bold'), 
                            padding=[15, 5], 
                            background='#D3D3D3', # Màu nền các tab chưa được chọn (Xám nhạt)
                            foreground='black')
                            
        self.style.map('TNotebook.Tab', 
                        background=[('selected', '#FF9999')], # Màu nền khi tab ĐƯỢC CHỌN (Hồng nhạt nổi bật)
                        foreground=[('selected', 'black')],
                        expand=[('selected', [1, 1, 1, 0])])  # Hiệu ứng làm tab chọn to lên một chút
        
        self.create_dashboard()

    # ==========================================
    # 1. DASHBOARD
    # ==========================================
    def create_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self, bg='#f0f0f0')
        self.current_frame.pack(fill='both', expand=True)
        
        title = tk.Label(self.current_frame, text="DASHBOARD - QUẢN LÝ CỬA HÀNG", font=('Arial', 24, 'bold'), bg='#f0f0f0')
        title.pack(pady=40)

        grid_frame = tk.Frame(self.current_frame, bg='#f0f0f0')
        grid_frame.pack(expand=True)

        modules = [
            ("Quản lý\nKho hàng", lambda: self.show_module(0), '#FF9999'),
            ("Nhà\nCung cấp", lambda: self.show_module(1), '#99FF99'),
            ("Phiếu\nNhập hàng", lambda: self.show_module(2), '#99CCFF'),
            ("Quản lý\nNhân viên", lambda: self.show_module(3), '#FFCC99'),
            ("Quản lý\nHóa đơn", lambda: self.show_module(4), '#E699FF'),
            ("Quản lý\nKhách hàng", lambda: self.show_module(5), '#FFFF99'),
            ("Chương trình\nKhuyến mãi", lambda: self.show_module(6), '#99FFE6')
        ]

        row, col = 0, 0
        for text, command, color in modules:
            btn = tk.Button(grid_frame, text=text, font=('Arial', 12, 'bold'), 
                            width=15, height=7, bg=color, relief='groove', cursor='hand2', command=command)
            btn.grid(row=row, column=col, padx=20, pady=20)
            col += 1
            if col > 3: 
                col = 0
                row += 1

    # ==========================================
    # KHỞI TẠO CÁC TAB & NẠP DATA
    # ==========================================
    def show_module(self, tab_index):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self)
        self.current_frame.pack(fill='both', expand=True)

        top_bar = tk.Frame(self.current_frame, bg='#333', height=40)
        top_bar.pack(fill='x')
        back_btn = tk.Button(top_bar, text="⬅ Về Dashboard", command=self.create_dashboard, bg='white', cursor='hand2')
        back_btn.pack(side='left', padx=10, pady=5)

        self.notebook = ttk.Notebook(self.current_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_tab_kho_hang()
        self.create_tab_ncc()
        self.create_tab_phieu_nhap()
        self.create_tab_nhan_vien()
        self.create_tab_hoa_don()
        self.create_tab_khach_hang()
        self.create_tab_khuyen_mai()

        self.insert_sample_data()
        self.notebook.select(tab_index)

    def create_treeview(self, parent, columns):
        bg_color = parent.cget('bg') if isinstance(parent, tk.Frame) else self.tab_bg
        tree_frame = tk.Frame(parent, bg=bg_color)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        
        scroll_y.pack(side='right', fill='y')
        scroll_x.pack(side='bottom', fill='x')
        tree.pack(side='left', fill='both', expand=True)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
            
        if "STT" in columns:
            tree.column("STT", width=60)
        if "Mã Phiếu" in columns:
            tree.column("Mã Phiếu", width=90)
        if "Mã HĐ" in columns:
            tree.column("Mã HĐ", width=90)
            
        return tree

    def create_control_panel(self, parent, sort_options, add_cmd, edit_cmd, delete_cmd):
        bg_color = parent.cget('bg') if isinstance(parent, tk.Frame) else self.tab_bg
        panel = tk.Frame(parent, bg=bg_color)
        panel.pack(fill='x', pady=5)
        
        tk.Button(panel, text="Thêm", width=10, bg='lightblue', command=add_cmd).pack(side='left', padx=5)
        tk.Button(panel, text="Sửa", width=10, bg='lightgreen', command=edit_cmd).pack(side='left', padx=5)
        tk.Button(panel, text="Xóa", width=10, bg='#ff6666', command=delete_cmd).pack(side='left', padx=5)
        
        tk.Label(panel, text="Tìm kiếm:", bg=bg_color).pack(side='left', padx=(20, 5))
        tk.Entry(panel, width=20).pack(side='left', padx=5)
        tk.Button(panel, text="Tìm").pack(side='left', padx=5)
        
        if sort_options:
            tk.Label(panel, text="Sắp xếp:", bg=bg_color).pack(side='left', padx=(20, 5))
            cb = ttk.Combobox(panel, values=sort_options, state="readonly")
            cb.pack(side='left', padx=5)
            cb.set("Chọn tiêu chí")
            tk.Button(panel, text="Lọc").pack(side='left', padx=5)

    # ==========================================
    # LOGIC CRUD CHUNG CỦA BẢNG
    # ==========================================
    def open_form_window(self, title, tree, fields, is_edit=False):
        selected_item = None
        current_values = []
        
        if is_edit:
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng trên bảng để sửa!")
                return
            selected_item = selected[0]
            current_values = tree.item(selected_item, 'values')

        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("420x520")
        win.grab_set() 
        
        entries = {}
        for idx, field in enumerate(fields):
            tk.Label(win, text=field + ":", font=('Arial', 10, 'bold')).pack(anchor='w', padx=25, pady=(12, 2))
            ent = tk.Entry(win, font=('Arial', 10), width=45)
            ent.pack(padx=25, pady=2)
            if is_edit and len(current_values) > idx + 1:
                ent.insert(0, current_values[idx + 1])
            entries[field] = ent
            
        def save_data():
            vals = [entries[f].get().strip() for f in fields]
            if any(v == "" for v in vals):
                messagebox.showerror("Lỗi", "Vui lòng không để trống thông tin!")
                return
                
            if is_edit:
                stt = current_values[0] 
                new_vals = [stt] + vals
                tree.item(selected_item, values=new_vals)
                messagebox.showinfo("Thành công", "Đã cập nhật dữ liệu thành công!")
            else:
                stt = len(tree.get_children()) + 1 
                new_vals = [stt] + vals
                tree.insert('', 'end', values=new_vals)
                messagebox.showinfo("Thành công", "Đã thêm dữ liệu mới thành công!")
            win.destroy()
            
        tk.Button(win, text="LƯU DỮ LIỆU", bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'), width=20, command=save_data).pack(pady=25)

    def delete_item(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để xóa!")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa dữ liệu đã chọn?"):
            for item in selected:
                tree.delete(item)
            self.reindex_stt(tree)

    def reindex_stt(self, tree):
        if "STT" in tree['columns']:
            for idx, item in enumerate(tree.get_children(), start=1):
                vals = list(tree.item(item, 'values'))
                vals[0] = idx
                tree.item(item, values=vals)

    # ==========================================
    # CÀI ĐẶT CÁC TAB 
    # ==========================================
    def create_tab_kho_hang(self):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text="Kho Hàng")
        cols = ("STT", "Tên sản phẩm", "Phân loại", "Số lượng", "Dung tích", "Giá bán", "NSX", "HSD")
        self.tree_kho = self.create_treeview(tab, cols)
        fields = ["Tên sản phẩm", "Phân loại", "Số lượng", "Dung tích", "Giá bán", "NSX", "HSD"]
        self.create_control_panel(tab, ["Giá bán tăng dần", "Giá bán giảm dần", "Tên A-Z", "Tên Z-A"],
            lambda: self.open_form_window("Thêm Sản Phẩm Mới", self.tree_kho, fields),
            lambda: self.open_form_window("Sửa Thông Tin Sản Phẩm", self.tree_kho, fields, is_edit=True),
            lambda: self.delete_item(self.tree_kho))

    def create_tab_ncc(self):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text="Nhà Cung Cấp")
        cols = ("STT", "Tên nhà cung cấp", "SĐT", "Email", "Địa chỉ")
        self.tree_ncc = self.create_treeview(tab, cols)
        fields = ["Tên nhà cung cấp", "SĐT", "Email", "Địa chỉ"]
        self.create_control_panel(tab, ["Tên A-Z", "Tên Z-A"],
            lambda: self.open_form_window("Thêm Nhà Cung Cấp Mới", self.tree_ncc, fields),
            lambda: self.open_form_window("Sửa Thông Tin", self.tree_ncc, fields, is_edit=True),
            lambda: self.delete_item(self.tree_ncc))

    def create_tab_nhan_vien(self):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text="Nhân Viên")
        cols = ("STT", "Tên nhân viên", "Ngày sinh", "SĐT", "Email", "Chức vụ", "Lương")
        self.tree_nhan_vien = self.create_treeview(tab, cols)
        fields = ["Tên nhân viên", "Ngày sinh", "SĐT", "Email", "Chức vụ", "Lương"]
        self.create_control_panel(tab, ["Lương tăng dần", "Lương giảm dần", "Tên A-Z"],
            lambda: self.open_form_window("Thêm Nhân Viên", self.tree_nhan_vien, fields),
            lambda: self.open_form_window("Sửa Thông Tin", self.tree_nhan_vien, fields, is_edit=True),
            lambda: self.delete_item(self.tree_nhan_vien))

    def create_tab_khach_hang(self):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text="Khách Hàng")
        cols = ("STT", "Tên khách hàng", "Ngày sinh", "SĐT", "Lượt mua")
        self.tree_khach_hang = self.create_treeview(tab, cols)
        fields = ["Tên khách hàng", "Ngày sinh", "SĐT", "Lượt mua"]
        self.create_control_panel(tab, ["Lượt mua tăng dần", "Lượt mua giảm dần", "Tên A-Z"],
            lambda: self.open_form_window("Thêm Khách Hàng", self.tree_khach_hang, fields),
            lambda: self.open_form_window("Sửa Thông Tin", self.tree_khach_hang, fields, is_edit=True),
            lambda: self.delete_item(self.tree_khach_hang))

    def create_tab_khuyen_mai(self):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text="Khuyến Mãi")
        cols = ("STT", "Chương trình (Mô tả)", "Phần trăm khuyến mãi (%)", "Ngày bắt đầu", "Ngày kết thúc")
        self.tree_khuyen_mai = self.create_treeview(tab, cols)
        fields = ["Chương trình (Mô tả)", "Phần trăm khuyến mãi (%)", "Ngày bắt đầu", "Ngày kết thúc"]
        self.create_control_panel(tab, [], 
            lambda: self.open_form_window("Thêm Chương Trình", self.tree_khuyen_mai, fields),
            lambda: self.open_form_window("Sửa Chương Trình", self.tree_khuyen_mai, fields, is_edit=True),
            lambda: self.delete_item(self.tree_khuyen_mai))

    # ==========================================
    # CÁC TAB ĐẶC THÙ (PHIẾU NHẬP & HÓA ĐƠN)
    # ==========================================
    def create_tab_phieu_nhap(self):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text="Phiếu Nhập Hàng")
        
        btn_frame = tk.Frame(tab, bg=self.tab_bg)
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="TẠO PHIẾU NHẬP HÀNG", bg='yellow', font=('Arial', 10, 'bold'), command=self.open_import_window).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Xóa Phiếu", bg='#ff6666', command=lambda: self.delete_item(self.tree_phieu_nhap)).pack(side='left', padx=5)
        
        cols = ("Mã Phiếu", "Nhà Cung Cấp", "Ngày Nhập", "Tổng Giá Trị", "Trạng Thái")
        self.tree_phieu_nhap = self.create_treeview(tab, cols)
        self.tree_phieu_nhap.bind("<Double-1>", self.on_import_double_click)

    def create_tab_hoa_don(self):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text="Hóa Đơn")
        
        btn_frame = tk.Frame(tab, bg=self.tab_bg)
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="TẠO HÓA ĐƠN MỚI", bg='yellow', font=('Arial', 10, 'bold'), command=self.open_invoice_window).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Xóa Hóa Đơn", bg='#ff6666', command=lambda: self.delete_item(self.tree_hoa_don)).pack(side='left', padx=5)
        
        cols = ("Mã HĐ", "Khách Hàng", "Nhân Viên", "Ngày Lập", "Tổng Giá Trị", "Trạng Thái")
        self.tree_hoa_don = self.create_treeview(tab, cols)
        self.tree_hoa_don.bind("<Double-1>", self.on_invoice_double_click)

    # Sự kiện Double Click để lấy dữ liệu dòng đang chọn
    def on_import_double_click(self, event):
        selected = self.tree_phieu_nhap.selection()
        if selected:
            item_data = self.tree_phieu_nhap.item(selected[0], 'values')
            self.open_import_window(view_data=item_data)

    def on_invoice_double_click(self, event):
        selected = self.tree_hoa_don.selection()
        if selected:
            item_data = self.tree_hoa_don.item(selected[0], 'values')
            self.open_invoice_window(view_data=item_data)

    # ==========================================
    # CỬA SỔ PHIẾU NHẬP HÀNG 
    # ==========================================
    def open_import_window(self, view_data=None):
        win = tk.Toplevel(self)
        win.title("Chi Tiết Phiếu Nhập Hàng" if view_data else "Tạo Phiếu Nhập Hàng")
        win.geometry("950x650")
        win.grab_set()

        top_frame = tk.LabelFrame(win, text="Thông tin chung", font=('Arial', 10, 'bold'))
        top_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(top_frame, text="Tên Nhà Cung Cấp:").grid(row=0, column=0, padx=5, pady=5)
        ent_ncc = tk.Entry(top_frame, width=25)
        ent_ncc.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(top_frame, text="Tên Nhân Viên:").grid(row=0, column=2, padx=5, pady=5)
        ent_nv = tk.Entry(top_frame, width=20)
        ent_nv.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(top_frame, text="Ngày Nhập:").grid(row=0, column=4, padx=5, pady=5)
        ent_ngay = tk.Entry(top_frame, width=15)
        ent_ngay.grid(row=0, column=5, padx=5, pady=5)

        mid_frame = tk.LabelFrame(win, text="Thêm Sản Phẩm", font=('Arial', 10, 'bold'))
        mid_frame.pack(fill='x', padx=10, pady=5)
        
        labels = ["Tên SP", "Phân loại", "Số lượng", "Dung tích", "Giá nhập", "NSX", "HSD"]
        entries = {}
        for i, lbl in enumerate(labels):
            tk.Label(mid_frame, text=lbl).grid(row=0, column=i, padx=5, pady=2)
            ent = tk.Entry(mid_frame, width=12)
            ent.grid(row=1, column=i, padx=5, pady=5)
            entries[lbl] = ent

        cols = ("Tên SP", "Phân loại", "Số lượng", "Dung tích", "Giá nhập", "NSX", "HSD", "Thành tiền")
        tree = self.create_treeview(win, cols)

        def update_total():
            total = 0
            for child in tree.get_children():
                val = tree.item(child, 'values')[-1].replace(',', '')
                total += float(val)
            lbl_total.config(text=f"Tổng giá trị: {total:,.0f} VNĐ")
            return total

        def add_item():
            try:
                qty = int(entries["Số lượng"].get())
                price = float(entries["Giá nhập"].get().replace(',', ''))
                total_price = qty * price
                
                row_data = [entries[lbl].get() for lbl in labels]
                row_data.append(f"{total_price:,.0f}")
                
                tree.insert('', 'end', values=row_data)
                update_total()
                
                for ent in entries.values():
                    ent.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập Số lượng (số nguyên) và Giá nhập (số) hợp lệ!")

        def remove_item():
            selected = tree.selection()
            if selected:
                for item in selected:
                    tree.delete(item)
                update_total()
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng muốn xóa!")

        def save_import_receipt():
            if view_data:
                win.destroy()
                return

            ncc = ent_ncc.get().strip()
            ngay = ent_ngay.get().strip()
            trang_thai = cb_status.get()
            total_val = update_total()

            if total_val == 0:
                messagebox.showwarning("Cảnh báo", "Phiếu nhập chưa có sản phẩm nào!")
                return
            if not ncc or not ngay:
                messagebox.showwarning("Cảnh báo", "Vui lòng điền đủ Tên Nhà Cung Cấp và Ngày Nhập!")
                return

            current_count = len(self.tree_phieu_nhap.get_children())
            new_id = f"PN{current_count + 1:03d}" 
            
            self.tree_phieu_nhap.insert('', 'end', values=(new_id, ncc, ngay, f"{total_val:,.0f}", trang_thai))
            
            messagebox.showinfo("Thông báo", f"Đã lưu thành công Phiếu Nhập: {new_id}")
            win.destroy()

        action_frame = tk.Frame(mid_frame)
        action_frame.grid(row=1, column=len(labels), padx=10)
        btn_add = tk.Button(action_frame, text="Thêm ⬇", bg='lightblue', font=('Arial', 9, 'bold'), command=add_item)
        btn_add.pack(side='left', padx=2)
        btn_del = tk.Button(action_frame, text="Xóa dòng", bg='#ffcccc', command=remove_item)
        btn_del.pack(side='left', padx=2)

        bot_frame = tk.Frame(win)
        bot_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(bot_frame, text="Trạng thái:").pack(side='left')
        cb_status = ttk.Combobox(bot_frame, values=["Đã thanh toán", "Chưa thanh toán"], state='readonly')
        cb_status.pack(side='left', padx=10)
        cb_status.set("Chưa thanh toán")
        
        lbl_total = tk.Label(bot_frame, text="Tổng giá trị: 0 VNĐ", font=('Arial', 14, 'bold'), fg='red')
        lbl_total.pack(side='left', padx=50)
        
        btn_chot = tk.Button(bot_frame, text="CHỐT & LƯU PHIẾU", bg='lightgreen', font=('Arial', 12, 'bold'), command=save_import_receipt)
        btn_chot.pack(side='right')

        if view_data:
            ent_ncc.insert(0, view_data[1])
            ent_nv.insert(0, "Nguyễn Văn A (Mẫu)")
            ent_ngay.insert(0, view_data[2])
            cb_status.set(view_data[4])
            
            sample_items = [
                ("Trà Đen", "Trà", "50", "500g", "150,000", "01/01/2026", "01/01/2027", "7,500,000"),
                ("Đường Cát", "Gia vị", "20", "1kg", "25,000", "15/02/2026", "15/02/2027", "500,000")
            ]
            for item in sample_items:
                tree.insert('', 'end', values=item)
            
            update_total()
            btn_add.config(state='disabled')
            btn_del.config(state='disabled')
            btn_chot.config(text="ĐÓNG", bg='gray', fg='white')

    # ==========================================
    # CỬA SỔ HÓA ĐƠN
    # ==========================================
    def open_invoice_window(self, view_data=None):
        win = tk.Toplevel(self)
        win.title("Chi Tiết Hóa Đơn" if view_data else "Tạo Hóa Đơn")
        win.geometry("950x650")
        win.grab_set()
        
        top_frame = tk.LabelFrame(win, text="Thông tin hóa đơn", font=('Arial', 10, 'bold'))
        top_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(top_frame, text="Tên Khách Hàng:").grid(row=0, column=0, padx=5, pady=5)
        ent_kh = tk.Entry(top_frame, width=25)
        ent_kh.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(top_frame, text="Tên Nhân Viên:").grid(row=0, column=2, padx=5, pady=5)
        ent_nv = tk.Entry(top_frame, width=25)
        ent_nv.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(top_frame, text="Ngày Lập:").grid(row=0, column=4, padx=5, pady=5)
        ent_ngay = tk.Entry(top_frame, width=15)
        ent_ngay.grid(row=0, column=5, padx=5, pady=5)

        mid_frame = tk.LabelFrame(win, text="Chi tiết mua hàng", font=('Arial', 10, 'bold'))
        mid_frame.pack(fill='x', padx=10, pady=5)
        
        labels = ["Tên SP", "Phân loại", "Số lượng", "Dung tích", "Giá bán"]
        entries = {}
        for i, lbl in enumerate(labels):
            tk.Label(mid_frame, text=lbl).grid(row=0, column=i, padx=5, pady=2)
            ent = tk.Entry(mid_frame, width=15)
            ent.grid(row=1, column=i, padx=5, pady=5)
            entries[lbl] = ent
            
        cols = ("Tên SP", "Phân loại", "Số lượng", "Dung tích", "Giá bán", "Thành tiền")
        tree = self.create_treeview(win, cols)

        def update_total():
            total = 0
            for child in tree.get_children():
                val = tree.item(child, 'values')[-1].replace(',', '')
                total += float(val)
            lbl_total.config(text=f"Tổng giá trị: {total:,.0f} VNĐ")
            return total

        def add_item():
            try:
                qty = int(entries["Số lượng"].get())
                price = float(entries["Giá bán"].get().replace(',', ''))
                total_price = qty * price
                
                row_data = [entries[lbl].get() for lbl in labels]
                row_data.append(f"{total_price:,.0f}") 
                
                tree.insert('', 'end', values=row_data)
                update_total()
                
                for ent in entries.values():
                    ent.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập Số lượng (số nguyên) và Giá bán (số) hợp lệ!")

        def remove_item():
            selected = tree.selection()
            if selected:
                for item in selected:
                    tree.delete(item)
                update_total()
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng muốn xóa!")

        def save_invoice():
            if view_data:
                win.destroy()
                return

            kh = ent_kh.get().strip()
            nv = ent_nv.get().strip()
            ngay = ent_ngay.get().strip()
            trang_thai = cb_status.get()
            total_val = update_total()

            if total_val == 0:
                messagebox.showwarning("Cảnh báo", "Hóa đơn chưa có sản phẩm nào!")
                return
            if not kh or not nv or not ngay:
                messagebox.showwarning("Cảnh báo", "Vui lòng điền đủ thông tin Khách Hàng, Nhân Viên và Ngày Lập!")
                return

            current_count = len(self.tree_hoa_don.get_children())
            new_id = f"HD{current_count + 1:03d}"
            
            self.tree_hoa_don.insert('', 'end', values=(new_id, kh, nv, ngay, f"{total_val:,.0f}", trang_thai))
            
            messagebox.showinfo("Thông báo", f"Xuất hóa đơn thành công: {new_id}")
            win.destroy()

        action_frame = tk.Frame(mid_frame)
        action_frame.grid(row=1, column=len(labels), padx=10)
        btn_add = tk.Button(action_frame, text="Thêm ⬇", bg='lightblue', font=('Arial', 9, 'bold'), command=add_item)
        btn_add.pack(side='left', padx=2)
        btn_del = tk.Button(action_frame, text="Xóa dòng", bg='#ffcccc', command=remove_item)
        btn_del.pack(side='left', padx=2)

        bot_frame = tk.Frame(win)
        bot_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(bot_frame, text="Trạng thái:").pack(side='left')
        cb_status = ttk.Combobox(bot_frame, values=["Đã thanh toán", "Chưa thanh toán"], state='readonly')
        cb_status.pack(side='left', padx=10)
        cb_status.set("Đã thanh toán")
        
        lbl_total = tk.Label(bot_frame, text="Tổng giá trị: 0 VNĐ", font=('Arial', 14, 'bold'), fg='red')
        lbl_total.pack(side='left', padx=50)
        
        btn_chot = tk.Button(bot_frame, text="CHỐT & XUẤT HÓA ĐƠN", bg='lightgreen', font=('Arial', 12, 'bold'), command=save_invoice)
        btn_chot.pack(side='right')

        if view_data:
            ent_kh.insert(0, view_data[1])
            ent_nv.insert(0, view_data[2])
            ent_ngay.insert(0, view_data[3])
            cb_status.set(view_data[5])
            
            sample_items = [
                ("Trà Sữa Trân Châu", "Trà sữa", "2", "500ml", "35,000", "70,000"),
                ("Cà Phê Đen Đá", "Cà phê", "1", "300ml", "20,000", "20,000")
            ]
            for item in sample_items:
                tree.insert('', 'end', values=item)
                
            update_total()
            btn_add.config(state='disabled')
            btn_del.config(state='disabled')
            btn_chot.config(text="ĐÓNG", bg='gray', fg='white')

    # ==========================================
    # DATA MẪU
    # ==========================================
    def insert_sample_data(self):
        kho_data = [
            (1, "Trà Sữa Trân Châu", "Trà sữa", "50", "500ml", "35,000", "01/05/2026", "01/06/2026"),
            (2, "Cà Phê Đen Đá", "Cà phê", "30", "300ml", "20,000", "20/05/2026", "25/05/2026"),
            (3, "Trà Đào Cam Sả", "Trà trái cây", "40", "700ml", "45,000", "22/05/2026", "24/05/2026")
        ]
        for item in kho_data: self.tree_kho.insert('', 'end', values=item)

        ncc_data = [
            (1, "Công ty Trà Phúc Long", "0123456789", "phuclong@email.com", "TP.HCM"),
            (2, "Cà phê Trung Nguyên", "0987654321", "trungnguyen@email.com", "Đắk Lắk")
        ]
        for item in ncc_data: self.tree_ncc.insert('', 'end', values=item)

        pn_data = [
            ("PN001", "Công ty Trà Phúc Long", "24/05/2026", "5,000,000", "Đã thanh toán"),
            ("PN002", "Cà phê Trung Nguyên", "20/05/2026", "2,500,000", "Chưa thanh toán")
        ]
        for item in pn_data: self.tree_phieu_nhap.insert('', 'end', values=item)

        nv_data = [
            (1, "Nguyễn Văn A", "01/01/2000", "0909090909", "nva@email.com", "Quản lý", "15,000,000"),
            (2, "Trần Thị B", "05/05/2002", "0808080808", "ttb@email.com", "Pha chế", "8,000,000")
        ]
        for item in nv_data: self.tree_nhan_vien.insert('', 'end', values=item)

        hd_data = [
            ("HD001", "Lê Văn C", "Trần Thị B", "24/05/2026", "90,000", "Đã thanh toán"),
            ("HD002", "Khách vãng lai", "Trần Thị B", "24/05/2026", "35,000", "Đã thanh toán")
        ]
        for item in hd_data: self.tree_hoa_don.insert('', 'end', values=item)

        kh_data = [
            (1, "Lê Văn C", "10/10/1995", "0707070707", "5"),
            (2, "Phạm Thị D", "12/12/1998", "0606060606", "2")
        ]
        for item in kh_data: self.tree_khach_hang.insert('', 'end', values=item)

        km_data = [
            (1, "Giảm giá khai trương mùa hè", "20%", "01/06/2026", "30/06/2026"),
            (2, "Combo Thứ 7 Mua 2 Tặng 1", "33%", "01/01/2026", "31/12/2026")
        ]
        for item in km_data: self.tree_khuyen_mai.insert('', 'end', values=item)

if __name__ == "__main__":
    app = BeverageManagementSystem()
    app.mainloop()