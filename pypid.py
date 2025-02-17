import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import io
from reportlab.pdfgen import canvas as rl_canvas
from PyPDF2 import PdfReader, PdfWriter

# Global variables for region selection and template info
start_x, start_y = None, None
rect = None
selected_region = None
template_pdf = None   # Path to the uploaded PDF
template_image = None # PIL image from the PDF
photo_image = None    # Tkinter image reference

def upload_pdf():
    global template_pdf, template_image, photo_image
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        template_pdf = file_path
        try:
            # Convert first page of PDF to image for display
            pages = convert_from_path(file_path, first_page=1, last_page=1)
            if not pages:
                raise Exception("No pages found in PDF")
            template_image = pages[0]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert PDF: {e}")
            return

        # Resize image to fit the canvas if needed
        template_image.thumbnail((600, 800))
        photo_image = ImageTk.PhotoImage(template_image)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=photo_image)
        canvas.config(width=photo_image.width(), height=photo_image.height())
        messagebox.showinfo("Success", "PDF loaded. Now select the region for the names.")

def on_button_press(event):
    global start_x, start_y, rect
    start_x = event.x
    start_y = event.y
    rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

def on_move_press(event):
    curX, curY = event.x, event.y
    canvas.coords(rect, start_x, start_y, curX, curY)

def on_button_release(event):
    global selected_region
    end_x, end_y = event.x, event.y
    selected_region = (min(start_x, end_x), min(start_y, end_y),
                       max(start_x, end_x), max(start_y, end_y))
    messagebox.showinfo("Region Selected", f"Region: {selected_region}")

def generate_certificates():
    if not selected_region:
        messagebox.showwarning("No Region", "Please select a region for the name placement.")
        return
    names_text = names_entry.get("1.0", tk.END).strip()
    if not names_text:
        messagebox.showwarning("No Names", "Please enter names (one per line).")
        return
    names = names_text.splitlines()

    # Open PDF in binary mode and ensure there's at least one page.
    try:
        with open(template_pdf, "rb") as f:
            template_reader = PdfReader(f)
            if len(template_reader.pages) < 1:
                raise Exception("PDF has no pages")
            template_page = template_reader.pages[0]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read template PDF: {e}")
        return

    page_width = float(template_page.mediabox.width)
    page_height = float(template_page.mediabox.height)

    # Compute scaling factors from the displayed image to the actual PDF page
    scale_x = page_width / photo_image.width()
    scale_y = page_height / photo_image.height()

    for name in names:
        packet = io.BytesIO()
        # Create overlay PDF with ReportLab
        c = rl_canvas.Canvas(packet, pagesize=(page_width, page_height))
        x, y, x2, y2 = selected_region
        # Convert canvas coordinates to PDF coordinates
        pdf_x = x * scale_x
        pdf_y = y * scale_y
        pdf_x2 = x2 * scale_x
        pdf_y2 = y2 * scale_y
        text_x = pdf_x + (pdf_x2 - pdf_x) / 2
        # PDF coordinate origin is bottom-left so invert y-axis
        text_y = page_height - (pdf_y + (pdf_y2 - pdf_y) / 2)
        c.setFont("Helvetica", 20)
        c.drawCentredString(text_x, text_y, name)
        c.save()
        packet.seek(0)

        try:
            overlay_pdf = PdfReader(packet)
            overlay_page = overlay_pdf.pages[0]
            new_page = template_page
            new_page.merge_page(overlay_page)
            writer = PdfWriter()
            writer.add_page(new_page)
            output_filename = f"certificate_{name.replace(' ', '_')}.pdf"
            with open(output_filename, "wb") as out_f:
                writer.write(out_f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate certificate for {name}: {e}")
            continue

    messagebox.showinfo("Done", "Certificates generated successfully.")

# ---------------------- UI Setup with Dark Theme ---------------------- #
root = tk.Tk()
root.title("Certificate Generator")
root.configure(bg="#2E2E2E")  # Dark background

# Use ttk styling for a modern look
style = ttk.Style(root)
# Attempt to use a built-in theme; "clam" works well with custom colors
if "clam" in style.theme_names():
    style.theme_use("clam")
style.configure("TButton", background="#444444", foreground="white", borderwidth=1, padding=5)
style.configure("TLabel", background="#2E2E2E", foreground="white", padding=5)

# Upload Button
upload_btn = ttk.Button(root, text="Upload Template PDF", command=upload_pdf)
upload_btn.pack(pady=5)

# Canvas to display the PDF page
canvas = tk.Canvas(root, width=600, height=800, bg="#3E3E3E", highlightthickness=0)
canvas.pack(padx=10, pady=10)
canvas.bind("<ButtonPress-1>", on_button_press)
canvas.bind("<B1-Motion>", on_move_press)
canvas.bind("<ButtonRelease-1>", on_button_release)

# Names entry section
label = ttk.Label(root, text="Enter Names (one per line):")
label.pack(pady=5)
names_entry = tk.Text(root, height=10, width=50, bg="#444444", fg="white", insertbackground="white")
names_entry.pack(padx=10, pady=5)

# Generate Certificates Button
gen_btn = ttk.Button(root, text="Generate Certificates", command=generate_certificates)
gen_btn.pack(pady=10)

root.mainloop()
