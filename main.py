import tkinter as tk
from tkinter import ttk, messagebox
from database.database import DatabaseManager # Import class kết nối CSDL
from datetime import datetime
import re # Tự động tạo Mã PNH tăng dần (VD: PNH001, PNH002...)

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
            ("Chương trình\nKhuyến mãi", lambda: self.show_module(6), '#99FFE6'),
            ("Thiết lập\nDanh mục", self.open_settings_window, '#CCCCCC')
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
        
        # 3. Phiếu nhập 
        self.tree_phieu_nhap = self.setup_transaction_tab(
            "Phiếu Nhập Hàng", "TẠO PHIẾU NHẬP HÀNG", self.open_import_window,
            ("Mã Phiếu", "Mã NCC", "Mã NV", "Ngày Nhập", "Tổng Giá Trị", "Trạng Thái"),
            table_name="PhieuNhapHang", id_col="MaPNH"
        )
        self.load_phieu_nhap_data()
        self.tree_phieu_nhap.bind("<Double-1>", lambda e: self.on_phieu_nhap_double_click())

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
            ("Mã HĐ", "Khách Hàng", "Nhân Viên", "Ngày Lập", "Tổng Giá Trị", "Trạng Thái"),
            table_name="HoaDon", id_col="MaHD"
        )
        self.load_hoa_don_data()
        self.tree_hoa_don.bind("<Double-1>", lambda e: self.on_hoa_don_double_click())

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

    def load_phieu_nhap_data(self):
        query = """
            SELECT p.MaPNH, ncc.MaNCC, nv.MaNV, p.NgayNhap, p.TongGiaTri, p.TrangThai 
            FROM PhieuNhapHang p
            LEFT JOIN NhaCungCap ncc ON p.IdNCC = ncc.IdNCC
            LEFT JOIN NhanVien nv ON p.IdNV = nv.IdNV
        """
        self.tree_phieu_nhap.delete(*self.tree_phieu_nhap.get_children())
        for row in self.db.fetch_all(query):
            self.tree_phieu_nhap.insert('', 'end', values=row)

    def load_hoa_don_data(self):
        query = """
            SELECT h.MaHD, kh.MaKH, nv.MaNV, h.NgayLap, h.TongGiaTri, h.TrangThai 
            FROM HoaDon h
            LEFT JOIN KhachHang kh ON h.IdKH = kh.IdKH
            LEFT JOIN NhanVien nv ON h.IdNV = nv.IdNV
        """
        self.tree_hoa_don.delete(*self.tree_hoa_don.get_children())
        for row in self.db.fetch_all(query):
            self.tree_hoa_don.insert('', 'end', values=row)

    def on_phieu_nhap_double_click(self):
        selected = self.tree_phieu_nhap.selection()
        if selected:
            val = self.tree_phieu_nhap.item(selected[0], 'values')
            self.open_import_window(view_data=val)

    def on_hoa_don_double_click(self):
        selected = self.tree_hoa_don.selection()
        if selected:
            val = self.tree_hoa_don.item(selected[0], 'values')
            self.open_invoice_window(view_data=val)

    def open_settings_window(self):
        settings_win = tk.Toplevel(self)
        settings_win.title("Thiết Lập Danh Mục Hệ Thống")
        settings_win.geometry("1000x600")
        settings_win.grab_set() 

        # Khung chứa Phân Loại (Nửa bên trái)
        frame_loai = tk.LabelFrame(settings_win, text="Quản lý Phân Loại", font=("Arial", 11, "bold"), fg="#2C3E50")
        frame_loai.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 10), pady=20)
        
        self.setup_standard_tab("Phân Loại", "AUTO", "PhanLoai", "IdLoai",
            ("STT", "Tên Phân Loại"), ["Tên Phân Loại"], ["TenLoai"], parent_frame=frame_loai)

        # Khung chứa Chức Vụ (Nửa bên phải)
        frame_cv = tk.LabelFrame(settings_win, text="Quản lý Chức Vụ", font=("Arial", 11, "bold"), fg="#2C3E50")
        frame_cv.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=20)
        
        self.setup_standard_tab("Chức Vụ", "AUTO", "ChucVu", "IdCV",
            ("STT", "Tên Chức Vụ"), ["Tên Chức Vụ"], ["TenCV"], parent_frame=frame_cv)
    
    # ==========================================
    # 3. CÁC HÀM XÂY DỰNG UI TÁI SỬ DỤNG
    # ==========================================
    # SỬA LỖI: Bổ sung tham số mặc định parent_frame=None để nhận dữ liệu từ pop-up thiết lập
    def setup_standard_tab(self, tab_title, id_prefix, table_name, id_col, cols, fields, db_cols, custom_query=None, parent_frame=None):
        # Nếu có truyền parent_frame (giao diện pop-up) thì dùng nó, ngược lại thì thêm vào notebook chính
        parent = parent_frame if parent_frame else self.notebook
        tab = tk.Frame(parent, bg=self.tab_bg)
        
        if parent_frame is None:
            self.notebook.add(tab, text=tab_title)
        else:
            tab.pack(fill='both', expand=True)
        
        tree = self.create_treeview(tab, cols)
        
        self.create_control_panel(tab, 
            lambda: self.open_form_window(f"Thêm {tab_title}", tree, fields, db_cols, table_name, id_col, id_prefix=id_prefix),
            lambda: self.open_form_window(f"Sửa {tab_title}", tree, fields, db_cols, table_name, id_col, is_edit=True),
            lambda: self.delete_item(tree, table_name, id_col))
        
        self.load_data_from_db(tree, table_name, id_col, db_cols, custom_query)
        return tree

    def setup_transaction_tab(self, tab_title, btn_text, open_cmd, cols, table_name=None, id_col=None):
        tab = tk.Frame(self.notebook, bg=self.tab_bg)
        self.notebook.add(tab, text=tab_title)
        
        # Cải tiến: Tạo tree trước nút bấm để tránh lỗi cảnh báo tham chiếu (Late-binding warning)
        tree = self.create_treeview(tab, cols)
        
        btn_frame = tk.Frame(tab, bg=self.tab_bg)
        btn_frame.pack(fill='x', pady=10, before=tree.master) # Đảm bảo nút nằm phía trên bảng dữ liệu
        
        inner_frame = tk.Frame(btn_frame, bg=self.tab_bg)
        inner_frame.pack(anchor='center')
        
        tk.Button(inner_frame, text=btn_text, bg='yellow', width=25, font=('Arial', 10, 'bold'), command=open_cmd).pack(side='left', padx=10)
        tk.Button(inner_frame, text="Xóa", bg='#ff6666', width=15, font=('Arial', 10, 'bold'), 
        command=lambda: self.delete_item(tree, table_name, id_col)).pack(side='left', padx=10)
        
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
            
            db_vals = vals.copy()
            display_vals = vals.copy()

            # 1. Xử lý cho bảng Sản Phẩm (Khóa ngoại Phân Loại)
            if table_name == "SanPham":
                ten_loai = vals[-1]
                query_find = f"SELECT IdLoai FROM PhanLoai WHERE TenLoai = '{ten_loai}'"
                loai_record = self.db.fetch_all(query_find)
                
                if loai_record:
                    id_loai = loai_record[0][0]
                else:
                    insert_loai_query = "INSERT INTO PhanLoai (TenLoai) VALUES (%s)"
                    if self.db.execute_query(insert_loai_query, (ten_loai,)):
                        get_id_query = f"SELECT IdLoai FROM PhanLoai WHERE TenLoai = '{ten_loai}'"
                        new_loai_record = self.db.fetch_all(get_id_query)
                        if new_loai_record:
                            id_loai = new_loai_record[0][0]
                        else:
                            messagebox.showerror("Lỗi", "Không thể lấy ID phân loại vừa tạo.")
                            return
                    else:
                        messagebox.showerror("Lỗi", "Không thể tự động thêm Phân Loại mới.")
                        return
                db_vals[-1] = id_loai

            # 2. Xử lý cho bảng Nhân Viên (Khóa ngoại Chức Vụ)
            elif table_name == "NhanVien":
                ten_cv = vals[-1]
                query_find = f"SELECT IdCV FROM ChucVu WHERE TenCV = '{ten_cv}'"
                cv_record = self.db.fetch_all(query_find)
                
                if cv_record:
                    id_cv = cv_record[0][0]
                else:
                    insert_cv_query = "INSERT INTO ChucVu (TenCV) VALUES (%s)"
                    if self.db.execute_query(insert_cv_query, (ten_cv,)):
                        get_id_query = f"SELECT IdCV FROM ChucVu WHERE TenCV = '{ten_cv}'"
                        new_cv_record = self.db.fetch_all(get_id_query)
                        if new_cv_record:
                            id_cv = new_cv_record[0][0]
                        else:
                            messagebox.showerror("Lỗi", "Không thể lấy ID chức vụ vừa tạo.")
                            return
                    else:
                        messagebox.showerror("Lỗi", "Không thể tự động thêm Chức Vụ mới vào CSDL.")
                        return
                db_vals[-1] = id_cv
            
            # QUÁ TRÌNH LƯU DỮ LIỆU CHÍNH
            if is_edit:
                # SỬA DỮ LIỆU
                item_id = current_values[0]
                set_clause = ", ".join([f"{col} = %s" for col in db_cols])
                query = f"UPDATE {table_name} SET {set_clause} WHERE {id_col} = %s"
                params = tuple(db_vals) + (item_id,)
                
                if self.db.execute_query(query, params):
                    selected_item = tree.selection()[0]
                    tree.item(selected_item, values=[item_id] + display_vals)
                    messagebox.showinfo("Thành công", "Cập nhật dữ liệu CSDL thành công!")
                    win.destroy()
                else:
                    messagebox.showerror("Lỗi CSDL", "Không thể cập nhật CSDL.")
            else:
                # THÊM DỮ LIỆU
                if id_prefix == "AUTO":
                    cols_str = ", ".join(db_cols)
                    placeholders = ", ".join(["%s"] * len(db_cols))
                    query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
                    params = tuple(db_vals)
                    
                    if self.db.execute_query(query, params):
                        last_id_query = f"SELECT {id_col} FROM {table_name} ORDER BY {id_col} DESC LIMIT 1"
                        new_record = self.db.fetch_all(last_id_query)
                        new_id = new_record[0][0] if new_record else "NEW"
                        
                        tree.insert('', 'end', values=[new_id] + display_vals)
                        messagebox.showinfo("Thành công", "Đã lưu Danh mục vào CSDL thành công!")
                        win.destroy()
                    else:
                        messagebox.showerror("Lỗi CSDL", "Không thể thêm vào CSDL.")
                        
                else:
                    if id_prefix:
                        # Lấy ID cuối cùng từ CSDL
                        last_id_query = f"SELECT {id_col} FROM {table_name} ORDER BY {id_col} DESC LIMIT 1"
                        last_record = self.db.fetch_all(last_id_query)

                        if last_record and last_record[0][0]:
                            match = re.search(r'\d+', last_record[0][0])
                            if match:
                                new_num = int(match.group()) + 1
                                new_id = f"{id_prefix}{new_num:03d}"
                            else:
                                new_id = f"{id_prefix}001"
                        else:
                            new_id = f"{id_prefix}001"
                    else:
                        new_id = f"{len(tree.get_children()) + 1}" 
                    cols_str = ", ".join([id_col] + db_cols)
                    placeholders = ", ".join(["%s"] * (len(db_cols) + 1))
                    query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
                    params = tuple([new_id] + db_vals)
                    
                    if self.db.execute_query(query, params):
                        tree.insert('', 'end', values=[new_id] + display_vals)
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
        win = tk.Toplevel(self)
        win.title("Chi Tiết Phiếu Nhập Hàng")
        win.geometry("850x650")
        win.grab_set()

        # Biến quản lý tổng tiền realtime
        total_var = tk.StringVar(value="0 VNĐ")
        is_view_mode = view_data is not None
        
        # BỔ SUNG: Khởi tạo biến lưu trạng thái hiện tại
        current_status = ""

        # --- PHẦN 1 & 2: THÔNG TIN CHUNG ---
        info_frame = tk.LabelFrame(win, text="Thông tin phiếu nhập", font=('Arial', 11, 'bold'), pady=10, padx=10)
        info_frame.pack(fill='x', padx=15, pady=10)

        tk.Label(info_frame, text="Mã Phiếu:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ent_ma_pnh = tk.Entry(info_frame, width=15)
        ent_ma_pnh.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(info_frame, text="Mã Nhà Cung Cấp:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ent_ma_ncc = tk.Entry(info_frame, width=15)
        ent_ma_ncc.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(info_frame, text="Mã Nhân Viên:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ent_ma_nv = tk.Entry(info_frame, width=15)
        ent_ma_nv.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(info_frame, text="Ngày nhập:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        ent_ngay = tk.Entry(info_frame, width=15)
        ent_ngay.grid(row=1, column=3, padx=5, pady=5)

        # THAY ĐỔI: Thêm nhãn Trạng thái cho cả 2 chế độ
        tk.Label(info_frame, text="Trạng thái:").grid(row=2, column=0, padx=5, pady=5, sticky='w')

        if not is_view_mode:
            now = datetime.now()
            ent_ngay.insert(0, now.strftime("%Y-%m-%d %H:%M:%S"))
            
            # Tạo mã tự động (giữ nguyên logic của bạn)
            last_pnh = self.db.fetch_all("SELECT MaPNH FROM PhieuNhapHang ORDER BY IdPN DESC LIMIT 1")
            if last_pnh and last_pnh[0][0]:
                match = re.search(r'\d+', last_pnh[0][0])
                if match:
                    new_id = int(match.group()) + 1
                    ent_ma_pnh.insert(0, f"PN{new_id:03d}")
                else: ent_ma_pnh.insert(0, "PN001")
            else: ent_ma_pnh.insert(0, "PN001")
            
            # THAY ĐỔI: Thêm Combobox để chọn trạng thái khi TẠO MỚI
            cbo_status = ttk.Combobox(info_frame, values=["Chưa Thanh Toán", "Đã Thanh Toán"], width=15, state="readonly")
            cbo_status.set("Chưa Thanh Toán") # Mặc định ban đầu
            cbo_status.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        else:
            ent_ma_pnh.insert(0, view_data[0])
            ent_ma_ncc.insert(0, view_data[1])
            ent_ngay.insert(0, view_data[3])
            total_var.set(f"{view_data[4]} VNĐ")
            
            nv_res = self.db.fetch_all(f"SELECT nv.MaNV, p.TrangThai FROM PhieuNhapHang p JOIN NhanVien nv ON p.IdNV = nv.IdNV WHERE p.MaPNH='{view_data[0]}'")
            if nv_res: 
                ent_ma_nv.insert(0, nv_res[0][0])
                current_status = nv_res[0][1]
            
            # Ở chế độ XEM: Chỉ hiển thị text thông thường không cho sửa
            status_color = 'red' if current_status.lower() == 'chưa thanh toán' else 'green'
            tk.Label(info_frame, text=current_status, fg=status_color, font=('Arial', 10, 'bold')).grid(row=2, column=1, padx=5, pady=5, sticky='w')
            
            ent_ma_pnh.config(state='readonly')
            ent_ma_ncc.config(state='readonly')
            ent_ma_nv.config(state='readonly')
            ent_ngay.config(state='readonly')

        # --- PHẦN 3: THÊM SẢN PHẨM MỚI (CHỈ HIỆN KHI THÊM MỚI) ---
        if not is_view_mode:
            add_item_frame = tk.LabelFrame(win, text="Thêm sản phẩm nhập", font=('Arial', 10, 'bold'))
            add_item_frame.pack(fill='x', padx=15, pady=5)

            tk.Label(add_item_frame, text="Mã SP:").grid(row=0, column=0, padx=5, pady=5)
            ent_item_sp = tk.Entry(add_item_frame, width=12)
            ent_item_sp.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(add_item_frame, text="Số Lượng:").grid(row=0, column=2, padx=5, pady=5)
            ent_item_sl = tk.Entry(add_item_frame, width=8)
            ent_item_sl.grid(row=0, column=3, padx=5, pady=5)

            tk.Label(add_item_frame, text="Giá Nhập:").grid(row=0, column=4, padx=5, pady=5)
            ent_item_gia = tk.Entry(add_item_frame, width=12)
            ent_item_gia.grid(row=0, column=5, padx=5, pady=5)

        # --- BẢNG DANH SÁCH CHI TIẾT SẢN PHẨM ---
        table_frame = tk.Frame(win)
        table_frame.pack(fill='both', expand=True, padx=15, pady=10)

        cols = ("Mã sản phẩm", "Số lượng", "Giá nhập", "Thành tiền")
        tree_detail = ttk.Treeview(table_frame, columns=cols, show='headings', height=8)
        tree_detail.pack(side='left', fill='both', expand=True)
        
        for col in cols:
            tree_detail.heading(col, text=col)
            tree_detail.column(col, anchor='center', width=130)

        # Hàm tính toán lại tổng tiền của toàn phiếu nhập
        def recalculate_total():
            grand_total = 0
            for item in tree_detail.get_children():
                grand_total += float(tree_detail.item(item, 'values')[3])
            total_var.set(f"{grand_total:,.0f} VNĐ")

        # Logic thêm sản phẩm vào bảng tạm
        def add_item_to_list():
            ma_sp = ent_item_sp.get().strip()
            qty_str = ent_item_sl.get().strip()
            price_str = ent_item_gia.get().strip()

            if not (ma_sp and qty_str and price_str):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sản phẩm.")
                return
            try:
                qty = int(qty_str)
                price = float(price_str)
                if qty <= 0 or price <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng và Giá nhập phải là số dương lớn hơn 0.")
                return

            # Kiểm tra SP có tồn tại trong CSDL không
            sp_check = self.db.fetch_all(f"SELECT TenSP FROM SanPham WHERE MaSP='{ma_sp}'")
            if not sp_check:
                messagebox.showerror("Lỗi", f"Mã sản phẩm '{ma_sp}' không tồn tại hệ thống.")
                return

            thanh_tien = qty * price
            tree_detail.insert('', 'end', values=(ma_sp, qty, price, thanh_tien))
            recalculate_total()
            
            # Xóa sạch ô nhập để tiện nhập dòng tiếp theo
            ent_item_sp.delete(0, tk.END)
            ent_item_sl.delete(0, tk.END)
            ent_item_gia.delete(0, tk.END)

        def delete_item_from_list():
            selected = tree_detail.selection()
            if not selected:
                messagebox.showwarning("Cảnh báo", "Chọn dòng sản phẩm muốn xóa.")
                return
            for item in selected:
                tree_detail.delete(item)
            recalculate_total()

        # Nút điều hướng dòng (Chỉ xuất hiện khi tạo mới)
        if not is_view_mode:
            tk.Button(add_item_frame, text="➕ Thêm Dòng", bg='#4CAF50', fg='white', command=add_item_to_list).grid(row=0, column=6, padx=15)
            btn_del = tk.Button(win, text="❌ Xóa Dòng Chọn", bg='#FF5722', fg='white', command=delete_item_from_list)
            btn_del.pack(anchor='w', padx=15)
        else:
            # Ở chế độ xem: Truy vấn chi tiết sản phẩm từ Database ra để hiển thị
            query_details = f"""
                SELECT sp.MaSP, c.SoLuong, c.GiaNhap, (c.SoLuong * c.GiaNhap) AS ThanhTien
                FROM ChiTietPhieuNhap c
                JOIN PhieuNhapHang p ON c.IdPNH = p.IdPNH
                JOIN SanPham sp ON c.IdSP = sp.IdSP
                WHERE p.MaPNH = '{view_data[0]}'
            """
            for row in self.db.fetch_all(query_details):
                tree_detail.insert('', 'end', values=row)

        # --- PHẦN CUỐI: HIỂN THỊ TỔNG TIỀN VÀ NÚT LƯU CSDL ---
        bottom_frame = tk.Frame(win)
        bottom_frame.pack(fill='x', padx=15, pady=15)

        tk.Label(bottom_frame, text="TỔNG GIÁ TRỊ PHIẾU:", font=('Arial', 12, 'bold')).pack(side='left')
        tk.Label(bottom_frame, textvariable=total_var, font=('Arial', 14, 'bold'), fg='red').pack(side='left', padx=10)

        # Xử lý TRANSACTION lưu dữ liệu an toàn tuyệt đối vào MySQL (Cho Thêm Mới)
        def save_import_to_db():
            ma_pnh = ent_ma_pnh.get().strip()
            ma_ncc = ent_ma_ncc.get().strip()
            ma_nv = ent_ma_nv.get().strip()
            ngay_nhap = ent_ngay.get().strip()
            
            # THAY ĐỔI: Lấy giá trị trạng thái người dùng chọn từ Combobox
            trang_thai = cbo_status.get() 
            
            items = tree_detail.get_children()
            if not items:
                messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất 1 sản phẩm.")
                return

            # Kiểm tra Mã NCC, Mã NV tồn tại... (Logic cũ của bạn)
            res_ncc = self.db.fetch_all(f"SELECT IdNCC FROM NhaCungCap WHERE MaNCC='{ma_ncc}'")
            if not res_ncc: return messagebox.showerror("Lỗi", "Mã nhà cung cấp không khớp.")
            id_ncc = res_ncc[0][0]

            res_nv = self.db.fetch_all(f"SELECT IdNV FROM NhanVien WHERE MaNV='{ma_nv}'")
            if not res_nv: return messagebox.showerror("Lỗi", "Mã nhân viên không khớp.")
            id_nv = res_nv[0][0]

            tong_tien = sum(float(tree_detail.item(i, 'values')[3]) for i in items)

            try:
                self.db.execute_query("START TRANSACTION")
                
                # THAY ĐỔI: Truyền biến `trang_thai` từ combobox vào câu lệnh INSERT
                sql_pnh = "INSERT INTO PhieuNhapHang (MaPNH, TongGiaTri, NgayNhap, TrangThai, IdNCC, IdNV) VALUES (%s, %s, %s, %s, %s, %s)"
                self.db.execute_query(sql_pnh, (ma_pnh, tong_tien, ngay_nhap, trang_thai, id_ncc, id_nv))
                
                res_id_pnh = self.db.fetch_all(f"SELECT IdPN FROM PhieuNhapHang WHERE MaPNH='{ma_pnh}'")
                id_pnh = res_id_pnh[0][0]

                for item in items:
                    val = tree_detail.item(item, 'values')
                    ma_sp, so_luong, don_gia = val[0], int(val[1]), float(val[2])
                    
                    res_sp = self.db.fetch_all(f"SELECT IdSP FROM SanPham WHERE MaSP='{ma_sp}'")
                    id_sp = res_sp[0][0]

                    sql_ct = "INSERT INTO ChiTietPhieuNhap (IdPNH, IdSP, SoLuong, DonGia) VALUES (%s, %s, %s, %s)"
                    self.db.execute_query(sql_ct, (id_pnh, id_sp, so_luong, don_gia))

                    # Cộng kho khi nhập hàng
                    sql_congho = "UPDATE SanPham SET SoLuong = SoLuong + %s WHERE IdSP = %s"
                    self.db.execute_query(sql_congho, (so_luong, id_sp))

                self.db.execute_query("COMMIT")
                messagebox.showinfo("Thành công", "Đã lưu phiếu nhập hàng!")
                self.load_phieu_nhap_data()
                win.destroy()
            except Exception as e:
                self.db.execute_query("ROLLBACK")
                messagebox.showerror("Lỗi", f"Giao dịch hủy bỏ: {e}")

        # --- PHẦN ĐUÔI FORM (Hiển thị nút bấm duyệt hóa đơn cũ nếu cần) ---
        if not is_view_mode:
            tk.Button(bottom_frame, text="📥 LƯU PHIẾU NHẬP", font=('Arial', 11, 'bold'), bg='#007BFF', fg='white', width=22, command=save_import_to_db).pack(side='right')
        else:
            if current_status.lower() == 'chưa thanh toán':
                def update_import_payment_status():
                    if messagebox.askyesno("Xác nhận", "Chuyển phiếu nhập này thành 'Đã Thanh Toán'?"):
                        try:
                            self.db.execute_query(f"UPDATE PhieuNhapHang SET TrangThai = 'Đã Thanh Toán' WHERE MaPNH = '{view_data[0]}'")
                            self.db.execute_query("COMMIT")
                            messagebox.showinfo("Thành công", "Đã cập nhật trạng thái!")
                            self.load_phieu_nhap_data()
                            win.destroy()
                        except Exception as e: messagebox.showerror("Lỗi", str(e))
                tk.Button(bottom_frame, text="💰 XÁC NHẬN ĐÃ THANH TOÁN", font=('Arial', 11, 'bold'), bg='#28A745', fg='white', width=26, command=update_import_payment_status).pack(side='right') 

    def open_invoice_window(self, view_data=None):
        win = tk.Toplevel(self)
        win.title("Chi Tiết Hóa Đơn Khách Hàng")
        win.geometry("850x650")
        win.grab_set()

        total_var = tk.StringVar(value="0 VNĐ")
        is_view_mode = view_data is not None
        current_status = ""

        # --- PHẦN 1 & 2: THÔNG TIN CHUNG HÓA ĐƠN ---
        info_frame = tk.LabelFrame(win, text="Thông tin hóa đơn", font=('Arial', 11, 'bold'), pady=10, padx=10)
        info_frame.pack(fill='x', padx=15, pady=10)

        tk.Label(info_frame, text="Mã Hóa Đơn:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ent_ma_hd = tk.Entry(info_frame, width=15)
        ent_ma_hd.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(info_frame, text="Mã Khách Hàng:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ent_ma_kh = tk.Entry(info_frame, width=15)
        ent_ma_kh.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(info_frame, text="Mã Nhân Viên:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ent_ma_nv = tk.Entry(info_frame, width=15)
        ent_ma_nv.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(info_frame, text="Ngày Lập:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        ent_ngay = tk.Entry(info_frame, width=15)
        ent_ngay.grid(row=1, column=3, padx=5, pady=5)

        # THAY ĐỔI: Thêm nhãn Trạng thái cho hóa đơn
        tk.Label(info_frame, text="Trạng thái:").grid(row=2, column=0, padx=5, pady=5, sticky='w')

        if not is_view_mode:
            now = datetime.now()
            ent_ngay.insert(0, now.strftime("%Y-%m-%d %H:%M:%S"))
            
            # Tạo mã tự động (giữ nguyên logic của bạn)
            last_hd = self.db.fetch_all("SELECT MaHD FROM HoaDon ORDER BY IdHD DESC LIMIT 1")
            if last_hd and last_hd[0][0]:
                match = re.search(r'\d+', last_hd[0][0])
                if match:
                    new_id = int(match.group()) + 1
                    ent_ma_hd.insert(0, f"HD{new_id:03d}")
                else: ent_ma_hd.insert(0, "HD001")
            else: ent_ma_hd.insert(0, "HD001")
            
            # THAY ĐỔI: Thêm Combobox để chọn trạng thái khi TẠO MỚI HÓA ĐƠN
            cbo_status = ttk.Combobox(info_frame, values=["Chưa Thanh Toán", "Đã Thanh Toán"], width=15, state="readonly")
            cbo_status.set("Chưa Thanh Toán") # Hoặc đổi thành "Đã Thanh Toán" tùy ý bạn muốn mặc định trước
            cbo_status.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        else:
            ent_ma_hd.insert(0, view_data[0])
            ent_ma_kh.insert(0, view_data[1])
            ent_ngay.insert(0, view_data[3])
            total_var.set(f"{view_data[4]} VNĐ")
            
            nv_res = self.db.fetch_all(f"SELECT nv.MaNV, h.TrangThai FROM HoaDon h JOIN NhanVien nv ON h.IdNV = nv.IdNV WHERE h.MaHD='{view_data[0]}'")
            if nv_res: 
                ent_ma_nv.insert(0, nv_res[0][0])
                current_status = nv_res[0][1]
            
            status_color = 'red' if current_status.lower() == 'chưa thanh toán' else 'green'
            tk.Label(info_frame, text=current_status, fg=status_color, font=('Arial', 10, 'bold')).grid(row=2, column=1, padx=5, pady=5, sticky='w')
            
            ent_ma_hd.config(state='readonly')
            ent_ma_kh.config(state='readonly')
            ent_ma_nv.config(state='readonly')
            ent_ngay.config(state='readonly')

        # --- PHẦN 3: Ô CHỌN MUA SẢN PHẨM ---
        if not is_view_mode:
            add_item_frame = tk.LabelFrame(win, text="Thêm sản phẩm xuất hóa đơn", font=('Arial', 10, 'bold'))
            add_item_frame.pack(fill='x', padx=15, pady=5)

            tk.Label(add_item_frame, text="Mã SP:").grid(row=0, column=0, padx=5, pady=5)
            ent_item_sp = tk.Entry(add_item_frame, width=12)
            ent_item_sp.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(add_item_frame, text="Số Lượng:").grid(row=0, column=2, padx=5, pady=5)
            ent_item_sl = tk.Entry(add_item_frame, width=8)
            ent_item_sl.grid(row=0, column=3, padx=5, pady=5)

            tk.Label(add_item_frame, text="Đơn Giá:").grid(row=0, column=4, padx=5, pady=5)
            ent_item_gia = tk.Entry(add_item_frame, width=12)
            ent_item_gia.grid(row=0, column=5, padx=5, pady=5)

            # Sự kiện tự động điền đơn giá niêm yết khi gõ mã SP giúp tăng trải nghiệm UX
            def auto_fetch_price(event):
                sp_code = ent_item_sp.get().strip()
                if sp_code:
                    res = self.db.fetch_all(f"SELECT GiaBan FROM SanPham WHERE MaSP='{sp_code}'")
                    if res:
                        ent_item_gia.delete(0, tk.END)
                        ent_item_gia.insert(0, str(res[0][0]))
            ent_item_sp.bind("<FocusOut>", auto_fetch_price)

        # --- BẢNG CHI TIẾT HÓA ĐƠN ---
        table_frame = tk.Frame(win)
        table_frame.pack(fill='both', expand=True, padx=15, pady=10)

        cols = ("Mã sản phẩm", "Số lượng", "Đơn giá", "Thành tiền")
        tree_detail = ttk.Treeview(table_frame, columns=cols, show='headings', height=8)
        tree_detail.pack(side='left', fill='both', expand=True)
        
        for col in cols:
            tree_detail.heading(col, text=col)
            tree_detail.column(col, anchor='center', width=130)

        def recalculate_total():
            grand_total = 0
            for item in tree_detail.get_children():
                grand_total += float(tree_detail.item(item, 'values')[3])
            total_var.set(f"{grand_total:,.0f} VNĐ")

        def add_item_to_list():
            ma_sp = ent_item_sp.get().strip()
            qty_str = ent_item_sl.get().strip()
            price_str = ent_item_gia.get().strip()

            if not (ma_sp and qty_str and price_str):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin hàng hóa.")
                return
            try:
                qty = int(qty_str)
                price = float(price_str)
                if qty <= 0 or price <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng và Đơn giá phải lớn hơn 0.")
                return

            # Kiểm tra xem sản phẩm có tồn kho đủ để xuất không
            sp_check = self.db.fetch_all(f"SELECT SoLuong FROM SanPham WHERE MaSP='{ma_sp}'")
            if not sp_check:
                messagebox.showerror("Lỗi", "Mã sản phẩm không có sẵn trên hệ thống.")
                return
            elif sp_check[0][0] < qty:
                messagebox.showerror("Lỗi", f"Sản phẩm tồn kho không đủ! (Hiện còn {sp_check[0][0]} sản phẩm)")
                return

            thanh_tien = qty * price
            tree_detail.insert('', 'end', values=(ma_sp, qty, price, thanh_tien))
            recalculate_total()
            
            ent_item_sp.delete(0, tk.END)
            ent_item_sl.delete(0, tk.END)
            ent_item_gia.delete(0, tk.END)

        def delete_item_from_list():
            selected = tree_detail.selection()
            if not selected: return
            for item in selected:
                tree_detail.delete(item)
            recalculate_total()

        if not is_view_mode:
            tk.Button(add_item_frame, text="➕ Thêm Dòng", bg='#4CAF50', fg='white', command=add_item_to_list).grid(row=0, column=6, padx=15)
            tk.Button(win, text="❌ Xóa Dòng Chọn", bg='#FF5722', fg='white', command=delete_item_from_list).pack(anchor='w', padx=15)
        else:
            query_details = f"""
                SELECT sp.MaSP, c.SoLuong, c.DonGia, (c.SoLuong * c.DonGia) AS ThanhTien
                FROM ChiTietHoaDon c
                JOIN HoaDon h ON c.IdHD = h.IdHD
                JOIN SanPham sp ON c.IdSP = sp.IdSP
                WHERE h.MaHD = '{view_data[0]}'
            """
            for row in self.db.fetch_all(query_details):
                tree_detail.insert('', 'end', values=row)

        # --- KHUNG TỔNG KẾT VÀ LƯU HÓA ĐƠN ---
        bottom_frame = tk.Frame(win)
        bottom_frame.pack(fill='x', padx=15, pady=15)

        tk.Label(bottom_frame, text="TỔNG TIỀN THANH TOÁN:", font=('Arial', 12, 'bold')).pack(side='left')
        tk.Label(bottom_frame, textvariable=total_var, font=('Arial', 14, 'bold'), fg='blue').pack(side='left', padx=10)

        # DATABASE TRANSACTION CHO HÓA ĐƠN KHÁCH HÀNG
        def save_invoice_to_db():
            ma_hd = ent_ma_hd.get().strip()
            ma_kh = ent_ma_kh.get().strip()
            ma_nv = ent_ma_nv.get().strip()
            ngay_lap = ent_ngay.get().strip()
            
            # THAY ĐỔI: Lấy trạng thái do người dùng chọn từ Combobox
            trang_thai = cbo_status.get() 
            
            items = tree_detail.get_children()
            if not items:
                messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất 1 sản phẩm trước khi thanh toán.")
                return

            res_kh = self.db.fetch_all(f"SELECT IdKH FROM KhachHang WHERE MaKH='{ma_kh}'")
            if not res_kh: return messagebox.showerror("Lỗi", "Mã khách hàng không khớp.")
            id_kh = res_kh[0][0]

            res_nv = self.db.fetch_all(f"SELECT IdNV FROM NhanVien WHERE MaNV='{ma_nv}'")
            if not res_nv: return messagebox.showerror("Lỗi", "Mã nhân viên bán hàng không khớp.")
            id_nv = res_nv[0][0]

            tong_tien = sum(float(tree_detail.item(i, 'values')[3]) for i in items)

            try:
                self.db.execute_query("START TRANSACTION")
                
                # THAY ĐỔI: Gán biến `trang_thai` từ combobox vào câu lệnh INSERT thay vì gán cứng
                sql_hd = "INSERT INTO HoaDon (MaHD, TongGiaTri, NgayLap, TrangThai, IdKH, IdNV) VALUES (%s, %s, %s, %s, %s, %s)"
                self.db.execute_query(sql_hd, (ma_hd, tong_tien, ngay_lap, trang_thai, id_kh, id_nv))
                
                res_id_hd = self.db.fetch_all(f"SELECT IdHD FROM HoaDon WHERE MaHD='{ma_hd}'")
                id_hd = res_id_hd[0][0]

                for item in items:
                    val = tree_detail.item(item, 'values')
                    ma_sp, so_luong, don_gia = val[0], int(val[1]), float(val[2])
                    
                    res_sp = self.db.fetch_all(f"SELECT IdSP, SoLuong FROM SanPham WHERE MaSP='{ma_sp}'")
                    id_sp = res_sp[0][0]
                    curr_stock = res_sp[0][1]

                    if curr_stock < so_luong:
                        raise Exception(f"Sản phẩm {ma_sp} không còn đủ số lượng tồn kho.")

                    sql_ct = "INSERT INTO ChiTietHoaDon (IdHD, IdSP, SoLuong, DonGia) VALUES (%s, %s, %s, %s)"
                    self.db.execute_query(sql_ct, (id_hd, id_sp, so_luong, don_gia))

                    # Xuất kho: trừ số lượng tương ứng
                    sql_trukho = "UPDATE SanPham SET SoLuong = SoLuong - %s WHERE IdSP = %s"
                    self.db.execute_query(sql_trukho, (so_luong, id_sp))

                self.db.execute_query("COMMIT")
                messagebox.showinfo("Thành công", "Đã xuất hóa đơn thành công!")
                self.load_hoa_don_data()
                win.destroy()
            except Exception as e:
                self.db.execute_query("ROLLBACK")
                messagebox.showerror("Giao dịch hủy bỏ", f"Quá trình thất bại: {e}")

        # --- PHẦN ĐUÔI HIỂN THỊ NÚT BẤM DUYỆT HÓA ĐƠN XEM LẠI ---
        if not is_view_mode:
            tk.Button(bottom_frame, text="💳 XUẤT HÓA ĐƠN", font=('Arial', 11, 'bold'), bg='#007BFF', fg='white', width=22, command=save_invoice_to_db).pack(side='right')
        else:
            if current_status.lower() == 'chưa thanh toán':
                def update_invoice_payment_status():
                    if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn chuyển hóa đơn này thành 'Đã Thanh Toán'?"):
                        try:
                            self.db.execute_query(f"UPDATE HoaDon SET TrangThai = 'Đã Thanh Toán' WHERE MaHD = '{view_data[0]}'")
                            self.db.execute_query("COMMIT")
                            messagebox.showinfo("Thành công", "Hóa đơn đã chuyển sang trạng thái 'Đã Thanh Toán'!")
                            self.load_hoa_don_data()
                            win.destroy()
                        except Exception as e: messagebox.showerror("Lỗi", str(e))
                tk.Button(bottom_frame, text="💰 XÁC NHẬN ĐÃ THANH TOÁN", font=('Arial', 11, 'bold'), bg='#28A745', fg='white', width=26, command=update_invoice_payment_status).pack(side='right') 

if __name__ == "__main__":
    app = BeverageManagementSystem()
    app.mainloop()