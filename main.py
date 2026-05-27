import tkinter as tk
from tkinter import ttk, messagebox
from database.database import DatabaseManager # Import class kết nối CSDL
from datetime import datetime

class BeverageManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Cửa Hàng Đồ Uống")
        self.geometry("1100x700")
        self.state('zoomed') 
        
        # Kết nối Cơ sở dữ liệu
        self.db = DatabaseManager()
        
        self.current_frame = None
        self.tab_bg = '#E8F4F8'

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Dashboard.TButton', font=('Arial', 14, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        
        self.create_dashboard()

    # ==========================================
    # 1. GIAO DIỆN CHÍNH (DASHBOARD)
    # ==========================================
    def create_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self, bg='#f0f0f0')
        self.current_frame.pack(fill='both', expand=True)
        
        tk.Label(self.current_frame, text="DASHBOARD - QUẢN LÝ CỬA HÀNG", font=('Arial', 24, 'bold'), bg='#f0f0f0').pack(pady=40)

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

        for idx, (text, command, color) in enumerate(modules):
            row, col = divmod(idx, 4)
            btn = tk.Button(grid_frame, text=text, font=('Arial', 12, 'bold'), 
                            width=15, height=7, bg=color, relief='groove', cursor='hand2', command=command)
            btn.grid(row=row, column=col, padx=20, pady=20)

    # ==========================================
    # 2. KHỞI TẠO CÁC TAB & GIAO DIỆN BẢNG
    # ==========================================
    def show_module(self, tab_index):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self)
        self.current_frame.pack(fill='both', expand=True)

        top_bar = tk.Frame(self.current_frame, bg='#333', height=40)
        top_bar.pack(fill='x')
        tk.Button(top_bar, text="⬅ Về Dashboard", command=self.create_dashboard, bg='white', cursor='hand2').pack(side='left', padx=10, pady=5)

        self.notebook = ttk.Notebook(self.current_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.init_all_tabs()
        self.notebook.select(tab_index)

    def init_all_tabs(self):
        # 1. Sản phẩm 
        san_pham_query = """
            SELECT SanPham.MaSP, SanPham.TenSP, SanPham.SoLuong, SanPham.DungTich, SanPham.GiaBan, SanPham.NXS, SanPham.HSD, PhanLoai.TenLoai 
            FROM SanPham 
            LEFT JOIN PhanLoai ON SanPham.IdLoai = PhanLoai.IdLoai
        """
        self.tree_kho = self.setup_standard_tab(
            "Sản Phẩm", "SP", "SanPham", "MaSP",  
            ("Mã sản phẩm", "Tên sản phẩm", "Số lượng", "Dung tích", "Giá bán", "NXS", "HSD", "Phân Loại"),
            ["Tên sản phẩm", "Số lượng", "Dung tích", "Giá bán", "NXS", "HSD", "Phân Loại"],
            ["TenSP", "SoLuong", "DungTich", "GiaBan", "NXS", "HSD", "IdLoai"],
            custom_query=san_pham_query
        )
        
        # 2. Nhà cung cấp 
        self.tree_ncc = self.setup_standard_tab(
            "Nhà Cung Cấp", "NCC", "NhaCungCap", "MaNCC",
            ("Mã NCC", "Tên nhà cung cấp", "SĐT", "Email", "Địa chỉ"),
            ["Tên nhà cung cấp", "SĐT", "Email", "Địa chỉ"],
            ["TenNCC", "SDT", "Email", "DiaChi"]
        )
        
        # 3. Phiếu nhập (Giao dịch)
        self.tree_phieu_nhap = self.setup_transaction_tab(
            "Phiếu Nhập Hàng", "TẠO PHIẾU NHẬP HÀNG", self.open_import_window,
            ("Mã Phiếu", "Nhà Cung Cấp", "Ngày Nhập", "Tổng Giá Trị", "Trạng Thái")
        )

        # 4. Nhân viên
        nhan_vien_query = """
            SELECT NhanVien.MaNV, NhanVien.HoTen, NhanVien.NgaySinh, NhanVien.GioiTinh, NhanVien.SDT, NhanVien.Email, ChucVu.TenCV 
            FROM NhanVien 
            LEFT JOIN ChucVu ON NhanVien.IdCV = ChucVu.IdCV
        """
        self.tree_nhan_vien = self.setup_standard_tab(
            "Nhân Viên", "NV", "NhanVien", "MaNV",
            ("Mã nhân viên", "Họ tên", "Ngày sinh", "Giới tính", "SĐT", "Email", "Chức vụ"),
            ["Họ tên", "Ngày sinh", "Giới tính", "SĐT", "Email", "Chức vụ"],
            ["HoTen", "NgaySinh", "GioiTinh", "SDT", "Email", "IdCV"],
            custom_query=nhan_vien_query
        )
        
        # 5. Hóa đơn 
        self.tree_hoa_don = self.setup_transaction_tab(
            "Hóa Đơn", "TẠO HÓA ĐƠN MỚI", self.open_invoice_window,
            ("Mã HĐ", "Khách Hàng", "Nhân Viên", "Ngày Lập", "Tổng Giá Trị", "Trạng Thái")
        )

        # 6. Khách hàng 
        self.tree_khach_hang = self.setup_standard_tab(
            "Khách Hàng", "KH", "KhachHang", "MaKH",
            ("Mã khách hàng", "Họ tên", "Ngày sinh", "SĐT"),
            ["Họ tên", "Ngày sinh", "SĐT"],
            ["HoTen", "NgaySinh", "SDT"]
        )
        
        # 7. Khuyến mãi
        self.tree_khuyen_mai = self.setup_standard_tab(
            "Khuyến Mãi", "KM", "KhuyenMai", "MaKM",
            ("Mã khuyến mãi", "Chương trình", "Phần trăm giảm", "Ngày bắt đầu", "Ngày kết thúc"),
            ["Chương trình", "Phần trăm giảm", "Ngày bắt đầu", "Ngày kết thúc"],
            ["ChuongTrinh", "PhanTramGiam", "NgayBatDau", "NgayKetThuc"]
        )

    # ==========================================
    # 3. CÁC HÀM XÂY DỰNG UI TÁI SỬ DỤNG
    # ==========================================
    def setup_standard_tab(self, tab_title, id_prefix, table_name, id_col, cols, fields, db_cols, custom_query=None):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text=tab_title)
        
        tree = self.create_treeview(tab, cols)
        
        self.create_control_panel(tab, 
            lambda: self.open_form_window(f"Thêm {tab_title}", tree, fields, db_cols, table_name, id_col, id_prefix=id_prefix),
            lambda: self.open_form_window(f"Sửa {tab_title}", tree, fields, db_cols, table_name, id_col, is_edit=True),
            lambda: self.delete_item(tree, table_name, id_col))
        
        self.load_data_from_db(tree, table_name, id_col, db_cols, custom_query)
        return tree

    def setup_transaction_tab(self, tab_title, btn_text, open_cmd, cols):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text=tab_title)
        
        # Căn giữa các nút bấm cho giao dịch
        btn_frame = tk.Frame(tab, bg=self.tab_bg)
        btn_frame.pack(fill='x', pady=10)
        
        inner_frame = tk.Frame(btn_frame, bg=self.tab_bg)
        inner_frame.pack(anchor='center')
        
        tk.Button(inner_frame, text=btn_text, bg='yellow', width=25, font=('Arial', 10, 'bold'), command=open_cmd).pack(side='left', padx=10)
        tk.Button(inner_frame, text="Xóa", bg='#ff6666', width=15, font=('Arial', 10, 'bold'), command=lambda: self.delete_item(tree)).pack(side='left', padx=10)
        
        tree = self.create_treeview(tab, cols)
        return tree

    def create_treeview(self, parent, columns):
        tree_frame = tk.Frame(parent, bg=self.tab_bg)
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
            width = 100 if "Mã" in col or "Giới tính" in col else 120
            tree.column(col, width=width, anchor='center')
            
        return tree

    def create_control_panel(self, parent, add_cmd, edit_cmd, delete_cmd):
        panel = tk.Frame(parent, bg=self.tab_bg)
        panel.pack(fill='x', pady=10)
        
        # Sub-frame để căn giữa các nút điều khiển
        btn_center_frame = tk.Frame(panel, bg=self.tab_bg)
        btn_center_frame.pack(anchor='center')
        
        actions = [("Thêm", 'lightblue', add_cmd), ("Sửa", 'lightgreen', edit_cmd), ("Xóa", '#ff6666', delete_cmd)]
        for text, color, cmd in actions:
            tk.Button(btn_center_frame, text=text, width=15, font=('Arial', 10, 'bold'), bg=color, command=cmd).pack(side='left', padx=15)

    # ==========================================
    # 4. LOGIC XỬ LÝ CSDL (TẢI, CRUD)
    # ==========================================
    def load_data_from_db(self, tree, table_name, id_col, db_cols, custom_query=None):
        tree.delete(*tree.get_children())
        
        if custom_query:
            query = custom_query
        else:
            cols_str = f"{id_col}, " + ", ".join(db_cols)
            query = f"SELECT {cols_str} FROM {table_name}"
            
        records = self.db.fetch_all(query)
        for row in records:
            tree.insert('', 'end', values=row)

    def get_selected_values(self, tree):
        selected = tree.selection()
        return tree.item(selected[0], 'values') if selected else None

    def open_form_window(self, title, tree, fields, db_cols, table_name, id_col, is_edit=False, id_prefix=""):
        current_values = self.get_selected_values(tree) if is_edit else []
        if is_edit and not current_values:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng trên bảng để sửa!")
            return

        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("420x560")
        win.grab_set() 
        
        entries = {}
        for idx, field in enumerate(fields):
            tk.Label(win, text=f"{field}:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=25, pady=(12, 2))
            
            if field == "Giới tính":
                ent = ttk.Combobox(win, values=["Nam", "Nữ"], font=('Arial', 10), width=43, state='readonly')
                ent.pack(padx=25, pady=2)
                if is_edit and len(current_values) > idx + 1:
                    ent.set(current_values[idx + 1])
                else:
                    ent.set("Nam")
            else:
                ent = tk.Entry(win, font=('Arial', 10), width=45)
                ent.pack(padx=25, pady=2)
                if is_edit and len(current_values) > idx + 1:
                    ent.insert(0, current_values[idx + 1])
                    
            entries[field] = ent
            
        def save_data():
            vals = [entries[f].get().strip() for f in fields]
            if not all(vals):
                messagebox.showerror("Lỗi", "Vui lòng không để trống thông tin!")
                return
                
            if is_edit:
                # SỬA DỮ LIỆU
                item_id = current_values[0]
                set_clause = ", ".join([f"{col} = %s" for col in db_cols])
                query = f"UPDATE {table_name} SET {set_clause} WHERE {id_col} = %s"
                params = tuple(vals) + (item_id,)
                
                if self.db.execute_query(query, params):
                    selected_item = tree.selection()[0]
                    tree.item(selected_item, values=[item_id] + vals)
                    messagebox.showinfo("Thành công", "Cập nhật dữ liệu CSDL thành công!")
                    win.destroy()
                else:
                    messagebox.showerror("Lỗi CSDL", "Không thể cập nhật CSDL.")
            else:
                # THÊM DỮ LIỆU
                new_id = f"{id_prefix}{len(tree.get_children()) + 1:03d}" if id_prefix else f"{len(tree.get_children()) + 1}"
                cols_str = ", ".join([id_col] + db_cols)
                placeholders = ", ".join(["%s"] * (len(db_cols) + 1))
                query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
                params = tuple([new_id] + vals)
                
                if self.db.execute_query(query, params):
                    tree.insert('', 'end', values=[new_id] + vals)
                    messagebox.showinfo("Thành công", "Đã lưu vào CSDL thành công!")
                    win.destroy()
                else:
                    messagebox.showerror("Lỗi CSDL", "Không thể thêm vào CSDL.")
            
        tk.Button(win, text="LƯU DỮ LIỆU", bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'), width=20, command=save_data).pack(pady=25)

    def delete_item(self, tree, table_name=None, id_col=None):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để xóa!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa dữ liệu này khỏi CSDL?"):
            for item in selected:
                if table_name and id_col:
                    item_id = tree.item(item, 'values')[0]
                    query = f"DELETE FROM {table_name} WHERE {id_col} = %s"
                    if self.db.execute_query(query, (item_id,)):
                        tree.delete(item)
                    else:
                        messagebox.showerror("Lỗi", f"Lỗi xóa ID {item_id} từ CSDL.")
                else:
                    tree.delete(item)

    # ==========================================
    # 5. NGHIỆP VỤ PHIẾU NHẬP / HÓA ĐƠN
    # ==========================================
    def open_import_window(self, view_data=None):
        pass 

    def open_invoice_window(self, view_data=None):
        pass 

if __name__ == "__main__":
    app = BeverageManagementSystem()
    app.mainloop()