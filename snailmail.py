# Email set up and sending
import graphing

def send_email(attachment_path=None):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("danielpicone2@gmail.com")
    to_email = Email("danielpicone2@gmail.com")
    subject = "Stock report for " + today_date
    content = Content("text/plain", "This is just an update for your stock portfolio")
    mail = Mail(from_email, subject, to_email, content)

    if attachment_path:
        attachment = create_attachment(attachment_path = None)
        mail.add_attachment(attachment)


    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

def create_attachment(attachment_path = None):
    if attachment_path:
        import base64
        attachment = Attachment()
        with open(attachment_path, "rb") as f:
            data = f.read()

        encoded = base64.b64encode(data).decode()
        attachment.content=encoded
        attachment.type="application/pdf"
        attachment.filename="Stock report for " + today_date + ".pdf"
        attachment.disposition="attachment"
        attachment.content_id="PDF Document file"
        return attachment
    else:
        print("No attachment to create")
        return False


def generate_email(file_name = "portfolio_charts.pdf"):
    graphing.graph_indiv_stock(file_name)
    send_email(file_name)
    return True
