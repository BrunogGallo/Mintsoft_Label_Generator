import base64
from dotenv import load_dotenv
import smtplib
from PIL import Image
import os
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
load_dotenv()

class MailService():
        def send_label_email(self, client_name, order_number, label):
            # Configuración del servidor (Ejemplo con Gmail)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = os.getenv("EMAIL_USER")
            sender_password = os.getenv("EMAIL_PASSWORD")
            receiver = "bgallo@the5411.com" # online@the5411.com

            message = MIMEMultipart("alternative")
            message["Subject"] = f"Shipping label para '{order_number}' - Cliente: {client_name}"
            message["From"] = sender_email
            message["To"] = receiver

            body = f"Hola,\n\nSe ha generado la shipping label para la orden {order_number}.\nCliente: {client_name}"
            message.attach(MIMEText(body, "plain"))

            try:
                # Pasar label de base64 a formato pdf
                image_data = base64.b64decode(label)
                img = Image.open(io.BytesIO(image_data))

                if img.mode != 'RGB':
                    img = img.convert('RGB')
            
                pdf_buffer = io.BytesIO()
                img.save(pdf_buffer, format="PDF")
                pdf_bytes = pdf_buffer.getvalue()

                part = MIMEApplication(pdf_bytes, Name=f"Label_{order_number}.pdf")
                part['Content-Disposition'] = f'attachment; filename="Label_{order_number}.pdf"'
                message.attach(part)

                # 4. Envío del correo
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver, message.as_string())
                server.quit()
                
                print(f"📧 Email enviado con éxito para la orden {order_number}")

            except Exception as e:
                print(f"❌ Error enviando email: {e}")

