
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3, os
from datetime import datetime

DB = "restaurant.db"
def db_connect():
    return sqlite3.connect(DB)

class GustoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gusto e Pasta - Restaurant Management v2")
        self.geometry("1100x700")
        self.configure(bg="#fff7f3")
        self.create_styles()
        self.create_layout()
        self.show_home()
        self.refresh_all()

    def create_styles(self):
        style = ttk.Style(self)
        style.configure("sidebar.TFrame", background="#ff8a4b")
        style.configure("page.TFrame", background="#fff7f3")
        style.configure("h1.TLabel", background="#fff7f3", font=("Helvetica", 26, "bold"))
        style.configure("h2.TLabel", background="#fff7f3", font=("Helvetica", 16, "bold"))

    def create_layout(self):
        self.sidebar = ttk.Frame(self, style="sidebar.TFrame", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.content = ttk.Frame(self, style="page.TFrame")
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        logo = tk.Label(self.sidebar, text="🍝\nGusto e Pasta", bg="#ff8a4b", fg="white", font=("Segoe UI", 16, "bold"), justify="center")
        logo.pack(pady=(20,10))

        btns = [("Home", self.show_home), ("Menu & Orders", self.show_menu_orders), ("Tables", self.show_tables),
                ("Orders (Manage)", self.show_orders_manage), ("Sales", self.show_sales), ("Staff", self.show_staff)]
        for txt, cmd in btns:
            b = ttk.Button(self.sidebar, text=txt, command=cmd)
            b.pack(fill="x", padx=12, pady=6)

        self.pages = {}
        for name in ("home","menu","tables","orders_manage","sales","staff"):
            f = ttk.Frame(self.content, style="page.TFrame")
            f.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[name] = f

        self.build_home(self.pages["home"])
        self.build_menu(self.pages["menu"])
        self.build_tables(self.pages["tables"])
        self.build_orders_manage(self.pages["orders_manage"])
        self.build_sales(self.pages["sales"])
        self.build_staff(self.pages["staff"])

    def hide_all(self):
        for p in self.pages.values():
            p.lower()

    def show_home(self):
        self.hide_all(); self.pages["home"].lift()

    def show_menu_orders(self):
        self.hide_all(); self.pages["menu"].lift(); self.refresh_menu_items(); self.refresh_table_combobox()

    def show_tables(self):
        self.hide_all(); self.pages["tables"].lift(); self.refresh_tables_view()

    def show_orders_manage(self):
        self.hide_all(); self.pages["orders_manage"].lift(); self.refresh_orders_list()

    def show_sales(self):
        self.hide_all(); self.pages["sales"].lift(); self.refresh_sales_view()

    def show_staff(self):
        self.hide_all(); self.pages["staff"].lift(); self.refresh_staff_view()

    def build_home(self, frame):
        ttk.Label(frame, text="Welcome to Gusto e Pasta", style="h1.TLabel").pack(pady=20)
        ttk.Label(frame, text="Now tables that are Occupied/Reserved cannot take new orders.", style="h2.TLabel").pack(pady=10)
        ttk.Button(frame, text="Go to Menu", command=self.show_menu_orders).pack(pady=10)

    def build_menu(self, frame):
        ttk.Label(frame, text="📋 Menu & Orders", style="h1.TLabel").pack(pady=8)
        container = ttk.Frame(frame); container.pack(fill="both", expand=True, pady=10)
        left = ttk.Frame(container, width=350); left.pack(side="left", fill="y", padx=10)
        ttk.Label(left, text="Table No:").pack(anchor="w")
        self.table_cb = ttk.Combobox(left, values=[]); self.table_cb.pack(anchor="w", pady=5)
        ttk.Label(left, text="Select Items:").pack(anchor="w")
        self.menu_checks = ttk.Frame(left); self.menu_checks.pack(fill="y", expand=True)
        ttk.Button(left, text="Place Order", command=self.place_order).pack(pady=8)
        right = ttk.Frame(container); right.pack(side="left", fill="both", expand=True, padx=10)
        ttk.Label(right, text="Cart", style="h2.TLabel").pack(anchor="nw")
        cols = ("menu","qty","price","subtotal")
        self.cart_tree = ttk.Treeview(right, columns=cols, show="headings", height=12)
        for c in cols: self.cart_tree.heading(c, text=c.title())
        self.cart_tree.pack(fill="both", expand=True, pady=5)
        ttk.Button(right, text="Clear Selection", command=self.clear_selection).pack(pady=5)
        self.menu_vars = {}

    def refresh_menu_items(self):
        for w in self.menu_checks.winfo_children(): w.destroy()
        conn = db_connect(); c = conn.cursor()
        c.execute("SELECT id, name, price FROM menu ORDER BY category, name")
        rows = c.fetchall(); conn.close()
        self.menu_vars = {}
        for mid, name, price in rows:
            var = tk.IntVar(value=0)
            f = ttk.Frame(self.menu_checks); f.pack(anchor="w", pady=2, fill="x")
            chk = ttk.Checkbutton(f, text=f"{name} - ${price:.2f}", variable=var); chk.pack(side="left")
            qty = ttk.Entry(f, width=4); qty.insert(0,"1"); qty.pack(side="left", padx=8)
            self.menu_vars[mid] = (var, qty, name, price)

    def refresh_table_combobox(self):
        # only list tables that are Available (not reserved and not occupied)
        conn = db_connect(); c = conn.cursor()
        c.execute("SELECT table_no FROM tables WHERE reserved=0 AND occupied=0 ORDER BY table_no")
        rows = [r[0] for r in c.fetchall()]; conn.close()
        self.table_cb['values'] = rows

    def place_order(self):
        # ensure table selected and available
        try:
            table_no = int(self.table_cb.get())
        except:
            messagebox.showerror("Error", "Select a valid available table from dropdown.")
            return
        conn = db_connect(); c = conn.cursor()
        c.execute("SELECT reserved, occupied FROM tables WHERE table_no=?", (table_no,))
        row = c.fetchone()
        if not row:
            messagebox.showerror("Error", "Table not found."); conn.close(); return
        reserved, occupied = row
        if reserved or occupied:
            messagebox.showwarning("Unavailable", f"Table {table_no} is reserved or occupied. Cannot place order.")
            conn.close(); return
        selections = []
        for mid, (var, qty_entry, name, price) in self.menu_vars.items():
            if var.get():
                try:
                    q = int(qty_entry.get()); 
                    if q <= 0: continue
                except:
                    q = 1
                selections.append((mid, name, q, price))
        if not selections:
            messagebox.showinfo("No items", "Select items to order."); conn.close(); return
        total = sum(q*p for (_,_,q,p) in selections)
        c.execute("INSERT INTO orders (table_no, total, paid, created_at) VALUES (?, ?, ?, ?)", (table_no, total, 0, datetime.now().isoformat()))
        oid = c.lastrowid
        for mid, name, q, price in selections:
            c.execute("INSERT INTO order_items (order_id, menu_id, qty, price) VALUES (?, ?, ?, ?)", (oid, mid, q, price))
        # mark table as occupied
        c.execute("UPDATE tables SET occupied=1 WHERE table_no=?", (table_no,))
        conn.commit(); conn.close()
        messagebox.showinfo("Order Placed", f"Order #{oid} placed. Table {table_no} now Occupied.")
        self.clear_selection(); self.refresh_table_combobox(); self.refresh_orders_list(); self.refresh_sales_view()

    def clear_selection(self):
        for mid, (var, qty_entry, name, price) in self.menu_vars.items():
            var.set(0)
            qty_entry.delete(0, 'end'); qty_entry.insert(0, "1")
        for i in self.cart_tree.get_children(): self.cart_tree.delete(i)

    def build_tables(self, frame):
        ttk.Label(frame, text="🪑 Table Management", style="h1.TLabel").pack(pady=6)
        self.tables_tree = ttk.Treeview(frame, columns=("table","status"), show="headings", height=8)
        self.tables_tree.heading("table", text="Table No"); self.tables_tree.heading("status", text="Status")
        self.tables_tree.pack(pady=8)
        btnf = ttk.Frame(frame); btnf.pack(pady=6)
        ttk.Button(btnf, text="Reserve", command=self.reserve_table_dialog).pack(side="left", padx=4)
        ttk.Button(btnf, text="Cancel Reservation", command=self.cancel_reservation).pack(side="left", padx=4)
        ttk.Button(btnf, text="Set Available", command=self.set_table_available).pack(side="left", padx=4)
        ttk.Button(btnf, text="Refresh", command=self.refresh_tables_view).pack(side="left", padx=4)

    def refresh_tables_view(self):
        for i in self.tables_tree.get_children(): self.tables_tree.delete(i)
        conn = db_connect(); c = conn.cursor()
        for row in c.execute("SELECT table_no, reserved, reserved_name, reserved_time, occupied FROM tables ORDER BY table_no"):
            t, reserved, rname, rtime, occupied = row
            status = "Available"
            if reserved: status = f"Reserved ({rname})"
            if occupied: status = "Occupied"
            self.tables_tree.insert("", "end", values=(t, status))
        conn.close()

    def reserve_table_dialog(self):
        try:
            table_no = int(simpledialog.askstring("Table No","Enter table number to reserve:"))
        except: return
        name = simpledialog.askstring("Name","Reservation name:"); 
        if not name: return
        time = simpledialog.askstring("Time","Reservation time (e.g. 2025-11-03 19:00):")
        conn = db_connect(); c = conn.cursor()
        c.execute("SELECT reserved FROM tables WHERE table_no=?", (table_no,))
        r = c.fetchone()
        if not r: messagebox.showerror("Error","Table not found"); conn.close(); return
        if r[0]: messagebox.showinfo("Already","Table already reserved"); conn.close(); return
        c.execute("UPDATE tables SET reserved=1, reserved_name=?, reserved_time=? WHERE table_no=?", (name, time, table_no))
        conn.commit(); conn.close(); messagebox.showinfo("Reserved", f"Table {table_no} reserved for {name} at {time}"); self.refresh_tables_view(); self.refresh_table_combobox()

    def cancel_reservation(self):
        try:
            table_no = int(simpledialog.askstring("Table No","Enter table number to cancel reservation:"))
        except: return
        conn = db_connect(); c = conn.cursor()
        c.execute("UPDATE tables SET reserved=0, reserved_name=NULL, reserved_time=NULL WHERE table_no=?", (table_no,))
        conn.commit(); conn.close(); messagebox.showinfo("Cancelled", f"Reservation for table {table_no} cancelled"); self.refresh_tables_view(); self.refresh_table_combobox()

    def set_table_available(self):
        try:
            table_no = int(simpledialog.askstring("Table No","Enter table number to set available:"))
        except: return
        conn = db_connect(); c = conn.cursor()
        c.execute("UPDATE tables SET occupied=0 WHERE table_no=?", (table_no,))
        conn.commit(); conn.close(); messagebox.showinfo("Updated", f"Table {table_no} set to Available"); self.refresh_tables_view(); self.refresh_table_combobox()

    def build_orders_manage(self, frame):
        ttk.Label(frame, text="🧾 Orders Management", style="h1.TLabel").pack(pady=6)
        cols = ("order_id","table_no","total","paid","created_at")
        self.orders_tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        for c in cols: self.orders_tree.heading(c, text=c.title())
        self.orders_tree.pack(pady=8, fill="x")
        btnf = ttk.Frame(frame); btnf.pack(pady=6)
        ttk.Button(btnf, text="Mark Paid (set table Available)", command=self.mark_paid).pack(side="left", padx=6)
        ttk.Button(btnf, text="Refresh", command=self.refresh_orders_list).pack(side="left", padx=6)

    def refresh_orders_list(self):
        for i in self.orders_tree.get_children(): self.orders_tree.delete(i)
        conn = db_connect(); c = conn.cursor()
        for row in c.execute("SELECT id, table_no, total, paid, created_at FROM orders ORDER BY created_at DESC"):
            self.orders_tree.insert("", "end", values=row)
        conn.close()

    def mark_paid(self):
        sel = self.orders_tree.selection()
        if not sel: messagebox.showinfo("Select","Select an order"); return
        item = self.orders_tree.item(sel[0])['values']
        oid, table_no, total, paid, created_at = item
        if paid:
            messagebox.showinfo("Already", "Order already paid"); return
        conn = db_connect(); c = conn.cursor()
        c.execute("UPDATE orders SET paid=1 WHERE id=?", (oid,))
        # Set table available when paid
        c.execute("UPDATE tables SET occupied=0 WHERE table_no=?", (table_no,))
        conn.commit(); conn.close()
        messagebox.showinfo("Paid", f"Order #{oid} marked paid. Table {table_no} now Available.")
        self.refresh_orders_list(); self.refresh_tables_view(); self.refresh_table_combobox(); self.refresh_sales_view()

    def build_sales(self, frame):
        ttk.Label(frame, text="💰 Sales", style="h1.TLabel").pack(pady=6)
        self.sales_lbl = ttk.Label(frame, text="Total Revenue: $0.00\nTotal Orders: 0", background="#fff7f3", font=("Helvetica", 14))
        self.sales_lbl.pack(pady=8)
        cols = ("order_id","table_no","total","paid","created_at")
        self.sales_tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c in cols: self.sales_tree.heading(c, text=c.title())
        self.sales_tree.pack(pady=8, fill="x")
        ttk.Button(frame, text="Refresh Sales", command=self.refresh_sales_view).pack(pady=6)

    def refresh_sales_view(self):
        for i in self.sales_tree.get_children(): self.sales_tree.delete(i)
        conn = db_connect(); c = conn.cursor()
        total = 0.0; orders_count = 0
        for row in c.execute("SELECT id, table_no, total, paid, created_at FROM orders ORDER BY created_at DESC"):
            self.sales_tree.insert("", "end", values=row)
            total += row[2]; orders_count += 1
        conn.close()
        self.sales_lbl.config(text=f"Total Revenue: ${total:.2f}\\nTotal Orders: {orders_count}")

    def build_staff(self, frame):
        ttk.Label(frame, text="👥 Staff", style="h1.TLabel").pack(pady=6)
        cols = ("id","name","role")
        self.staff_tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c in cols: self.staff_tree.heading(c, text=c.title())
        self.staff_tree.pack(pady=8, fill="x")
        frm = ttk.Frame(frame); frm.pack(pady=6)
        ttk.Label(frm, text="Name:").grid(row=0, column=0); self.staff_name = ttk.Entry(frm); self.staff_name.grid(row=0, column=1)
        ttk.Label(frm, text="Role:").grid(row=0, column=2); self.staff_role = ttk.Entry(frm); self.staff_role.grid(row=0, column=3)
        ttk.Button(frm, text="Add", command=self.add_staff).grid(row=0, column=4, padx=6)
        ttk.Button(frm, text="Delete", command=self.delete_staff).grid(row=0, column=5, padx=6)

    def refresh_staff_view(self):
        for i in self.staff_tree.get_children(): self.staff_tree.delete(i)
        conn = db_connect(); c = conn.cursor()
        for row in c.execute("SELECT id,name,role FROM staff"): self.staff_tree.insert("", "end", values=row)
        conn.close()

    def add_staff(self):
        name = self.staff_name.get().strip(); role = self.staff_role.get().strip()
        if not name: return
        conn = db_connect(); c = conn.cursor(); c.execute("INSERT INTO staff (name, role) VALUES (?, ?)", (name, role)); conn.commit(); conn.close()
        self.staff_name.delete(0,'end'); self.staff_role.delete(0,'end'); self.refresh_staff_view()

    def delete_staff(self):
        sel = self.staff_tree.selection()
        if not sel: return
        sid = self.staff_tree.item(sel[0])['values'][0]
        conn = db_connect(); c = conn.cursor(); c.execute("DELETE FROM staff WHERE id=?", (sid,)); conn.commit(); conn.close(); self.refresh_staff_view()

    def refresh_all(self):
        self.refresh_menu_items(); self.refresh_table_combobox(); self.refresh_tables_view(); self.refresh_staff_view(); self.refresh_sales_view(); self.refresh_orders_list()

if __name__ == '__main__':
    # ensure DB in same folder
    try:
        from db_init import init_db
        init_db()
    except Exception as e:
        print("DB init failed:", e)
    app = GustoApp(); app.mainloop()
